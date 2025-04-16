#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Client Main Entry Point
----------------------------------
This module serves as the entry point for the StopJudol client application.
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication
from src.client import MainWindow

def main():
    """Main entry point for the StopJudol client application"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("client.log")
        ]
    )
    
    # Create application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
