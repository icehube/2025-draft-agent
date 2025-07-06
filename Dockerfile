# Use Python 3.11 image with conda for easier SCIP installation
FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Install SCIP via conda-forge (much faster and more reliable)
RUN conda install -c conda-forge scip pyscipopt -y \
    && conda clean -afy

# Install additional Python dependencies via pip
COPY requirements_do.txt requirements.txt
RUN pip install --no-cache-dir streamlit pandas numpy psycopg2-binary sqlalchemy tabulate

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