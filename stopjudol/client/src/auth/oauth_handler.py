#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - OAuth Handler
------------------------
This module handles OAuth authentication with Google/YouTube API.
"""

import os
import json
import logging
import webbrowser
import keyring
from PyQt6.QtWidgets import QMessageBox, QInputDialog, QLineEdit
from PyQt6.QtCore import QSettings
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import requests
from ..rpc_client import RPCClient  # Perbaiki import RPCClient dengan path yang benar
import sys

class OAuthHandler:
    """Handler for OAuth authentication with Google/YouTube API"""
    
    # Define the required scopes for YouTube API
    SCOPES = [
        "https://www.googleapis.com/auth/youtube.force-ssl",
        "https://www.googleapis.com/auth/youtube"
    ]
    
    def __init__(self, parent=None):
        """Initialize the OAuth handler"""
        self.parent = parent
        self.credentials = None
        self.settings = QSettings("StopJudol", "Client")
        self.server_url = self.settings.value("server/url", "http://localhost:5000")
        self.logger = logging.getLogger("OAuthHandler")
        self.logger.setLevel(logging.DEBUG)  # Tambahkan inisialisasi logger
        
        # Determine base directory
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle (PyInstaller)
            self.base_dir = sys._MEIPASS
        else:
            # If running from script
            self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # Set paths
        self.config_dir = os.path.join(self.base_dir, 'config')
        self.client_secrets_path = os.path.join(self.config_dir, 'client_secret.json')
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
    
    def authenticate(self, client_secret_file=None):
        """
        Authenticate with Google/YouTube API
        
        Args:
            client_secret_file (str, optional): Path to client secret file
            
        Returns:
            Credentials or None if authentication failed
        """
        try:
            # Check if we already have valid credentials
            credentials = self.get_credentials()
            if credentials and not credentials.expired:
                self.credentials = credentials
                return credentials
            
            # If credentials are expired but we have a refresh token, try to refresh
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                    self.credentials = credentials
                    self.save_credentials(credentials)
                    return credentials
                except Exception as e:
                    self.logger.error(f"Error refreshing credentials: {e}")
                    # Clear invalid credentials
                    keyring.delete_password("StopJudol", "youtube_credentials")
            
            # Gunakan client_secret.json dari lokasi tetap
            client_secret_file = self.client_secrets_path
            if not os.path.exists(client_secret_file):
                self.logger.warning("Client secret file not found in fixed location")
                return False
            
            try:
                with open(client_secret_file, 'r') as f:
                    client_secret_dict = json.load(f)
                if 'web' not in client_secret_dict:
                    raise ValueError("Invalid client secret file")
                client_secret_dict = client_secret_dict['web']
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing client secret file: {e}")
                if self.parent:
                    QMessageBox.critical(
                        self.parent,
                        "Error",
                        "Invalid client secret file"
                    )
                return False
            except ValueError as e:
                self.logger.error(f"Error parsing client secret file: {e}")
                if self.parent:
                    QMessageBox.critical(
                        self.parent,
                        "Error",
                        "Invalid client secret file"
                    )
                return False
            
            # Start the OAuth flow
            try:
                flow = InstalledAppFlow.from_client_config(
                    client_secret_dict, self.SCOPES
                )
            except ValueError as e:
                self.logger.error(f"Error creating OAuth flow: {e}")
                if self.parent:
                    QMessageBox.critical(
                        self.parent,
                        "Error",
                        "Invalid client secret file"
                    )
                return False
            
            # Run the local server flow
            self.credentials = flow.run_local_server(port=0)
            
            # Store credentials if requested
            if self.settings.value("auth/remember_credentials", True, type=bool):
                self.save_credentials(self.credentials)
            
            return self.credentials
        
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            if self.parent:
                QMessageBox.critical(
                    self.parent,
                    "Authentication Error",
                    f"Error during authentication: {str(e)}"
                )
            return False
    
    def save_credentials(self, credentials):
        """Store credentials in keyring"""
        if credentials:
            creds_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            keyring.set_password("StopJudol", "youtube_credentials", json.dumps(creds_data))
    
    def get_credentials(self):
        """Get the credentials object from keyring"""
        try:
            creds_data = keyring.get_password("StopJudol", "youtube_credentials")
            if creds_data:
                creds_data = json.loads(creds_data)
                return Credentials(
                    token=creds_data['token'],
                    refresh_token=creds_data['refresh_token'],
                    token_uri=creds_data['token_uri'],
                    client_id=creds_data['client_id'],
                    client_secret=creds_data['client_secret'],
                    scopes=creds_data['scopes']
                )
        except Exception as e:
            self.logger.error(f"Error getting credentials: {e}")
        return None
    
    def _verify_credentials(self):
        """
        Verify credentials by making a test API call
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            # Convert credentials to JSON
            creds_json = json.dumps({
                'token': self.credentials.token,
                'refresh_token': self.credentials.refresh_token,
                'token_uri': self.credentials.token_uri,
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret,
                'scopes': self.credentials.scopes
            })
            
            # Make a request to the server to get channel info
            response = requests.post(
                f"{self.server_url}/rpc",
                json={
                    "jsonrpc": "2.0",
                    "method": "get_channel_info",
                    "params": {"credentials_json": creds_json},
                    "id": 1
                }
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error verifying credentials: {e}")
            return False
    
    def logout(self):
        """Log out and clear stored credentials"""
        try:
            # Clear credentials
            self.credentials = None
            
            # Remove from keyring
            keyring.delete_password("StopJudol", "youtube_credentials")
            
            return True
        except Exception as e:
            self.logger.error(f"Error during logout: {e}")
            return False
            
    def clear_credentials(self):
        """Clear stored credentials (alias for logout)"""
        return self.logout()
    
    def get_credentials_json(self):
        """
        Get credentials as a JSON string
        
        Returns:
            str: Credentials as JSON string, or None if not authenticated
        """
        if not self.credentials:
            return None
        
        return json.dumps({
            'token': self.credentials.token,
            'refresh_token': self.credentials.refresh_token,
            'token_uri': self.credentials.token_uri,
            'client_id': self.credentials.client_id,
            'client_secret': self.credentials.client_secret,
            'scopes': self.credentials.scopes
        })
    
    def is_authenticated(self):
        """
        Check if the user is authenticated
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.credentials is not None
