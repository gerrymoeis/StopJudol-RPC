# StopJudol - User Guide

## Introduction

StopJudol is a desktop application designed to help YouTube content creators automatically identify and remove spam comments, online gambling ads (judol), and other illegal content from their videos. This guide will walk you through the setup and usage of the application.

## Getting Started

### Installation

1. Download the StopJudol application for Windows
2. Run the installer or extract the ZIP file to your preferred location
3. Launch the application by double-clicking on `StopJudol.exe`

### First-Time Setup

Before you can use StopJudol, you need to authenticate with your YouTube account:

1. When you first run the application, click the "Login with YouTube" button
2. A browser window will open asking you to authorize StopJudol to access your YouTube account
3. Sign in with your Google account and grant the requested permissions
4. Once authenticated, the application will display your channel name

## Using StopJudol

### Scanning Comments

1. Enter a YouTube video URL in the input field (e.g., `https://www.youtube.com/watch?v=VIDEO_ID`)
2. Click the "Scan Comments" button
3. The application will fetch and analyze comments from the video
4. A progress bar will show the scanning progress

### Reviewing Flagged Comments

After scanning, the application will display a table of flagged comments:

- Each row represents a comment that was identified as potential spam or gambling content
- The table shows the author name, comment text, and the reason it was flagged
- All comments are selected by default for deletion

### Managing Comments

You can:

- Use the "Select All" button to select all comments
- Use the "Deselect All" button to deselect all comments
- Manually check/uncheck individual comments using the checkboxes

### Deleting Comments

1. Ensure the comments you want to delete are selected
2. Click the "Delete Selected" button
3. Confirm the deletion when prompted
4. The application will delete the selected comments and show a progress bar
5. Once complete, the deleted comments will be removed from the table

## Customizing Settings

StopJudol uses a configuration file with blacklisted and whitelisted terms. The default configuration includes common spam and gambling terms, but you can customize it:

1. The configuration file is located at: `%APPDATA%\Local\StopJudol\settings.json`
2. You can edit this file to add or remove terms from the blacklist and whitelist
3. Changes will take effect the next time you scan comments

## Troubleshooting

### Authentication Issues

- If you encounter authentication errors, try logging out and logging back in
- Ensure you have a stable internet connection
- Make sure you're granting all the required permissions

### Comment Scanning Issues

- Verify that the video URL is correct
- Ensure the video has public comments enabled
- Check that you have permission to moderate comments on the video

### Deletion Issues

- Confirm that you're authenticated with an account that has permission to delete comments
- Some comments may fail to delete if they've already been removed or if you don't have permission

## Logging Out

To log out of your YouTube account:

1. Click the "Logout" button in the authentication section
2. Your credentials will be removed from the system
3. You'll need to authenticate again to use the application

## Getting Help

If you encounter any issues not covered in this guide, please check the logs located at:
`%APPDATA%\Local\StopJudol\logs\`

These logs can provide detailed information about any errors that occur during the use of the application.
