#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Test YouTube API Module (Mocked)
--------------------------------------------
Unit tests for the YouTube API wrapper using mocked responses.
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch, call

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the googleapiclient module
sys.modules['googleapiclient'] = MagicMock()
sys.modules['googleapiclient.discovery'] = MagicMock()
sys.modules['googleapiclient.errors'] = MagicMock()

# Create a mock HttpError class
class MockHttpError(Exception):
    def __init__(self, resp, content):
        self.resp = resp
        self.content = content
        super().__init__(f"{resp.status} {resp.reason}: {content}")

# Assign the mock class to the mocked module
sys.modules['googleapiclient.errors'].HttpError = MockHttpError

# Now import the module that uses googleapiclient
from src.core.youtube_api import YouTubeAPI

class TestYouTubeAPI(unittest.TestCase):
    """Test cases for YouTubeAPI with mocked responses"""
    
    def setUp(self):
        """Set up test environment with mocked credentials"""
        self.mock_credentials = MagicMock()
        
        # Create a patch for the build function
        self.build_patch = patch('src.core.youtube_api.build')
        self.mock_build = self.build_patch.start()
        
        # Create a mock YouTube API client
        self.mock_youtube = MagicMock()
        self.mock_build.return_value = self.mock_youtube
        
        # Initialize the API with mock credentials
        self.api = YouTubeAPI(self.mock_credentials)
    
    def tearDown(self):
        """Clean up after tests"""
        self.build_patch.stop()
    
    def test_extract_video_id(self):
        """Test video ID extraction from different URL formats"""
        # Standard YouTube URL
        video_id = self.api.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(video_id, "dQw4w9WgXcQ")
        
        # Short YouTube URL
        video_id = self.api.extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        self.assertEqual(video_id, "dQw4w9WgXcQ")
        
        # URL with additional parameters
        video_id = self.api.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s")
        self.assertEqual(video_id, "dQw4w9WgXcQ")
        
        # Invalid URL
        video_id = self.api.extract_video_id("https://example.com")
        self.assertIsNone(video_id)
        
        # Invalid video ID format
        video_id = self.api.extract_video_id("https://www.youtube.com/watch?v=invalid")
        self.assertIsNone(video_id)
    
    def test_get_channel_name(self):
        """Test getting channel name"""
        # Mock the channels().list().execute() response
        channels_list = MagicMock()
        self.mock_youtube.channels.return_value.list.return_value = channels_list
        
        # Set up the mock response
        mock_response = {
            'items': [
                {
                    'snippet': {
                        'title': 'Test Channel'
                    }
                }
            ]
        }
        channels_list.execute.return_value = mock_response
        
        # Call the method
        channel_name = self.api.get_channel_name()
        
        # Verify the result
        self.assertEqual(channel_name, 'Test Channel')
        
        # Verify the API was called correctly
        self.mock_youtube.channels.return_value.list.assert_called_with(
            part='snippet',
            mine=True
        )
    
    def test_get_comments(self):
        """Test getting comments"""
        # Mock the commentThreads().list().execute() response
        comment_threads_list = MagicMock()
        self.mock_youtube.commentThreads.return_value.list.return_value = comment_threads_list
        
        # Set up the mock response
        mock_response = {
            'items': [
                {
                    'id': 'comment1',
                    'snippet': {
                        'topLevelComment': {
                            'id': 'comment1',
                            'snippet': {
                                'textDisplay': 'Test comment 1',
                                'authorDisplayName': 'User 1'
                            }
                        }
                    }
                },
                {
                    'id': 'comment2',
                    'snippet': {
                        'topLevelComment': {
                            'id': 'comment2',
                            'snippet': {
                                'textDisplay': 'Test comment 2',
                                'authorDisplayName': 'User 2'
                            }
                        }
                    }
                }
            ],
            'nextPageToken': 'token123'
        }
        comment_threads_list.execute.return_value = mock_response
        
        # Call the method
        response = self.api.get_comments('video123')
        
        # Verify the result
        self.assertEqual(len(response['items']), 2)
        self.assertEqual(response['nextPageToken'], 'token123')
        
        # Verify the API was called correctly
        self.mock_youtube.commentThreads.return_value.list.assert_called_with(
            part='snippet',
            videoId='video123',
            maxResults=100,
            pageToken=None,
            textFormat='html'
        )
    
    def test_delete_comment(self):
        """Test deleting a comment"""
        # Mock the comments().delete().execute() response
        comments_delete = MagicMock()
        self.mock_youtube.comments.return_value.delete.return_value = comments_delete
        
        # Set up the mock response (delete returns empty response on success)
        comments_delete.execute.return_value = {}
        
        # Call the method
        result = self.api.delete_comment('comment123')
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the API was called correctly
        self.mock_youtube.comments.return_value.delete.assert_called_with(
            id='comment123'
        )
    
    def test_delete_comment_error(self):
        """Test error handling when deleting a comment"""
        # Mock the comments().delete().execute() to raise an exception
        comments_delete = MagicMock()
        self.mock_youtube.comments.return_value.delete.return_value = comments_delete
        
        mock_response = MagicMock()
        mock_response.status = 403
        mock_response.reason = 'Forbidden'
        
        # Set up the mock to raise an exception
        comments_delete.execute.side_effect = MockHttpError(mock_response, b'Permission denied')
        
        # Call the method
        result = self.api.delete_comment('comment123')
        
        # Verify the result
        self.assertFalse(result)

    def test_get_all_comments(self):
        """Test getting all comments with pagination"""
        # Mock the get_comments method
        self.api.get_comments = MagicMock()
        
        # Set up mock responses for two pages
        first_page = {
            'items': [
                {'id': 'comment1'},
                {'id': 'comment2'}
            ],
            'nextPageToken': 'token123'
        }
        
        second_page = {
            'items': [
                {'id': 'comment3'},
                {'id': 'comment4'}
            ]
            # No nextPageToken means this is the last page
        }
        
        # Configure the mock to return different responses on consecutive calls
        self.api.get_comments.side_effect = [first_page, second_page]
        
        # Call the method
        all_comments = self.api.get_all_comments('video123')
        
        # Verify the results
        self.assertEqual(len(all_comments), 4)
        self.assertEqual(all_comments[0]['id'], 'comment1')
        self.assertEqual(all_comments[3]['id'], 'comment4')
        
        # Verify get_comments was called correctly
        expected_calls = [
            call('video123', None, 100),
            call('video123', 'token123', 100)
        ]
        self.api.get_comments.assert_has_calls(expected_calls)
    
    def test_get_video_info(self):
        """Test getting video information"""
        # Mock the videos().list().execute() response
        videos_list = MagicMock()
        self.mock_youtube.videos.return_value.list.return_value = videos_list
        
        # Set up the mock response
        mock_response = {
            'items': [
                {
                    'id': 'video123',
                    'snippet': {
                        'title': 'Test Video',
                        'channelTitle': 'Test Channel'
                    },
                    'statistics': {
                        'viewCount': '1000',
                        'likeCount': '100',
                        'commentCount': '50'
                    }
                }
            ]
        }
        videos_list.execute.return_value = mock_response
        
        # Call the method
        video_info = self.api.get_video_info('video123')
        
        # Verify the result
        self.assertEqual(video_info['id'], 'video123')
        self.assertEqual(video_info['snippet']['title'], 'Test Video')
        self.assertEqual(video_info['statistics']['commentCount'], '50')
        
        # Verify the API was called correctly
        self.mock_youtube.videos.return_value.list.assert_called_with(
            part='snippet,statistics',
            id='video123'
        )
    
    def test_get_video_info_not_found(self):
        """Test getting info for a non-existent video"""
        # Mock the videos().list().execute() response
        videos_list = MagicMock()
        self.mock_youtube.videos.return_value.list.return_value = videos_list
        
        # Set up the mock response with no items
        mock_response = {'items': []}
        videos_list.execute.return_value = mock_response
        
        # Call the method
        video_info = self.api.get_video_info('nonexistent')
        
        # Verify the result
        self.assertIsNone(video_info)
    
    def test_check_api_quota_available(self):
        """Test checking API quota when it's available"""
        # Mock the channels().list().execute() response
        channels_list = MagicMock()
        self.mock_youtube.channels.return_value.list.return_value = channels_list
        
        # Set up the mock response (any successful response)
        channels_list.execute.return_value = {'items': []}
        
        # Call the method
        result = self.api.check_api_quota()
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the API was called correctly
        self.mock_youtube.channels.return_value.list.assert_called_with(
            part='id',
            mine=True,
            maxResults=1
        )
    
    def test_check_api_quota_exceeded(self):
        """Test checking API quota when it's exceeded"""
        # Mock the channels().list().execute() to raise a quota exceeded error
        channels_list = MagicMock()
        self.mock_youtube.channels.return_value.list.return_value = channels_list
        
        mock_response = MagicMock()
        mock_response.status = 403
        mock_response.reason = 'Forbidden'
        
        # Set up the mock to raise a quota exceeded exception
        channels_list.execute.side_effect = MockHttpError(mock_response, b'quotaExceeded')
        
        # Call the method
        result = self.api.check_api_quota()
        
        # Verify the result
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
