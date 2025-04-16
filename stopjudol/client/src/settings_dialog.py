#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Settings Dialog
--------------------------
This module provides a dialog for configuring client settings.
"""

import os
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFormLayout, QGroupBox, QCheckBox,
    QMessageBox, QSpinBox
)
from PyQt6.QtCore import Qt, QSettings

class SettingsDialog(QDialog):
    """Dialog for configuring client settings"""
    
    def __init__(self, parent=None):
        """Initialize the settings dialog"""
        super().__init__(parent)
        self.setWindowTitle("StopJudol Settings")
        self.setMinimumWidth(450)
        
        # Initialize settings
        self.settings = QSettings("StopJudol", "Client")
        
        # Create the UI
        self.create_ui()
        
        # Load settings
        self.load_settings()
    
    def create_ui(self):
        """Create the UI elements"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Server settings group
        server_group = QGroupBox("Server Connection")
        server_layout = QFormLayout()
        
        # Server URL
        self.server_url = QLineEdit()
        self.server_url.setPlaceholderText("http://localhost:5000")
        server_layout.addRow("Server URL:", self.server_url)
        
        # Connection timeout
        self.timeout = QSpinBox()
        self.timeout.setRange(1, 60)
        self.timeout.setValue(10)
        self.timeout.setSuffix(" seconds")
        server_layout.addRow("Connection Timeout:", self.timeout)
        
        # Auto reconnect
        self.auto_reconnect = QCheckBox("Automatically reconnect if connection is lost")
        server_layout.addRow("", self.auto_reconnect)
        
        server_group.setLayout(server_layout)
        main_layout.addWidget(server_group)
        
        # Authentication settings group
        auth_group = QGroupBox("Authentication")
        auth_layout = QFormLayout()
        
        # Remember credentials
        self.remember_credentials = QCheckBox("Remember YouTube credentials")
        auth_layout.addRow("", self.remember_credentials)
        
        # Auto login
        self.auto_login = QCheckBox("Automatically log in at startup")
        auth_layout.addRow("", self.auto_login)
        
        auth_group.setLayout(auth_layout)
        main_layout.addWidget(auth_group)
        
        # Application settings group
        app_group = QGroupBox("Application Settings")
        app_layout = QFormLayout()
        
        # Auto check for updates
        self.check_updates = QCheckBox("Check for updates at startup")
        app_layout.addRow("", self.check_updates)
        
        # Show confirmation dialogs
        self.show_confirmations = QCheckBox("Show confirmation dialogs before actions")
        app_layout.addRow("", self.show_confirmations)
        
        app_group.setLayout(app_layout)
        main_layout.addWidget(app_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Reset button
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_settings)
        button_layout.addWidget(self.reset_button)
        
        # Spacer
        button_layout.addStretch()
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
    
    def load_settings(self):
        """Load settings from QSettings"""
        # Server settings
        self.server_url.setText(self.settings.value("server/url", "http://localhost:5000"))
        self.timeout.setValue(int(self.settings.value("server/timeout", 10)))
        self.auto_reconnect.setChecked(self.settings.value("server/auto_reconnect", True, type=bool))
        
        # Authentication settings
        self.remember_credentials.setChecked(self.settings.value("auth/remember_credentials", True, type=bool))
        self.auto_login.setChecked(self.settings.value("auth/auto_login", False, type=bool))
        
        # Application settings
        self.check_updates.setChecked(self.settings.value("app/check_updates", True, type=bool))
        self.show_confirmations.setChecked(self.settings.value("app/show_confirmations", True, type=bool))
    
    def save_settings(self):
        """Save settings to QSettings"""
        # Validate server URL
        server_url = self.server_url.text().strip()
        if not server_url:
            server_url = "http://localhost:5000"
        
        # Server settings
        self.settings.setValue("server/url", server_url)
        self.settings.setValue("server/timeout", self.timeout.value())
        self.settings.setValue("server/auto_reconnect", self.auto_reconnect.isChecked())
        
        # Authentication settings
        self.settings.setValue("auth/remember_credentials", self.remember_credentials.isChecked())
        self.settings.setValue("auth/auto_login", self.auto_login.isChecked())
        
        # Application settings
        self.settings.setValue("app/check_updates", self.check_updates.isChecked())
        self.settings.setValue("app/show_confirmations", self.show_confirmations.isChecked())
        
        # Sync settings
        self.settings.sync()
        
        # Close dialog
        self.accept()
    
    def reset_settings(self):
        """Reset settings to defaults"""
        # Confirm reset
        confirm = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Server settings
            self.server_url.setText("http://localhost:5000")
            self.timeout.setValue(10)
            self.auto_reconnect.setChecked(True)
            
            # Authentication settings
            self.remember_credentials.setChecked(True)
            self.auto_login.setChecked(False)
            
            # Application settings
            self.check_updates.setChecked(True)
            self.show_confirmations.setChecked(True)
    
    @staticmethod
    def get_settings():
        """Get the current settings as a dictionary"""
        settings = QSettings("StopJudol", "Client")
        
        return {
            "server": {
                "url": settings.value("server/url", "http://localhost:5000"),
                "timeout": int(settings.value("server/timeout", 10)),
                "auto_reconnect": settings.value("server/auto_reconnect", True, type=bool)
            },
            "auth": {
                "remember_credentials": settings.value("auth/remember_credentials", True, type=bool),
                "auto_login": settings.value("auth/auto_login", False, type=bool)
            },
            "app": {
                "check_updates": settings.value("app/check_updates", True, type=bool),
                "show_confirmations": settings.value("app/show_confirmations", True, type=bool)
            }
        }
