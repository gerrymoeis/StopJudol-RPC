#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Comment Schemas
--------------------------
This module provides Marshmallow schemas for validating comment data.
"""

from marshmallow import Schema, fields, validate

class CommentSnippetSchema(Schema):
    """Schema for comment snippet data"""
    authorDisplayName = fields.Str(required=True)
    authorProfileImageUrl = fields.Str()
    authorChannelUrl = fields.Str()
    authorChannelId = fields.Dict(keys=fields.Str(), values=fields.Str())
    textDisplay = fields.Str(required=True)
    textOriginal = fields.Str()
    likeCount = fields.Int()
    publishedAt = fields.Str()
    updatedAt = fields.Str()

class TopLevelCommentSchema(Schema):
    """Schema for top level comment data"""
    id = fields.Str(required=True)
    snippet = fields.Nested(CommentSnippetSchema, required=True)

class CommentThreadSnippetSchema(Schema):
    """Schema for comment thread snippet data"""
    videoId = fields.Str(required=True)
    topLevelComment = fields.Nested(TopLevelCommentSchema, required=True)
    canReply = fields.Bool()
    totalReplyCount = fields.Int()
    isPublic = fields.Bool()

class CommentThreadSchema(Schema):
    """Schema for comment thread data"""
    id = fields.Str(required=True)
    snippet = fields.Nested(CommentThreadSnippetSchema, required=True)

class AnalysisResultSchema(Schema):
    """Schema for comment analysis result"""
    is_flagged = fields.Bool(required=True)
    reason = fields.Str(allow_none=True)

class FlaggedCommentSchema(Schema):
    """Schema for flagged comment data"""
    id = fields.Str(required=True)
    snippet = fields.Nested(CommentThreadSnippetSchema, required=True)
    analysis_result = fields.Nested(AnalysisResultSchema, required=True)

class DeleteCommentResultSchema(Schema):
    """Schema for delete comment result"""
    action_type = fields.Str(required=True, validate=validate.OneOf(['deleted', 'marked_as_spam', 'none']))
    success = fields.Bool(required=True)
    message = fields.Str(allow_none=True)
