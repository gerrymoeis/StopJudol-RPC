#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - YouTube API Wrapper
-------------------------------
This module provides a wrapper for the YouTube Data API v3 to fetch and delete comments.
"""

import re
import logging
import time
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeAPI:
    """Wrapper for YouTube Data API v3"""
    
    def __init__(self, credentials):
        """
        Initialize the YouTube API client
        
        Args:
            credentials: OAuth2 credentials object
        """
        self.youtube = build('youtube', 'v3', credentials=credentials)
        self.channel_info = None
    
    def get_channel_name(self):
        """
        Get the authenticated user's channel name
        
        Returns:
            str: Channel name
        """
        if not self.channel_info:
            try:
                # Get channel info for the authenticated user
                response = self.youtube.channels().list(
                    part='snippet',
                    mine=True
                ).execute()
                
                if 'items' in response and len(response['items']) > 0:
                    self.channel_info = response['items'][0]
                    return self.channel_info['snippet']['title']
                else:
                    return "Unknown Channel"
            except HttpError as e:
                logging.error(f"Error fetching channel info: {e}")
                return "Error fetching channel"
        else:
            return self.channel_info['snippet']['title']
    
    def extract_video_id(self, url):
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
    
    def get_comments(self, video_id, page_token=None, max_results=100):
        """
        Fetch comments for a YouTube video
        
        Args:
            video_id (str): YouTube video ID
            page_token (str, optional): Token for pagination
            max_results (int, optional): Maximum number of results per page
            
        Returns:
            dict: API response containing comments
        """
        try:
            # Call the API to get comment threads
            response = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_results,
                pageToken=page_token,
                textFormat='html'  # Get formatted text with HTML
            ).execute()
            
            return response
        except HttpError as e:
            error_message = str(e)
            if "quotaExceeded" in error_message:
                logging.error("YouTube API quota exceeded. Please try again tomorrow.")
                raise Exception("YouTube API quota exceeded. Please try again tomorrow.")
            elif "videoNotFound" in error_message or "404" in error_message:
                logging.error(f"Video not found: {video_id}")
                raise Exception(f"Video not found or is private: {video_id}")
            elif "commentsDisabled" in error_message:
                logging.error(f"Comments are disabled for video: {video_id}")
                raise Exception(f"Comments are disabled for this video: {video_id}")
            elif "403" in error_message:
                logging.error(f"Permission denied: {e}")
                raise Exception("Permission denied. Please check your authentication.")
            else:
                logging.error(f"Error fetching comments: {e}")
                raise Exception(f"Error fetching comments: {e}")
    
    def delete_comment(self, comment_id):
        """
        Delete a YouTube comment
        
        Args:
            comment_id (str): Comment ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Call the API to delete the comment
            self.youtube.comments().delete(
                id=comment_id
            ).execute()
            
            logging.info(f"Successfully deleted comment: {comment_id}")
            return True
        except HttpError as e:
            error_message = str(e)
            if "quotaExceeded" in error_message:
                logging.error("YouTube API quota exceeded. Please try again tomorrow.")
            elif "commentNotFound" in error_message or "404" in error_message:
                logging.error(f"Comment not found: {comment_id}")
            elif "403" in error_message:
                logging.error(f"Permission denied to delete comment: {comment_id}")
            else:
                logging.error(f"Error deleting comment {comment_id}: {e}")
            return False
            
    def get_all_comments(self, video_id, max_results=100, max_pages=10):
        """
        Fetch all comments for a YouTube video using pagination
        
        Args:
            video_id (str): YouTube video ID
            max_results (int, optional): Maximum number of results per page
            max_pages (int, optional): Maximum number of pages to fetch
            
        Returns:
            list: List of all comment items
        """
        all_comments = []
        next_page_token = None
        page_count = 0
        
        try:
            while page_count < max_pages:
                page_count += 1
                response = self.get_comments(video_id, next_page_token, max_results)
                
                if 'items' in response:
                    all_comments.extend(response['items'])
                
                # Check if there are more pages
                if 'nextPageToken' in response:
                    next_page_token = response['nextPageToken']
                    # Add a small delay to avoid hitting rate limits
                    time.sleep(0.5)
                else:
                    break
            
            return all_comments
        except Exception as e:
            logging.error(f"Error fetching all comments: {e}")
            raise
    
    def get_video_info(self, video_id):
        """
        Get information about a YouTube video
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            dict: Video information
        """
        try:
            response = self.youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()
            
            if 'items' in response and len(response['items']) > 0:
                return response['items'][0]
            else:
                logging.error(f"Video not found: {video_id}")
                return None
        except HttpError as e:
            logging.error(f"Error fetching video info: {e}")
            raise Exception(f"Error fetching video info: {e}")
    
    def check_api_quota(self):
        """
        Check if the API quota is still available
        
        Returns:
            bool: True if quota is available, False otherwise
        """
        try:
            # Make a minimal API call to check quota
            self.youtube.channels().list(
                part='id',
                mine=True,
                maxResults=1
            ).execute()
            return True
        except HttpError as e:
            if "quotaExceeded" in str(e):
                logging.error("YouTube API quota exceeded")
                return False
            # If it's another error, quota is probably still available
            return True
