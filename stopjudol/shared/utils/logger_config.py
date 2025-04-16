#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Logger Configuration
-------------------------------
This module provides a common logging configuration for both client and server.
"""

import os
import logging
import logging.handlers
from datetime import datetime

def configure_logger(name, log_file=None, console_level=logging.INFO, file_level=logging.DEBUG):
    """
    Configure a logger with console and file handlers
    
    Args:
        name (str): Logger name
        log_file (str, optional): Path to log file. If None, use name.log
        console_level (int, optional): Console logging level
        file_level (int, optional): File logging level
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set to lowest level to capture all logs
    
    # Create formatters
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    
    # Create file handler
    if log_file is None:
        log_file = f"{name.lower()}.log"
    
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create rotating file handler (10 MB max size, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def log_rpc_request(logger, method, params):
    """
    Log an RPC request
    
    Args:
        logger (logging.Logger): Logger to use
        method (str): RPC method name
        params (dict): RPC parameters
    """
    logger.debug(f"RPC Request: {method} - {params}")

def log_rpc_response(logger, method, result):
    """
    Log an RPC response
    
    Args:
        logger (logging.Logger): Logger to use
        method (str): RPC method name
        result: RPC result
    """
    # Truncate result if it's too long
    result_str = str(result)
    if len(result_str) > 1000:
        result_str = result_str[:1000] + "..."
    
    logger.debug(f"RPC Response: {method} - {result_str}")

def log_rpc_error(logger, method, error):
    """
    Log an RPC error
    
    Args:
        logger (logging.Logger): Logger to use
        method (str): RPC method name
        error: RPC error
    """
    logger.error(f"RPC Error: {method} - {error}")

def log_api_call(logger, api, method, params):
    """
    Log a YouTube API call
    
    Args:
        logger (logging.Logger): Logger to use
        api (str): API name
        method (str): API method name
        params (dict): API parameters
    """
    logger.debug(f"API Call: {api}.{method} - {params}")

def log_api_response(logger, api, method, response):
    """
    Log a YouTube API response
    
    Args:
        logger (logging.Logger): Logger to use
        api (str): API name
        method (str): API method name
        response: API response
    """
    # Truncate response if it's too long
    response_str = str(response)
    if len(response_str) > 1000:
        response_str = response_str[:1000] + "..."
    
    logger.debug(f"API Response: {api}.{method} - {response_str}")

def log_api_error(logger, api, method, error):
    """
    Log a YouTube API error
    
    Args:
        logger (logging.Logger): Logger to use
        api (str): API name
        method (str): API method name
        error: API error
    """
    logger.error(f"API Error: {api}.{method} - {error}")
