#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Error Handler
------------------------
This module provides error handling utilities for the StopJudol client.
"""

import logging
from PyQt6.QtWidgets import QMessageBox

# Error codes and messages
ERROR_CODES = {
    # HTTP status codes
    400: "Bad Request: The server could not understand the request.",
    401: "Unauthorized: Authentication is required and has failed or has not been provided.",
    403: "Forbidden: You don't have permission to access this resource.",
    404: "Not Found: The requested resource could not be found.",
    429: "Too Many Requests: You have sent too many requests in a given amount of time.",
    500: "Internal Server Error: The server encountered an unexpected condition.",
    503: "Service Unavailable: The server is currently unavailable.",
    
    # YouTube API specific errors
    1000: "YouTube API Error: An error occurred while communicating with the YouTube API.",
    1001: "YouTube API Quota Exceeded: Your daily quota for YouTube API requests has been exceeded.",
    1002: "YouTube Authentication Error: Failed to authenticate with YouTube.",
    1003: "YouTube Permission Error: You don't have permission to perform this action.",
    
    # Comment-specific errors
    2000: "Comment Not Found: The specified comment could not be found.",
    2001: "Comment Deletion Failed: The comment could not be deleted.",
    2002: "Comment Analysis Failed: The comment could not be analyzed.",
    
    # RPC-specific errors
    3000: "RPC Error: An error occurred while communicating with the server.",
    3001: "RPC Connection Error: Could not connect to the server.",
    3002: "RPC Authentication Error: Failed to authenticate with the server.",
    
    # General errors
    9000: "Unknown Error: An unknown error occurred.",
    9001: "Network Error: A network error occurred.",
    9002: "Timeout Error: The operation timed out."
}

class ErrorHandler:
    """Handler for client-side errors"""
    
    def __init__(self, parent=None):
        """
        Initialize the error handler
        
        Args:
            parent: Parent widget for dialogs
        """
        self.logger = logging.getLogger("ErrorHandler")
        self.parent = parent
    
    def get_error_message(self, code, default_message=None):
        """
        Get a human-readable error message for an error code
        
        Args:
            code (int): Error code
            default_message (str, optional): Default message if code is not found
            
        Returns:
            str: Error message
        """
        if code in ERROR_CODES:
            return ERROR_CODES[code]
        elif default_message:
            return default_message
        else:
            return f"Error {code}: An unknown error occurred."
    
    def show_error_dialog(self, title, message, details=None):
        """
        Show an error dialog
        
        Args:
            title (str): Dialog title
            message (str): Error message
            details (str, optional): Detailed error information
        """
        # Log the error
        self.logger.error(f"{title}: {message}")
        if details:
            self.logger.error(f"Details: {details}")
        
        # Create and show the dialog
        dialog = QMessageBox(self.parent)
        dialog.setIcon(QMessageBox.Icon.Critical)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        
        if details:
            dialog.setDetailedText(details)
        
        dialog.addButton(QMessageBox.StandardButton.Ok)
        dialog.exec()
    
    def handle_rpc_error(self, error, operation=None):
        """
        Handle an RPC error
        
        Args:
            error: Error object or message
            operation (str, optional): Operation that failed
        """
        # Determine the error message
        if isinstance(error, dict) and "code" in error and "message" in error:
            # JSON-RPC error object
            code = error["code"]
            message = error["message"]
            title = f"Error {code}"
            details = str(error)
        elif isinstance(error, Exception):
            # Exception object
            title = "Error"
            message = str(error)
            details = f"{type(error).__name__}: {str(error)}"
        else:
            # String or other error
            title = "Error"
            message = str(error)
            details = None
        
        # Add operation context if provided
        if operation:
            title = f"{operation} Error"
        
        # Show the error dialog
        self.show_error_dialog(title, message, details)
    
    def handle_youtube_error(self, error, operation=None):
        """
        Handle a YouTube API error
        
        Args:
            error: Error object or message
            operation (str, optional): Operation that failed
        """
        # YouTube API errors often have a 'reason' field
        if hasattr(error, 'reason'):
            message = error.reason
        else:
            message = str(error)
        
        # Check for quota exceeded errors
        if "quota" in message.lower():
            code = 1001
            message = self.get_error_message(code)
        # Check for authentication errors
        elif "auth" in message.lower() or "unauthorized" in message.lower():
            code = 1002
            message = self.get_error_message(code)
        # Check for permission errors
        elif "permission" in message.lower() or "access" in message.lower():
            code = 1003
            message = self.get_error_message(code)
        else:
            code = 1000
        
        # Set title based on operation or code
        if operation:
            title = f"{operation} Error"
        else:
            title = self.get_error_message(code).split(":")[0]
        
        # Show the error dialog
        self.show_error_dialog(title, message, str(error))
    
    def handle_network_error(self, error, operation=None):
        """
        Handle a network error
        
        Args:
            error: Error object or message
            operation (str, optional): Operation that failed
        """
        # Determine if it's a timeout error
        if "timeout" in str(error).lower():
            code = 9002
            message = self.get_error_message(code)
        else:
            code = 9001
            message = self.get_error_message(code)
        
        # Set title based on operation or code
        if operation:
            title = f"{operation} Error"
        else:
            title = self.get_error_message(code).split(":")[0]
        
        # Show the error dialog
        self.show_error_dialog(title, message, str(error))
