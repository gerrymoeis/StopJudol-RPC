#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Worker Threads
-------------------------
This module provides worker threads for background operations.
"""

import logging
import traceback
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

class Worker(QObject):
    """Base worker class for background operations"""
    
    # Signals
    finished = pyqtSignal(object)  # Result of the operation
    error = pyqtSignal(object)     # Error that occurred
    progress = pyqtSignal(int, int)  # Current progress, total
    
    def __init__(self):
        """Initialize the worker"""
        super().__init__()
        self.logger = logging.getLogger("Worker")
        self.is_running = False
    
    @pyqtSlot()
    def run(self):
        """Run the worker (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement run()")
    
    def stop(self):
        """Stop the worker"""
        self.is_running = False

class FetchCommentsWorker(Worker):
    """Worker for fetching comments"""
    
    def __init__(self, rpc_client, video_id, credentials_json=None):
        """
        Initialize the worker
        
        Args:
            rpc_client: RPC client
            video_id (str): YouTube video ID
            credentials_json (str, optional): OAuth credentials as JSON string
        """
        super().__init__()
        self.rpc_client = rpc_client
        self.video_id = video_id
        self.credentials_json = credentials_json
    
    @pyqtSlot()
    def run(self):
        """Run the worker"""
        try:
            self.is_running = True
            
            # Fetch comments
            success, result = self.rpc_client.fetch_comments(
                self.video_id, 
                self.credentials_json
            )
            
            if not success:
                self.error.emit(result)
                return
            
            # Analyze comments
            success, analyzed_result = self.rpc_client.analyze_comments(result)
            
            if not success:
                self.error.emit(analyzed_result)
                return
            
            # Emit result
            self.finished.emit(analyzed_result)
        except Exception as e:
            self.logger.error(f"Error fetching comments: {e}")
            self.logger.error(traceback.format_exc())
            self.error.emit(str(e))
        finally:
            self.is_running = False

class DeleteCommentsWorker(Worker):
    """Worker for deleting comments"""
    
    def __init__(self, rpc_client, comments, credentials_json=None):
        """
        Initialize the worker
        
        Args:
            rpc_client: RPC client
            comments (list): List of comments to delete
            credentials_json (str, optional): OAuth credentials as JSON string
        """
        super().__init__()
        self.rpc_client = rpc_client
        self.comments = comments
        self.credentials_json = credentials_json
        self.results = []
    
    @pyqtSlot()
    def run(self):
        """Run the worker"""
        try:
            self.is_running = True
            total = len(self.comments)
            
            for i, comment in enumerate(self.comments):
                if not self.is_running:
                    break
                
                # Get comment ID and thread ID
                # This is critical - we need both the comment ID and thread ID
                # The comment ID is used for direct deletion
                # The thread ID is used for moderation (marking as spam)
                comment_id = comment['snippet']['topLevelComment']['id']
                thread_id = comment['id']
                
                # Update progress
                self.progress.emit(i + 1, total)
                
                # Delete comment
                success, result = self.rpc_client.delete_comment(
                    comment_id, 
                    thread_id, 
                    self.credentials_json
                )
                
                # Store result
                self.results.append({
                    'comment': comment,
                    'success': success,
                    'result': result
                })
            
            # Emit results
            self.finished.emit(self.results)
        except Exception as e:
            self.logger.error(f"Error deleting comments: {e}")
            self.logger.error(traceback.format_exc())
            self.error.emit(str(e))
        finally:
            self.is_running = False

def run_in_thread(worker):
    """
    Run a worker in a thread
    
    Args:
        worker: Worker to run
        
    Returns:
        QThread: Thread object
    """
    thread = QThread()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    thread.finished.connect(thread.deleteLater)
    thread.start()
    return thread
