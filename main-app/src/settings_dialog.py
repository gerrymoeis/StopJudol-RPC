#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Settings Dialog
---------------------------
This module provides a dialog for configuring application settings.
"""

import os
import sys
import logging
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QCheckBox, QSpinBox, QFormLayout, QMessageBox, QGroupBox,
    QFileDialog, QComboBox, QInputDialog, QMenu
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QAction

from src.core.config_manager import ConfigManager

class SettingsDialog(QDialog):
    """Dialog for configuring application settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("StopJudol - Settings")
        self.setMinimumSize(600, 400)
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        
        # Set up UI
        self.init_ui()
        
        # Load current settings
        self.load_settings()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Create tabs
        blacklist_tab = QWidget()
        whitelist_tab = QWidget()
        general_tab = QWidget()
        
        # Set up tab layouts
        self.setup_blacklist_tab(blacklist_tab)
        self.setup_whitelist_tab(whitelist_tab)
        self.setup_general_tab(general_tab)
        
        # Add tabs to widget
        tab_widget.addTab(blacklist_tab, "Blacklist")
        tab_widget.addTab(whitelist_tab, "Whitelist")
        tab_widget.addTab(general_tab, "General")
        
        # Add tab widget to main layout
        main_layout.addWidget(tab_widget)
        
        # Add buttons
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        
        main_layout.addLayout(buttons_layout)
    
    def setup_blacklist_tab(self, tab):
        """Set up the blacklist tab"""
        layout = QVBoxLayout(tab)
        
        # Add description
        description = QLabel(
            "Blacklisted terms will flag comments for review. "
            "These terms are case-insensitive and will match anywhere in the comment text."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.blacklist_search = QLineEdit()
        self.blacklist_search.setPlaceholderText("Search terms...")
        self.blacklist_search.textChanged.connect(self.filter_blacklist)
        
        # Add category filter
        category_label = QLabel("Category:")
        self.blacklist_category_filter = QComboBox()
        self.blacklist_category_filter.addItem("All Categories")
        self.blacklist_category_filter.addItem("Gambling")
        self.blacklist_category_filter.addItem("Contact Info")
        self.blacklist_category_filter.addItem("Spam")
        self.blacklist_category_filter.addItem("Other")
        self.blacklist_category_filter.currentTextChanged.connect(self.filter_blacklist)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.blacklist_search)
        search_layout.addWidget(category_label)
        search_layout.addWidget(self.blacklist_category_filter)
        layout.addLayout(search_layout)
        
        # Add list widget for terms
        self.blacklist_widget = QListWidget()
        self.blacklist_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.blacklist_widget.customContextMenuRequested.connect(self.show_blacklist_context_menu)
        layout.addWidget(self.blacklist_widget)
        
        # Add controls for adding/removing terms
        controls_layout = QHBoxLayout()
        
        self.blacklist_input = QLineEdit()
        self.blacklist_input.setPlaceholderText("Enter new blacklist term...")
        
        # Category selection for new terms
        self.blacklist_category = QComboBox()
        self.blacklist_category.addItem("Gambling")
        self.blacklist_category.addItem("Contact Info")
        self.blacklist_category.addItem("Spam")
        self.blacklist_category.addItem("Other")
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_blacklist_term)
        
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_blacklist_term)
        
        controls_layout.addWidget(self.blacklist_input)
        controls_layout.addWidget(self.blacklist_category)
        controls_layout.addWidget(add_button)
        controls_layout.addWidget(remove_button)
        
        layout.addLayout(controls_layout)
        
        # Add import/export buttons
        import_export_layout = QHBoxLayout()
        
        import_button = QPushButton("Import Terms")
        import_button.clicked.connect(self.import_blacklist)
        
        export_button = QPushButton("Export Terms")
        export_button.clicked.connect(self.export_blacklist)
        
        import_export_layout.addWidget(import_button)
        import_export_layout.addWidget(export_button)
        
        layout.addLayout(import_export_layout)
    
    def setup_whitelist_tab(self, tab):
        """Set up the whitelist tab"""
        layout = QVBoxLayout(tab)
        
        # Add description
        description = QLabel(
            "Whitelisted terms will override blacklist matches. "
            "If a comment contains both blacklisted and whitelisted terms, it will not be flagged."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.whitelist_search = QLineEdit()
        self.whitelist_search.setPlaceholderText("Search terms...")
        self.whitelist_search.textChanged.connect(self.filter_whitelist)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.whitelist_search)
        layout.addLayout(search_layout)
        
        # Add list widget for terms
        self.whitelist_widget = QListWidget()
        self.whitelist_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.whitelist_widget.customContextMenuRequested.connect(self.show_whitelist_context_menu)
        layout.addWidget(self.whitelist_widget)
        
        # Add controls for adding/removing terms
        controls_layout = QHBoxLayout()
        
        self.whitelist_input = QLineEdit()
        self.whitelist_input.setPlaceholderText("Enter new whitelist term...")
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_whitelist_term)
        
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_whitelist_term)
        
        controls_layout.addWidget(self.whitelist_input)
        controls_layout.addWidget(add_button)
        controls_layout.addWidget(remove_button)
        
        layout.addLayout(controls_layout)
        
        # Add import/export buttons
        import_export_layout = QHBoxLayout()
        
        import_button = QPushButton("Import Terms")
        import_button.clicked.connect(self.import_whitelist)
        
        export_button = QPushButton("Export Terms")
        export_button.clicked.connect(self.export_whitelist)
        
        import_export_layout.addWidget(import_button)
        import_export_layout.addWidget(export_button)
        
        layout.addLayout(import_export_layout)
    
    def setup_general_tab(self, tab):
        """Set up the general settings tab"""
        layout = QVBoxLayout(tab)
        
        # Create form layout for settings
        form_layout = QFormLayout()
        
        # Auto-delete setting
        self.auto_delete_checkbox = QCheckBox("Auto-delete flagged comments without review")
        form_layout.addRow("Auto-delete:", self.auto_delete_checkbox)
        
        # Max comments per scan
        self.max_comments_spinbox = QSpinBox()
        self.max_comments_spinbox.setMinimum(10)
        self.max_comments_spinbox.setMaximum(1000)
        self.max_comments_spinbox.setSingleStep(10)
        form_layout.addRow("Max comments per scan:", self.max_comments_spinbox)
        
        # Check interval
        self.check_interval_spinbox = QSpinBox()
        self.check_interval_spinbox.setMinimum(0)
        self.check_interval_spinbox.setMaximum(86400)  # 24 hours in seconds
        self.check_interval_spinbox.setSingleStep(60)
        self.check_interval_spinbox.setSpecialValueText("Disabled")
        form_layout.addRow("Auto-check interval (seconds):", self.check_interval_spinbox)
        
        # Add form to layout
        layout.addLayout(form_layout)
        
        # Add explanation for settings
        explanation = QLabel(
            "Note: Auto-delete will immediately delete comments that match blacklist terms without showing them for review. "
            "Use with caution. Auto-check interval of 0 disables automatic scanning."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def load_settings(self):
        """Load current settings into the UI"""
        # Load blacklist with categories
        self.blacklist_widget.clear()
        blacklist = self.config_manager.get_blacklist()
        blacklist_categories = self.config_manager.config.get('blacklist_categories', {})
        
        for term in blacklist:
            category = blacklist_categories.get(term, "Other")
            display_text = f"{term} [{category}]"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, {"term": term, "category": category})
            self.blacklist_widget.addItem(item)
        
        # Load whitelist
        self.whitelist_widget.clear()
        for term in self.config_manager.get_whitelist():
            self.whitelist_widget.addItem(term)
        
        # Load general settings
        self.auto_delete_checkbox.setChecked(
            self.config_manager.get_setting('auto_delete', False)
        )
        
        self.max_comments_spinbox.setValue(
            self.config_manager.get_setting('max_comments_per_scan', 500)
        )
        
        self.check_interval_spinbox.setValue(
            self.config_manager.get_setting('check_interval_seconds', 0)
        )
    
    def add_blacklist_term(self):
        """Add a term to the blacklist"""
        term = self.blacklist_input.text().strip()
        category = self.blacklist_category.currentText()
        
        if not term:
            return
        
        # Check if term already exists
        for i in range(self.blacklist_widget.count()):
            if self.blacklist_widget.item(i).text().split(' [')[0] == term:
                QMessageBox.warning(self, "Duplicate Term", "This term is already in the blacklist.")
                return
        
        # Add to list widget with category
        display_text = f"{term} [{category}]"
        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, {"term": term, "category": category})
        self.blacklist_widget.addItem(item)
        
        # Clear input
        self.blacklist_input.clear()
    
    def remove_blacklist_term(self):
        """Remove selected term from the blacklist"""
        selected_items = self.blacklist_widget.selectedItems()
        
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a term to remove.")
            return
        
        # Remove selected items
        for item in selected_items:
            self.blacklist_widget.takeItem(self.blacklist_widget.row(item))
    
    def add_whitelist_term(self):
        """Add a term to the whitelist"""
        term = self.whitelist_input.text().strip()
        
        if not term:
            return
        
        # Check if term already exists
        for i in range(self.whitelist_widget.count()):
            if self.whitelist_widget.item(i).text() == term:
                QMessageBox.warning(self, "Duplicate Term", "This term is already in the whitelist.")
                return
        
        # Add to list widget
        self.whitelist_widget.addItem(term)
        
        # Clear input
        self.whitelist_input.clear()
    
    def remove_whitelist_term(self):
        """Remove selected term from the whitelist"""
        selected_items = self.whitelist_widget.selectedItems()
        
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a term to remove.")
            return
        
        # Remove selected items
        for item in selected_items:
            self.whitelist_widget.takeItem(self.whitelist_widget.row(item))
    
    def save_settings(self):
        """Save settings to config file"""
        # Collect blacklist terms with categories
        blacklist = []
        blacklist_categories = {}
        
        for i in range(self.blacklist_widget.count()):
            item = self.blacklist_widget.item(i)
            item_data = item.data(Qt.ItemDataRole.UserRole)
            
            if item_data:
                term = item_data["term"]
                category = item_data["category"]
                blacklist.append(term)
                blacklist_categories[term] = category
            else:
                # For backward compatibility with older items
                text = item.text()
                if '[' in text and ']' in text:
                    term = text.split(' [')[0]
                    category = text.split('[')[1].split(']')[0]
                    blacklist.append(term)
                    blacklist_categories[term] = category
                else:
                    blacklist.append(text)
                    blacklist_categories[text] = "Other"
        
        # Collect whitelist terms
        whitelist = []
        for i in range(self.whitelist_widget.count()):
            whitelist.append(self.whitelist_widget.item(i).text())
        
        # Update config
        config = {
            'blacklist': blacklist,
            'blacklist_categories': blacklist_categories,
            'whitelist': whitelist,
            'settings': {
                'auto_delete': self.auto_delete_checkbox.isChecked(),
                'max_comments_per_scan': self.max_comments_spinbox.value(),
                'check_interval_seconds': self.check_interval_spinbox.value()
            }
        }
        
        # Save config
        self.config_manager.config = config
        self.config_manager.save_config()
        
        # Close dialog
        self.accept()
    
    def filter_blacklist(self):
        """Filter the blacklist based on search text and category"""
        search_text = self.blacklist_search.text().lower()
        category_filter = self.blacklist_category_filter.currentText()
        
        for i in range(self.blacklist_widget.count()):
            item = self.blacklist_widget.item(i)
            item_data = item.data(Qt.ItemDataRole.UserRole)
            
            if item_data:
                term = item_data["term"].lower()
                category = item_data["category"]
            else:
                # For backward compatibility
                text = item.text()
                if '[' in text and ']' in text:
                    term = text.split(' [')[0].lower()
                    category = text.split('[')[1].split(']')[0]
                else:
                    term = text.lower()
                    category = "Other"
            
            # Check if item matches search and category filters
            matches_search = search_text == "" or search_text in term
            matches_category = category_filter == "All Categories" or category_filter == category
            
            # Show or hide item based on filters
            item.setHidden(not (matches_search and matches_category))
    
    def filter_whitelist(self):
        """Filter the whitelist based on search text"""
        search_text = self.whitelist_search.text().lower()
        
        for i in range(self.whitelist_widget.count()):
            item = self.whitelist_widget.item(i)
            term = item.text().lower()
            
            # Show or hide item based on search filter
            item.setHidden(not (search_text == "" or search_text in term))
    
    def show_blacklist_context_menu(self, position):
        """Show context menu for blacklist items"""
        menu = QMenu()
        selected_items = self.blacklist_widget.selectedItems()
        
        if selected_items:
            edit_action = QAction("Edit Term", self)
            edit_action.triggered.connect(self.edit_blacklist_term)
            menu.addAction(edit_action)
            
            change_category_action = QAction("Change Category", self)
            change_category_action.triggered.connect(self.change_blacklist_category)
            menu.addAction(change_category_action)
            
            remove_action = QAction("Remove", self)
            remove_action.triggered.connect(self.remove_blacklist_term)
            menu.addAction(remove_action)
            
            menu.exec(self.blacklist_widget.mapToGlobal(position))
    
    def show_whitelist_context_menu(self, position):
        """Show context menu for whitelist items"""
        menu = QMenu()
        selected_items = self.whitelist_widget.selectedItems()
        
        if selected_items:
            edit_action = QAction("Edit Term", self)
            edit_action.triggered.connect(self.edit_whitelist_term)
            menu.addAction(edit_action)
            
            remove_action = QAction("Remove", self)
            remove_action.triggered.connect(self.remove_whitelist_term)
            menu.addAction(remove_action)
            
            menu.exec(self.whitelist_widget.mapToGlobal(position))
    
    def edit_blacklist_term(self):
        """Edit the selected blacklist term"""
        selected_items = self.blacklist_widget.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        item_data = item.data(Qt.ItemDataRole.UserRole)
        
        if item_data:
            old_term = item_data["term"]
            category = item_data["category"]
        else:
            # For backward compatibility
            text = item.text()
            if '[' in text and ']' in text:
                old_term = text.split(' [')[0]
                category = text.split('[')[1].split(']')[0]
            else:
                old_term = text
                category = "Other"
        
        new_term, ok = QInputDialog.getText(
            self, "Edit Term", "Edit blacklist term:", QLineEdit.EchoMode.Normal, old_term
        )
        
        if ok and new_term.strip():
            # Check for duplicates
            for i in range(self.blacklist_widget.count()):
                other_item = self.blacklist_widget.item(i)
                if other_item != item:
                    other_data = other_item.data(Qt.ItemDataRole.UserRole)
                    if other_data and other_data["term"] == new_term.strip():
                        QMessageBox.warning(self, "Duplicate Term", "This term is already in the blacklist.")
                        return
            
            # Update item
            display_text = f"{new_term.strip()} [{category}]"
            item.setText(display_text)
            item.setData(Qt.ItemDataRole.UserRole, {"term": new_term.strip(), "category": category})
    
    def edit_whitelist_term(self):
        """Edit the selected whitelist term"""
        selected_items = self.whitelist_widget.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        old_term = item.text()
        
        new_term, ok = QInputDialog.getText(
            self, "Edit Term", "Edit whitelist term:", QLineEdit.EchoMode.Normal, old_term
        )
        
        if ok and new_term.strip():
            # Check for duplicates
            for i in range(self.whitelist_widget.count()):
                other_item = self.whitelist_widget.item(i)
                if other_item != item and other_item.text() == new_term.strip():
                    QMessageBox.warning(self, "Duplicate Term", "This term is already in the whitelist.")
                    return
            
            # Update item
            item.setText(new_term.strip())
    
    def change_blacklist_category(self):
        """Change the category of the selected blacklist term"""
        selected_items = self.blacklist_widget.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        item_data = item.data(Qt.ItemDataRole.UserRole)
        
        if item_data:
            term = item_data["term"]
            old_category = item_data["category"]
        else:
            # For backward compatibility
            text = item.text()
            if '[' in text and ']' in text:
                term = text.split(' [')[0]
                old_category = text.split('[')[1].split(']')[0]
            else:
                term = text
                old_category = "Other"
        
        categories = ["Gambling", "Contact Info", "Spam", "Other"]
        category_index = categories.index(old_category) if old_category in categories else 3  # Default to "Other"
        
        new_category, ok = QInputDialog.getItem(
            self, "Change Category", "Select category:", categories, category_index, False
        )
        
        if ok and new_category:
            # Update item
            display_text = f"{term} [{new_category}]"
            item.setText(display_text)
            item.setData(Qt.ItemDataRole.UserRole, {"term": term, "category": new_category})
    
    def import_blacklist(self):
        """Import blacklist terms from a JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Blacklist", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list) and not isinstance(data, dict):
                QMessageBox.warning(self, "Invalid Format", "The file does not contain a valid blacklist format.")
                return
            
            # Handle different import formats
            terms_added = 0
            
            if isinstance(data, list):
                # Simple list of terms
                for term in data:
                    if isinstance(term, str) and term.strip():
                        # Check if term already exists
                        exists = False
                        for i in range(self.blacklist_widget.count()):
                            item = self.blacklist_widget.item(i)
                            item_data = item.data(Qt.ItemDataRole.UserRole)
                            if item_data and item_data["term"] == term.strip():
                                exists = True
                                break
                        
                        if not exists:
                            display_text = f"{term.strip()} [Other]"
                            item = QListWidgetItem(display_text)
                            item.setData(Qt.ItemDataRole.UserRole, {"term": term.strip(), "category": "Other"})
                            self.blacklist_widget.addItem(item)
                            terms_added += 1
            
            elif isinstance(data, dict):
                # Check for our format with categories
                if "blacklist" in data and "blacklist_categories" in data:
                    for term in data["blacklist"]:
                        if isinstance(term, str) and term.strip():
                            # Check if term already exists
                            exists = False
                            for i in range(self.blacklist_widget.count()):
                                item = self.blacklist_widget.item(i)
                                item_data = item.data(Qt.ItemDataRole.UserRole)
                                if item_data and item_data["term"] == term.strip():
                                    exists = True
                                    break
                            
                            if not exists:
                                category = data["blacklist_categories"].get(term, "Other")
                                if category not in ["Gambling", "Contact Info", "Spam", "Other"]:
                                    category = "Other"
                                
                                display_text = f"{term.strip()} [{category}]"
                                item = QListWidgetItem(display_text)
                                item.setData(Qt.ItemDataRole.UserRole, {"term": term.strip(), "category": category})
                                self.blacklist_widget.addItem(item)
                                terms_added += 1
                else:
                    # Treat keys as terms and values as categories if possible
                    for term, value in data.items():
                        if isinstance(term, str) and term.strip():
                            # Check if term already exists
                            exists = False
                            for i in range(self.blacklist_widget.count()):
                                item = self.blacklist_widget.item(i)
                                item_data = item.data(Qt.ItemDataRole.UserRole)
                                if item_data and item_data["term"] == term.strip():
                                    exists = True
                                    break
                            
                            if not exists:
                                category = "Other"
                                if isinstance(value, str) and value in ["Gambling", "Contact Info", "Spam", "Other"]:
                                    category = value
                                
                                display_text = f"{term.strip()} [{category}]"
                                item = QListWidgetItem(display_text)
                                item.setData(Qt.ItemDataRole.UserRole, {"term": term.strip(), "category": category})
                                self.blacklist_widget.addItem(item)
                                terms_added += 1
            
            QMessageBox.information(self, "Import Complete", f"Successfully imported {terms_added} terms.")
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Error importing blacklist: {str(e)}")
    
    def export_blacklist(self):
        """Export blacklist terms to a JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Blacklist", "blacklist.json", "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Collect terms and categories
            blacklist = []
            blacklist_categories = {}
            
            for i in range(self.blacklist_widget.count()):
                item = self.blacklist_widget.item(i)
                item_data = item.data(Qt.ItemDataRole.UserRole)
                
                if item_data:
                    term = item_data["term"]
                    category = item_data["category"]
                    blacklist.append(term)
                    blacklist_categories[term] = category
                else:
                    # For backward compatibility
                    text = item.text()
                    if '[' in text and ']' in text:
                        term = text.split(' [')[0]
                        category = text.split('[')[1].split(']')[0]
                        blacklist.append(term)
                        blacklist_categories[term] = category
                    else:
                        blacklist.append(text)
                        blacklist_categories[text] = "Other"
            
            # Create export data
            export_data = {
                "blacklist": blacklist,
                "blacklist_categories": blacklist_categories
            }
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)
            
            QMessageBox.information(self, "Export Complete", f"Successfully exported {len(blacklist)} terms.")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting blacklist: {str(e)}")
    
    def import_whitelist(self):
        """Import whitelist terms from a JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Whitelist", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list) and not isinstance(data, dict):
                QMessageBox.warning(self, "Invalid Format", "The file does not contain a valid whitelist format.")
                return
            
            # Handle different import formats
            terms_added = 0
            
            if isinstance(data, list):
                # Simple list of terms
                for term in data:
                    if isinstance(term, str) and term.strip():
                        # Check if term already exists
                        exists = False
                        for i in range(self.whitelist_widget.count()):
                            if self.whitelist_widget.item(i).text() == term.strip():
                                exists = True
                                break
                        
                        if not exists:
                            self.whitelist_widget.addItem(term.strip())
                            terms_added += 1
            
            elif isinstance(data, dict) and "whitelist" in data:
                # Our format with whitelist key
                for term in data["whitelist"]:
                    if isinstance(term, str) and term.strip():
                        # Check if term already exists
                        exists = False
                        for i in range(self.whitelist_widget.count()):
                            if self.whitelist_widget.item(i).text() == term.strip():
                                exists = True
                                break
                        
                        if not exists:
                            self.whitelist_widget.addItem(term.strip())
                            terms_added += 1
            
            QMessageBox.information(self, "Import Complete", f"Successfully imported {terms_added} terms.")
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Error importing whitelist: {str(e)}")
    
    def export_whitelist(self):
        """Export whitelist terms to a JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Whitelist", "whitelist.json", "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Collect terms
            whitelist = []
            for i in range(self.whitelist_widget.count()):
                whitelist.append(self.whitelist_widget.item(i).text())
            
            # Create export data
            export_data = {"whitelist": whitelist}
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)
            
            QMessageBox.information(self, "Export Complete", f"Successfully exported {len(whitelist)} terms.")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting whitelist: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset settings to defaults"""
        confirm = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            success = self.config_manager.reset_to_defaults()
            if success:
                # Clear existing items
                self.blacklist_widget.clear()
                self.whitelist_widget.clear()
                
                # Reload settings
                self.load_settings()
                QMessageBox.information(self, "Reset Complete", "Settings have been reset to defaults.")
            else:
                QMessageBox.warning(self, "Reset Failed", "Failed to reset settings to defaults.")
