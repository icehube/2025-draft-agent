import streamlit as st
import pandas as pd
import numpy as np
import json
import base64
import os
from fantasy_auction import FantasyAuction, teams_data, SALARY, FORWARD, DEFENCE, GOALIE


# Page configuration
st.set_page_config(page_title="Fantasy Hockey Auction Manager",
                   page_icon="🏒",
                   layout="wide")


# CSS styling for groups, positions, and teams
def load_custom_css():
    css = """
    <style>
    /* Group styling */
    .group-3 { border: 1px solid rgba(69, 90, 100, 0) !important; background-color: rgba(69, 90, 100, 0.1) !important; color: #455a64 !important; }
    .group-2 { border: 1px solid rgba(67, 160, 71, 0) !important; background-color: rgba(67, 160, 71, 0.1) !important; color: #43a047 !important; }
    .group-A { border: 1px solid rgba(41, 182, 246, 0) !important; background-color: rgba(41, 182, 246, 0.1) !important; color: #29b6f6 !important; }
    .group-B { border: 1px solid rgba(3, 169, 244, 0) !important; background-color: rgba(3, 169, 244, 0.1) !important; color: #03a9f4 !important; }
    .group-C { border: 1px solid rgba(3, 155, 229, 0) !important; background-color: rgba(3, 155, 229, 0.1) !important; color: #039be5 !important; }
    .group-D { border: 1px solid rgba(2, 136, 209, 0) !important; background-color: rgba(2, 136, 209, 0.1) !important; color: #0288d1 !important; }
    .group-E { border: 1px solid rgba(2, 119, 189, 0) !important; background-color: rgba(2, 119, 189, 0.1) !important; color: #0277bd !important; }
    .group-F { border: 1px solid rgba(1, 87, 155, 0) !important; background-color: rgba(1, 87, 155, 0.1) !important; color: #01579b !important; }
    .group-G { border: 1px solid rgba(1, 87, 155, 0) !important; background-color: rgba(1, 87, 155, 0.1) !important; color: #01579b !important; }
    .group-T { border: 1px solid rgba(240, 98, 146, 0) !important; background-color: rgba(240, 98, 146, 0.1) !important; color: #f06292 !important; }
    .group-RFA1 { border: 1px solid #fff3e0 !important; background-color: #fff3e0 !important; color: #ff9800 !important; }
    .group-RFA2 { border: 1px solid #ffcc80 !important; background-color: #ffcc80 !important; color: #e65100 !important; }
    
    /* Position styling */
    .position-F { border: 1px solid #188ae2 !important; background-color: #188ae2 !important; color: #fff !important; }
    .position-D { border: 1px solid #5b69bc !important; background-color: #5b69bc !important; color: #fff !important; }
    .position-G { border: 1px solid #3b3e47 !important; background-color: #3b3e47 !important; color: #fff !important; }
    
    /* Team panel styling */
    .panel-1 { background: linear-gradient(to right, #ea217b, #ff7e31); color: #fff; }
    .panel-2 { background: linear-gradient(to right, #000, #464646); color: #fff; }
    .panel-3 { background: linear-gradient(to right, #F4DD2E, #E02B15); color: #000; }
    .panel-4 { background: linear-gradient(to right, #26535f, #ed8e37); color: #fff; }
    .panel-5 { background: linear-gradient(to right, #0D4499, #E7CD38); color: #fff; }
    .panel-6 { background: linear-gradient(to right, #003876, #001f43); color: #fff; }
    .panel-7 { background: linear-gradient(to right, #012169, #FC4C02); color: #fff; }
    .panel-8 { background: linear-gradient(to right, #000, #d10000); color: #fff; }
    .panel-9 { background: linear-gradient(to right, #164846, #80C042); color: #fff; }
    .panel-10 { background: linear-gradient(to right, #172b1d, #8eaf38); color: #fff; }
    .panel-11 { background: linear-gradient(to right, #BD2F2E, #815061); color: #fff; }
    
    /* Styling for badges */
    .group-badge, .position-badge, .team-badge {
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.85em;
        font-weight: 500;
        display: inline-block;
        margin: 1px;
    }
    
    .nhl-logo {
        width: 20px;
        height: 20px;
        margin-right: 5px;
        vertical-align: middle;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# Helper functions for styling
def get_nhl_logo_path(team_code):
    """Get the path to NHL team logo"""
    # Try the new NHL logos first
    logo_path = f"assets/nhl_logos/{team_code}.png"
    if os.path.exists(logo_path):
        return logo_path
    # Fallback to FCHL logos
    logo_path = f"assets/nhl_logos/{team_code}.png"
    if os.path.exists(logo_path):
        return logo_path
    return None


def get_logo_base64(team_code):
    """Get base64 encoded logo for a team"""
    logo_path = get_nhl_logo_path(team_code)
    if logo_path:
        try:
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            return None
    return None


def display_styled_dataframe(df, columns, title="", show_logos=True):
    """Display a dataframe with custom styling for groups, positions, and logos"""
    if df.empty:
        st.info(f"No data to display{' for ' + title if title else ''}")
        return

    # Create a copy for display
    display_df = df[columns].copy()

    if title:
        st.subheader(title)

    # Style the dataframe with custom HTML
    html_table = "<div style='max-height: 400px; overflow-y: auto;'><table style='width: 100%; border-collapse: collapse;'>"

    # Header
    html_table += "<thead><tr style='background-color: #f0f2f6; position: sticky; top: 0;'>"
    for col in display_df.columns:
        html_table += f"<th style='padding: 8px; text-align: left; border-bottom: 2px solid #ddd;'>{col}</th>"
    html_table += "</tr></thead><tbody>"

    # Rows
    for idx, row in display_df.iterrows():
        html_table += "<tr style='border-bottom: 1px solid #eee;'>"
        for col in display_df.columns:
            cell_value = str(row[col])
            style = "padding: 8px; vertical-align: middle;"

            # Add NHL logo for player column
            if col == 'PLAYER' and show_logos and 'NHL TEAM' in df.columns:
                nhl_team = df.loc[
                    idx, 'NHL TEAM'] if 'NHL TEAM' in df.columns else ''
                logo_b64 = get_logo_base64(nhl_team)
                if logo_b64:
                    cell_value = f'<img src="data:image/png;base64,{logo_b64}" style="width: 20px; height: 20px; margin-right: 5px; vertical-align: middle; object-fit: contain;">{cell_value}'

            # Style group column with full CSS styles
            elif col == 'GROUP':
                group_styles = {
                    '3':
                    'background-color: rgba(69, 90, 100, 0.1); color: #455a64; border: 1px solid rgba(69, 90, 100, 0.3);',
                    '2':
                    'background-color: rgba(67, 160, 71, 0.1); color: #43a047; border: 1px solid rgba(67, 160, 71, 0.3);',
                    'A':
                    'background-color: rgba(41, 182, 246, 0.1); color: #29b6f6; border: 1px solid rgba(41, 182, 246, 0.3);',
                    'B':
                    'background-color: rgba(3, 169, 244, 0.1); color: #03a9f4; border: 1px solid rgba(3, 169, 244, 0.3);',
                    'C':
                    'background-color: rgba(3, 155, 229, 0.1); color: #039be5; border: 1px solid rgba(3, 155, 229, 0.3);',
                    'D':
                    'background-color: rgba(2, 136, 209, 0.1); color: #0288d1; border: 1px solid rgba(2, 136, 209, 0.3);',
                    'E':
                    'background-color: rgba(2, 119, 189, 0.1); color: #0277bd; border: 1px solid rgba(2, 119, 189, 0.3);',
                    'F':
                    'background-color: rgba(1, 87, 155, 0.1); color: #01579b; border: 1px solid rgba(1, 87, 155, 0.3);',
                    'G':
                    'background-color: rgba(1, 87, 155, 0.1); color: #01579b; border: 1px solid rgba(1, 87, 155, 0.3);',
                    'T':
                    'background-color: rgba(240, 98, 146, 0.1); color: #f06292; border: 1px solid rgba(240, 98, 146, 0.3);'
                }
                group_style = group_styles.get(
                    cell_value, 'background-color: #f0f0f0; color: #666;')
                cell_value = f'<span style="padding: 2px 6px; border-radius: 4px; font-size: 0.85em; font-weight: 500; {group_style}">{cell_value}</span>'

            # Style position column with full CSS styles
            elif col == 'POS':
                pos_styles = {
                    'F':
                    'background-color: #188ae2; color: #fff; border: 1px solid #188ae2;',
                    'D':
                    'background-color: #5b69bc; color: #fff; border: 1px solid #5b69bc;',
                    'G':
                    'background-color: #3b3e47; color: #fff; border: 1px solid #3b3e47;'
                }
                pos_style = pos_styles.get(
                    cell_value, 'background-color: #b2b2b2; color: #fff;')
                cell_value = f'<span style="padding: 2px 6px; border-radius: 4px; font-size: 0.85em; font-weight: 500; {pos_style}">{cell_value}</span>'

            # Style team column with full CSS styles
            elif col == 'FCHL TEAM' and cell_value in teams_data:
                panel_id = teams_data[cell_value].get('id', 1)
                team_styles = {
                    1:
                    'background: linear-gradient(to right, #ea217b, #ff7e31); color: #fff;',
                    2:
                    'background: linear-gradient(to right, #000, #464646); color: #fff;',
                    3:
                    'background: linear-gradient(to right, #F4DD2E, #E02B15); color: #000;',
                    4:
                    'background: linear-gradient(to right, #26535f, #ed8e37); color: #fff;',
                    5:
                    'background: linear-gradient(to right, #0D4499, #E7CD38); color: #fff;',
                    6:
                    'background: linear-gradient(to right, #003876, #001f43); color: #fff;',
                    7:
                    'background: linear-gradient(to right, #012169, #FC4C02); color: #fff;',
                    8:
                    'background: linear-gradient(to right, #000, #d10000); color: #fff;',
                    9:
                    'background: linear-gradient(to right, #164846, #80C042); color: #fff;',
                    10:
                    'background: linear-gradient(to right, #172b1d, #8eaf38); color: #fff;',
                    11:
                    'background: linear-gradient(to right, #BD2F2E, #815061); color: #fff;'
                }
                team_style = team_styles.get(
                    panel_id, 'background-color: #f0f0f0; color: #666;')
                cell_value = f'<span style="padding: 2px 6px; border-radius: 4px; font-size: 0.85em; font-weight: 500; {team_style}">{cell_value}</span>'

            html_table += f"<td style='{style}'>{cell_value}</td>"
        html_table += "</tr>"

    html_table += "</tbody></table></div>"

    st.markdown(html_table, unsafe_allow_html=True)

    return display_df


def format_player_with_logo(player_name, nhl_team):
    """Format player name with NHL team logo (simplified for display)"""
    return f"🏒 {player_name}"  # Simple fallback while we work on the styling


def format_group_badge(group):
    """Format group with appropriate styling"""
    return group


def format_position_badge(position):
    """Format position with appropriate styling"""
    return position


def format_team_badge(team_code):
    """Format team with appropriate styling"""
    return team_code


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
        required_columns = [
            'PLAYER', 'POS', 'GROUP', 'STATUS', 'FCHL TEAM', 'NHL TEAM', 'AGE',
            'SALARY', 'BID', 'PTS'
        ]
        missing_columns = [
            col for col in required_columns if col not in df.columns
        ]

        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
            return None

        # Convert data types - handle NaN values
        df['AGE'] = df['AGE'].astype(str).replace('nan', '0').astype(int)
        df['PTS'] = df['PTS'].astype(str).replace('nan', '0').astype(int)
        df['SALARY'] = df['SALARY'].astype(str).replace('nan', '0.0').astype(float)
        df['BID'] = df['BID'].astype(str).replace('nan', '0.0').astype(float)
        
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return None

def format_team_name_with_symbol(team_code, team_name):
    """Format team name with a symbol/emoji"""
    team_symbols = {
        'MAC': '⛹️‍♂️',  
        'BOT': '🤖',  
        'GVR': '💧', 
        'VPP': '🪖',  
        'ZSK': '🦄',  
        'HSM': '🇮🇶',  
        'LPT': '🍲',  
        'SHF': '🦸🏻‍♂️', 
        'JHN': '🍁',  
        'SRL': '♛',  
        'LGN': '🧙🏻‍♂️',  
    }
    symbol = team_symbols.get(team_code, '🏒')
    return f"{symbol} {team_name}"

def display_team_budgets():
    """Display team budget summary"""
    if st.session_state.auction is None:
        return

    team_budgets = st.session_state.auction.get_team_budgets()

    st.subheader("Team Budget Summary")

    # Create budget summary table with numeric values for better formatting
    budget_data = []
    for team_code, budget in team_budgets.items():
        # Format team name with symbol
        team_name_with_symbol = format_team_name_with_symbol(team_code, budget['name'])
        
        budget_data.append({
            'Team': team_name_with_symbol,
            'F': budget['f_count'],
            'D': budget['d_count'],
            'G': budget['g_count'],
            'Committed': budget['committed_salary'],
            'Penalty': budget['penalty'],
            'Total Spent': budget['total_spent'],
            'Remaining': budget['remaining']
        })

    budget_df = pd.DataFrame(budget_data)
    
    # Style the budget dataframe with conditional formatting
    def style_budget_table(df):
        styled_df = df.style
        
        # Format currency columns
        styled_df = styled_df.format({
            'Committed': '${:.1f}',
            'Penalty': '${:.1f}',
            'Total Spent': '${:.1f}',
            'Remaining': '${:.1f}'
        })
        
        # Apply conditional formatting for position counts
        def highlight_position_counts(row):
            styles = [''] * len(row)
            
            # Highlight F column if >= 12 (red background)
            if row['F'] >= 12:
                styles[df.columns.get_loc('F')] = 'background-color: rgba(255, 0, 0, 0.2); color: #cc0000; font-weight: bold;'
            # Highlight D column if >= 8 (red background)
            if row['D'] >= 8:
                styles[df.columns.get_loc('D')] = 'background-color: rgba(255, 0, 0, 0.2); color: #cc0000; font-weight: bold;'
            # Highlight G column if >= 3 (red background)
            if row['G'] >= 3:
                styles[df.columns.get_loc('G')] = 'background-color: rgba(255, 0, 0, 0.2); color: #cc0000; font-weight: bold;'
            return styles
        
        styled_df = styled_df.apply(highlight_position_counts, axis=1)
        return styled_df
    
    # Apply styling and display
    styled_budget_df = style_budget_table(budget_df)
    # Calculate height: ~35px per row + header
    calculated_height = min(35 * len(budget_df) + 50, 500)  # Cap at 500px max
    st.dataframe(styled_budget_df, use_container_width=True, hide_index=True, height=calculated_height)

    # Pool summary table (F, D, G Drafted and Available)
    st.subheader("Player Pool Summary")

    # Calculate drafted and available counts
    total_players = len(st.session_state.auction.players_df)
    drafted_players = len(
        st.session_state.auction.
        players_df[~st.session_state.auction.players_df['FCHL TEAM'].
                   isin(['UFA', 'RFA', 'ENT'])])
    available_players = total_players - drafted_players

    # Position breakdowns
    all_players = st.session_state.auction.players_df
    drafted = all_players[~all_players['FCHL TEAM'].isin(['UFA', 'RFA', 'ENT']
                                                         )]
    available = all_players[all_players['FCHL TEAM'].isin(
        ['UFA', 'RFA', 'ENT'])]

    pool_data = []
    for pos in ['F', 'D', 'G']:
        drafted_count = len(drafted[drafted['POS'] == pos])
        available_count = len(available[available['POS'] == pos])
        total_count = drafted_count + available_count

        pool_data.append({
            'Position': pos,
            'Drafted': drafted_count,
            'Available': available_count,
            'Total': total_count
        })

    # Add totals row
    pool_data.append({
        'Position': 'Total',
        'Drafted': drafted_players,
        'Available': available_players,
        'Total': total_players
    })

    pool_df = pd.DataFrame(pool_data)
    
    # Style the dataframe to highlight the Total row
    def highlight_total_row(df):
        # Create a styled dataframe
        styled_df = df.style
        # Apply styling to the Total row (last row) - works in both light and dark modes
        styled_df = styled_df.apply(lambda x: ['background-color: rgba(0,0,0,0.1); font-weight: bold; border-top: 2px solid rgba(0,0,0,0.2);' if i == len(df)-1 else '' for i in range(len(df))], axis=0)
        return styled_df
    
    # Apply styling and display
    styled_pool_df = highlight_total_row(pool_df)
    st.dataframe(styled_pool_df, use_container_width=True, hide_index=True)

    # League financial summary (removed Total Auction)
    total_committed = sum(b['committed_salary'] for b in team_budgets.values())
    total_penalties = sum(b['penalty'] for b in team_budgets.values())
    total_spent = total_committed + total_penalties
    total_available = (SALARY * 11) - total_spent

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pool", f"${SALARY * 11:.1f}")
    with col2:
        st.metric("Total Committed", f"${total_committed:.1f}")
    with col3:
        st.metric("Available", f"${total_available:.1f}")


def remaining_players_interface():
    """Interface showing remaining players available for auction"""
    if st.session_state.auction is None:
        return

    st.subheader("Remaining Players")

    # Get available players for auction
    available_players = st.session_state.auction.get_available_players()

    if not available_players.empty:
        # Filter options
        col1, col2 = st.columns(2)

        with col1:
            position_filter = st.selectbox("Filter by Position",
                                           ["All", "F", "D", "G"],
                                           key="remaining_pos_filter")

        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Points (High to Low)", "Bid (High to Low)", "Player Name"],
                key="remaining_sort")

        # Apply filters
        filtered_df = available_players.copy()

        if position_filter != "All":
            filtered_df = filtered_df[filtered_df['POS'] == position_filter]

        # Sort the data
        if sort_by == "Points (High to Low)":
            filtered_df = filtered_df.sort_values('PTS', ascending=False)
        elif sort_by == "Bid (High to Low)":
            filtered_df = filtered_df.sort_values('BID', ascending=False)
        elif sort_by == "Player Name":
            filtered_df = filtered_df.sort_values('PLAYER')

        # Display available players with NHL logos and styling
        if not filtered_df.empty:
            display_columns = ['PLAYER', 'POS', 'PTS', 'GROUP', 'BID']

            # Use the custom styled display function
            display_styled_dataframe(filtered_df,
                                     display_columns,
                                     show_logos=True)

            st.info(
                f"Showing {len(filtered_df)} available players for auction")
        else:
            st.info("No available players match the current filters.")

        # Player assignment form
        st.subheader("Assign Player to Team")

        if not available_players.empty:
            player_options = [
                (idx, f"{row['PLAYER']} ({row['POS']}) - ${row['BID']:.1f}")
                for idx, row in available_players.iterrows()
            ]

            col1, col2, col3 = st.columns(3)

            with col1:
                selected_player = st.selectbox(
                    "Select Player",
                    options=[None] + player_options,
                    format_func=lambda x: "Select a player..."
                    if x is None else x[1],
                    key="assign_player_select")

            with col2:
                selected_team = st.selectbox(
                    "Assign to Team",
                    options=list(teams_data.keys()),
                    format_func=lambda x: f"{x} - {teams_data[x]['name']}",
                    key="assign_team_select")

            with col3:
                # Pre-fill with optimal bid if player selected
                default_price = 1.0
                if selected_player is not None:
                    player_row = available_players.loc[selected_player[0]]
                    default_price = float(player_row['BID'])

                auction_price = st.number_input("Auction Price",
                                                min_value=0.0,
                                                max_value=20.0,
                                                value=default_price,
                                                step=0.1,
                                                key="assign_price_input")

            if st.button(
                    "Assign Player",
                    key="assign_player_btn") and selected_player is not None:
                player_idx = selected_player[0]

                # Check if team has budget
                team_budgets = st.session_state.auction.get_team_budgets()
                if team_budgets[selected_team]['remaining'] >= auction_price:
                    # Assign player
                    st.session_state.auction.assign_player_to_team(
                        player_idx, selected_team, auction_price)
                    auto_recalculate()
                    st.success(
                        f"Assigned {selected_player[1].split(' (')[0]} to {teams_data[selected_team]['name']} for ${auction_price}"
                    )
                    st.rerun()
                else:
                    st.error(
                        f"Insufficient budget! {teams_data[selected_team]['name']} has ${team_budgets[selected_team]['remaining']:.1f} remaining"
                    )

    else:
        st.info("No players currently available for auction")

def auto_recalculate():
    """Auto-recalculate when data changes"""
    if st.session_state.auction is not None:
        result = st.session_state.auction.process_data()
        if result:
            st.session_state.players_df = st.session_state.auction.players_df
            # Auto-run optimization for BOT team
            try:
                st.session_state.auction.build_model()
                solution = st.session_state.auction.solve_model()
                if solution:
                    st.session_state.optimal_team = st.session_state.auction.get_bot_optimal_team(
                    )
            except:
                pass  # Silent fail for optimization


def bot_team_interface():
    """Interface for BOT (Bridlewood AI) team optimization"""
    if st.session_state.auction is None:
        return

    st.subheader("🤖 Bridlewood AI Team Optimization")

    # Current BOT roster
    bot_roster = st.session_state.auction.get_team_roster('BOT')

    st.subheader("Current BOT Roster")
    if not bot_roster.empty:
        # Single editable table with position and group styling
        edit_columns = ['PLAYER', 'POS', 'PTS', 'STATUS', 'GROUP', 'SALARY']
        styled_display = bot_roster[edit_columns].copy()
        styled_display.columns = [
            'Player', 'Pos', 'Points', '✏️ Status', 'Group', '✏️ Salary'
        ]

        # Create editable data with styling
        edited_df = st.data_editor(
            styled_display,
            use_container_width=True,
            height=300,
            column_config={
                "✏️ Status":
                st.column_config.SelectboxColumn(
                    "Status",
                    options=["START", "MINOR"],
                    help="Player status affects budget calculation"),
                "✏️ Salary":
                st.column_config.NumberColumn("Salary",
                                              min_value=0.0,
                                              max_value=15.0,
                                              step=0.1,
                                              format="$%.1f")
            },
            disabled=["Player", "Pos", "Points", "Group", "FCHL Team"],
            hide_index=True)

        # Handle changes
        if not edited_df.equals(styled_display):
            for idx, (old_row, new_row) in enumerate(
                    zip(styled_display.itertuples(), edited_df.itertuples())):
                if old_row.Status != new_row.Status:
                    player_idx = bot_roster.index[idx]
                    st.session_state.auction.update_player_status(
                        player_idx, new_row.Status)

                if abs(old_row.Salary - new_row.Salary) > 0.05:
                    player_idx = bot_roster.index[idx]
                    st.session_state.auction.update_player_salary(
                        player_idx, new_row.Salary)

            auto_recalculate()
            st.rerun()

        # Player removal
        st.markdown("**Remove Players:**")
        player_options = [
            (idx, f"{row['PLAYER']} ({row['POS']}) - ${row['SALARY']:.1f}")
            for idx, row in bot_roster.iterrows()
        ]

        col1, col2 = st.columns(2)
        with col1:
            selected_player = st.selectbox(
                "Select Player to Remove",
                options=[None] + player_options,
                format_func=lambda x: "Select a player..."
                if x is None else x[1],
                key="bot_remove_player_select")

        with col2:
            if st.button("Remove Player", key="bot_remove_player_btn"
                         ) and selected_player is not None:
                player_idx = selected_player[0]
                player_name = selected_player[1].split(' (')[0]
                st.session_state.auction.remove_player_from_team(player_idx)
                auto_recalculate()
                st.success(f"Removed {player_name} from BOT roster")
                st.rerun()

    else:
        st.info("No players currently on BOT roster")

    # Budget & Requirements section moved below
    st.subheader("Budget & Requirements")
    team_budgets = st.session_state.auction.get_team_budgets()
    bot_budget = team_budgets.get('BOT', {})

    if bot_budget:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Remaining Budget",
                      f"${bot_budget.get('remaining', 0):.1f}")
        with col2:
            st.write(f"**Target:** {FORWARD}F / {DEFENCE}D / {GOALIE}G")
        with col3:
            st.write(
                f"**Current:** {bot_budget.get('f_count', 0)}F / {bot_budget.get('d_count', 0)}D / {bot_budget.get('g_count', 0)}G"
            )

    # Display optimal team if available
    if 'optimal_team' in st.session_state and st.session_state.optimal_team is not None:
        st.subheader("🏆 Optimal BOT Team Configuration")

        optimal_df = st.session_state.optimal_team
        if not optimal_df.empty:
            # Sort by position and points
            position_order = {'F': 1, 'D': 2, 'G': 3}
            optimal_df = optimal_df.copy()
            optimal_df['pos_order'] = optimal_df['POS'].map(position_order)
            optimal_df = optimal_df.sort_values(['pos_order', 'PTS'],
                                                ascending=[True, False])
            optimal_df = optimal_df.drop('pos_order', axis=1)

            # Display the optimal team
            display_columns = [
                'PLAYER', 'POS', 'PTS', 'SALARY', 'BID', 'TOTAL_COST',
                'FCHL TEAM', 'STATUS'
            ]
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


def team_preview_interface():
    """Team Preview interface for managing all team rosters"""
    if st.session_state.auction is None:
        return

    # Team selection
    selected_team = st.selectbox(
        "Select Team to View/Edit",
        options=list(teams_data.keys()),
        format_func=lambda x: f"{x} - {teams_data[x]['name']}")

    if selected_team:
        team_roster = st.session_state.auction.get_team_roster(selected_team)

        if not team_roster.empty:

            # Sort roster: START/MINOR first, then by Position
            def get_sort_key(row):
                status_order = {
                    'START': 0,
                    'MINOR': 1,
                    'AUCTION': 2,
                    'UFA': 3,
                    'RFA': 4,
                    'ENT': 5
                }
                position_order = {'F': 0, 'D': 1, 'G': 2}
                return (status_order.get(row['STATUS'],
                                         9), position_order.get(row['POS'], 9))

            sorted_roster = team_roster.copy()
            sorted_roster['sort_key'] = sorted_roster.apply(get_sort_key,
                                                            axis=1)
            sorted_roster = sorted_roster.sort_values('sort_key').drop(
                'sort_key', axis=1)

            # Apply gradient styling to team name header
            team_info = teams_data[selected_team]
            panel_id = team_info.get('id', 1)
            team_styles = {
                1:
                'background: linear-gradient(to right, #ea217b, #ff7e31); color: #fff;',
                2:
                'background: linear-gradient(to right, #000, #464646); color: #fff;',
                3:
                'background: linear-gradient(to right, #F4DD2E, #E02B15); color: #000;',
                4:
                'background: linear-gradient(to right, #26535f, #ed8e37); color: #fff;',
                5:
                'background: linear-gradient(to right, #0D4499, #E7CD38); color: #fff;',
                6:
                'background: linear-gradient(to right, #003876, #001f43); color: #fff;',
                7:
                'background: linear-gradient(to right, #012169, #FC4C02); color: #fff;',
                8:
                'background: linear-gradient(to right, #000, #d10000); color: #fff;',
                9:
                'background: linear-gradient(to right, #164846, #80C042); color: #fff;',
                10:
                'background: linear-gradient(to right, #172b1d, #8eaf38); color: #fff;',
                11:
                'background: linear-gradient(to right, #BD2F2E, #815061); color: #fff;'
            }
            team_style = team_styles.get(
                panel_id, 'background-color: #f0f0f0; color: #666;')

            st.markdown(f"""
            <div style="padding: 10px; border-radius: 8px; margin-bottom: 20px; {team_style}">
                <h3 style="margin: 0; text-align: center;">{team_info['name']} Roster</h3>
            </div>
            """,
                        unsafe_allow_html=True)

            # Budget Summary - always show current state
            team_budgets = st.session_state.auction.get_team_budgets()
            team_budget = team_budgets.get(selected_team, {})

            col1, col2 = st.columns([2, 1])

            with col1:
                # Display used budget
                if team_budget:
                    used_budget = team_budget['total_spent']
                    st.metric("Used Budget", f"${used_budget:.1f}")

            with col2:
                if team_budget:
                    st.metric("Remaining Budget",
                              f"${team_budget.get('remaining', 0):.1f}")

            # Single editable table with position and group styling
            edit_columns = [
                'PLAYER', 'POS', 'NHL TEAM', 'PTS', 'STATUS', 'GROUP', 'SALARY'
            ]
            styled_display = sorted_roster[edit_columns].copy()

            # Format Position column with styling
            styled_display['POS'] = styled_display['POS'].apply(
                format_position_badge)

            # Format Group column with styling
            styled_display['GROUP'] = styled_display['GROUP'].apply(
                format_group_badge)

            # Create base64 encoded logos for NHL teams - insert after NHL TEAM column
            def get_logo_data_url(team_code):
                if pd.notna(team_code):
                    logo_path = get_nhl_logo_path(team_code)
                    if logo_path and os.path.exists(logo_path):
                        with open(logo_path, "rb") as f:
                            import base64
                            encoded = base64.b64encode(f.read()).decode()
                            return f"data:image/png;base64,{encoded}"
                return None

            # Replace NHL TEAM column with Logo column
            styled_display['NHL TEAM'] = styled_display['NHL TEAM'].apply(get_logo_data_url)

            # Rename columns for display (7 columns total)
            styled_display.columns = [
                'Player', 'Pos', 'Logo', 'Points', '✏️ Status', 'Group', '✏️ Salary'
            ]

            # Single editable data editor with styled columns
            st.markdown("**Team Roster (Edit Status & Salary):**")

            # Keep original position and group values for comparison
            original_pos = sorted_roster['POS'].tolist()
            original_group = sorted_roster['GROUP'].tolist()

            edited_df = st.data_editor(
                styled_display,
                column_config={
                    "✏️ Status":
                    st.column_config.SelectboxColumn(
                        "✏️ Status",
                        options=[
                            "START", "MINOR", "AUCTION", "UFA", "RFA", "ENT"
                        ],
                        required=True,
                        help="Editable: Change player status"),
                    "✏️ Salary":
                    st.column_config.NumberColumn(
                        "✏️ Salary",
                        min_value=0.0,
                        max_value=20.0,
                        step=0.1,
                        format="$%.1f",
                        help="Editable: Adjust salary if needed"),
                    "Player":
                    st.column_config.TextColumn("Player", disabled=True),
                    "Pos":
                    st.column_config.Column("Pos", disabled=True),
                    "Logo":
                    st.column_config.ImageColumn("Logo",
                                                 help="NHL Team Logo",
                                                 width="small"),
                    "Points":
                    st.column_config.NumberColumn("Points", disabled=True),
                    "Group":
                    st.column_config.Column("Group", disabled=True)
                },
                use_container_width=True,
                key=f"team_editor_{selected_team}",
                height=25 * (len(styled_display) + 1),
                hide_index=True)

            # Save Changes Button
            col_save, col_space = st.columns([1, 2])
            with col_save:
                if st.button("💾 Save Changes & Recalculate",
                             key=f"save_changes_{selected_team}",
                             type="primary"):
                    changes_made = False
                    # Check for changes and apply them
                    if edited_df is not None and len(edited_df) > 0:
                        for idx, (original_idx,
                                  row) in enumerate(sorted_roster.iterrows()):
                            if idx < len(edited_df):
                                new_status = edited_df.iloc[idx]['✏️ Status']
                                new_salary = edited_df.iloc[idx]['✏️ Salary']

                                if row['STATUS'] != new_status:
                                    st.session_state.auction.update_player_status(
                                        original_idx, new_status)
                                    changes_made = True

                                if abs(row['SALARY'] - new_salary) > 0.01:
                                    st.session_state.auction.update_player_salary(
                                        original_idx, new_salary)
                                    changes_made = True

                    if changes_made:
                        # Trigger complete recalculation including optimization
                        auto_recalculate()
                        st.success("Changes saved and model recalculated!")
                        st.rerun()
                    else:
                        st.info("No changes detected")

            # Team composition and budget summary - sorted by START/MINOR first, then Position
            composition = st.session_state.auction.get_team_composition(
                selected_team)
            team_budgets = st.session_state.auction.get_team_budgets()
            budget = team_budgets[selected_team]

            # Create Team Composition table with proper structure
            st.markdown("**Team Composition:**")
            composition_data = {
                'Position': ['F', 'D', 'G', 'Total'],
                'START': [
                    composition['start_f'], composition['start_d'],
                    composition['start_g'], composition['start_f'] +
                    composition['start_d'] + composition['start_g']
                ],
                'MINOR': [
                    composition['minor_f'], composition['minor_d'],
                    composition['minor_g'], composition['minor_f'] +
                    composition['minor_d'] + composition['minor_g']
                ],
                'Total': [
                    composition['total_f'], composition['total_d'],
                    composition['total_g'], composition['total_f'] +
                    composition['total_d'] + composition['total_g']
                ]
            }

            composition_df = pd.DataFrame(composition_data)
            st.dataframe(composition_df,
                         hide_index=True,
                         use_container_width=True)

            # Remove Player section moved to bottom
            st.markdown("---")
            st.markdown("**Remove Player from Team:**")
            if not team_roster.empty:
                player_to_remove = st.selectbox(
                    "Select player to remove and return to auction pool",
                    options=[(idx, f"{row['PLAYER']} ({row['POS']})")
                             for idx, row in team_roster.iterrows()],
                    format_func=lambda x: x[1],
                    key=f"remove_player_{selected_team}")

                if st.button("🗑️ Remove Player",
                             key=f"remove_btn_{selected_team}"):
                    st.session_state.auction.remove_player_from_team(
                        player_to_remove[0])
                    auto_recalculate()
                    st.success(
                        f"Removed {player_to_remove[1].split(' (')[0]} from team"
                    )
                    st.rerun()

        else:
            st.info(
                f"No players currently on {teams_data[selected_team]['name']} roster"
            )


def optimization_interface():
    """Interface for running optimization"""
    if st.session_state.auction is None:
        return

    # Show both BOT optimization and team management
    bot_team_interface()
    st.markdown("---")
    team_preview_interface()


def main():
    # Set page configuration with hidden sidebar
    st.set_page_config(page_title="2025 BOT Draft Agent",
                       page_icon="🏒",
                       layout="wide",
                       initial_sidebar_state="collapsed")

    # Load custom CSS styling
    load_custom_css()

    # Auto-load the saved CSV file
    csv_file_path = "players-24.csv"

    try:
        # Load CSV data automatically
        if st.session_state.players_df is None:
            df = pd.read_csv(csv_file_path)

            # Data validation and processing
            df['SALARY'] = df['SALARY'].astype(str).replace('nan', '0.0').astype(float)
            df['BID'] = df['BID'].astype(str).replace('nan', '0.0').astype(float)
            df['PTS'] = df['PTS'].astype(str).replace('nan', '0.0').astype(float)
            df['AGE'] = df['AGE'].astype(str).replace('nan', '0').astype(int)
            
            # Initialize session state
            st.session_state.players_df = df
            st.session_state.baseline_df = df.copy()
            st.session_state.auction = FantasyAuction(df=df)

            # Process initial data and auto-optimize
            result = st.session_state.auction.process_data()
            if result:
                st.session_state.players_df = st.session_state.auction.players_df
                # Auto-run initial optimization
                try:
                    st.session_state.auction.build_model()
                    solution = st.session_state.auction.solve_model()
                    if solution:
                        st.session_state.optimal_team = st.session_state.auction.get_bot_optimal_team(
                        )
                except:
                    pass  # Silent fail for initial optimization
                st.success("Player data loaded and optimized!")
            else:
                st.error("Error processing player data")

    except FileNotFoundError:
        st.error("players-24.csv file not found in the project directory")
        st.info(
            "Please ensure the players-24.csv file is present in the main project folder"
        )
    except Exception as e:
        st.error(f"Error loading player data: {e}")

    # Sidebar for controls
    with st.sidebar:
        st.title("🏒 2025 BOT Draft Agent")
        st.header("Controls")

        # Reset button
        if st.session_state.auction is not None:
            if st.button("🔄 Reset to Baseline",
                         help="Reset all auction assignments"):
                st.session_state.auction.reset_to_baseline()
                auto_recalculate()
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
        st.info("Loading player data...")
        return

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Summary", 
        "🤖 BOT Team", 
        "👥 Team Preview", 
        "📋 Remaining Players"
    ])

    with tab1:
        display_team_budgets()

    with tab2:
        bot_team_interface()

    with tab3:
        team_preview_interface()

    with tab4:
        remaining_players_interface()


if __name__ == "__main__":
    main()
