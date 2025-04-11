#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Helper Utilities
----------------------------
This module provides utility functions for the StopJudol application.
"""

import re
import os
import sys
import logging
from datetime import datetime

def format_timestamp(timestamp_str):
    """
    Format a YouTube timestamp string to a readable format
    
    Args:
        timestamp_str (str): ISO 8601 timestamp from YouTube API
        
    Returns:
        str: Formatted timestamp string
    """
    try:
        # Parse ISO 8601 timestamp
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        # Format as readable string
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logging.error(f"Error formatting timestamp: {e}")
        return timestamp_str

def truncate_text(text, max_length=100):
    """
    Truncate text to a maximum length
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + '...'

def html_to_plain_text(html_text):
    """
    Convert HTML text to plain text
    
    Args:
        html_text (str): HTML formatted text
        
    Returns:
        str: Plain text
    """
    # Remove HTML tags
    plain_text = re.sub(r'<[^>]+>', ' ', html_text)
    
    # Replace HTML entities
    plain_text = plain_text.replace('&amp;', '&')
    plain_text = plain_text.replace('&lt;', '<')
    plain_text = plain_text.replace('&gt;', '>')
    plain_text = plain_text.replace('&quot;', '"')
    plain_text = plain_text.replace('&#39;', "'")
    plain_text = plain_text.replace('&nbsp;', ' ')
    
    # Remove extra whitespace
    plain_text = re.sub(r'\s+', ' ', plain_text).strip()
    
    return plain_text

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    
    Args:
        relative_path (str): Relative path to the resource
        
    Returns:
        str: Absolute path to the resource
    """
    # Determine base directory
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (PyInstaller)
        base_dir = sys._MEIPASS
    else:
        # If running from script
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return os.path.join(base_dir, relative_path)

def create_user_data_dir():
    """
    Create user data directory if it doesn't exist
    
    Returns:
        str: Path to user data directory
    """
    user_data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'StopJudol')
    os.makedirs(user_data_dir, exist_ok=True)
    return user_data_dir
