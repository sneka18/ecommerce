"""
Database Connection Verification Script
Tests the connection to MySQL using parameters loaded from .env
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the Backend directory
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "ai_ecommerce_db")

print("=" * 60)
print("MySQL Database Connection Diagnostic")
print("=" * 60)
print(f"Host:     {DB_HOST}")
print(f"Port:     {DB_PORT}")
print(f"User:     {DB_USER}")
print(f"Database: {DB_NAME}")
masked_pwd = "*" * len(DB_PASSWORD) if DB_PASSWORD else "(EMPTY/BLANK)"
print(f"Password: {masked_pwd}")
print("=" * 60)

# Step 1: Test with raw PyMySQL
print("\n[Step 1] Testing direct connection using PyMySQL...")
try:
    import pymysql
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4'
    )
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        print(f" SUCCESS: Connected to MySQL Server! Version: {version[0]}")
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        print(f" Existing tables in '{DB_NAME}': {table_names if table_names else 'None (Empty Database)'}")
    connection.close()
except Exception as e:
    print(f" FAILED direct PyMySQL connection: {e}")
    if "1045" in str(e):
        print("\n--> TIP: Access denied for root. Please update DB_PASSWORD in Backend/.env with your MySQL root password.")
    sys.exit(1)

# Step 2: Test with SQLAlchemy
print("\n[Step 2] Testing connection using SQLAlchemy ORM engine...")
try:
    from urllib.parse import quote_plus
    from sqlalchemy import create_engine, text
    # Build database URL with pymysql driver
    encoded_pwd = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
    url = f"mysql+pymysql://{DB_USER}:{encoded_pwd}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT 1")).scalar()
        print(f" SUCCESS: SQLAlchemy connection pool successfully verified! (Result: {res})")
except Exception as e:
    print(f" FAILED SQLAlchemy connection: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print(" DATABASE VERIFICATION COMPLETE: ALL SYSTEMS READY!")
print("=" * 60)

