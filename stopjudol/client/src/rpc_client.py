#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - RPC Client
---------------------
This module provides a client for communicating with the StopJudol JSON-RPC server.
"""

import json
import logging
import requests
from PyQt6.QtCore import QSettings
from jsonrpcclient import request, parse, Ok, Error

class RPCClient:
    """Client for communicating with the StopJudol JSON-RPC server"""
    
    def __init__(self, server_url=None):
        """Initialize the RPC client"""
        self.settings = QSettings("StopJudol", "Client")
        if server_url is not None:
            self.server_url = server_url
        else:
            self.server_url = self.settings.value("server/url", "http://localhost:5000")
        self.timeout = int(self.settings.value("server/timeout", 10))
        self.logger = logging.getLogger("RPCClient")
        self.token = None
    
    def set_server_url(self, url):
        """
        Set the server URL
        
        Args:
            url (str): Server URL
        """
        self.server_url = url
        self.settings.setValue("server/url", url)
    
    def set_token(self, token):
        """
        Set the authentication token
        
        Args:
            token (str): Authentication token
        """
        self.token = token
    
    def login(self, username, password):
        """
        Log in to the server
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            tuple: (success, token or error message)
        """
        try:
            response = requests.post(
                f"{self.server_url}/token",
                json={"username": username, "password": password},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.token = data["token"]
                    return True, self.token
                else:
                    return False, "Invalid response from server"
            else:
                return False, f"Authentication failed: {response.text}"
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False, f"Error connecting to server: {str(e)}"
    
    def call(self, method, **params):
        """
        Call a method on the RPC server
        
        Args:
            method (str): Method name
            **params: Method parameters
            
        Returns:
            tuple: (success, result or error message)
        """
        try:
            # Prepare headers
            headers = {"Content-Type": "application/json"}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            # Make the request
            # In jsonrpcclient 4.0.3, we need to create the request manually
            request_data = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": 1
            }
            
            response = requests.post(
                f"{self.server_url}/rpc",
                json=request_data,
                headers=headers,
                timeout=self.timeout
            )
            
            # Parse the response
            if response.status_code == 200:
                # Handle the response manually
                response_data = response.json()
                
                if "result" in response_data:
                    return True, response_data["result"]
                elif "error" in response_data:
                    error_msg = response_data["error"]
                    self.logger.error(f"RPC error: {error_msg}")
                    return False, error_msg
                else:
                    return False, "Invalid response from server"
            else:
                self.logger.error(f"HTTP error: {response.status_code} - {response.text}")
                return False, f"HTTP error: {response.status_code}"
        except Exception as e:
            self.logger.error(f"RPC call error: {e}")
            return False, f"Error: {str(e)}"
    
    def fetch_comments(self, video_id, credentials_json=None):
        """
        Fetch comments for a YouTube video
        
        Args:
            video_id (str): YouTube video ID
            credentials_json (str, optional): OAuth credentials as JSON string
            
        Returns:
            tuple: (success, comments or error message)
        """
        return self.call("fetch_comments", video_id=video_id, credentials_json=credentials_json)
    
    def analyze_comments(self, comments):
        """
        Analyze comments for spam, gambling, etc.
        
        Args:
            comments (list): List of comment objects from YouTube API
            
        Returns:
            tuple: (success, flagged comments or error message)
        """
        return self.call("analyze_comments", comments=comments)
    
    def delete_comment(self, comment_id, thread_id=None, credentials_json=None):
        """
        Delete a YouTube comment
        
        Args:
            comment_id (str): Comment ID to delete
            thread_id (str, optional): Comment thread ID, used for moderation
            credentials_json (str, optional): OAuth credentials as JSON string
            
        Returns:
            tuple: (success, result or error message)
        """
        # Kirim parameter langsung tanpa menggunakan dictionary
        return self.call("delete_comment", 
                         comment_id=comment_id, 
                         thread_id=thread_id, 
                         credentials_json=credentials_json)
    
    def get_channel_info(self, credentials_json):
        """
        Get information about the authenticated user's channel
        
        Args:
            credentials_json (str): OAuth credentials as JSON string
            
        Returns:
            tuple: (success, channel info or error message)
        """
        return self.call("get_channel_info", credentials_json=credentials_json)
    
    def extract_video_id(self, url):
        """
        Extract video ID from a YouTube URL
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            tuple: (success, video ID or error message)
        """
        return self.call("extract_video_id", url=url)
    
    def get_blacklist(self):
        """
        Get the blacklist of keywords
        
        Returns:
            tuple: (success, blacklist or error message)
        """
        return self.call("get_blacklist")
    
    def get_whitelist(self):
        """
        Get the whitelist of keywords
        
        Returns:
            tuple: (success, whitelist or error message)
        """
        return self.call("get_whitelist")
    
    def add_blacklist_term(self, term, category="Other"):
        """
        Add a term to the blacklist
        
        Args:
            term (str): Term to add
            category (str, optional): Category for the term
            
        Returns:
            tuple: (success, result or error message)
        """
        return self.call("add_blacklist_term", term=term, category=category)
    
    def remove_blacklist_term(self, term):
        """
        Remove a term from the blacklist
        
        Args:
            term (str): Term to remove
            
        Returns:
            tuple: (success, result or error message)
        """
        return self.call("remove_blacklist_term", term=term)
    
    def add_whitelist_term(self, term):
        """
        Add a term to the whitelist
        
        Args:
            term (str): Term to add
            
        Returns:
            tuple: (success, result or error message)
        """
        return self.call("add_whitelist_term", term=term)
    
    def remove_whitelist_term(self, term):
        """
        Remove a term from the whitelist
        
        Args:
            term (str): Term to remove
            
        Returns:
            tuple: (success, result or error message)
        """
        return self.call("remove_whitelist_term", term=term)
    
    def get_setting(self, key, default=None):
        """
        Get a setting from the server
        
        Args:
            key (str): Setting key
            default: Default value if setting is not found
            
        Returns:
            tuple: (success, setting value or error message)
        """
        return self.call("get_setting", key=key, default=default)
    
    def set_setting(self, key, value):
        """
        Set a setting on the server
        
        Args:
            key (str): Setting key
            value: Setting value
            
        Returns:
            tuple: (success, result or error message)
        """
        return self.call("set_setting", key=key, value=value)
    
    def get_client_secret(self):
        """
        Get the client secret
        
        Returns:
            tuple: (success, client secret or error message)
        """
        return self.call("get_client_secret")
    
    def check_api_quota(self, credentials_json=None):
        """
        Check if the API quota is still available
        
        Args:
            credentials_json (str, optional): OAuth credentials as JSON string
            
        Returns:
            bool: True if quota is available, False otherwise
        """
        return self.call("check_api_quota", credentials_json=credentials_json)
