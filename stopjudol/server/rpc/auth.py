#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Authentication Module
--------------------------------
This module handles JWT authentication for the JSON-RPC server.
"""

import os
import jwt
import time
import logging
from datetime import datetime, timedelta

# Get JWT secret key from environment or use default (in production, always use environment variable)
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "StopJudol_Secret_Key_Change_This_In_Production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24  # Token expires after 24 hours

def create_token(data: dict):
    """
    Create a JWT token
    
    Args:
        data (dict): Data to encode in the token
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    
    # Set expiration time
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire.timestamp()})
    
    # Create token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate(token: str) -> bool:
    """
    Authenticate a JWT token
    
    Args:
        token (str): JWT token
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if token is expired
        expiration = payload.get("exp")
        if expiration is None:
            return False
            
        if time.time() > expiration:
            return False
            
        return True
    except jwt.PyJWTError as e:
        logging.error(f"JWT authentication error: {e}")
        return False
