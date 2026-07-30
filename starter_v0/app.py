import os
import sys
from pathlib import Path

# Add parent directory of app.py to sys.path to allow proper imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environmental variables
from env_loader import load_lab_env
load_lab_env(Path(__file__).parent)

# Start web server
from app import run_server

if __name__ == "__main__":
    run_server()
