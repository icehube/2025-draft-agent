import streamlit as st
import pandas as pd
import numpy as np
import json
from fantasy_auction import FantasyAuction, teams_data, SALARY, FORWARD, DEFENCE, GOALIE

# Page configuration
st.set_page_config(
    page_title="Fantasy Hockey Auction Manager",
    page_icon="🏒",
    layout="wide"
)

# Initialize session state
if 'auction' not in st.session_state:
    st.session_state.auction = None
if 'players_df' not in st.session_state:
    st.session_state.players_df = None
if 'baseline_df' not in st.session_state:
    st.session_state.baseline_df = None

def load_csv_data(uploaded_file):
    """Load and process CSV data"""
    try:
        df = pd.read_csv(uploaded_file)
        # Ensure required columns exist
        required_columns = ['PLAYER', 'POS', 'GROUP', 'STATUS', 'FCHL TEAM', 'NHL TEAM', 'AGE', 'SALARY', 'BID', 'PTS']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
            return None
            
        # Convert data types
        df['AGE'] = pd.to_numeric(df['AGE'], errors='coerce').fillna(0).astype(int)
        df['PTS'] = pd.to_numeric(df['PTS'], errors='coerce').fillna(0).astype(int)
        df['SALARY'] = pd.to_numeric(df['SALARY'], errors='coerce').fillna(0.0)
        df['BID'] = pd.to_numeric(df['BID'], errors='coerce').fillna(0.0)
        
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return None

def display_team_budgets():
    """Display team budget summary"""
    if st.session_state.auction is None:
        return
        
    team_budgets = st.session_state.auction.get_team_budgets()
    
    st.subheader("Team Budget Summary")
    
    # Create budget summary table
    budget_data = []
    for team_code, budget in team_budgets.items():
        budget_data.append({
            'Team': budget['name'],
            'Code': team_code,
            'F': budget['f_count'],
            'D': budget['d_count'],
            'G': budget['g_count'],
            'Committed': f"${budget['committed_salary']:.1f}",
            'Auction': f"${budget['auction_spending']:.1f}",
            'Penalty': f"${budget['penalty']:.1f}",
            'Total Spent': f"${budget['total_spent']:.1f}",
            'Remaining': f"${budget['remaining']:.1f}",
            'Status': '✅' if budget['remaining'] >= 0 else '❌'
        })
    
    budget_df = pd.DataFrame(budget_data)
    st.dataframe(budget_df, use_container_width=True)
    
    # League summary
    total_committed = sum(b['committed_salary'] for b in team_budgets.values())
    total_auction = sum(b['auction_spending'] for b in team_budgets.values())
    total_penalties = sum(b['penalty'] for b in team_budgets.values())
    total_spent = total_committed + total_auction + total_penalties
    total_available = (SALARY * 11) - total_spent
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Pool", f"${SALARY * 11:.1f}")
    with col2:
        st.metric("Total Committed", f"${total_committed:.1f}")
    with col3:
        st.metric("Total Auction", f"${total_auction:.1f}")
    with col4:
        st.metric("Available", f"${total_available:.1f}")

