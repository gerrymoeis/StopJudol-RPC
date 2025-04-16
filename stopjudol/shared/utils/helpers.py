#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Helper Utilities
---------------------------
This module provides helper functions used by both client and server.
"""

import re
from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    """
    Extract video ID from a YouTube URL
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str: Video ID or None if invalid
    """
    # Handle different URL formats
    if 'youtu.be' in url:
        # Short URL format: https://youtu.be/VIDEO_ID
        video_id = url.split('/')[-1].split('?')[0]
    else:
        # Standard format: https://www.youtube.com/watch?v=VIDEO_ID
        parsed_url = urlparse(url)
        if parsed_url.netloc in ('www.youtube.com', 'youtube.com'):
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('v', [None])[0]
        else:
            video_id = None
    
    # Validate video ID format (typically 11 characters)
    if video_id and re.match(r'^[A-Za-z0-9_-]{11}$', video_id):
        return video_id
    return None

def get_comment_id(comment):
    """
    Get the comment ID from a comment object
    
    Args:
        comment (dict): Comment object from YouTube API
        
    Returns:
        str: Comment ID
    """
    # Make sure we're getting the actual comment ID, not the thread ID
    # This was a critical bug in the original application
    return comment['snippet']['topLevelComment']['id']

def get_thread_id(comment):
    """
    Get the thread ID from a comment object
    
    Args:
        comment (dict): Comment object from YouTube API
        
    Returns:
        str: Thread ID
    """
    return comment['id']

def format_error_message(error_code, error_message=None):
    """
    Format an error message based on error code
    
    Args:
        error_code (int): Error code
        error_message (str, optional): Custom error message
        
    Returns:
        str: Formatted error message
    """
    error_messages = {
        400: "Bad Request",
        401: "Unauthorized. Please log in again.",
        403: "Permission denied. You may have exceeded your API quota or don't have permission for this action.",
        404: "Not found. The requested resource doesn't exist.",
        429: "Too many requests. Please try again later.",
        500: "Server error. Please try again later.",
        503: "Service unavailable. Please try again later."
    }
    
    if error_message:
        return error_message
    
    return error_messages.get(error_code, f"Error {error_code}")

def credentials_to_json(credentials):
    """
    Convert Google OAuth credentials to a JSON-serializable dict
    
    Args:
        credentials: Google OAuth credentials
        
    Returns:
        dict: JSON-serializable credentials dict
    """
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
