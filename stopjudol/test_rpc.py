#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - RPC Test Script
--------------------------
This script tests the JSON-RPC communication between client and server.
"""

import os
import sys
import json
import logging
import argparse
import requests
from jsonrpcclient import request, parse, Ok, Error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RPC-Test")

def test_connection(server_url):
    """
    Test connection to the server
    
    Args:
        server_url (str): Server URL
        
    Returns:
        bool: True if connection is successful
    """
    try:
        # Make a simple request to extract_video_id
        # In jsonrpcclient 4.0.3, we need to be careful with parameter names
        # Create a request with params as a dictionary
        request_data = {
            "jsonrpc": "2.0",
            "method": "extract_video_id",
            "params": {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            "id": 1
        }
        
        response = requests.post(
            f"{server_url}/rpc",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # In jsonrpcclient 4.0.3, we need to handle the response manually
            response_data = response.json()
            
            if "result" in response_data:
                logger.info(f"Connection successful: {response_data['result']}")
                return True
            elif "error" in response_data:
                logger.error(f"RPC error: {response_data['error']}")
                return False
        else:
            logger.error(f"HTTP error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return False

def test_authentication(server_url, username, password):
    """
    Test authentication with the server
    
    Args:
        server_url (str): Server URL
        username (str): Username
        password (str): Password
        
    Returns:
        tuple: (success, token or error message)
    """
    try:
        # Make a request to get a token
        response = requests.post(
            f"{server_url}/token",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            if "token" in data:
                logger.info("Authentication successful")
                return True, data["token"]
            else:
                logger.error(f"Invalid response: {data}")
                return False, "Invalid response from server"
        else:
            logger.error(f"Authentication failed: {response.status_code} - {response.text}")
            return False, f"Authentication failed: {response.text}"
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return False, f"Error: {str(e)}"

def test_authenticated_request(server_url, token):
    """
    Test an authenticated request
    
    Args:
        server_url (str): Server URL
        token (str): Authentication token
        
    Returns:
        bool: True if request is successful
    """
    try:
        # Make a request to get_blacklist
        request_data = {
            "jsonrpc": "2.0",
            "method": "get_blacklist",
            "params": {},
            "id": 1
        }
        
        response = requests.post(
            f"{server_url}/rpc",
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # In jsonrpcclient 4.0.3, we need to handle the response manually
            response_data = response.json()
            
            if "result" in response_data:
                logger.info(f"Authenticated request successful: {response_data['result']}")
                return True
            elif "error" in response_data:
                logger.error(f"RPC error: {response_data['error']}")
                return False
        else:
            logger.error(f"HTTP error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Request error: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test JSON-RPC communication")
    parser.add_argument("--url", default="http://localhost:5000", help="Server URL")
    parser.add_argument("--username", default="admin", help="Username for authentication")
    parser.add_argument("--password", default="password", help="Password for authentication")
    args = parser.parse_args()
    
    # Print header
    print("=" * 50)
    print(" StopJudol RPC Test ".center(50, "="))
    print("=" * 50)
    print(f"Server URL: {args.url}")
    print("=" * 50)
    
    # Test connection
    print("\nTesting connection...")
    if not test_connection(args.url):
        print("[X] Connection test failed")
        return 1
    print("[OK] Connection test passed")
    
    # Test authentication
    print("\nTesting authentication...")
    auth_success, token = test_authentication(args.url, args.username, args.password)
    if not auth_success:
        print("[X] Authentication test failed")
        return 1
    print("[OK] Authentication test passed")
    
    # Test authenticated request
    print("\nTesting authenticated request...")
    if not test_authenticated_request(args.url, token):
        print("[X] Authenticated request test failed")
        return 1
    print("[OK] Authenticated request test passed")
    
    # All tests passed
    print("\n" + "=" * 50)
    print(" All Tests Passed ".center(50, "="))
    print("=" * 50)
    return 0

if __name__ == "__main__":
    sys.exit(main())
