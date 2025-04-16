#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - JSON-RPC Server
--------------------------
This module provides the main server application for StopJudol.
"""

import os
import json
import logging
from aiohttp import web
from jsonrpcserver import async_dispatch, Success, Error
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server.log", mode='a', encoding='utf-8', delay=False)
    ]
)

# Import RPC handlers
from .rpc.handler import *
from .rpc.auth import authenticate, create_token

# Load environment variables
load_dotenv()

# Authentication middleware
@web.middleware
async def auth_middleware(request, handler):
    # Skip authentication for the token endpoint
    if request.path == "/token":
        return await handler(request)
    
    # Skip authentication for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        return await handler(request)
    
    # Get the authorization header
    auth_header = request.headers.get("Authorization")
    
    # If no auth header is provided, check if the method requires authentication
    if not auth_header:
        # Parse the request to get the method name
        try:
            request_data = await request.json()
            method = request_data.get("method")
            
            # List of methods that don't require authentication
            public_methods = [
                "extract_video_id", 
                "get_blacklist", 
                "get_whitelist",
                "get_setting"
            ]
            
            if method in public_methods:
                return await handler(request)
                
        except Exception:
            pass
            
        return web.Response(
            text=json.dumps({"error": {"code": 401, "message": "Unauthorized"}}),
            status=401,
            content_type="application/json"
        )
    
    # Validate the token
    token = auth_header.replace("Bearer ", "")
    if not authenticate(token):
        return web.Response(
            text=json.dumps({"error": {"code": 401, "message": "Invalid token"}}),
            status=401,
            content_type="application/json"
        )
    
    # Continue with the request
    return await handler(request)

# Handle RPC requests
async def handle_rpc(request):
    """Handle JSON-RPC requests"""
    try:
        # Get the request body
        request_data = await request.text()
        logging.info(f"Received RPC request: {request_data}")
        
        # Dispatch the request
        response = await async_dispatch(request_data)
        logging.info(f"RPC response: {response}")
        
        # Return the response
        return web.Response(text=response, content_type="application/json")
    except Exception as e:
        logging.error(f"Error handling RPC request: {e}")
        return web.Response(text=json.dumps({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": "Internal error"},
            "id": None
        }), content_type="application/json")

# Handle token requests
async def handle_token(request):
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        # In a real application, you would validate the credentials against a database
        # For this example, we'll use environment variables
        valid_username = os.environ.get("API_USERNAME", "admin")
        valid_password = os.environ.get("API_PASSWORD", "password")
        
        if username == valid_username and password == valid_password:
            token = create_token({"username": username})
            return web.Response(
                text=json.dumps({"token": token}),
                content_type="application/json"
            )
        else:
            return web.Response(
                text=json.dumps({"error": "Invalid credentials"}),
                status=401,
                content_type="application/json"
            )
    except Exception as e:
        logging.error(f"Error generating token: {e}")
        return web.Response(
            text=json.dumps({"error": str(e)}),
            status=500,
            content_type="application/json"
        )

# CORS middleware
@web.middleware
async def cors_middleware(request, handler):
    response = await handler(request)
    
    # Add CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    
    return response

# Create the application
app = web.Application(middlewares=[cors_middleware, auth_middleware])

# Add routes
app.router.add_post("/rpc", handle_rpc)
app.router.add_post("/token", handle_token)
app.router.add_options("/rpc", lambda request: web.Response())  # Handle CORS preflight
app.router.add_options("/token", lambda request: web.Response())  # Handle CORS preflight

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 5000))
    
    # Run the server
    logging.info(f"Starting StopJudol JSON-RPC server on port {port}")
    web.run_app(app, port=port)
