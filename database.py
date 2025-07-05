"""
Database management for Fantasy Hockey Auction System
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json

Base = declarative_base()

class FantasyDatabase:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not found")
        
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.metadata = MetaData()
        
    def init_database(self):
        """Initialize database tables"""
        with self.engine.connect() as conn:
            # Create players table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    player_name VARCHAR(255) NOT NULL,
                    position VARCHAR(10) NOT NULL,
                    nhl_team VARCHAR(10),
                    fchl_team VARCHAR(10),
                    status VARCHAR(20),
                    group_code VARCHAR(10),
                    age INTEGER,
                    salary DECIMAL(10,2),
                    bid DECIMAL(10,2),
                    points INTEGER,
                    z_score DECIMAL(10,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create auction_sessions table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS auction_sessions (
                    id SERIAL PRIMARY KEY,
                    session_name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT FALSE
                )
            """))
            
            # Create auction_history table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS auction_history (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER REFERENCES auction_sessions(id),
                    player_id INTEGER REFERENCES players(id),
                    from_team VARCHAR(10),
                    to_team VARCHAR(10),
                    auction_price DECIMAL(10,2),
                    action_type VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create team_budgets table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS team_budgets (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER REFERENCES auction_sessions(id),
                    team_code VARCHAR(10) NOT NULL,
                    committed_salary DECIMAL(10,2) DEFAULT 0,
                    auction_spending DECIMAL(10,2) DEFAULT 0,
                    remaining_budget DECIMAL(10,2),
                    f_count INTEGER DEFAULT 0,
                    d_count INTEGER DEFAULT 0,
                    g_count INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.commit()
    
    def save_players_data(self, df, session_id=None):
        """Save players dataframe to database"""
        if session_id is None:
            session_id = self.create_auction_session("Default Session")
        
        # Clear existing data for this session
        with self.engine.connect() as conn:
            conn.execute(text("DELETE FROM players WHERE id IN (SELECT player_id FROM auction_history WHERE session_id = :session_id)"), 
                        {"session_id": session_id})
        
        # Prepare data for database
        db_data = []
        for _, row in df.iterrows():
            db_data.append({
                'player_name': row['PLAYER'],
                'position': row['POS'],
                'nhl_team': row.get('NHL TEAM', ''),
                'fchl_team': row.get('FCHL TEAM', ''),
                'status': row.get('STATUS', 'UFA'),
                'group_code': row.get('GROUP', ''),
                'age': int(row.get('AGE', 0)) if pd.notna(row.get('AGE', 0)) else None,
                'salary': float(row.get('SALARY', 0)) if pd.notna(row.get('SALARY', 0)) else 0,
                'bid': float(row.get('BID', 0)) if pd.notna(row.get('BID', 0)) else 0,
                'points': int(row.get('PTS', 0)) if pd.notna(row.get('PTS', 0)) else 0,
                'z_score': float(row.get('Z_SCORE', 0)) if pd.notna(row.get('Z_SCORE', 0)) else 0
            })
        
        # Insert data
        df_to_insert = pd.DataFrame(db_data)
        df_to_insert.to_sql('players', self.engine, if_exists='append', index=False)
        
        return session_id
    
    def load_players_data(self, session_id=None):
        """Load players data from database"""
        query = """
            SELECT player_name as "PLAYER", position as "POS", nhl_team as "NHL TEAM",
                   fchl_team as "FCHL TEAM", status as "STATUS", group_code as "GROUP",
                   age as "AGE", salary as "SALARY", bid as "BID", points as "PTS",
                   z_score as "Z_SCORE"
            FROM players
        """
        
        if session_id:
            query += f" WHERE id IN (SELECT player_id FROM auction_history WHERE session_id = {session_id})"
        
        return pd.read_sql(query, self.engine)
    
    def create_auction_session(self, session_name):
        """Create a new auction session"""
        with self.engine.connect() as conn:
            # Deactivate all existing sessions
            conn.execute(text("UPDATE auction_sessions SET is_active = FALSE"))
            
            # Create new session
            result = conn.execute(text("""
                INSERT INTO auction_sessions (session_name, is_active) 
                VALUES (:name, TRUE) 
                RETURNING id
            """), {"name": session_name})
            
            session_id = result.fetchone()[0]
            conn.commit()
            return session_id
    
    def get_active_session(self):
        """Get the active auction session"""
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT id, session_name FROM auction_sessions WHERE is_active = TRUE LIMIT 1"))
            row = result.fetchone()
            return {"id": row[0], "name": row[1]} if row else None
    
    def log_auction_action(self, session_id, player_id, from_team, to_team, auction_price, action_type):
        """Log an auction action"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO auction_history (session_id, player_id, from_team, to_team, auction_price, action_type)
                VALUES (:session_id, :player_id, :from_team, :to_team, :auction_price, :action_type)
            """), {
                "session_id": session_id,
                "player_id": player_id,
                "from_team": from_team,
                "to_team": to_team,
                "auction_price": auction_price,
                "action_type": action_type
            })
            conn.commit()
    
    def update_team_budgets(self, session_id, team_budgets):
        """Update team budget information"""
        with self.engine.connect() as conn:
            # Clear existing budget data for this session
            conn.execute(text("DELETE FROM team_budgets WHERE session_id = :session_id"), {"session_id": session_id})
            
            # Insert new budget data
            for team_code, budget_info in team_budgets.items():
                conn.execute(text("""
                    INSERT INTO team_budgets (session_id, team_code, committed_salary, auction_spending, 
                                            remaining_budget, f_count, d_count, g_count)
                    VALUES (:session_id, :team_code, :committed_salary, :auction_spending,
                            :remaining_budget, :f_count, :d_count, :g_count)
                """), {
                    "session_id": session_id,
                    "team_code": team_code,
                    "committed_salary": budget_info.get('committed_salary', 0),
                    "auction_spending": budget_info.get('auction_spending', 0),
                    "remaining_budget": budget_info.get('remaining', 0),
                    "f_count": budget_info.get('f_count', 0),
                    "d_count": budget_info.get('d_count', 0),
                    "g_count": budget_info.get('g_count', 0)
                })
            conn.commit()
    
    def get_auction_history(self, session_id=None):
        """Get auction history"""
        query = """
            SELECT ah.*, p.player_name, s.session_name
            FROM auction_history ah
            JOIN players p ON ah.player_id = p.id
            JOIN auction_sessions s ON ah.session_id = s.id
        """
        
        if session_id:
            query += f" WHERE ah.session_id = {session_id}"
        
        query += " ORDER BY ah.timestamp DESC"
        
        return pd.read_sql(query, self.engine)
    
    def get_session_list(self):
        """Get list of all auction sessions"""
        query = "SELECT id, session_name, created_at, is_active FROM auction_sessions ORDER BY created_at DESC"
        return pd.read_sql(query, self.engine)