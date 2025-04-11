#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Main Application Window
-----------------------------------
This module contains the main application window class for the StopJudol application.
"""

import os
import sys
import logging
import threading
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QTableWidget, 
    QTableWidgetItem, QProgressBar, QMessageBox,
    QCheckBox, QGroupBox, QTabWidget, QTextEdit,
    QStatusBar, QHeaderView, QMenuBar, QMenu,
    QDialog
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QIcon, QPixmap

from src.core.youtube_api import YouTubeAPI
from src.core.analysis import CommentAnalyzer
from src.core.config_manager import ConfigManager
from src.auth.oauth_handler import OAuthHandler
from src.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    """Main application window for StopJudol"""
    
    # Define signals for thread communication
    fetch_completed = pyqtSignal(list)
    fetch_error = pyqtSignal(str)
    delete_completed = pyqtSignal(list)
    delete_error = pyqtSignal(str)
    progress_update = pyqtSignal(int, int)  # current, total
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.oauth_handler = OAuthHandler()
        self.youtube_api = None  # Will be initialized after authentication
        self.comment_analyzer = CommentAnalyzer(self.config_manager)
        
        # UI state variables
        self.is_authenticated = False
        self.comments_data = []
        self.flagged_comments = []
        
        # Set up UI
        self.init_ui()
        
        # Connect signals
        self.connect_signals()
        
        # Check authentication status on startup
        self.check_auth_status()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("StopJudol - YouTube Comment Moderator")
        self.setMinimumSize(1000, 700)  # Increased window size for better readability
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Authentication section
        auth_group = QGroupBox("Authentication")
        auth_layout = QHBoxLayout()
        
        self.auth_status_label = QLabel("Not authenticated")
        self.auth_button = QPushButton("Login with YouTube")
        self.auth_button.clicked.connect(self.handle_auth)
        
        auth_layout.addWidget(self.auth_status_label)
        auth_layout.addWidget(self.auth_button)
        auth_group.setLayout(auth_layout)
        main_layout.addWidget(auth_group)
        
        # Video URL input section
        url_group = QGroupBox("Video URL")
        url_layout = QHBoxLayout()
        
        url_label = QLabel("YouTube Video URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        self.scan_button = QPushButton("Scan Comments")
        self.scan_button.clicked.connect(self.start_comment_scan)
        self.scan_button.setEnabled(False)  # Disabled until authenticated
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.scan_button)
        url_group.setLayout(url_layout)
        main_layout.addWidget(url_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Comments table
        self.comments_table = QTableWidget(0, 4)  # rows, columns
        self.comments_table.setHorizontalHeaderLabels(["Select", "Author", "Comment", "Reason"])
        
        # Set column sizes for better proportions
        self.comments_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Select column
        self.comments_table.setColumnWidth(0, 60)  # Fixed width for Select column
        
        self.comments_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # Author column
        self.comments_table.setColumnWidth(1, 150)  # Default width for Author column
        
        self.comments_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Comment column stretches
        self.comments_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)  # Reason column
        self.comments_table.setColumnWidth(3, 200)  # Default width for Reason column
        
        # Set alternate row colors for better readability
        self.comments_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.comments_table)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all_comments)
        self.select_all_button.setEnabled(False)
        
        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.clicked.connect(self.deselect_all_comments)
        self.deselect_all_button.setEnabled(False)
        
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected_comments)
        self.delete_button.setEnabled(False)
        
        actions_layout.addWidget(self.select_all_button)
        actions_layout.addWidget(self.deselect_all_button)
        actions_layout.addWidget(self.delete_button)
        main_layout.addLayout(actions_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)
        
        # File menu
        file_menu = QMenu("File", self)
        menu_bar.addMenu(file_menu)
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = QMenu("Help", self)
        menu_bar.addMenu(help_menu)
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def connect_signals(self):
        """Connect signals to slots"""
        # Connect thread signals
        self.fetch_completed.connect(self.on_fetch_completed)
        self.fetch_error.connect(self.on_fetch_error)
        self.delete_completed.connect(self.on_delete_completed)
        self.delete_error.connect(self.on_delete_error)
        self.progress_update.connect(self.update_progress)
    
    def check_auth_status(self):
        """Check if user is already authenticated"""
        try:
            credentials = self.oauth_handler.get_credentials()
            if credentials and not credentials.expired:
                self.is_authenticated = True
                self.youtube_api = YouTubeAPI(credentials)
                self.auth_status_label.setText(f"Authenticated as: {self.youtube_api.get_channel_name()}")
                self.auth_button.setText("Logout")
                self.scan_button.setEnabled(True)
                self.status_bar.showMessage("Authenticated with YouTube")
            else:
                self.is_authenticated = False
                self.auth_status_label.setText("Not authenticated")
                self.auth_button.setText("Login with YouTube")
                self.scan_button.setEnabled(False)
        except Exception as e:
            logging.error(f"Error checking authentication status: {e}")
            self.is_authenticated = False
    
    def handle_auth(self):
        """Handle authentication button click"""
        if self.is_authenticated:
            # Logout
            try:
                self.oauth_handler.clear_credentials()
                self.is_authenticated = False
                self.youtube_api = None
                self.auth_status_label.setText("Not authenticated")
                self.auth_button.setText("Login with YouTube")
                self.scan_button.setEnabled(False)
                self.status_bar.showMessage("Logged out")
            except Exception as e:
                logging.error(f"Error during logout: {e}")
                QMessageBox.critical(self, "Logout Error", f"Error during logout: {e}")
        else:
            # Login
            try:
                credentials = self.oauth_handler.authenticate()
                if credentials:
                    self.is_authenticated = True
                    self.youtube_api = YouTubeAPI(credentials)
                    self.auth_status_label.setText(f"Authenticated as: {self.youtube_api.get_channel_name()}")
                    self.auth_button.setText("Logout")
                    self.scan_button.setEnabled(True)
                    self.status_bar.showMessage("Authentication successful")
            except Exception as e:
                logging.error(f"Error during authentication: {e}")
                QMessageBox.critical(self, "Authentication Error", f"Error during authentication: {e}")
    
    def start_comment_scan(self):
        """Start scanning comments in a background thread"""
        video_url = self.url_input.text().strip()
        
        if not video_url:
            QMessageBox.warning(self, "Input Error", "Please enter a YouTube video URL")
            return
        
        # Extract video ID from URL
        video_id = self.youtube_api.extract_video_id(video_url)
        if not video_id:
            QMessageBox.warning(self, "Input Error", "Invalid YouTube video URL")
            return
            
        # Get max comments setting
        max_comments = self.config_manager.get_setting('max_comments_per_scan', 500)
        
        # Disable UI elements during scan
        self.url_input.setEnabled(False)
        self.scan_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.select_all_button.setEnabled(False)
        self.deselect_all_button.setEnabled(False)
        
        # Clear previous results
        self.comments_table.setRowCount(0)
        self.comments_data = []
        self.flagged_comments = []
        
        # Show progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Start background thread for fetching comments
        self.status_bar.showMessage(f"Scanning comments for video ID: {video_id}")
        
        fetch_thread = threading.Thread(
            target=self.fetch_comments_thread,
            args=(video_id,)
        )
        fetch_thread.daemon = True
        fetch_thread.start()
    
    def fetch_comments_thread(self, video_id):
        """Background thread for fetching and analyzing comments"""
        try:
            comments = []
            page_token = None
            total_comments = 0
            processed_comments = 0
            
            # Get max comments setting
            max_comments = self.config_manager.get_setting('max_comments_per_scan', 500)
            
            # First get an estimate of total comments
            response = self.youtube_api.get_comments(video_id)
            if 'pageInfo' in response and 'totalResults' in response['pageInfo']:
                total_comments = min(response['pageInfo']['totalResults'], max_comments)
            else:
                total_comments = max_comments  # Default estimate
            
            # Fetch all comments with pagination
            while True:
                response = self.youtube_api.get_comments(video_id, page_token)
                
                if 'items' not in response:
                    break
                
                items = response['items']
                comments.extend(items)
                
                processed_comments += len(items)
                self.progress_update.emit(processed_comments, total_comments)
                
                # Check if there are more pages and if we've reached the max comments limit
                if 'nextPageToken' in response and len(comments) < max_comments:
                    page_token = response['nextPageToken']
                else:
                    break
            
            # Analyze comments
            flagged_comments = []
            for comment in comments:
                comment_text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                is_flagged, reason = self.comment_analyzer.analyze(comment_text)
                
                if is_flagged:
                    comment['flag_reason'] = reason
                    flagged_comments.append(comment)
                    
                    # If auto-delete is enabled, delete the comment immediately
                    if self.config_manager.get_setting('auto_delete', False):
                        comment_id = comment['snippet']['topLevelComment']['id']
                        self.youtube_api.delete_comment(comment_id)
            
            # Update UI with results
            self.comments_data = comments
            self.flagged_comments = flagged_comments
            self.fetch_completed.emit(flagged_comments)
            
        except Exception as e:
            logging.error(f"Error fetching comments: {e}")
            self.fetch_error.emit(str(e))
    
    @pyqtSlot(list)
    def on_fetch_completed(self, flagged_comments):
        """Handle completion of comment fetching"""
        # Update table with flagged comments
        self.comments_table.setRowCount(len(flagged_comments))
        
        for i, comment in enumerate(flagged_comments):
            # Create checkbox for selection
            checkbox = QCheckBox()
            checkbox.setChecked(True)  # Select by default
            checkbox_cell = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_cell)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            
            # Get comment data
            snippet = comment['snippet']['topLevelComment']['snippet']
            author = snippet['authorDisplayName']
            text = snippet['textDisplay']
            reason = comment['flag_reason']
            
            # Format reason text with better readability
            if ',' in reason:
                # If multiple reasons, format as bullet points
                reasons = reason.split(',')
                formatted_reason = '• ' + '\n• '.join([r.strip() for r in reasons])
            else:
                formatted_reason = reason
            
            # Create table items
            author_item = QTableWidgetItem(author)
            text_item = QTableWidgetItem(text)
            reason_item = QTableWidgetItem(formatted_reason)
            
            # Style the reason item based on content
            if 'gambling' in reason.lower():
                reason_item.setForeground(Qt.GlobalColor.darkRed)
            elif 'spam' in reason.lower():
                reason_item.setForeground(Qt.GlobalColor.darkOrange)
            elif 'contact' in reason.lower():
                reason_item.setForeground(Qt.GlobalColor.darkBlue)
            
            # Add items to table
            self.comments_table.setCellWidget(i, 0, checkbox_cell)
            self.comments_table.setItem(i, 1, author_item)
            self.comments_table.setItem(i, 2, text_item)
            self.comments_table.setItem(i, 3, reason_item)
            
            # Set row height to accommodate multi-line reason text
            self.comments_table.setRowHeight(i, max(50, 20 * (1 + formatted_reason.count('\n'))))
        
        # Re-enable UI elements
        self.url_input.setEnabled(True)
        self.scan_button.setEnabled(True)
        
        # Enable action buttons if we have results
        if len(flagged_comments) > 0:
            self.select_all_button.setEnabled(True)
            self.deselect_all_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            self.status_bar.showMessage(f"Found {len(flagged_comments)} suspicious comments out of {len(self.comments_data)} total")
        else:
            self.status_bar.showMessage(f"No suspicious comments found in {len(self.comments_data)} total comments")
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
    
    @pyqtSlot(str)
    def on_fetch_error(self, error_message):
        """Handle error in comment fetching"""
        error_details = ""
        
        # Provide more helpful error messages based on common issues
        if "quota" in error_message.lower():
            error_details = "\n\nYou have exceeded your YouTube API quota. Please try again tomorrow or use a different API key."
        elif "authenticate" in error_message.lower() or "auth" in error_message.lower():
            error_details = "\n\nAuthentication error. Please try logging out and logging back in."
        elif "network" in error_message.lower() or "connection" in error_message.lower():
            error_details = "\n\nNetwork connection error. Please check your internet connection and try again."
        
        QMessageBox.critical(self, "Error", f"Error fetching comments: {error_message}{error_details}")
        
        # Re-enable UI elements
        self.url_input.setEnabled(True)
        self.scan_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Error fetching comments")
    
    @pyqtSlot(int, int)
    def update_progress(self, current, total):
        """Update progress bar"""
        percentage = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percentage)
        self.status_bar.showMessage(f"Processing comments: {current}/{total}")
    
    def select_all_comments(self):
        """Select all comments in the table"""
        for i in range(self.comments_table.rowCount()):
            checkbox_cell = self.comments_table.cellWidget(i, 0)
            checkbox = checkbox_cell.findChild(QCheckBox)
            checkbox.setChecked(True)
    
    def deselect_all_comments(self):
        """Deselect all comments in the table"""
        for i in range(self.comments_table.rowCount()):
            checkbox_cell = self.comments_table.cellWidget(i, 0)
            checkbox = checkbox_cell.findChild(QCheckBox)
            checkbox.setChecked(False)
    
    def open_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            # Reload configuration
            self.comment_analyzer = CommentAnalyzer(self.config_manager)
            self.status_bar.showMessage("Settings updated", 3000)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About StopJudol",
            "<h1>StopJudol</h1>"
            "<p>Version 1.0</p>"
            "<p>A desktop application to help YouTube content creators automatically identify "
            "and remove spam comments, online gambling ads, and other illegal content.</p>"
            "<p>Built with Python and PyQt6</p>"
        )
    
    def delete_selected_comments(self):
        """Delete selected comments"""
        # Confirm deletion
        selected_count = 0
        for i in range(self.comments_table.rowCount()):
            checkbox_cell = self.comments_table.cellWidget(i, 0)
            checkbox = checkbox_cell.findChild(QCheckBox)
            if checkbox.isChecked():
                selected_count += 1
        
        if selected_count == 0:
            QMessageBox.information(self, "No Selection", "No comments selected for deletion")
            return
        
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {selected_count} comments?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        # Collect comment IDs to delete
        comments_to_delete = []
        for i in range(self.comments_table.rowCount()):
            checkbox_cell = self.comments_table.cellWidget(i, 0)
            checkbox = checkbox_cell.findChild(QCheckBox)
            if checkbox.isChecked():
                comment_id = self.flagged_comments[i]['id']
                comments_to_delete.append(comment_id)
        
        # Disable UI during deletion
        self.url_input.setEnabled(False)
        self.scan_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.select_all_button.setEnabled(False)
        self.deselect_all_button.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Start background thread for deletion
        self.status_bar.showMessage(f"Deleting {len(comments_to_delete)} comments...")
        
        delete_thread = threading.Thread(
            target=self.delete_comments_thread,
            args=(comments_to_delete,)
        )
        delete_thread.daemon = True
        delete_thread.start()
    
    def delete_comments_thread(self, comment_ids):
        """Background thread for deleting comments"""
        try:
            deleted_ids = []
            total = len(comment_ids)
            
            for i, comment_id in enumerate(comment_ids):
                success = self.youtube_api.delete_comment(comment_id)
                if success:
                    deleted_ids.append(comment_id)
                
                # Update progress
                self.progress_update.emit(i + 1, total)
            
            self.delete_completed.emit(deleted_ids)
            
        except Exception as e:
            logging.error(f"Error deleting comments: {e}")
            self.delete_error.emit(str(e))
    
    @pyqtSlot(list)
    def on_delete_completed(self, deleted_ids):
        """Handle completion of comment deletion"""
        # Remove deleted comments from table
        rows_to_remove = []
        for i in range(self.comments_table.rowCount()):
            comment_id = self.flagged_comments[i]['id']
            if comment_id in deleted_ids:
                rows_to_remove.append(i)
        
        # Remove rows in reverse order to avoid index shifting
        for i in sorted(rows_to_remove, reverse=True):
            self.comments_table.removeRow(i)
            self.flagged_comments.pop(i)
        
        # Re-enable UI elements
        self.url_input.setEnabled(True)
        self.scan_button.setEnabled(True)
        
        # Enable action buttons if we still have results
        if self.comments_table.rowCount() > 0:
            self.select_all_button.setEnabled(True)
            self.deselect_all_button.setEnabled(True)
            self.delete_button.setEnabled(True)
        else:
            self.select_all_button.setEnabled(False)
            self.deselect_all_button.setEnabled(False)
            self.delete_button.setEnabled(False)
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Update status
        self.status_bar.showMessage(f"Successfully deleted {len(deleted_ids)} comments")
        
        # Show success message
        QMessageBox.information(
            self,
            "Deletion Complete",
            f"Successfully deleted {len(deleted_ids)} comments"
        )
    
    @pyqtSlot(str)
    def on_delete_error(self, error_message):
        """Handle error in comment deletion"""
        error_details = ""
        
        # Provide more helpful error messages based on common issues
        if "quota" in error_message.lower():
            error_details = "\n\nYou have exceeded your YouTube API quota. Please try again tomorrow or use a different API key."
        elif "authenticate" in error_message.lower() or "auth" in error_message.lower():
            error_details = "\n\nAuthentication error. Please try logging out and logging back in."
        elif "permission" in error_message.lower():
            error_details = "\n\nYou don't have permission to delete these comments. You can only delete comments on your own videos."
        elif "network" in error_message.lower() or "connection" in error_message.lower():
            error_details = "\n\nNetwork connection error. Please check your internet connection and try again."
        
        QMessageBox.critical(self, "Error", f"Error deleting comments: {error_message}{error_details}")
        
        # Re-enable UI elements
        self.url_input.setEnabled(True)
        self.scan_button.setEnabled(True)
        self.select_all_button.setEnabled(True)
        self.deselect_all_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Error deleting comments")
