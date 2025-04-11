#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Main Entry Point
----------------------------
A desktop application to help YouTube content creators automatically identify and remove
spam comments, online gambling ads, and other illegal content using YouTube Data API v3.
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Set up base path for relative imports
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle (PyInstaller)
    BASE_DIR = sys._MEIPASS
else:
    # If running from script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add src to path for imports
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

# Import application modules
from src.utils.logger_config import setup_logger
from src.app import MainWindow

def main():
    """Main application entry point"""
    # Setup logging
    setup_logger()
    logging.info("Starting StopJudol application")
    
    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("StopJudol")
    app.setOrganizationName("StopJudol")
    
    # Set application icon if available
    icon_path = os.path.join(BASE_DIR, 'assets', 'icons', 'app_icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
