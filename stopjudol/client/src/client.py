#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Main Client Application
-----------------------------------
This module contains the main application window class for the StopJudol client.
"""

import os
import sys
import logging
import threading
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QTableWidget, 
    QTableWidgetItem, QProgressBar, QMessageBox,
    QCheckBox, QGroupBox, QTabWidget, QTextEdit,
    QStatusBar, QHeaderView, QMenuBar, QMenu,
    QDialog, QInputDialog
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QIcon, QPixmap

from jsonrpcclient import request, parse_json, Ok, Error
import requests

# Import settings dialog
from .settings_dialog import SettingsDialog

# Import OAuth handler for authentication
from .auth.oauth_handler import OAuthHandler

# Import RPC client and error handler
from .rpc_client import RPCClient
from .error_handler import ErrorHandler
from .worker import FetchCommentsWorker, DeleteCommentsWorker, run_in_thread
from PyQt6.QtCore import QSettings

class MainWindow(QMainWindow):
    """Main application window for StopJudol"""
    
    # Define signals for thread communication
    fetch_completed = pyqtSignal(list)
    fetch_error = pyqtSignal(str)
    delete_completed = pyqtSignal(list, list, list, list, list, list)  # Perbaiki nama emitter
    delete_error = pyqtSignal(str)
    progress_update = pyqtSignal(int, int)  # current, total
    
    def __init__(self):
        super().__init__()
        
        # Initialize logger
        self.logger = logging.getLogger("MainWindow")
        self.logger.setLevel(logging.DEBUG)
        
        # Initialize settings
        self.settings = QSettings("StopJudol", "Client")
        
        # Initialize RPC client
        server_url = self.settings.value("server/url", "http://localhost:5000")
        self.rpc_client = RPCClient(server_url)
        
        # Initialize OAuth handler
        self.oauth_handler = OAuthHandler(self)
        
        # Initialize error handler
        self.error_handler = ErrorHandler(self)
        
        # Initialize components
        self.credentials = None
        self.credentials_json = None
        
        # Server configuration
        self.server_url = server_url  # Default server URL
        
        # UI state variables
        self.is_authenticated = False
        self.comments_data = []
        self.flagged_comments = []
        
        # Set up UI
        self.init_ui()
        
        # Connect signals
        self.connect_signals()
        
        # Try to login to the server
        self._login_to_server()
        
        # Authenticate with YouTube if auto-login is enabled
        if self.settings.value("auth/auto_login", False, type=bool):
            self.authenticate()
            
        # Check authentication status on startup
        self.check_auth_status()
    
    def _login_to_server(self):
        """Attempt to login to the server with default credentials"""
        try:
            # Try to login with default credentials (for development)
            username = self.settings.value("server/username", "admin")
            password = self.settings.value("server/password", "password")
            success, result = self.rpc_client.login(username, password)
            
            if success:
                self.logger.info("Successfully logged in to server")
            else:
                self.logger.warning(f"Failed to login to server: {result}")
                # Show login dialog if needed
                # self._show_login_dialog()
        except Exception as e:
            self.logger.error(f"Error logging in to server: {e}")
    
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
        header = self.comments_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Select
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Author
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Comment
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Reason
        
        main_layout.addWidget(self.comments_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all_comments)
        self.select_all_button.setEnabled(False)
        
        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.clicked.connect(self.deselect_all_comments)
        self.deselect_all_button.setEnabled(False)
        
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected_comments)
        self.delete_button.setEnabled(False)
        
        action_layout.addWidget(self.select_all_button)
        action_layout.addWidget(self.deselect_all_button)
        action_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(action_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def connect_signals(self):
        """Connect signals to slots"""
        self.fetch_completed.connect(self.on_fetch_completed)
        self.fetch_error.connect(self.on_fetch_error)
        self.delete_completed.connect(self.on_delete_completed)
        self.delete_error.connect(self.on_delete_error)
        self.progress_update.connect(self.update_progress)
    
    def check_auth_status(self):
        """Check if user is already authenticated"""
        credentials = self.oauth_handler.get_credentials()
        
        if credentials and not credentials.expired:
            self.credentials = credentials
            self.credentials_json = self.credentials_to_json(credentials)
            self.is_authenticated = True
            
            # Get channel name via RPC
            threading.Thread(target=self.get_channel_name_thread).start()
            
            self.auth_status_label.setText("Checking authentication...")
            self.auth_button.setText("Logout")
            self.scan_button.setEnabled(True)
        else:
            self.auth_status_label.setText("Not authenticated")
            self.auth_button.setText("Login with YouTube")
            self.scan_button.setEnabled(False)
    
    def handle_auth(self):
        """Handle authentication button click"""
        if self.is_authenticated:
            # Logout
            if self.oauth_handler.clear_credentials():
                self.is_authenticated = False
                self.credentials = None
                self.credentials_json = None
                self.auth_status_label.setText("Not authenticated")
                self.auth_button.setText("Login with YouTube")
                self.scan_button.setEnabled(False)
                self.status_bar.showMessage("Logged out successfully")
            else:
                QMessageBox.warning(self, "Logout Error", "Failed to clear credentials")
        else:
            # Login
            try:
                credentials = self.oauth_handler.authenticate()
                
                if credentials:
                    self.credentials = credentials
                    self.credentials_json = self.credentials_to_json(credentials)
                    self.is_authenticated = True
                    
                    # Get channel name via RPC
                    threading.Thread(target=self.get_channel_name_thread).start()
                    
                    self.auth_status_label.setText("Checking authentication...")
                    self.auth_button.setText("Logout")
                    self.scan_button.setEnabled(True)
                    self.status_bar.showMessage("Authenticated successfully")
                else:
                    QMessageBox.warning(self, "Authentication Error", "Failed to authenticate with YouTube")
            except Exception as e:
                QMessageBox.critical(self, "Authentication Error", f"Error during authentication: {e}")
    
    def credentials_to_json(self, credentials):
        """Convert credentials to JSON string"""
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        return json.dumps(token_data)
    
    def get_channel_name_thread(self):
        """Get channel name in a background thread"""
        try:
            success, result = self.rpc_client.get_channel_info(self.credentials_json)
            
            if success:
                channel_name = result.get("channel_name", "Unknown Channel")
                self.auth_status_label.setText(f"Authenticated as: {channel_name}")
            else:
                self.auth_status_label.setText("Authentication error")
                self.error_handler.handle_rpc_error(self, result, "Authentication")
                logging.error(f"Error getting channel name: {result}")
        except Exception as e:
            self.auth_status_label.setText("Authentication error")
            self.error_handler.handle_network_error(self, e, "Authentication")
            logging.error(f"Error getting channel name: {e}")
    
    def start_comment_scan(self):
        """Start scanning comments in a background thread"""
        # Get the video URL from the input field
        video_url = self.url_input.text().strip()
        
        if not video_url:
            QMessageBox.warning(self, "Input Error", "Please enter a YouTube video URL")
            return
        
        # Disable UI elements during scan
        self.url_input.setEnabled(False)
        self.scan_button.setEnabled(False)
        self.select_all_button.setEnabled(False)
        self.deselect_all_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
        # Clear previous results
        self.comments_table.setRowCount(0)
        self.flagged_comments = []
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Update status
        self.status_bar.showMessage("Extracting video ID...")
        
        # Start the comment fetching in a background thread
        threading.Thread(target=self.fetch_comments_thread, args=(video_url,)).start()
    
    def fetch_comments_thread(self, video_url):
        """Background thread for fetching and analyzing comments"""
        try:
            # First, extract the video ID
            success, result = self.rpc_client.extract_video_id(video_url)
            
            if not success:
                self.fetch_error.emit(f"Error extracting video ID: {result}")
                return
                
            video_id = result.get("video_id")
            if not video_id:
                self.fetch_error.emit("Invalid YouTube URL")
                return
            
            # Update status
            self.status_bar.showMessage(f"Fetching comments for video {video_id}...")
            
            # Fetch comments via RPC
            success, comments = self.rpc_client.fetch_comments(video_id, self.credentials_json)
            
            if not success:
                self.fetch_error.emit(f"Error fetching comments: {comments}")
                return
                
            if not comments:
                self.fetch_error.emit("No comments found for this video")
                return
            
            # Update progress
            self.progress_update.emit(50, 100)
            
            # Update status
            self.status_bar.showMessage(f"Analyzing {len(comments)} comments...")
            
            # Analyze comments via RPC
            success, flagged_comments = self.rpc_client.analyze_comments(comments)
            
            if not success:
                self.fetch_error.emit(f"Error analyzing comments: {flagged_comments}")
                return
                
            if not flagged_comments:
                self.fetch_error.emit("No suspicious comments found")
                return
            
            # Update progress
            self.progress_update.emit(100, 100)
            
            # Send the results back to the main thread
            self.fetch_completed.emit(flagged_comments)
            
        except Exception as e:
            self.fetch_error.emit(f"Error: {e}")
    
    @pyqtSlot(list)
    def on_fetch_completed(self, flagged_comments):
        """Handle completion of comment fetching"""
        # Store the flagged comments for later use
        self.flagged_comments = flagged_comments
        
        # Update the table with the flagged comments
        self.comments_table.setRowCount(len(flagged_comments))
        
        for i, comment in enumerate(flagged_comments):
            # Create checkbox for selection
            checkbox = QCheckBox()
            checkbox.setChecked(True)  # Select by default
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            
            # Get comment data
            author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
            text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
            reason = comment['analysis_result']['reason'] if 'analysis_result' in comment else "Unknown"
            
            # Add items to table
            self.comments_table.setCellWidget(i, 0, checkbox_widget)
            self.comments_table.setItem(i, 1, QTableWidgetItem(author))
            self.comments_table.setItem(i, 2, QTableWidgetItem(text))
            self.comments_table.setItem(i, 3, QTableWidgetItem(reason))
        
        # Re-enable UI elements
        self.url_input.setEnabled(True)
        self.scan_button.setEnabled(True)
        self.select_all_button.setEnabled(True)
        self.deselect_all_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Update status
        self.status_bar.showMessage(f"Found {len(flagged_comments)} suspicious comments")
    
    @pyqtSlot(str)
    def on_fetch_error(self, error_message):
        """Handle error in comment fetching"""
        # Re-enable UI elements
        self.url_input.setEnabled(True)
        self.scan_button.setEnabled(True)
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Update status
        self.status_bar.showMessage("Error fetching comments")
        
        # Show error message
        QMessageBox.critical(self, "Error", f"Error fetching comments: {error_message}")
    
    @pyqtSlot(int, int)
    def update_progress(self, current, total):
        """Update progress bar"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
    
    def select_all_comments(self):
        """Select all comments in the table"""
        for i in range(self.comments_table.rowCount()):
            checkbox_widget = self.comments_table.cellWidget(i, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(True)
    
    def deselect_all_comments(self):
        """Deselect all comments in the table"""
        for i in range(self.comments_table.rowCount()):
            checkbox_widget = self.comments_table.cellWidget(i, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(False)
    
    def open_settings(self):
        """Open the settings dialog"""
        # Get server URL from user
        server_url, ok = QInputDialog.getText(
            self, "Server Settings", "Enter JSON-RPC Server URL:",
            text=self.server_url
        )
        
        if ok and server_url:
            self.server_url = server_url
            self.status_bar.showMessage(f"Server URL set to: {self.server_url}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About StopJudol",
            "StopJudol - YouTube Comment Moderator\n\n"
            "Version: 2.0.0 (JSON-RPC)\n"
            " 2025 StopJudol Team\n\n"
            "A tool to help YouTube content creators identify and remove spam, gambling ads, "
            "and other unwanted content from their videos."
        )
    
    def delete_selected_comments(self):
        """Delete selected comments"""
        # Get selected comments
        selected_indices = []
        selected_comments = []
        
        for i in range(self.comments_table.rowCount()):
            checkbox_widget = self.comments_table.cellWidget(i, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_indices.append(i)
                    selected_comments.append(self.flagged_comments[i])
        
        if not selected_comments:
            QMessageBox.warning(self, "No Selection", "Please select at least one comment to delete")
            return
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(selected_comments)} selected comments?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        # Disable UI elements during deletion
        self.url_input.setEnabled(False)
        self.scan_button.setEnabled(False)
        self.select_all_button.setEnabled(False)
        self.deselect_all_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(selected_comments))
        
        # Update status
        self.status_bar.showMessage("Deleting comments...")
        
        # Start the deletion in a background thread
        threading.Thread(target=self.delete_comments_thread, args=(selected_indices, selected_comments)).start()
    
    def delete_comments_thread(self, selected_indices, selected_comments):
        """Background thread for deleting comments"""
        deleted_indices = []
        deleted_ids = []
        marked_as_spam_indices = []
        marked_as_spam_ids = []
        error_indices = []
        error_messages = []
        
        try:
            for i, comment in enumerate(selected_comments):
                try:
                    # Get comment ID and thread ID
                    comment_id = comment['snippet']['topLevelComment']['id']
                    thread_id = comment['id']
                    
                    # Update progress
                    self.progress_update.emit(i + 1, len(selected_comments))
                    
                    # Delete comment via RPC client
                    success, result = self.rpc_client.delete_comment(
                        comment_id=comment_id, 
                        thread_id=thread_id,
                        credentials_json=self.credentials_json
                    )
                    
                    if not success:
                        error_indices.append(selected_indices[i])
                        error_messages.append(str(result))
                        continue
                    
                    action_type = result.get('action_type', 'none')
                    success = result.get('success', False)
                    
                    if success:
                        if action_type == 'deleted':
                            deleted_indices.append(selected_indices[i])
                            deleted_ids.append(comment_id)
                        elif action_type == 'marked_as_spam':
                            marked_as_spam_indices.append(selected_indices[i])
                            marked_as_spam_ids.append(comment_id)
                    else:
                        error_indices.append(selected_indices[i])
                        error_messages.append(result.get('message', 'Unknown error'))
                        
                except Exception as e:
                    error_indices.append(selected_indices[i])
                    error_messages.append(str(e))
            
            # Update UI with results
            self.delete_completed.emit(
                deleted_indices, 
                deleted_ids, 
                marked_as_spam_indices, 
                marked_as_spam_ids, 
                error_indices, 
                error_messages
            )
            
        except Exception as e:
            self.delete_error.emit(str(e))
    
    @pyqtSlot(list, list, list, list, list, list)
    def on_delete_completed(self, deleted_indices, deleted_ids, marked_as_spam_indices, marked_as_spam_ids, error_indices, error_messages):
        """Handle completion of comment deletion"""
        # Remove deleted and marked as spam comments from table (in reverse order to avoid index shifting)
        all_indices_to_remove = sorted(deleted_indices + marked_as_spam_indices, reverse=True)
        
        for i in all_indices_to_remove:
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
        total_processed = len(deleted_ids) + len(marked_as_spam_ids)
        self.status_bar.showMessage(f"Processed {total_processed} comments ({len(deleted_ids)} deleted, {len(marked_as_spam_ids)} marked as spam)")
        
        # Prepare detailed message
        message = ""
        if deleted_ids:
            message += f"Successfully deleted {len(deleted_ids)} comments.\n\n"
        if marked_as_spam_ids:
            message += f"Marked {len(marked_as_spam_ids)} comments as spam.\n\n"
            message += "Note: Comments marked as spam will be reviewed by YouTube's system and may not be immediately removed. "
            message += "This is a limitation of YouTube's API for comments that you didn't create yourself."
        
        if error_indices:
            message += f"\n\nFailed to process {len(error_indices)} comments:\n"
            for i, error in enumerate(error_messages[:5]):
                message += f"- {error}\n"
            if len(error_messages) > 5:
                message += f"... and {len(error_messages) - 5} more errors"
        
        # Show success message
        QMessageBox.information(
            self,
            "Action Complete",
            message
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


# Main entry point
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
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
