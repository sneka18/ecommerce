"""
Quick Database Setup Runner
Execute this script to test your MySQL connection, create all 10 tables, and seed initial demo data.
"""
import sys
from pathlib import Path

# Add app directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.init_db import init_database

if __name__ == "__main__":
    print("AI-Enhanced E-Commerce Platform - Database Setup")
    init_database()

