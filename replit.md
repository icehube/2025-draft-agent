# Fantasy Hockey Auction Manager

## Overview

The Fantasy Hockey Auction Manager is a Streamlit-based web application designed to manage fantasy hockey auction drafts. The system processes player data from CSV files and provides auction management capabilities with team budget tracking and player valuation. The application supports 11 teams with specific budget penalties and position requirements (14 forwards, 7 defense, 3 goalies per team).

## System Architecture

### Frontend Architecture
- **Streamlit Web Interface**: Single-page application built with Streamlit for interactive user experience
- **Data Visualization**: Uses pandas DataFrames for data manipulation and display
- **Session State Management**: Streamlit session state maintains application state across user interactions

### Backend Architecture
- **Core Logic**: `FantasyAuction` class handles all business logic and data processing
- **Optimization Engine**: Integration with PySCIPOpt for mathematical optimization (linear programming)
- **Data Processing**: Pandas-based data manipulation and validation

### Data Storage
- **CSV Data Input**: Primary data source through CSV file uploads containing player information
- **JSON Configuration**: Static team configuration stored in `teams.json`
- **In-Memory Processing**: All data processing occurs in memory using pandas DataFrames

## Key Components

### 1. Main Application (`app.py`)
- Streamlit web interface entry point
- Handles file uploads and user interactions
- Manages session state for auction data
- Provides CSV data validation and processing

### 2. Auction Engine (`fantasy_auction.py`)
- Core `FantasyAuction` class for business logic
- Player data processing and validation
- Budget calculations and team management
- Integration with optimization solver

### 3. Team Configuration (`teams.json`)
- Static configuration for 11 fantasy teams
- Team names, IDs, and penalty structures
- Penalty values range from 0.5 to 2.5

### 4. Constants and Business Rules
- Salary cap: $56.8M per team
- Minimum salary: $0.5M
- Position requirements: 14F/7D/3G per team
- 11 total teams in the league

## Data Flow

1. **Data Input**: Users upload CSV files containing player data with required columns (PLAYER, POS, GROUP, STATUS, FCHL TEAM, NHL TEAM, AGE, SALARY, BID, PTS)
2. **Data Validation**: System validates required columns and converts data types
3. **Data Processing**: `FantasyAuction` class processes player data and applies business rules
4. **State Management**: Processed data stored in Streamlit session state
5. **User Interaction**: Web interface allows users to view and manage auction data
6. **Optimization**: PySCIPOpt solver used for mathematical optimization tasks

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **pyscipopt**: Mathematical optimization solver
- **json**: JSON data handling

### Data Dependencies
- CSV files with specific column structure for player data
- teams.json configuration file for team setup

## Deployment Strategy

### Current Setup
- Single-file Streamlit application deployable on any Python environment
- No database dependencies - all data processing in memory
- Static configuration files included in repository

### Scalability Considerations
- In-memory processing suitable for current data volumes
- No persistent storage - data reloaded on each session
- Stateless design allows for easy horizontal scaling

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- July 05, 2025. Initial setup