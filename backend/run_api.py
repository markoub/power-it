#!/usr/bin/env python3
import uvicorn
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Default values
    port = 8000
    environment = "production"
    
    # Check for test mode arguments
    if "--test" in sys.argv:
        environment = "test"
        port = 8001
        print(f"🧪 Running in TEST mode on port {port}")
        # Set environment variable for database selection
        os.environ["POWERIT_ENV"] = "test"
    elif "--port" in sys.argv:
        try:
            port_index = sys.argv.index("--port") + 1
            port = int(sys.argv[port_index])
            print(f"🚀 Running on custom port {port}")
        except (IndexError, ValueError):
            print("❌ Invalid port specified. Using default port 8000.")
            port = 8000
    
    print(f"🔧 Environment: {environment}")
    print(f"🌐 Port: {port}")
    
    # Run the API server with hot reload in development
    uvicorn.run(
        "api:app",
        host="0.0.0.0", 
        port=port, 
        reload=True,
        log_level="info"
    ) 