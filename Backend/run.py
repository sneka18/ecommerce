"""
Backend Launch Script
Runs the FastAPI server with dynamic host and port support for local and Render deployment
"""
import os
import sys
from pathlib import Path
import uvicorn

# Ensure the Backend directory is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "False").lower() in ("true", "1")
    print("=" * 60)
    print("Starting AI-Enhanced E-Commerce Platform Server...")
    print(f"URL: http://{host}:{port}")
    print(f"API Docs: http://{host}:{port}/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host=host, port=port, reload=debug)

