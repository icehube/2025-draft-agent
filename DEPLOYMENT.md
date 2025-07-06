# DigitalOcean App Platform Deployment Guide

## Quick Setup

### 1. Prepare Your Repository
Upload these files to your GitHub repository:

**Required Files:**
- `app.py` (main application)
- `fantasy_auction.py` (core logic)
- `database.py` (database management)
- `players-24.csv` (player data)
- `teams.json` (team configuration)
- `assets/` folder (NHL logos)

**Deployment Files:**
- `requirements_do.txt` → rename to `requirements.txt`
- `Dockerfile`
- `.do/app.yaml`
- `runtime.txt`
- `.streamlit/config.toml`

### 2. Create DigitalOcean App

1. **Go to DigitalOcean App Platform**
   - Log into your DigitalOcean account
   - Navigate to App Platform
   - Click "Create App"

2. **Connect Repository**
   - Choose "GitHub" as source
   - Select your repository
   - Choose the main branch

3. **Configure App**
   - App name: `fantasy-hockey-auction`
   - Select "Autodeploy" for automatic updates

4. **Set Environment Variables**
   ```
   PORT=8080
   STREAMLIT_SERVER_HEADLESS=true
   STREAMLIT_SERVER_ENABLE_CORS=false
   STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
   ```

5. **Deploy**
   - Review configuration
   - Click "Create Resources"
   - Wait for deployment (5-10 minutes)

### 3. Database Setup (Optional)
For full functionality with data persistence:

1. **Add PostgreSQL Database**
   - In your DigitalOcean app dashboard
   - Go to "Database" tab
   - Add PostgreSQL database
   - Note the connection details

2. **Update Environment Variables**
   ```
   DATABASE_URL=your_postgresql_connection_string
   ```

## Files Overview

### Requirements (`requirements.txt`)
```
streamlit>=1.46.1
pandas>=2.3.0
numpy>=2.3.1
pyscipopt>=5.5.0
psycopg2-binary>=2.9.10
sqlalchemy>=2.0.41
tabulate>=0.9.0
```

### Dockerfile
- Uses Python 3.11 slim image
- Installs SCIP solver for optimization
- Configures Streamlit for web deployment
- Exposes port 8080

### App Configuration (`.do/app.yaml`)
- Defines service configuration
- Sets up environment variables
- Configures build and run commands

## Deployment Features

✅ **Full PySCIPOpt Support** - Mathematical optimization works  
✅ **NHL Logo Display** - Assets properly served  
✅ **PostgreSQL Database** - Optional persistent storage  
✅ **Auto-deploy** - Updates automatically from GitHub  
✅ **Custom Domain** - Can add your own domain  

## Costs
- **Basic Plan**: ~$5/month for small apps
- **Pro Plan**: ~$12/month for production use
- **Database**: ~$7/month for managed PostgreSQL

## Troubleshooting

### Common Issues:
1. **Build fails**: Check requirements.txt formatting
2. **SCIP errors**: Dockerfile handles SCIP installation
3. **Port issues**: App automatically uses PORT environment variable
4. **Asset loading**: Ensure assets/ folder is in repository

### Logs:
- Check "Runtime Logs" in DigitalOcean dashboard
- Look for Streamlit startup messages
- Monitor resource usage

## Alternative Deployment Options

If DigitalOcean doesn't work:
- **Heroku** (with custom buildpack)
- **Google Cloud Run**
- **AWS ECS/Fargate**
- **Railway.app**

All support Docker containers and custom dependencies like SCIP solver.