import time
import pandas as pd 
import json
import numpy as np
from pyscipopt import Model

"""
Fantasy Hockey Auction Management System
Adapted for Streamlit web interface
"""

# Load teams from the JSON file
with open('teams.json', 'r') as file:
    teams_data = json.load(file)

# Extract penalties from the teams data
PENALTIES = {team: data['penalty'] for team, data in teams_data.items()}

# Constants
SALARY = 56.8
MIN_SALARY = 0.5
TEAMS = 11
FORWARD = 14
DEFENCE = 7
GOALIE = 3

class FantasyAuction:
    def __init__(self, csv_path=None, df=None):
        self.csv_path = csv_path
        if df is not None:
            self.players_df = df.copy()
        else:
            self.players_df = self.load_data()

    def load_data(self):
        if self.csv_path is None:
            return pd.DataFrame()
        
        try:
            # Load the data into a DataFrame
            df = pd.read_csv(
                self.csv_path, 
                dtype={'AGE': int, 'PTS': int, 'SALARY': float, 'BID': float}
            )
            return df
        except Exception as e:
            print(f"Error reading the CSV file: {e}")
            return pd.DataFrame()

    def process_data(self):
        if self.players_df is None or self.players_df.empty:
            print("Error: No data loaded.")
            return None
    
        # Initialize the Draftable column to NO
        self.players_df['Draftable'] = "NO"  
        # Fill missing values in the 'STATUS' column with 'NO'
        self.players_df['STATUS'] = self.players_df['STATUS'].fillna('NO')
        # Set the salary of players with 'FCHL TEAM' as 'RFA', 'UFA', or 'ENT' to 0
        self.players_df.loc[self.players_df['FCHL TEAM'].isin(['RFA', 'UFA', 'ENT']), 'SALARY'] = 0

        total_pool = SALARY * TEAMS
        # Calculate the sum of the salaries of players with 'STATUS' as 'START' or 'MINOR' and 'GROUP' as 2 or 3
        committed_salary = self.players_df[
            (self.players_df['STATUS'] == 'START') |
            ((self.players_df['STATUS'] == 'MINOR') & (self.players_df['GROUP'].isin(['2', '3'])))
        ]['SALARY'].sum()
        # Calculate the sum of the penalties
        total_penalties = sum(PENALTIES.values())   
        # Add the sum of the penalties to committed_salary
        committed_salary += total_penalties     
        available_to_spend = total_pool - committed_salary
        player_count, total_z = self.calculate_z_scores()
        total_bid_sum, restrict, dollar_per_z = self.update_bids(player_count, total_z, available_to_spend)
        return total_pool, committed_salary, available_to_spend, player_count, total_z, total_bid_sum, restrict, dollar_per_z

    def calculate_z_scores(self):
        grouped_players = self.players_df.groupby('POS')

        F_baseline = FORWARD * TEAMS
        D_baseline = DEFENCE * TEAMS
        G_baseline = GOALIE * TEAMS

        player_count = 0  # Initialize the counter
        total_z = 0 

        # Loop over each player group to perform calculations
        for pos, group in grouped_players:
            # Sort the group by points in descending order, and filter out 'MINOR' players
            group = group[group['STATUS'] != 'MINOR'].sort_values('PTS', ascending=False)

            if pos == 'F':
                baseline = F_baseline
            elif pos == 'D':
                baseline = D_baseline
            elif pos == 'G':
                baseline = G_baseline
            else:
                continue

            # Slice the DataFrame first, then apply the boolean condition
            below_baseline_slice = group.iloc[baseline:]
            below_baseline_start_players = below_baseline_slice[below_baseline_slice['STATUS'] == 'START']
            count_below_baseline_start = below_baseline_start_players.shape[0]

            # Adjust the baseline
            adjusted_baseline = baseline - count_below_baseline_start
            
            # Select the top players using the adjusted baseline
            top_players = group.head(adjusted_baseline)

            # Filter out players with 'FCHL TEAM' as 'ENT', 'RFA', or 'UFA'
            filtered_top_players = top_players[top_players['FCHL TEAM'].isin(['ENT', 'RFA', 'UFA'])]

            # Use .loc to update the Draftable column in self.players_df for filtered_top_players
            draftable_indices = filtered_top_players.index
            self.players_df.loc[draftable_indices, 'Draftable'] = "YES"

            # Update the counter with the number of rows in filtered_top_players
            player_count += len(filtered_top_players)

            # Calculate Z-scores for filtered top players
            points = filtered_top_players['PTS']
            if len(points) > 0:
                mean_pts = points.mean()
                stdev_pts = points.std()

                if stdev_pts == 0 or pd.isna(stdev_pts):
                    stdev_pts = 1  # Avoid division by zero

                # Calculate and assign Z-scores directly in the DataFrame
                z_scores = (points - mean_pts) / stdev_pts
                z_scores -= z_scores.min()  # Standardize Z-scores so the minimum is 0

                self.players_df.loc[draftable_indices, 'Z-score'] = z_scores.round(2)
                total_z += z_scores.sum()

        return player_count, total_z
    
    def build_model(self):
        self.model = Model("PlayerSelection")
        self.player_vars = {}

        # Filter players based on specific criteria and remove players with Bid = 0
        self.filtered_df = self.players_df[
            ((self.players_df['FCHL TEAM'].isin(['ENT', 'UFA', 'RFA'])) & (self.players_df['BID'] > 0)) |
            ((self.players_df['FCHL TEAM'] == 'BOT') & (self.players_df['STATUS'] == 'START'))
        ]

        for i, row in self.filtered_df.iterrows():
            player_name = row['PLAYER']
            player_position = row['POS']
            self.player_vars[i] = self.model.addVar(vtype="B", name=f"{player_name}_{player_position}")

        self.model.setObjective(
            sum(row['PTS'] * self.player_vars[i] for i, row in self.filtered_df.iterrows()),
            "maximize"
        )

        self.add_constraints(self.player_vars)

    def solve_model(self):
        try:
            self.model.optimize()
            status = self.model.getStatus()
            if status == "optimal":
                return self.get_solution()
            elif status == "timelimit":
                print("Warning: Optimization hit the time limit.")
            else:
                print(f"Warning: The model did not solve to optimality. Status: {status}")
            return None
        except ValueError as ve:
            print(f"ValueError during optimization: {ve}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during optimization: {e}")
            return None

    def add_constraints(self, player_vars):
        if self.filtered_df.empty:
            print("Error: No players to consider in the optimization.")
            return

        # Identify players that must be included in the team
        must_include_players = self.filtered_df.index[
            (self.filtered_df['FCHL TEAM'] == 'BOT') & (self.filtered_df['STATUS'] == 'START')
        ]

        # Constraint 1: Sum of the "Bid" values must be under 56.8
        self.model.addCons(
            sum((row['SALARY'] + row['BID']) * player_vars[i] for i, row in self.filtered_df.iterrows()) <= SALARY
        )

        # Constraint 3: Must have X Players with F in their Pos Column
        self.model.addCons(
            sum(player_vars[i] for i, row in self.filtered_df.iterrows() if row['POS'] == 'F') == FORWARD
        )

        # Constraint 4: Must have X Players with D in their Pos Column
        self.model.addCons(
            sum(player_vars[i] for i, row in self.filtered_df.iterrows() if row['POS'] == 'D') == DEFENCE
        )

        # Constraint 5: Must have X Players with G in their Pos Column
        self.model.addCons(
            sum(player_vars[i] for i, row in self.filtered_df.iterrows() if row['POS'] == 'G') == GOALIE
        )

        # Constraint: Must include players from BOT team with status "start"
        for i in must_include_players:
            self.model.addCons(player_vars[i] == 1)

    def get_solution(self):
        best_solution = self.model.getBestSol()
        return best_solution

    def update_bids(self, player_count, total_z, available_to_spend):
        if total_z == 0:
            return 0, 0, 0
            
        restrict = player_count * MIN_SALARY
        dollar_per_z = (available_to_spend - restrict) / total_z

        # Initialize Z-score column if it doesn't exist
        if 'Z-score' not in self.players_df.columns:
            self.players_df['Z-score'] = 0

        # Update bids for draftable players
        mask = self.players_df['Draftable'] == 'YES'
        self.players_df.loc[mask, 'BID'] = (self.players_df.loc[mask, 'Z-score'] * dollar_per_z) + MIN_SALARY
        self.players_df['BID'] = self.players_df['BID'].round(1)

        total_bid_sum = self.players_df['BID'].sum()
        return total_bid_sum, restrict, dollar_per_z

    def get_team_budgets(self):
        """Calculate current budget status for each team"""
        team_budgets = {}
        
        for team_code, team_info in teams_data.items():
            team_name = team_info['name']
            penalty = team_info['penalty']
            
            # Get players for this team
            team_players = self.players_df[self.players_df['FCHL TEAM'] == team_code]
            
            # Calculate committed salary (existing contracts)
            # Group A-G MINOR players don't count against salary cap
            committed_salary = team_players[
                (team_players['STATUS'] == 'START') | 
                ((team_players['STATUS'] == 'MINOR') & (team_players['GROUP'].isin(['2', '3'])))
            ]['SALARY'].sum()
            
            # Calculate auction spending (new acquisitions)
            auction_spending = team_players[
                team_players['FCHL TEAM'] == team_code
            ]['BID'].sum()
            
            total_spent = committed_salary + auction_spending + penalty
            remaining = SALARY - total_spent
            
            # Count players by position
            f_count = len(team_players[team_players['POS'] == 'F'])
            d_count = len(team_players[team_players['POS'] == 'D'])
            g_count = len(team_players[team_players['POS'] == 'G'])
            
            team_budgets[team_code] = {
                'name': team_name,
                'committed_salary': committed_salary,
                'auction_spending': auction_spending,
                'penalty': penalty,
                'total_spent': total_spent,
                'remaining': remaining,
                'f_count': f_count,
                'd_count': d_count,
                'g_count': g_count
            }
            
        return team_budgets

    def get_team_roster(self, team_code):
        """Get detailed roster for a specific team"""
        team_players = self.players_df[self.players_df['FCHL TEAM'] == team_code].copy()
        
        if team_players.empty:
            return team_players
            
        # Sort by position and points
        position_order = {'F': 1, 'D': 2, 'G': 3}
        team_players['pos_order'] = team_players['POS'].map(position_order)
        team_players = team_players.sort_values(['pos_order', 'PTS'], ascending=[True, False])
        team_players = team_players.drop('pos_order', axis=1)
        
        return team_players

    def get_bot_optimal_team(self):
        """Get the optimal team construction for BOT (Bridlewood AI)"""
        if not hasattr(self, 'model') or not hasattr(self, 'player_vars'):
            return None
            
        try:
            solution = self.get_solution()
            if solution is None:
                return None
                
            optimal_players = []
            for i, row in self.filtered_df.iterrows():
                if self.model.getSolVal(solution, self.player_vars[i]) > 0.5:
                    optimal_players.append({
                        'PLAYER': row['PLAYER'],
                        'POS': row['POS'],
                        'PTS': row['PTS'],
                        'SALARY': row['SALARY'],
                        'BID': row['BID'],
                        'TOTAL_COST': row['SALARY'] + row['BID'],
                        'FCHL TEAM': row['FCHL TEAM'],
                        'STATUS': row['STATUS'],
                        'GROUP': row['GROUP']
                    })
            
            return pd.DataFrame(optimal_players)
        except:
            return None

    def update_player_status(self, player_index, new_status):
        """Update a player's status"""
        self.players_df.loc[player_index, 'STATUS'] = new_status

    def update_player_salary(self, player_index, new_salary):
        """Update a player's salary"""
        self.players_df.loc[player_index, 'SALARY'] = new_salary

    def update_player_bid(self, player_index, new_bid):
        """Update a player's bid"""
        self.players_df.loc[player_index, 'BID'] = new_bid

    def remove_player_from_team(self, player_index):
        """Remove a player from their current team and return to auction pool"""
        self.players_df.loc[player_index, 'FCHL TEAM'] = 'UFA'
        self.players_df.loc[player_index, 'STATUS'] = 'NO'
        self.players_df.loc[player_index, 'BID'] = 0.0

    def get_available_players(self):
        """Get players available for auction (UFA, RFA, ENT)"""
        available = self.players_df[
            (self.players_df['FCHL TEAM'].isin(['UFA', 'RFA', 'ENT'])) &
            (self.players_df['Draftable'] == 'YES') &
            (self.players_df['BID'] > 0)
        ].copy()
        
        if available.empty:
            return available
            
        # Sort by position and points
        position_order = {'F': 1, 'D': 2, 'G': 3}
        available['pos_order'] = available['POS'].map(position_order)
        available = available.sort_values(['pos_order', 'PTS'], ascending=[True, False])
        available = available.drop('pos_order', axis=1)
        
        return available

    def get_team_composition(self, team_code):
        """Get detailed team composition with START/MINOR breakdown"""
        team_players = self.players_df[self.players_df['FCHL TEAM'] == team_code]
        
        if team_players.empty:
            return {
                'total_f': 0, 'start_f': 0, 'minor_f': 0,
                'total_d': 0, 'start_d': 0, 'minor_d': 0, 
                'total_g': 0, 'start_g': 0, 'minor_g': 0
            }
        
        composition = {}
        for pos in ['F', 'D', 'G']:
            pos_players = team_players[team_players['POS'] == pos]
            composition[f'total_{pos.lower()}'] = len(pos_players)
            composition[f'start_{pos.lower()}'] = len(pos_players[pos_players['STATUS'] == 'START'])
            composition[f'minor_{pos.lower()}'] = len(pos_players[pos_players['STATUS'] == 'MINOR'])
            
        return composition

    def assign_player_to_team(self, player_index, team_code, auction_price):
        """Assign a player to a team with auction price"""
        self.players_df.loc[player_index, 'FCHL TEAM'] = team_code
        self.players_df.loc[player_index, 'BID'] = auction_price
        self.players_df.loc[player_index, 'STATUS'] = 'START'

    def reset_to_baseline(self):
        """Reset all auction assignments to baseline state"""
        # Reset players that were assigned during auction
        auction_mask = self.players_df['STATUS'] == 'AUCTION'
        self.players_df.loc[auction_mask, 'FCHL TEAM'] = 'UFA'
        self.players_df.loc[auction_mask, 'BID'] = 0
        self.players_df.loc[auction_mask, 'STATUS'] = 'NO'
        
        # Reset any other auction-related changes
        self.players_df.loc[self.players_df['FCHL TEAM'].isin(['RFA', 'UFA', 'ENT']), 'BID'] = 0
