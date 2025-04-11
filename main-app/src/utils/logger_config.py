#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Logger Configuration
--------------------------------
This module configures the application's logging system.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

def setup_logger():
    """
    Configure the application's logging system
    
    Sets up logging to both console and file with appropriate formatting
    """
    # Determine log directory
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (PyInstaller)
        base_dir = sys._MEIPASS
    else:
        # If running from script
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # User log directory in AppData/Local
    user_log_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'StopJudol', 'logs')
    os.makedirs(user_log_dir, exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(user_log_dir, f'stopjudol_{timestamp}.log')
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # More detailed in file
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set formatters
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Log startup information
    logging.info(f"Logging initialized. Log file: {log_file}")
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Running from: {'PyInstaller bundle' if getattr(sys, 'frozen', False) else 'Python script'}")
    
    return logger
