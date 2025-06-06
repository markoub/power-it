#!/usr/bin/env python3
"""
Test Database Reset Script

This script resets the test database to its initial seeded state.
Useful for running E2E tests that need a fresh database state.
"""

import asyncio
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from init_test_db import main as init_test_db

async def main():
    """Reset the test database."""
    print("🔄 Resetting PowerIt Test Database")
    print("=" * 40)
    
    try:
        # Set environment to test mode
        os.environ["POWERIT_ENV"] = "test"
        
        # Run the initialization (which clears and seeds the database)
        await init_test_db()
        
        print("\n🎯 Test database has been reset!")
        print("All E2E tests can now run with fresh, consistent data.")
        
    except Exception as e:
        print(f"❌ Error resetting test database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())