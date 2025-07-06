#!/bin/bash

# Install SCIP solver for PySCIPOpt
apt-get update
apt-get install -y wget build-essential

# Download and install SCIP
wget https://scip.zib.de/download/release/scipoptsuite-8.0.4.tgz
tar -xzf scipoptsuite-8.0.4.tgz
cd scipoptsuite-8.0.4
make SHARED=true
make install SHARED=true
cd ..

# Set environment variables
export SCIPOPTDIR=/usr/local
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

# Start the Streamlit app
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true