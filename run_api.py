#!/usr/bin/env python3

import logging
import sys
import traceback
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from api import app  # Import the app from api module

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("powerit-backend")

# Clear existing exception handlers and middleware
# This ensures our middleware doesn't conflict with existing ones
app.middleware_stack = None
app.router.route_class.get_route_handler = lambda *args, **kwargs: None
app.exception_handlers = {}

# Add exception handler for detailed error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Request to {request.url} failed with error: {str(exc)}")
    error_details = traceback.format_exc()
    logger.error(f"Traceback: {error_details}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "traceback": error_details.split("\n"),
            "request_path": str(request.url)
        },
    )

if __name__ == "__main__":
    logger.info("Starting PowerIt backend with enhanced error handling...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 