#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Client Runner
------------------------
This script starts the StopJudol client application.
"""

import os
import sys
import logging

# Add the stopjudol directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("client.log")
        ]
    )
    
    # Print startup message
    print("=" * 50)
    print(" StopJudol Client ".center(50, "="))
    print("=" * 50)
    
    # Start the client application
    from PyQt6.QtWidgets import QApplication
    import client.src.client
    MainWindow = client.src.client.MainWindow
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
