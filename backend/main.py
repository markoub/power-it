#!/usr/bin/env python3

import logging
import sys
import uvicorn
import traceback
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from database import init_db
import api_new  # Using the new API structure

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("powerit-backend")

# Create a custom exception handler for better debug output
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Request to {request.url} failed with error: {str(e)}")
        error_details = traceback.format_exc()
        logger.error(f"Traceback: {error_details}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(e),
                "traceback": error_details.split("\n")
            },
        )

# Get the app instance from api_new
app = api_new.app

# Add the exception handler middleware
app.middleware("http")(catch_exceptions_middleware)

if __name__ == "__main__":
    logger.info("Starting PowerIt backend with enhanced debugging...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 