def player_assignment_interface():
    """Interface for assigning players to teams"""
    if st.session_state.auction is None or st.session_state.players_df is None:
        return
    
    st.subheader("Player Assignment")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        position_filter = st.selectbox(
            "Filter by Position",
            ["All", "F", "D", "G"]
        )
    
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "UFA", "RFA", "ENT", "START", "MINOR", "AUCTION"]
        )
    
    with col3:
        team_filter = st.selectbox(
            "Filter by Team",
            ["All"] + list(teams_data.keys())
        )
    
    # Apply filters
    filtered_df = st.session_state.players_df.copy()
    
    if position_filter != "All":
        filtered_df = filtered_df[filtered_df['POS'] == position_filter]
    
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['STATUS'] == status_filter]
    
    if team_filter != "All":
        filtered_df = filtered_df[filtered_df['FCHL TEAM'] == team_filter]
    
    # Display filtered players
    if not filtered_df.empty:
        # Select columns to display
        display_columns = ['PLAYER', 'POS', 'PTS', 'FCHL TEAM', 'STATUS', 'SALARY', 'BID']
        display_df = filtered_df[display_columns].copy()
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # Player assignment form
        st.subheader("Assign Player to Team")
        
        # Player selection
        available_players = filtered_df[filtered_df['FCHL TEAM'].isin(['UFA', 'RFA', 'ENT'])]
        
        if not available_players.empty:
            player_options = [(idx, f"{row['PLAYER']} ({row['POS']}) - {row['PTS']} pts") 
                            for idx, row in available_players.iterrows()]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_player = st.selectbox(
                    "Select Player",
                    options=[None] + player_options,
                    format_func=lambda x: "Select a player..." if x is None else x[1]
                )
            
            with col2:
                selected_team = st.selectbox(
                    "Assign to Team",
                    options=list(teams_data.keys()),
                    format_func=lambda x: f"{x} - {teams_data[x]['name']}"
                )
            
            with col3:
                auction_price = st.number_input(
                    "Auction Price",
                    min_value=0.0,
                    max_value=20.0,
                    value=1.0,
                    step=0.1
                )
            
            if st.button("Assign Player") and selected_player is not None:
                player_idx = selected_player[0]
                
                # Check if team has budget
                team_budgets = st.session_state.auction.get_team_budgets()
                if team_budgets[selected_team]['remaining'] >= auction_price:
                    # Assign player
                    st.session_state.auction.assign_player_to_team(player_idx, selected_team, auction_price)
                    st.session_state.players_df = st.session_state.auction.players_df
                    st.success(f"Assigned {selected_player[1].split(' (')[0]} to {teams_data[selected_team]['name']} for ${auction_price}")
                    st.rerun()
                else:
                    st.error(f"Insufficient budget! {teams_data[selected_team]['name']} has ${team_budgets[selected_team]['remaining']:.1f} remaining")
        else:
            st.info("No available players to assign with current filters.")
    else:
        st.info("No players match the current filters.")

