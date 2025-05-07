#!/usr/bin/env python3

"""
Main entry point for running the Presentation Assistant server.
This script allows running the server directly or through MCP CLI.
"""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import server module
from server import mcp

if __name__ == "__main__":
    print("Starting Presentation Assistant server...")
    mcp.run() 