# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for SCIP
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libgmp-dev \
    libreadline-dev \
    libncurses5-dev \
    zlib1g-dev \
    libbz2-dev \
    && rm -rf /var/lib/apt/lists/*

# Download and install SCIP
RUN wget -q https://github.com/scipopt/scip/releases/download/v800/SCIPOptSuite-8.0.0-Linux.sh \
    && chmod +x SCIPOptSuite-8.0.0-Linux.sh \
    && ./SCIPOptSuite-8.0.0-Linux.sh --skip-license \
    && rm SCIPOptSuite-8.0.0-Linux.sh

# Set environment variables for SCIP
ENV SCIPOPTDIR=/opt/scip
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/scip/lib

# Copy requirements and install Python dependencies
COPY requirements_do.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8080

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]