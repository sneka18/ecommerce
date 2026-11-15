"""
Backend Launch Script
Runs the FastAPI server with live reloading on http://127.0.0.1:8000
"""
import sys
from pathlib import Path
import uvicorn

# Ensure the Backend directory is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

if __name__ == "__main__":
    print("=" * 60)
    print("Starting AI-Enhanced E-Commerce Platform Server...")
    print("URL: http://127.0.0.1:8000")
    print("API Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

