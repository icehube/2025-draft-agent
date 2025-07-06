# Use miniconda for reliable SCIP installation
FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Update conda and install SCIP/PySCIPOpt via conda-forge
RUN conda update -n base -c defaults conda -y \
    && conda install -c conda-forge scip pyscipopt -y \
    && conda install -c conda-forge streamlit pandas numpy sqlalchemy psycopg2 tabulate -y \
    && conda clean -afy

# Copy application files
COPY . .

# Expose port
EXPOSE 8080

# Set environment variables
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]