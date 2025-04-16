#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Server Runner
------------------------
This script starts the StopJudol JSON-RPC server.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the stopjudol directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the server main module
import server.main
app = server.main.app

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("server.log")
        ]
    )
    
    # Load environment variables
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "server", ".env"))
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 5000))
    
    # Print startup message
    print("=" * 50)
    print(" StopJudol JSON-RPC Server ".center(50, "="))
    print("=" * 50)
    print(f"Starting server on port {port}...")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the server
    from aiohttp import web
    web.run_app(app, port=port)
