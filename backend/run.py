import uvicorn
import sys
import asyncio
import os

if __name__ == "__main__":
    # Fix for Playwright on Windows: Force ProactorEventLoop
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    print("🚀 Starting Price-Drop Sniper Pro Backend on Port 8000 (No Reload)...")
    
    # Run Uvicorn on port 8000
    # Reload is disabled to ensure ProactorEventLoop is correctly used on Windows
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False  # Disable reload to prevent subprocess loop issues
    )
