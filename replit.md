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

## Recent Changes

### July 06, 2025 - DigitalOcean Deployment Configuration
- Created DigitalOcean App Platform deployment configuration (.do/app.yaml)
- Added Dockerfile with SCIP solver installation for PySCIPOpt support
- Created deployment-ready requirements.txt (requirements_do.txt)
- Configured Streamlit for cloud deployment with proper port and CORS settings
- Added runtime.txt specifying Python 3.11.10
- Set up environment variables for SCIP optimization library

### July 06, 2025 - NHL Logo Column and Bug Fixes
- Added NHL Team logo column to Team Preview using ImageColumn
- Fixed column structure issues and base64 encoding for proper logo display
- Implemented save button for budget updates without callback errors
- All Team Preview functionality working: salary editing, status changes, logo display

### July 06, 2025 - Team Preview Table Consolidation
- Merged duplicate tables in Team Preview into single editable table
- Applied position (F/D/G) and group (A-G) styling directly to editable data editor
- Maintained gradient team headers while simplifying table display
- Improved user experience with unified table showing all data with styling

### July 05, 2025 - Interface Redesign and Summary Page Overhaul
- Set sidebar to be hidden on startup (collapsed state)
- Moved title "🏒 2025 BOT Draft Agent" to hidden sidebar instead of main page
- Removed descriptive text "Manage your fantasy hockey auction with real-time budget tracking and optimization"
- Renamed "Budget Summary" tab to "📊 Summary"
- Completely redesigned Summary page with new features:
  - Removed "Total Auction", "Status", and "Auction" columns from budget table
  - Added editable "Penalty" column with number input controls
  - Created new "Player Pool Summary" table showing F/D/G drafted and available counts
  - Simplified financial metrics to show only Total Pool, Total Committed, and Available
- Enhanced user experience with cleaner, more focused interface design

### July 05, 2025 - Automatic CSV Loading Implementation
- Saved players-24.csv permanently in project root directory
- Modified main() function to automatically load CSV data on startup
- Removed file upload requirement - app now starts immediately with player data
- Simplified sidebar by removing upload controls and showing only reset button
- Enhanced error handling for missing or corrupted CSV files
- Streamlined user experience - no more manual CSV uploads needed

### July 05, 2025 - Complete Interface Overhaul and Bug Fixes
- Removed duplicate tables from Team Preview and BOT Team pages - single table with styling now shown
- Applied gradient styling to team roster headers ("Heskel Salims Roster" style) 
- Added position and group styling to editable tables (F/D/G colors and A-G group colors)
- Moved "Remove Player from Team" section to bottom of pages for better flow
- Created proper Team Composition table with Position/START/MINOR/Total structure
- Positioned Budget Summary at top-right after team selection on Team Preview
- Removed points display from player assignment dropdown (cleaner selection)
- Fixed player assignment to set status to START instead of AUCTION (major bug fix)
- Enhanced NHL team logos with proper aspect ratio CSS (object-fit: contain)
- Implemented comprehensive visual styling system throughout all interfaces

### July 05, 2025 - PostgreSQL Database Integration
- Added PostgreSQL database support for persistent data storage
- Created comprehensive database schema with players, sessions, auction history, and team budgets
- Implemented database interface with session management and auction history tracking
- Added save/load functionality for seamless data persistence across sessions
- Created FantasyDatabase class with full CRUD operations for auction data
- Added new Database tab to main interface for auction session management

### July 05, 2025 - Auto-Reactive Interface with Enhanced Editing
- Implemented automatic recalculation and optimization when data changes (removed manual buttons)
- Enhanced Team Preview with visual indicators for editable fields (✏️ Status, Salary)
- Added real-time auto-updating of budgets and optimal team when cells are edited
- Replaced Player Assignment with focused "Remaining Players" interface showing only auction-available players
- Added player removal functionality to return players to auction pool
- Improved team composition tracking with START/MINOR breakdown by position
- Streamlined interface with clear visual cues for which fields can be edited

### July 05, 2025 - Enhanced BOT Team Features
- Added dedicated BOT (Bridlewood AI) team optimization interface
- Implemented optimal team configuration display with detailed roster view
- Enhanced budget tracking to include player counts by position (F/D/G)
- Added comprehensive team roster management with editable player status
- Improved Group visibility throughout the interface (Groups A-G MINOR players don't count against salary cap)
- Created specialized tabs: Budget Summary, BOT Team, Team Preview, Remaining Players
- Added real-time budget validation and team composition tracking

### July 05, 2025 - Initial Setup
- Created Streamlit web interface for fantasy hockey auction management
- Implemented core FantasyAuction class with Z-score calculations and optimization
- Set up file upload functionality for player CSV data
- Established team budget tracking and player assignment capabilities

## User Preferences

- Focus on Bridlewood AI (BOT) team optimization and management
- Need visibility into Group classifications for salary cap calculations
- Require editable team rosters with status management (START/MINOR affects budgets)
- Want clear view of optimal team construction after auction completion

## Changelog

Changelog:
- July 05, 2025. Enhanced with BOT team focus and team management features
- July 05, 2025. Initial setup