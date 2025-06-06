#!/usr/bin/env python3
"""Quick script to check test database contents"""

import asyncio
import os
import sys
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal

async def check_presentation_3():
    """Check the state of presentation ID 3"""
    os.environ["POWERIT_ENV"] = "test"
    
    async with SessionLocal() as db:
        result = await db.execute(text("""
            SELECT p.id, p.name, ps.step, ps.status
            FROM presentations p
            JOIN presentation_steps ps ON p.id = ps.presentation_id
            WHERE p.id = 3
            ORDER BY ps.step
        """))
        
        print("Presentation 3 status:")
        for row in result.fetchall():
            print(f"  {row[2]}: {row[3]}")

if __name__ == "__main__":
    asyncio.run(check_presentation_3())