import streamlit as st
import pandas as pd
import numpy as np
import json
import base64
import os

# Simplified version for Streamlit Cloud deployment
# This version works without PySCIPOpt optimization

# Page configuration
st.set_page_config(page_title="Fantasy Hockey Auction Manager",
                   page_icon="🏒",
                   layout="wide")

# Load teams data
@st.cache_data
def load_teams_data():
    try:
        with open('teams.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # Fallback teams data if file not found
        return {
            "BOT": {"name": "Bridlewood AI", "penalty": 2.5},
            "CAL": {"name": "Calgary", "penalty": 1.0},
            "EDM": {"name": "Edmonton", "penalty": 1.5},
            "VAN": {"name": "Vancouver", "penalty": 2.0},
            "WIN": {"name": "Winnipeg", "penalty": 0.5},
            "TOR": {"name": "Toronto", "penalty": 1.8},
            "MTL": {"name": "Montreal", "penalty": 1.2},
            "OTT": {"name": "Ottawa", "penalty": 0.8},
            "BUF": {"name": "Buffalo", "penalty": 1.3},
            "DET": {"name": "Detroit", "penalty": 1.7},
            "FLA": {"name": "Florida", "penalty": 2.2}
        }

# Load player data
@st.cache_data
def load_player_data():
    try:
        df = pd.read_csv('players-24.csv')
        return df
    except FileNotFoundError:
        st.error("⚠️ Player data file (players-24.csv) not found. Please upload the file to your repository.")
        return pd.DataFrame()

# Constants
SALARY_CAP = 56.8
MIN_SALARY = 0.5
TEAMS = 11
FORWARD = 14
DEFENCE = 7
GOALIE = 3

def main():
    # Load data
    teams_data = load_teams_data()
    df = load_player_data()
    
    if df.empty:
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.title("🏒 2025 BOT Draft Agent")
        
        if st.button("🔄 Reset to Baseline"):
            st.cache_data.clear()
            st.rerun()
    
    # Main interface
    st.title("Fantasy Hockey Auction Manager")
    st.markdown("*Simplified version for Streamlit Cloud deployment*")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Summary", "👥 Team Preview", "🎯 Available Players"])
    
    with tab1:
        st.header("Budget Summary")
        
        # Team budgets
        budget_data = []
        for team_code, team_info in teams_data.items():
            budget_data.append({
                "Team": team_info["name"],
                "Code": team_code,
                "Penalty": team_info["penalty"],
                "Budget": SALARY_CAP - team_info["penalty"],
                "Spent": 0.0,  # Would calculate from assigned players
                "Remaining": SALARY_CAP - team_info["penalty"]
            })
        
        budget_df = pd.DataFrame(budget_data)
        st.dataframe(budget_df, use_container_width=True)
        
        # Player pool summary
        st.subheader("Player Pool Summary")
        
        pos_summary = df.groupby('POS').size().reset_index(name='Total')
        st.dataframe(pos_summary, use_container_width=True)
    
    with tab2:
        st.header("Team Preview")
        
        # Team selection
        team_options = {f"{info['name']} ({code})": code for code, info in teams_data.items()}
        selected_team = st.selectbox("Select Team:", options=list(team_options.keys()))
        team_code = team_options[selected_team]
        
        # Show team players (filtered by FCHL TEAM column)
        if 'FCHL TEAM' in df.columns:
            team_players = df[df['FCHL TEAM'] == team_code]
        else:
            team_players = pd.DataFrame()  # Empty if no team assignments
        
        if not team_players.empty:
            st.dataframe(team_players, use_container_width=True)
        else:
            st.info(f"No players currently assigned to {teams_data[team_code]['name']}")
    
    with tab3:
        st.header("Available Players")
        
        # Filter available players
        if 'STATUS' in df.columns:
            available_players = df[df['STATUS'].isin(['AUCTION', 'UFA', 'RFA', 'ENT'])]
        else:
            available_players = df  # Show all if no status column
        
        # Position filter
        if 'POS' in df.columns:
            pos_filter = st.multiselect("Filter by Position:", 
                                      options=df['POS'].unique(), 
                                      default=df['POS'].unique())
            available_players = available_players[available_players['POS'].isin(pos_filter)]
        
        st.dataframe(available_players, use_container_width=True)
        
        st.info("💡 **Note**: This simplified version doesn't include optimization features. "
                "For full functionality with mathematical optimization, deploy on a platform that supports PySCIPOpt.")

if __name__ == "__main__":
    main()