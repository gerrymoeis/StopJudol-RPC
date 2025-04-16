#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Error Handling Module
--------------------------------
This module defines error codes and messages for the JSON-RPC server.
"""

# Define RPC error codes
RPC_ERRORS = {
    # Standard JSON-RPC errors
    -32700: "Parse error",
    -32600: "Invalid Request",
    -32601: "Method not found",
    -32602: "Invalid params",
    -32603: "Internal error",
    
    # Custom error codes
    400: "Bad Request",
    401: "Unauthorized",
    403: "YouTube API Quota Exceeded",
    404: "Comment Not Found",
    500: "Internal Server Error",
    501: "Not Implemented",
    
    # YouTube API specific errors
    1001: "Video Not Found",
    1002: "Comments Disabled",
    1003: "Permission Denied",
    1004: "Invalid Video ID",
    1005: "Invalid Comment ID",
    1006: "Invalid Credentials"
}

def get_error_message(code):
    """
    Get error message for a given error code
    
    Args:
        code (int): Error code
        
    Returns:
        str: Error message
    """
    return RPC_ERRORS.get(code, "Unknown Error")

class RpcError(Exception):
    """Custom exception for RPC errors"""
    
    def __init__(self, code, message=None, data=None):
        """
        Initialize RPC error
        
        Args:
            code (int): Error code
            message (str, optional): Error message. If None, get from RPC_ERRORS
            data (any, optional): Additional error data
        """
        self.code = code
        self.message = message or get_error_message(code)
        self.data = data
        super().__init__(self.message)
        
    def to_dict(self):
        """
        Convert error to dictionary
        
        Returns:
            dict: Error as dictionary
        """
        error = {
            "code": self.code,
            "message": self.message
        }
        
        if self.data:
            error["data"] = self.data
            
        return {"error": error}
