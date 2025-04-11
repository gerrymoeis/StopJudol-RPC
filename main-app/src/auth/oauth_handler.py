#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - OAuth Handler
-------------------------
This module handles OAuth 2.0 authentication with Google/YouTube API.
"""

import os
import sys
import json
import logging
import webbrowser
from pathlib import Path

import keyring
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class OAuthHandler:
    """Handler for OAuth 2.0 authentication with Google/YouTube API"""
    
    # Define constants
    CLIENT_SECRETS_FILE = 'client_secret.json'
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.force-ssl',  # Required for comment deletion
        'https://www.googleapis.com/auth/youtube.readonly'    # For reading comments
    ]
    KEYRING_SERVICE = 'StopJudol'
    KEYRING_USERNAME = 'YouTubeAPI'
    
    def __init__(self):
        """Initialize the OAuth handler"""
        # Determine base directory
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle (PyInstaller)
            self.base_dir = sys._MEIPASS
        else:
            # If running from script
            self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Set paths
        self.config_dir = os.path.join(self.base_dir, 'config')
        self.client_secrets_path = os.path.join(self.config_dir, self.CLIENT_SECRETS_FILE)
        
        # User config directory in AppData/Local
        self.user_config_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'StopJudol')
        os.makedirs(self.user_config_dir, exist_ok=True)
    
    def get_credentials(self):
        """
        Get stored credentials or None if not available
        
        Returns:
            google.oauth2.credentials.Credentials: OAuth2 credentials or None
        """
        try:
            # Try to get token from keyring
            token_json = keyring.get_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME)
            
            if token_json:
                token_data = json.loads(token_json)
                credentials = Credentials.from_authorized_user_info(token_data)
                
                # Check if credentials are expired and can be refreshed
                if credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                    self.save_credentials(credentials)
                
                return credentials
        except Exception as e:
            logging.error(f"Error retrieving credentials: {e}")
        
        return None
    
    def save_credentials(self, credentials):
        """
        Save credentials to keyring
        
        Args:
            credentials: OAuth2 credentials object
        """
        try:
            # Convert credentials to JSON
            token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            token_json = json.dumps(token_data)
            
            # Save to keyring
            keyring.set_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME, token_json)
            logging.info("Credentials saved to keyring")
        except Exception as e:
            logging.error(f"Error saving credentials: {e}")
    
    def clear_credentials(self):
        """Clear stored credentials"""
        try:
            keyring.delete_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME)
            logging.info("Credentials cleared from keyring")
            return True
        except Exception as e:
            logging.error(f"Error clearing credentials: {e}")
            return False
    
    def authenticate(self):
        """
        Perform OAuth 2.0 authentication flow
        
        Returns:
            google.oauth2.credentials.Credentials: OAuth2 credentials or None if failed
        """
        # First check if we already have valid credentials
        credentials = self.get_credentials()
        if credentials and not credentials.expired:
            logging.info("Using existing credentials")
            return credentials
        
        # Check if client secrets file exists
        if not os.path.exists(self.client_secrets_path):
            logging.error(f"Client secrets file not found at {self.client_secrets_path}")
            raise FileNotFoundError(f"Client secrets file not found. Please place {self.CLIENT_SECRETS_FILE} in the config directory.")
        
        try:
            # Create flow instance
            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secrets_path,
                scopes=self.SCOPES
            )
            
            # Run local server flow
            credentials = flow.run_local_server(
                port=0,  # Use a random port
                prompt='consent',
                authorization_prompt_message="Please authorize StopJudol to access your YouTube account. Your browser should open automatically."
            )
            
            # Save the credentials
            self.save_credentials(credentials)
            logging.info("Authentication successful")
            
            return credentials
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            raise
