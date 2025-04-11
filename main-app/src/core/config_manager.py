#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Configuration Manager
---------------------------------
This module handles loading and saving configuration settings, blacklists, and whitelists.
"""

import os
import sys
import json
import logging
import shutil
from pathlib import Path

class ConfigManager:
    """Manager for application configuration and settings"""
    
    def __init__(self):
        """Initialize the configuration manager"""
        # Determine base directory
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle (PyInstaller)
            self.base_dir = sys._MEIPASS
        else:
            # If running from script
            self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Set paths
        self.config_dir = os.path.join(self.base_dir, 'config')
        self.default_config_path = os.path.join(self.config_dir, 'default_settings.json')
        
        # User config directory in AppData/Local
        self.user_config_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'StopJudol')
        self.user_config_path = os.path.join(self.user_config_dir, 'settings.json')
        
        # Ensure user config directory exists
        os.makedirs(self.user_config_dir, exist_ok=True)
        
        # Load or create configuration
        self.config = self.load_config()
    
    def load_config(self):
        """
        Load configuration from user config file or create from default
        
        Returns:
            dict: Configuration settings
        """
        # Check if user config exists
        if os.path.exists(self.user_config_path):
            try:
                with open(self.user_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logging.info(f"Loaded configuration from {self.user_config_path}")
                return config
            except Exception as e:
                logging.error(f"Error loading user config: {e}")
                # Fall back to default config
        
        # If user config doesn't exist or failed to load, copy default config
        if os.path.exists(self.default_config_path):
            try:
                with open(self.default_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Save as user config
                self.save_config(config)
                logging.info(f"Created user config from default at {self.user_config_path}")
                return config
            except Exception as e:
                logging.error(f"Error loading default config: {e}")
        
        # If all else fails, return a basic default configuration
        logging.warning("Using built-in default configuration")
        default_config = {
            'blacklist': [
                # Common gambling terms (Indonesian)
                'judi online', 'slot online', 'togel', 'casino online',
                'situs judi', 'agen judi', 'bandar judi', 'poker online',
                'situs slot', 'slot gacor', 'slot maxwin', 'slot demo',
                'rtp slot', 'bocoran slot', 'link alternatif', 'bonus new member',
                
                # Common spam indicators
                'make money fast', 'work from home', 'earn money online',
                'click here', 'free money', 'get rich quick', 'earn $',
                
                # Contact info spam
                'whatsapp', 'wa:', 'hubungi', 'kontak', 'contact',
                'telegram', 'dm for', 'dm me', 'direct message'
            ],
            'blacklist_categories': {
                # Gambling terms
                'judi online': 'Gambling', 'slot online': 'Gambling', 'togel': 'Gambling', 'casino online': 'Gambling',
                'situs judi': 'Gambling', 'agen judi': 'Gambling', 'bandar judi': 'Gambling', 'poker online': 'Gambling',
                'situs slot': 'Gambling', 'slot gacor': 'Gambling', 'slot maxwin': 'Gambling', 'slot demo': 'Gambling',
                'rtp slot': 'Gambling', 'bocoran slot': 'Gambling', 'link alternatif': 'Gambling', 'bonus new member': 'Gambling',
                
                # Spam indicators
                'make money fast': 'Spam', 'work from home': 'Spam', 'earn money online': 'Spam',
                'click here': 'Spam', 'free money': 'Spam', 'get rich quick': 'Spam', 'earn $': 'Spam',
                
                # Contact info
                'whatsapp': 'Contact Info', 'wa:': 'Contact Info', 'hubungi': 'Contact Info', 'kontak': 'Contact Info', 'contact': 'Contact Info',
                'telegram': 'Contact Info', 'dm for': 'Contact Info', 'dm me': 'Contact Info', 'direct message': 'Contact Info'
            },
            'whitelist': [
                # Terms that might be legitimate in discussions
                'game slot', 'slot game', 'video game', 'game review',
                'tutorial', 'review', 'critique', 'analysis',
                'educational', 'learning', 'course', 'class'
            ],
            'settings': {
                'auto_delete': False,
                'check_interval_seconds': 0,  # 0 means disabled
                'max_comments_per_scan': 500
            }
        }
        
        # Save as user config
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config=None):
        """
        Save configuration to user config file
        
        Args:
            config (dict, optional): Configuration to save. If None, save current config.
        """
        if config is None:
            config = self.config
        
        try:
            with open(self.user_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            logging.info(f"Saved configuration to {self.user_config_path}")
        except Exception as e:
            logging.error(f"Error saving config: {e}")
    
    def get_blacklist(self):
        """
        Get the blacklist of keywords
        
        Returns:
            list: Blacklisted keywords
        """
        return self.config.get('blacklist', [])
        
    def get_blacklist_categories(self):
        """
        Get the blacklist categories mapping
        
        Returns:
            dict: Mapping of terms to categories
        """
        return self.config.get('blacklist_categories', {})
    
    def get_whitelist(self):
        """
        Get the whitelist of keywords
        
        Returns:
            list: Whitelisted keywords
        """
        return self.config.get('whitelist', [])
    
    def get_setting(self, key, default=None):
        """
        Get a specific setting value
        
        Args:
            key (str): Setting key
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        return self.config.get('settings', {}).get(key, default)
    
    def set_setting(self, key, value):
        """
        Set a specific setting value
        
        Args:
            key (str): Setting key
            value: Setting value
        """
        if 'settings' not in self.config:
            self.config['settings'] = {}
        
        self.config['settings'][key] = value
        self.save_config()
    
    def add_blacklist_term(self, term, category="Other"):
        """
        Add a term to the blacklist
        
        Args:
            term (str): Term to add
            category (str, optional): Category for the term. Defaults to "Other".
        """
        if 'blacklist' not in self.config:
            self.config['blacklist'] = []
        
        if 'blacklist_categories' not in self.config:
            self.config['blacklist_categories'] = {}
        
        if term not in self.config['blacklist']:
            self.config['blacklist'].append(term)
            self.config['blacklist_categories'][term] = category
            self.save_config()
    
    def remove_blacklist_term(self, term):
        """
        Remove a term from the blacklist
        
        Args:
            term (str): Term to remove
        """
        if 'blacklist' in self.config and term in self.config['blacklist']:
            self.config['blacklist'].remove(term)
            
            # Also remove from categories if present
            if 'blacklist_categories' in self.config and term in self.config['blacklist_categories']:
                del self.config['blacklist_categories'][term]
                
            self.save_config()
    
    def add_whitelist_term(self, term):
        """
        Add a term to the whitelist
        
        Args:
            term (str): Term to add
        """
        if 'whitelist' not in self.config:
            self.config['whitelist'] = []
        
        if term not in self.config['whitelist']:
            self.config['whitelist'].append(term)
            self.save_config()
    
    def remove_whitelist_term(self, term):
        """
        Remove a term from the whitelist
        
        Args:
            term (str): Term to remove
        """
        if 'whitelist' in self.config and term in self.config['whitelist']:
            self.config['whitelist'].remove(term)
            self.save_config()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        if os.path.exists(self.default_config_path):
            try:
                with open(self.default_config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.save_config()
                logging.info("Reset configuration to defaults")
                return True
            except Exception as e:
                logging.error(f"Error resetting to defaults: {e}")
                return False
        return False
