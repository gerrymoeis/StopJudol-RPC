#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Test Analysis Module
--------------------------------
Unit tests for the comment analysis module.
"""

import unittest
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.analysis import CommentAnalyzer
from src.core.config_manager import ConfigManager

class MockConfigManager:
    """Mock ConfigManager for testing"""
    
    def __init__(self, blacklist=None, whitelist=None):
        self.blacklist = blacklist or [
            "judi online", "slot online", "togel", "casino online",
            "whatsapp", "telegram", "hubungi", "kontak"
        ]
        self.whitelist = whitelist or [
            "game review", "tutorial", "educational"
        ]
    
    def get_blacklist(self):
        return self.blacklist
    
    def get_whitelist(self):
        return self.whitelist

class TestCommentAnalysis(unittest.TestCase):
    """Test cases for CommentAnalyzer"""
    
    def setUp(self):
        """Set up test environment"""
        self.config_manager = MockConfigManager()
        self.analyzer = CommentAnalyzer(self.config_manager)
        
    def test_load_methods(self):
        """Test the modular loading methods"""
        # Test load_blacklist
        original_blacklist = self.analyzer.blacklist.copy()
        self.analyzer.blacklist = []
        self.analyzer.load_blacklist()
        self.assertEqual(self.analyzer.blacklist, original_blacklist)
        
        # Test load_whitelist
        original_whitelist = self.analyzer.whitelist.copy()
        self.analyzer.whitelist = []
        self.analyzer.load_whitelist()
        self.assertEqual(self.analyzer.whitelist, original_whitelist)
        
        # Test load_patterns
        self.analyzer.patterns = {}
        self.analyzer.load_patterns()
        self.assertIn('phone_number', self.analyzer.patterns)
        self.assertIn('whatsapp', self.analyzer.patterns)
        
        # Test load_gambling_indicators
        self.analyzer.gambling_indicators = []
        self.analyzer.load_gambling_indicators()
        self.assertGreater(len(self.analyzer.gambling_indicators), 0)
        self.assertIn('judi', self.analyzer.gambling_indicators)
        self.assertIn('slot', self.analyzer.gambling_indicators)
    
    def test_is_normalized_different(self):
        """Test detection of obfuscated characters"""
        # Test normal text
        normal_text = "This is normal text"
        self.assertFalse(self.analyzer.is_normalized_different(normal_text))
        
        # Test text with special characters that would normalize differently
        special_text = "Ｔｈｉｓ　ｉｓ　ｗｉｄｅ　ｔｅｘｔ"
        self.assertTrue(self.analyzer.is_normalized_different(special_text))
    
    def test_normalize_text(self):
        """Test text normalization"""
        # Test HTML entity removal
        html_text = "This &amp; that &lt;b&gt;bold&lt;/b&gt;"
        normalized = self.analyzer.normalize_text(html_text)
        self.assertEqual(normalized, "this & that bold")
        
        # Test obfuscation handling
        obfuscated = "W4@t5App 08123456789"
        normalized = self.analyzer.normalize_text(obfuscated)
        self.assertEqual(normalized, "waatsapp o8123456789")
    
    def test_blacklist_detection(self):
        """Test blacklisted term detection"""
        # Test direct match
        is_flagged, reason = self.analyzer.analyze("Kunjungi situs judi online terpercaya")
        self.assertTrue(is_flagged)
        self.assertIn("judi online", reason.lower())
        
        # Test obfuscated match
        is_flagged, reason = self.analyzer.analyze("Kunjungi situs jud1 0nline terpercaya")
        self.assertTrue(is_flagged)
        self.assertIn("judi online", reason.lower())
        
        # Test clean comment
        is_flagged, reason = self.analyzer.analyze("Great video, really enjoyed the content!")
        self.assertFalse(is_flagged)
    
    def test_whitelist_override(self):
        """Test whitelist overriding blacklist"""
        # Comment with both blacklisted and whitelisted terms
        is_flagged, reason = self.analyzer.analyze("Ini tutorial game slot yang bagus")
        self.assertFalse(is_flagged)
        
        # Comment with only blacklisted term
        is_flagged, reason = self.analyzer.analyze("Main slot online yuk")
        self.assertTrue(is_flagged)
    
    def test_pattern_detection(self):
        """Test pattern detection"""
        # Test phone number pattern
        is_flagged, reason = self.analyzer.analyze("Hubungi saya di 081234567890")
        self.assertTrue(is_flagged)
        self.assertIn("phone_number", reason.lower())
        
        # Test WhatsApp pattern
        is_flagged, reason = self.analyzer.analyze("WA: 081234567890")
        self.assertTrue(is_flagged)
        self.assertIn("whatsapp", reason.lower())
        
        # Test Telegram pattern
        is_flagged, reason = self.analyzer.analyze("Telegram: @username")
        self.assertTrue(is_flagged)
        self.assertIn("telegram", reason.lower())
        
        # Test URL pattern
        is_flagged, reason = self.analyzer.analyze("Kunjungi https://example.com/judi")
        self.assertTrue(is_flagged)
        self.assertIn("url", reason.lower())
    
    def test_gambling_indicators(self):
        """Test gambling indicator detection"""
        # Test multiple gambling indicators
        is_flagged, reason = self.analyzer.analyze("Slot gacor maxwin dijamin jackpot terbesar")
        self.assertTrue(is_flagged)
        self.assertIn("gambling indicators", reason.lower())
        
        # Test single gambling indicator (should not flag)
        is_flagged, reason = self.analyzer.analyze("Jackpot dalam game ini susah didapat")
        self.assertFalse(is_flagged)
    
    def test_long_comment_with_numbers(self):
        """Test long comment with numbers detection"""
        # Create a very long comment with numbers
        long_comment = "This is a very long comment " * 50 + " with numbers 123456789"
        is_flagged, reason = self.analyzer.analyze(long_comment)
        self.assertTrue(is_flagged)
        self.assertIn("long comment", reason.lower())
        
    def test_reload_methods(self):
        """Test the reload methods"""
        # Test reload_blacklist
        original_blacklist = self.analyzer.blacklist.copy()
        self.analyzer.blacklist = []
        self.analyzer.reload_blacklist()
        self.assertEqual(self.analyzer.blacklist, original_blacklist)
        
        # Test reload_whitelist
        original_whitelist = self.analyzer.whitelist.copy()
        self.analyzer.whitelist = []
        self.analyzer.reload_whitelist()
        self.assertEqual(self.analyzer.whitelist, original_whitelist)
        
        # Test reload_config
        self.analyzer.blacklist = []
        self.analyzer.whitelist = []
        self.analyzer.gambling_indicators = []
        self.analyzer.reload_config()
        self.assertEqual(len(self.analyzer.blacklist), len(original_blacklist))
        self.assertEqual(len(self.analyzer.whitelist), len(original_whitelist))
        self.assertGreater(len(self.analyzer.gambling_indicators), 0)

if __name__ == '__main__':
    unittest.main()
