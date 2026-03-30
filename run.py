"""
Development server script for Personal Loan Tracker
"""

import uvicorn
import os
from pathlib import Path

def main():
    """Run the development server"""
    
    # Ensure required directories exist
    Path("templates").mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    
    # Set development environment
    os.environ["ENVIRONMENT"] = "development"
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()