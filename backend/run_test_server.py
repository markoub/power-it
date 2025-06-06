#!/usr/bin/env python3
"""
Test Server Runner

Starts the backend API server in test mode with:
- Test database (presentations_test.db)
- Test port (8001)
- Environment set to 'test'
"""

import asyncio
import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from init_test_db import main as init_test_db

async def setup_test_environment():
    """Set up the test environment and database."""
    print("🔧 Setting up test environment...")
    
    # Set environment variables for test mode
    os.environ["POWERIT_ENV"] = "test"
    os.environ["DATABASE_FILE"] = "presentations_test.db"
    
    # Initialize test database with seed data
    await init_test_db()
    
    print("✅ Test environment ready!")

def run_test_server():
    """Run the API server in test mode."""
    print("🚀 Starting PowerIt Test Server")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Set test environment
    os.environ["POWERIT_ENV"] = "test"
    
    # Run server on test port
    port = 8001
    print(f"🧪 Test server starting on port {port}")
    print(f"🗄️  Using test database: presentations_test.db")
    print(f"🌐 API will be available at: http://localhost:{port}")
    print(f"📚 API docs at: http://localhost:{port}/docs")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

async def main():
    """Main function to set up test environment and start server."""
    try:
        # Initialize test database first
        await setup_test_environment()
        
        # Start the server
        run_test_server()
        
    except KeyboardInterrupt:
        print("\n👋 Test server stopped by user")
    except Exception as e:
        print(f"❌ Error starting test server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if we should only initialize the database
    if "--init-only" in sys.argv:
        print("🗄️  Initializing test database only...")
        asyncio.run(init_test_db())
        print("✅ Database initialization complete")
    else:
        # Run the full setup and server
        asyncio.run(main())