def bot_team_interface():
    """Interface for BOT (Bridlewood AI) team optimization"""
    if st.session_state.auction is None:
        return
    
    st.subheader("🤖 Bridlewood AI Team Optimization")
    
    # Current BOT roster
    bot_roster = st.session_state.auction.get_team_roster('BOT')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current BOT Roster")
        if not bot_roster.empty:
            display_columns = ['PLAYER', 'POS', 'PTS', 'STATUS', 'GROUP', 'SALARY', 'BID']
            bot_display = bot_roster[display_columns].copy()
            st.dataframe(bot_display, use_container_width=True, height=300)
            
            # BOT team summary
            f_count = len(bot_roster[bot_roster['POS'] == 'F'])
            d_count = len(bot_roster[bot_roster['POS'] == 'D'])
            g_count = len(bot_roster[bot_roster['POS'] == 'G'])
            total_salary = bot_roster['SALARY'].sum()
            total_bid = bot_roster['BID'].sum()
            
            st.write(f"**Current:** {f_count}F / {d_count}D / {g_count}G")
            st.write(f"**Total Cost:** ${total_salary + total_bid:.1f}")
        else:
            st.info("No players currently on BOT roster")
    
    with col2:
        st.subheader("Optimization Controls")
        
        if st.button("Recalculate Z-Scores & Bids"):
            with st.spinner("Recalculating..."):
                result = st.session_state.auction.process_data()
                if result:
                    st.session_state.players_df = st.session_state.auction.players_df
                    st.success("Z-scores and bids updated!")
                    st.rerun()
                else:
                    st.error("Error in recalculation")
        
        if st.button("🎯 Optimize BOT Team"):
            with st.spinner("Running optimization..."):
                try:
                    st.session_state.auction.build_model()
                    solution = st.session_state.auction.solve_model()
                    if solution:
                        st.success("Optimization completed!")
                        st.session_state.optimal_team = st.session_state.auction.get_bot_optimal_team()
                        st.rerun()
                    else:
                        st.warning("Optimization did not find an optimal solution")
                except Exception as e:
                    st.error(f"Optimization error: {str(e)}")
    
    # Display optimal team if available
    if 'optimal_team' in st.session_state and st.session_state.optimal_team is not None:
        st.subheader("🏆 Optimal BOT Team Configuration")
        
        optimal_df = st.session_state.optimal_team
        if not optimal_df.empty:
            # Sort by position and points
            position_order = {'F': 1, 'D': 2, 'G': 3}
            optimal_df = optimal_df.copy()
            optimal_df['pos_order'] = optimal_df['POS'].map(position_order)
            optimal_df = optimal_df.sort_values(['pos_order', 'PTS'], ascending=[True, False])
            optimal_df = optimal_df.drop('pos_order', axis=1)
            
            # Display the optimal team
            display_columns = ['PLAYER', 'POS', 'PTS', 'SALARY', 'BID', 'TOTAL_COST', 'FCHL TEAM', 'STATUS']
            st.dataframe(optimal_df[display_columns], use_container_width=True)
            
            # Summary stats
            f_count = len(optimal_df[optimal_df['POS'] == 'F'])
            d_count = len(optimal_df[optimal_df['POS'] == 'D'])
            g_count = len(optimal_df[optimal_df['POS'] == 'G'])
            total_pts = optimal_df['PTS'].sum()
            total_cost = optimal_df['TOTAL_COST'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Formation", f"{f_count}F / {d_count}D / {g_count}G")
            with col2:
                st.metric("Total Points", f"{total_pts}")
            with col3:
                st.metric("Total Cost", f"${total_cost:.1f}")
            with col4:
                st.metric("Remaining Budget", f"${SALARY - total_cost:.1f}")

def team_management_interface():
    """Interface for managing all team rosters"""
    if st.session_state.auction is None:
        return
    
    st.subheader("Team Roster Management")
    
    # Team selection
    selected_team = st.selectbox(
        "Select Team to View/Edit",
        options=list(teams_data.keys()),
        format_func=lambda x: f"{x} - {teams_data[x]['name']}"
    )
    
    if selected_team:
        team_roster = st.session_state.auction.get_team_roster(selected_team)
        
        if not team_roster.empty:
            st.subheader(f"{teams_data[selected_team]['name']} Roster")
            
            # Display roster with editable status
            display_columns = ['PLAYER', 'POS', 'PTS', 'STATUS', 'GROUP', 'SALARY', 'BID']
            edited_df = st.data_editor(
                team_roster[display_columns],
                column_config={
                    "STATUS": st.column_config.SelectboxColumn(
                        "Status",
                        options=["START", "MINOR", "AUCTION", "UFA", "RFA", "ENT"],
                        required=True
                    ),
                    "PLAYER": st.column_config.TextColumn("Player", disabled=True),
                    "POS": st.column_config.TextColumn("Position", disabled=True),
                    "PTS": st.column_config.NumberColumn("Points", disabled=True),
                    "GROUP": st.column_config.TextColumn("Group", disabled=True),
                    "SALARY": st.column_config.NumberColumn("Salary", disabled=True),
                    "BID": st.column_config.NumberColumn("Bid", disabled=True)
                },
                use_container_width=True,
                height=400,
                key=f"team_editor_{selected_team}"
            )
            
            # Update button
            if st.button("Update Team Status"):
                # Apply status changes
                for idx, (original_idx, row) in enumerate(team_roster.iterrows()):
                    new_status = edited_df.iloc[idx]['STATUS']
                    if row['STATUS'] != new_status:
                        st.session_state.auction.update_player_status(original_idx, new_status)
                
                # Recalculate after changes
                result = st.session_state.auction.process_data()
                if result:
                    st.session_state.players_df = st.session_state.auction.players_df
                    st.success("Team status updated and budgets recalculated!")
                    st.rerun()
                else:
                    st.error("Error updating team status")
            
            # Team summary
            team_budgets = st.session_state.auction.get_team_budgets()
            budget = team_budgets[selected_team]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Players", f"{budget['f_count']}F / {budget['d_count']}D / {budget['g_count']}G")
            with col2:
                st.metric("Committed Salary", f"${budget['committed_salary']:.1f}")
            with col3:
                st.metric("Auction Spending", f"${budget['auction_spending']:.1f}")
            with col4:
                st.metric("Remaining Budget", f"${budget['remaining']:.1f}")
                
        else:
            st.info(f"No players currently on {teams_data[selected_team]['name']} roster")

def optimization_interface():
    """Interface for running optimization"""
    if st.session_state.auction is None:
        return
    
    # Show both BOT optimization and team management
    bot_team_interface()
    st.markdown("---")
    team_management_interface()

def main():
    st.title("🏒 Fantasy Hockey Auction Manager")
    st.markdown("Manage your fantasy hockey auction with real-time budget tracking and optimization")
    
    # Sidebar for file upload and controls
    with st.sidebar:
        st.header("Controls")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Player Data CSV",
            type=['csv'],
            help="Upload your player data CSV file"
        )
        
        if uploaded_file is not None:
            if st.session_state.players_df is None:
                df = load_csv_data(uploaded_file)
                if df is not None:
                    st.session_state.players_df = df
                    st.session_state.baseline_df = df.copy()
                    st.session_state.auction = FantasyAuction(df=df)
                    
                    # Process initial data
                    result = st.session_state.auction.process_data()
                    if result:
                        st.session_state.players_df = st.session_state.auction.players_df
                        st.success("Data loaded and processed!")
                    else:
                        st.error("Error processing data")
        
        # Reset button
        if st.session_state.auction is not None:
            st.markdown("---")
            if st.button("🔄 Reset to Baseline", help="Reset all auction assignments"):
                st.session_state.auction.reset_to_baseline()
                result = st.session_state.auction.process_data()
                if result:
                    st.session_state.players_df = st.session_state.auction.players_df
                    st.success("Reset to baseline state!")
                    st.rerun()
        
        # League info
        st.markdown("---")
        st.subheader("League Settings")
        st.write(f"**Salary Cap:** ${SALARY}")
        st.write(f"**Teams:** 11")
        st.write(f"**Forwards:** {FORWARD}")
        st.write(f"**Defence:** {DEFENCE}")
        st.write(f"**Goalies:** {GOALIE}")
    
    # Main content area
    if st.session_state.auction is None:
        st.info("👆 Please upload a player data CSV file to get started")
        
        # Show example of expected CSV format
        st.subheader("Expected CSV Format")
        example_data = {
            'PLAYER': ['Connor McDavid', 'Nathan MacKinnon'],
            'POS': ['F', 'F'],
            'GROUP': ['3', '3'],
            'STATUS': ['UFA', 'START'],
            'FCHL TEAM': ['UFA', 'MAC'],
            'NHL TEAM': ['EDM', 'COL'],
            'AGE': [27, 29],
            'SALARY': [0.0, 8.5],
            'BID': [0.0, 0.0],
            'PTS': [132, 140]
        }
        st.dataframe(pd.DataFrame(example_data))
        
    else:
        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Budget Summary", "🤖 BOT Team", "👥 Team Management", "📋 Player Assignment"])
        
        with tab1:
            display_team_budgets()
        
        with tab2:
            bot_team_interface()
        
        with tab3:
            team_management_interface()
            
        with tab4:
            player_assignment_interface()

if __name__ == "__main__":
    main()
