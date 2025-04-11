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
import httplib2
import json
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
    
    def delete_comment(self, comment_id, thread_id=None):
        """
        Delete a YouTube comment
        
        Args:
            comment_id (str): Comment ID to delete
            thread_id (str, optional): Comment thread ID, used for moderation
            
        Returns:
            tuple: (action_type, success)
                action_type: 'deleted' or 'marked_as_spam'
                success: True if successful, False otherwise
        """
        try:
            # Verify the comment ID format first
            if not comment_id or not isinstance(comment_id, str):
                logging.error(f"Invalid comment ID format: {comment_id}")
                return ('none', False)
                
            # Log the attempt for debugging
            logging.debug(f"Attempting to delete comment with ID: {comment_id}")
            
            # First try to delete using regular delete endpoint (works for your own comments)
            try:
                request = self.youtube.comments().delete(id=comment_id)
                request.http.follow_redirects = True
                response = request.execute()
                logging.info(f"Successfully deleted comment using delete endpoint: {comment_id}")
                return ('deleted', True)
            except HttpError as delete_error:
                error_message = str(delete_error)
                error_code = str(delete_error.status_code) if hasattr(delete_error, 'status_code') else 'unknown'
                
                # If we get permission error, try using markAsSpam instead
                if "403" in error_message or "400" in error_message:
                    if thread_id:
                        logging.debug(f"Attempting to mark comment as spam: {thread_id}")
                        success = self.moderate_comment(thread_id)
                        return ('marked_as_spam', success)
                    else:
                        logging.error("Cannot mark comment as spam: thread_id not provided")
                        return ('none', False)
                else:
                    # Re-raise for the outer exception handler
                    raise delete_error
                    
        except HttpError as e:
            error_message = str(e)
            error_code = str(e.status_code) if hasattr(e, 'status_code') else 'unknown'
            
            if "quotaExceeded" in error_message:
                logging.error("YouTube API quota exceeded. Please try again tomorrow.")
            elif "commentNotFound" in error_message or "404" in error_message:
                logging.error(f"Comment not found: {comment_id}")
            elif "403" in error_message:
                logging.error(f"Permission denied to delete comment: {comment_id}. You can only delete comments on your own videos or comments that you made yourself.")
            elif "400" in error_message:
                logging.error(f"Bad request when deleting comment {comment_id}. This may be because the comment ID is invalid or you don't have permission to delete it.")
                logging.error(f"Error details: {error_message}")
                
                # Provide more specific guidance
                if "processingFailure" in error_message:
                    logging.error("This is likely a permission issue. You can only delete comments on your own videos or comments that you made yourself.")
            else:
                logging.error(f"Error deleting comment {comment_id}: {e}")
            
            return False
            
    def moderate_comment(self, comment_id, moderation_status="rejected"):
        """
        Moderate a comment using setModerationStatus
        
        Args:
            comment_id (str): Comment ID to moderate
            moderation_status (str): Moderation status (rejected, published, heldForReview)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Verify the comment ID format
            if not comment_id or not isinstance(comment_id, str):
                logging.error(f"Invalid comment ID format: {comment_id}")
                return False
                
            logging.debug(f"Attempting to set moderation status to '{moderation_status}' for comment: {comment_id}")
            
            # Try using the built-in service method first
            try:
                # Try to use the built-in method if available
                try:
                    # This might work if the library has the method but it's not documented
                    request = self.youtube.comments().setModerationStatus(
                        id=comment_id,
                        moderationStatus=moderation_status,
                        banAuthor=False
                    )
                    response = request.execute()
                    logging.info(f"Successfully set moderation status to '{moderation_status}' for comment: {comment_id}")
                    return True
                except AttributeError:
                    # Method not available, use the raw API request
                    logging.debug("setModerationStatus method not available in client library, using raw request")
                    
                    # Use the YouTube API service's authorized http object directly
                    http = self.youtube._http
                    
                    # Build the URL with query parameters
                    url = "https://www.googleapis.com/youtube/v3/comments/setModerationStatus"
                    params = {
                        'id': comment_id,
                        'moderationStatus': moderation_status,
                        'banAuthor': 'false'  # API expects string 'false', not boolean
                    }
                    
                    # Convert params to query string
                    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
                    full_url = f"{url}?{query_string}"
                    
                    # Make the POST request
                    response, content = http.request(
                        full_url,
                        method="POST",
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    # Check if the request was successful
                    if response.status < 300:
                        logging.info(f"Successfully set moderation status to '{moderation_status}' for comment: {comment_id}")
                        return True
                    else:
                        content_str = content.decode('utf-8') if isinstance(content, bytes) else str(content)
                        logging.error(f"Error setting moderation status: {content_str}")
                        raise Exception(f"Error setting moderation status: {content_str}")
                    
            except Exception as direct_api_error:
                logging.warning(f"Direct API request failed: {direct_api_error}")
                logging.warning("Falling back to markAsSpam method...")
                
                # Fall back to markAsSpam if setModerationStatus fails
                try:
                    request = self.youtube.comments().markAsSpam(id=comment_id)
                    response = request.execute()
                    logging.info(f"Successfully marked comment as spam: {comment_id}")
                    logging.info(f"Comment marked as spam. Note that YouTube may not remove it immediately.")
                    return True
                except Exception as mark_spam_error:
                    logging.error(f"markAsSpam fallback also failed: {mark_spam_error}")
                    raise mark_spam_error
                    
        except HttpError as e:
            error_message = str(e)
            error_code = str(e.status_code) if hasattr(e, 'status_code') else 'unknown'
            
            if "quotaExceeded" in error_message:
                logging.error("YouTube API quota exceeded. Please try again tomorrow.")
            elif "404" in error_message:
                logging.error(f"Comment not found: {comment_id}")
            elif "403" in error_message:
                logging.error(f"Permission denied to moderate comment: {comment_id}. You can only moderate comments on your own videos.")
            else:
                logging.error(f"Error moderating comment {comment_id}: {e}")
            
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
