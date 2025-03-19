#!/bin/bash
PORT="${PORT:-5000}"
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true