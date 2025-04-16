#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Client Configuration
------------------------------
This module provides configuration utilities for the StopJudol client.
"""

import os
import json
import logging
from PyQt6.QtCore import QSettings

class ClientConfig:
    """Configuration manager for the StopJudol client"""
    
    def __init__(self):
        """Initialize the configuration manager"""
        self.settings = QSettings("StopJudol", "Client")
        self.logger = logging.getLogger("ClientConfig")
        
        # Set default values if not already set
        self._set_defaults()
    
    def _set_defaults(self):
        """Set default values for settings"""
        defaults = {
            "server/url": "http://localhost:5000",
            "server/timeout": 10,
            "server/auto_reconnect": True,
            "auth/remember_credentials": True,
            "auth/auto_login": False,
            "app/check_updates": True,
            "app/show_confirmations": True,
            "app/auto_scan": False,
            "app/max_comments": 500,
            "ui/theme": "system",
            "ui/font_size": 9,
            "ui/show_toolbar": True,
            "ui/show_statusbar": True
        }
        
        # Set defaults if not already set
        for key, value in defaults.items():
            if self.settings.value(key) is None:
                self.settings.setValue(key, value)
    
    def get(self, key, default=None):
        """
        Get a setting value
        
        Args:
            key (str): Setting key
            default: Default value if setting is not found
            
        Returns:
            Setting value or default
        """
        value = self.settings.value(key, default)
        
        # Convert string values to appropriate types
        if isinstance(default, bool) and isinstance(value, str):
            return value.lower() in ("true", "1", "yes")
        elif isinstance(default, int) and isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return default
        elif isinstance(default, float) and isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return default
        
        return value
    
    def set(self, key, value):
        """
        Set a setting value
        
        Args:
            key (str): Setting key
            value: Setting value
        """
        self.settings.setValue(key, value)
        self.settings.sync()
    
    def get_server_url(self):
        """
        Get the server URL
        
        Returns:
            str: Server URL
        """
        return self.get("server/url", "http://localhost:5000")
    
    def set_server_url(self, url):
        """
        Set the server URL
        
        Args:
            url (str): Server URL
        """
        self.set("server/url", url)
    
    def get_timeout(self):
        """
        Get the connection timeout
        
        Returns:
            int: Timeout in seconds
        """
        return self.get("server/timeout", 10)
    
    def set_timeout(self, timeout):
        """
        Set the connection timeout
        
        Args:
            timeout (int): Timeout in seconds
        """
        self.set("server/timeout", timeout)
    
    def get_auto_reconnect(self):
        """
        Get whether to automatically reconnect
        
        Returns:
            bool: True if auto reconnect is enabled
        """
        return self.get("server/auto_reconnect", True)
    
    def set_auto_reconnect(self, auto_reconnect):
        """
        Set whether to automatically reconnect
        
        Args:
            auto_reconnect (bool): True to enable auto reconnect
        """
        self.set("server/auto_reconnect", auto_reconnect)
    
    def get_remember_credentials(self):
        """
        Get whether to remember credentials
        
        Returns:
            bool: True if remember credentials is enabled
        """
        return self.get("auth/remember_credentials", True)
    
    def set_remember_credentials(self, remember):
        """
        Set whether to remember credentials
        
        Args:
            remember (bool): True to remember credentials
        """
        self.set("auth/remember_credentials", remember)
    
    def get_auto_login(self):
        """
        Get whether to automatically log in
        
        Returns:
            bool: True if auto login is enabled
        """
        return self.get("auth/auto_login", False)
    
    def set_auto_login(self, auto_login):
        """
        Set whether to automatically log in
        
        Args:
            auto_login (bool): True to enable auto login
        """
        self.set("auth/auto_login", auto_login)
    
    def get_all_settings(self):
        """
        Get all settings as a dictionary
        
        Returns:
            dict: All settings
        """
        result = {}
        
        # Get all keys
        for key in self.settings.allKeys():
            result[key] = self.settings.value(key)
        
        return result
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        # Clear all settings
        self.settings.clear()
        
        # Set defaults
        self._set_defaults()
        
        # Sync settings
        self.settings.sync()
