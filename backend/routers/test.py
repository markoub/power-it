"""
Test Router

Provides endpoints for E2E testing, including database reset functionality.
Only available in test environment.
"""

import os
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

# Import the test database initialization
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from init_test_db import clear_test_database, seed_test_database

router = APIRouter(prefix="/test", tags=["test"])

@router.post("/reset-database")
async def reset_test_database():
    """
    Reset the test database to its initial seeded state.
    Only available when running in test environment.
    """
    # Check if we're running in test environment
    env = os.getenv("POWERIT_ENV", "production")
    if env != "test":
        raise HTTPException(
            status_code=403, 
            detail="Database reset is only available in test environment"
        )
    
    try:
        # Clear and reseed the database
        await clear_test_database()
        await seed_test_database()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Test database reset successfully",
                "status": "success"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset test database: {str(e)}"
        )

@router.get("/presentations")
async def get_test_presentations():
    """
    Get a list of all test presentations with their current status.
    Only available when running in test environment.
    """
    # Check if we're running in test environment
    env = os.getenv("POWERIT_ENV", "production")
    if env != "test":
        raise HTTPException(
            status_code=403, 
            detail="Test endpoints are only available in test environment"
        )
    
    from database import SessionLocal
    from sqlalchemy import text
    
    try:
        async with SessionLocal() as db:
            result = await db.execute(text("""
                SELECT p.id, p.name, p.topic, p.author,
                       GROUP_CONCAT(ps.step || ':' || ps.status) as steps
                FROM presentations p
                LEFT JOIN presentation_steps ps ON p.id = ps.presentation_id
                WHERE p.is_deleted = 0
                GROUP BY p.id, p.name, p.topic, p.author
                ORDER BY p.id
            """))
            
            presentations = []
            for row in result.fetchall():
                steps_info = {}
                if row[4]:  # steps column
                    for step_status in row[4].split(','):
                        step, status = step_status.split(':')
                        steps_info[step] = status
                
                presentations.append({
                    "id": row[0],
                    "name": row[1], 
                    "topic": row[2],
                    "author": row[3],
                    "steps": steps_info
                })
            
            return JSONResponse(
                status_code=200,
                content={
                    "presentations": presentations,
                    "count": len(presentations)
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get test presentations: {str(e)}"
        )

@router.get("/environment")
async def get_test_environment():
    """
    Get information about the current test environment.
    """
    env = os.getenv("POWERIT_ENV", "production")
    
    return JSONResponse(
        status_code=200,
        content={
            "environment": env,
            "is_test_mode": env == "test",
            "database_file": os.getenv("DATABASE_FILE", "presentations.db"),
            "test_database_file": os.getenv("TEST_DATABASE_FILE", "presentations_test.db")
        }
    )