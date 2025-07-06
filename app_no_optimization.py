import streamlit as st
import pandas as pd
import numpy as np
import json
import base64
import os

# Fantasy Auction without optimization - for cloud deployment
try:
    from fantasy_auction import FantasyAuction, teams_data, SALARY, FORWARD, DEFENCE, GOALIE
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    # Fallback if PySCIPOpt not available
    OPTIMIZATION_AVAILABLE = False
    
    # Load teams data directly
    with open('teams.json', 'r') as file:
        teams_data = json.load(file)
    
    SALARY = 56.8
    FORWARD = 14
    DEFENCE = 7
    GOALIE = 3

try:
    from database import FantasyDatabase
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Page configuration
st.set_page_config(page_title="Fantasy Hockey Auction Manager",
                   page_icon="🏒",
                   layout="wide")

# Load custom CSS
def load_custom_css():
    css = """
    <style>
    /* Group styling */
    .group-A { border: 1px solid rgba(41, 182, 246, 0) !important; background-color: rgba(41, 182, 246, 0.1) !important; color: #29b6f6 !important; }
    .group-B { border: 1px solid rgba(3, 169, 244, 0) !important; background-color: rgba(3, 169, 244, 0.1) !important; color: #03a9f4 !important; }
    .group-C { border: 1px solid rgba(3, 155, 229, 0) !important; background-color: rgba(3, 155, 229, 0.1) !important; color: #039be5 !important; }
    .group-D { border: 1px solid rgba(2, 136, 209, 0) !important; background-color: rgba(2, 136, 209, 0.1) !important; color: #0288d1 !important; }
    .group-E { border: 1px solid rgba(2, 119, 189, 0) !important; background-color: rgba(2, 119, 189, 0.1) !important; color: #0277bd !important; }
    .group-F { border: 1px solid rgba(1, 87, 155, 0) !important; background-color: rgba(1, 87, 155, 0.1) !important; color: #01579b !important; }
    .group-G { border: 1px solid rgba(1, 87, 155, 0) !important; background-color: rgba(1, 87, 155, 0.1) !important; color: #01579b !important; }

    /* Position styling */
    .position-F { border: 1px solid rgba(76, 175, 80, 0) !important; background-color: rgba(76, 175, 80, 0.1) !important; color: #4caf50 !important; }
    .position-D { border: 1px solid rgba(63, 81, 181, 0) !important; background-color: rgba(63, 81, 181, 0.1) !important; color: #3f51b5 !important; }
    .position-G { border: 1px solid rgba(255, 152, 0, 0) !important; background-color: rgba(255, 152, 0, 0.1) !important; color: #ff9800 !important; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def main():
    load_custom_css()
    
    # Load player data
    try:
        df = pd.read_csv('players-24.csv')
    except FileNotFoundError:
        st.error("Player data file not found. Please ensure players-24.csv is in your repository.")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.title("🏒 2025 BOT Draft Agent")
        
        if st.button("🔄 Reset to Baseline"):
            st.cache_data.clear()
            st.rerun()
        
        if not OPTIMIZATION_AVAILABLE:
            st.warning("⚠️ Optimization features disabled - PySCIPOpt not available")
        
        if not DATABASE_AVAILABLE:
            st.info("ℹ️ Database features disabled - running in memory mode")
    
    # Main interface
    tabs = st.tabs(["📊 Summary", "👥 Team Preview", "🎯 Available Players"])
    
    with tabs[0]:
        st.header("Budget Summary")
        
        # Team budgets
        budget_data = []
        for team_code, team_info in teams_data.items():
            penalty = team_info["penalty"]
            budget_data.append({
                "Team": team_info["name"],
                "Code": team_code,
                "Penalty": penalty,
                "Budget": SALARY - penalty,
                "Spent": 0.0,  # Would calculate from assigned players
                "Remaining": SALARY - penalty
            })
        
        budget_df = pd.DataFrame(budget_data)
        st.dataframe(budget_df, use_container_width=True)
        
        # Player pool summary
        st.subheader("Player Pool Summary")
        if 'POS' in df.columns:
            pos_summary = df.groupby('POS').size().reset_index(name='Total')
            st.dataframe(pos_summary, use_container_width=True)
    
    with tabs[1]:
        st.header("Team Preview")
        
        # Team selection
        team_options = {f"{info['name']} ({code})": code for code, info in teams_data.items()}
        selected_team = st.selectbox("Select Team:", options=list(team_options.keys()))
        team_code = team_options[selected_team]
        
        # Show team players
        if 'FCHL TEAM' in df.columns:
            team_players = df[df['FCHL TEAM'] == team_code].copy()
        else:
            team_players = pd.DataFrame()
        
        if not team_players.empty:
            # Add styling columns
            if 'POS' in team_players.columns:
                team_players['Position_Style'] = team_players['POS'].apply(lambda x: f'position-{x}')
            if 'GROUP' in team_players.columns:
                team_players['Group_Style'] = team_players['GROUP'].apply(lambda x: f'group-{x}')
            
            st.dataframe(team_players, use_container_width=True)
        else:
            st.info(f"No players currently assigned to {teams_data[team_code]['name']}")
    
    with tabs[2]:
        st.header("Available Players")
        
        # Filter available players
        if 'STATUS' in df.columns:
            available_players = df[df['STATUS'].isin(['AUCTION', 'UFA', 'RFA', 'ENT'])].copy()
        else:
            available_players = df.copy()
        
        # Position filter
        if 'POS' in df.columns:
            pos_filter = st.multiselect("Filter by Position:", 
                                      options=df['POS'].unique(), 
                                      default=df['POS'].unique())
            available_players = available_players[available_players['POS'].isin(pos_filter)]
        
        # Add styling
        if 'POS' in available_players.columns:
            available_players['Position_Style'] = available_players['POS'].apply(lambda x: f'position-{x}')
        if 'GROUP' in available_players.columns:
            available_players['Group_Style'] = available_players['GROUP'].apply(lambda x: f'group-{x}')
        
        st.dataframe(available_players, use_container_width=True)
    
    # Status messages
    if not OPTIMIZATION_AVAILABLE:
        st.info("💡 **Note**: This is a simplified version without mathematical optimization. "
                "For full BOT team optimization features, deploy with PySCIPOpt support.")

if __name__ == "__main__":
    main()