#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - JSON-RPC Handler
----------------------------
This module provides the JSON-RPC methods for the StopJudol server.
"""

import logging
from jsonrpcserver import method, Success, Error
from ..core.youtube_api import YouTubeAPI
from ..core.analysis import CommentAnalyzer
from ..core.config_manager import ConfigManager
from google.oauth2.credentials import Credentials
import json

# Initialize the config manager
config_manager = ConfigManager()

@method
async def fetch_comments(video_id: str, credentials_json: str = None):
    """
    Fetch comments for a YouTube video
    
    Args:
        video_id (str): YouTube video ID
        credentials_json (str, optional): OAuth credentials as JSON string
        
    Returns:
        dict: API response containing comments
    """
    try:
        # Initialize YouTube API with credentials if provided
        if credentials_json:
            credentials_data = json.loads(credentials_json)
            credentials = Credentials.from_authorized_user_info(credentials_data)
            youtube_api = YouTubeAPI(credentials)
        else:
            # Use API key instead (limited functionality)
            api_key = config_manager.get_api_key()
            if not api_key:
                return Error(403, "No API key or credentials provided")
            youtube_api = YouTubeAPI(None)  # TODO: Implement API key support
            
        # Get comments
        comments = youtube_api.get_all_comments(video_id)
        return Success(comments)
    except Exception as e:
        logging.error(f"Error fetching comments: {e}")
        return Error(500, str(e))

@method
async def analyze_comments(comments: list):
    """
    Analyze comments for spam, gambling, etc.
    
    Args:
        comments (list): List of comment objects from YouTube API
        
    Returns:
        list: List of flagged comments with analysis results
    """
    try:
        analyzer = CommentAnalyzer(config_manager)
        flagged_comments = analyzer.analyze_comments_batch(comments)
        return Success(flagged_comments)
    except Exception as e:
        logging.error(f"Error analyzing comments: {e}")
        return Error(500, str(e))

@method
async def delete_comment(comment_id: str, thread_id: str = None, credentials_json: str = None):
    """
    Delete a YouTube comment
    
    Args:
        comment_id (str): Comment ID to delete
        thread_id (str, optional): Comment thread ID, used for moderation
        credentials_json (str): OAuth credentials as JSON string
        
    Returns:
        dict: Result of the deletion operation
    """
    try:
        if not credentials_json:
            return Error(401, "Credentials required for deletion")
            
        credentials_data = json.loads(credentials_json)
        credentials = Credentials.from_authorized_user_info(credentials_data)
        youtube_api = YouTubeAPI(credentials)
        
        result = youtube_api.delete_comment(comment_id, thread_id)
        return Success(result)
    except Exception as e:
        logging.error(f"Error deleting comment: {e}")
        return Error(500, str(e))

@method
async def get_channel_info(credentials_json: str):
    """
    Get information about the authenticated user's channel
    
    Args:
        credentials_json (str): OAuth credentials as JSON string
        
    Returns:
        dict: Channel information
    """
    try:
        if not credentials_json:
            return Error(401, "Credentials required")
            
        credentials_data = json.loads(credentials_json)
        credentials = Credentials.from_authorized_user_info(credentials_data)
        youtube_api = YouTubeAPI(credentials)
        
        channel_name = youtube_api.get_channel_name()
        return Success({"channel_name": channel_name})
    except Exception as e:
        logging.error(f"Error getting channel info: {e}")
        return Error(500, str(e))

@method
async def extract_video_id(url: str):
    """
    Extract video ID from a YouTube URL
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str: Video ID or None if invalid
    """
    try:
        # Extract video ID directly without using YouTubeAPI class
        import re
        from urllib.parse import urlparse, parse_qs
        
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
            return Success({"video_id": video_id})
        else:
            return Error(400, "Invalid YouTube URL")
    except Exception as e:
        logging.error(f"Error extracting video ID: {e}")
        return Error(500, str(e))

@method
async def get_blacklist():
    """
    Get the blacklist of keywords
    
    Returns:
        list: Blacklisted keywords
    """
    try:
        blacklist = config_manager.get_blacklist()
        return Success(blacklist)
    except Exception as e:
        logging.error(f"Error getting blacklist: {e}")
        return Error(500, str(e))

@method
async def get_whitelist():
    """
    Get the whitelist of keywords
    
    Returns:
        list: Whitelisted keywords
    """
    try:
        whitelist = config_manager.get_whitelist()
        return Success(whitelist)
    except Exception as e:
        logging.error(f"Error getting whitelist: {e}")
        return Error(500, str(e))

@method
async def add_blacklist_term(term: str, category: str = "Other"):
    """
    Add a term to the blacklist
    
    Args:
        term (str): Term to add
        category (str, optional): Category for the term
        
    Returns:
        bool: Success status
    """
    try:
        config_manager.add_blacklist_term(term, category)
        return Success(True)
    except Exception as e:
        logging.error(f"Error adding blacklist term: {e}")
        return Error(500, str(e))

@method
async def remove_blacklist_term(term: str):
    """
    Remove a term from the blacklist
    
    Args:
        term (str): Term to remove
        
    Returns:
        bool: Success status
    """
    try:
        config_manager.remove_blacklist_term(term)
        return Success(True)
    except Exception as e:
        logging.error(f"Error removing blacklist term: {e}")
        return Error(500, str(e))

@method
async def add_whitelist_term(term: str):
    """
    Add a term to the whitelist
    
    Args:
        term (str): Term to add
        
    Returns:
        bool: Success status
    """
    try:
        config_manager.add_whitelist_term(term)
        return Success(True)
    except Exception as e:
        logging.error(f"Error adding whitelist term: {e}")
        return Error(500, str(e))

@method
async def remove_whitelist_term(term: str):
    """
    Remove a term from the whitelist
    
    Args:
        term (str): Term to remove
        
    Returns:
        bool: Success status
    """
    try:
        config_manager.remove_whitelist_term(term)
        return Success(True)
    except Exception as e:
        logging.error(f"Error removing whitelist term: {e}")
        return Error(500, str(e))

@method
async def get_setting(key: str, default=None):
    """
    Get a specific setting value
    
    Args:
        key (str): Setting key
        default: Default value if setting not found
        
    Returns:
        Setting value or default
    """
    try:
        value = config_manager.get_setting(key, default)
        return Success(value)
    except Exception as e:
        logging.error(f"Error getting setting: {e}")
        return Error(500, str(e))

@method
async def set_setting(key: str, value):
    """
    Set a specific setting value
    
    Args:
        key (str): Setting key
        value: Setting value
        
    Returns:
        bool: Success status
    """
    try:
        config_manager.set_setting(key, value)
        return Success(True)
    except Exception as e:
        logging.error(f"Error setting setting: {e}")
        return Error(500, str(e))

@method
async def check_api_quota(credentials_json: str = None):
    """
    Check if the API quota is still available
    
    Args:
        credentials_json (str, optional): OAuth credentials as JSON string
        
    Returns:
        bool: True if quota is available, False otherwise
    """
    try:
        # If credentials were provided, use them
        if credentials_json:
            credentials_data = json.loads(credentials_json)
            credentials = Credentials.from_authorized_user_info(credentials_data)
            youtube_api = YouTubeAPI(credentials)
            quota_available = youtube_api.check_api_quota()
            return Success(quota_available)
        
        # If no credentials provided, we'll just return success
        # since we can't actually check the quota without credentials
        return Success(True)
    except Exception as e:
        logging.error(f"Error checking API quota: {e}")
        return Error(500, str(e))

@method
async def get_client_secret():
    """
    Get the client secret
    
    Returns:
        str: Client secret
    """
    try:
        client_secret = config_manager.get_client_secret()
        return Success(client_secret)
    except Exception as e:
        logging.error(f"Error getting client secret: {e}")
        return Error(500, str(e))
