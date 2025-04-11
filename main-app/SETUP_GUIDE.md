# StopJudol - Setup Guide

## Prerequisites

Before using StopJudol, you need to set up the following:

1. Python 3.8 or higher
2. Required Python packages (listed in requirements.txt)
3. Google/YouTube API credentials

## Installation

### 1. Install Required Packages

Install the required packages using pip:

```bash
pip install -r requirements.txt
```

### 2. Set Up Google API Credentials

To use StopJudol, you need to create a Google Cloud project and enable the YouTube Data API v3:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the YouTube Data API v3 for your project
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" as the application type
   - Enter a name for your OAuth client (e.g., "StopJudol")
   - Click "Create"
5. Download the client secret JSON file
6. Rename the downloaded file to `client_secret.json` and place it in the `config` directory

### 3. Configure the Application

1. Review the default settings in `config/default_settings.json`
2. Customize the blacklist and whitelist as needed

## Running the Application

### Development Mode

To run the application in development mode:

```bash
python main.py
```

### Building the Executable

To build a standalone executable:

```bash
python build.py --clean
```

This will create a single-file executable in the `dist` directory.

Options:
- `--dir`: Build as a directory instead of a single file
- `--console`: Show console window (for debugging)
- `--clean`: Clean build directories before building

## First-Time Use

1. Launch the application
2. Click "Login with YouTube" to authenticate with your Google account
3. Enter a YouTube video URL and click "Scan Comments"
4. Review and delete flagged comments as needed

## Troubleshooting

### Authentication Issues

- Ensure your `client_secret.json` file is correctly placed in the `config` directory
- Check that you've enabled the YouTube Data API v3 in your Google Cloud project
- Verify that your OAuth 2.0 credentials are configured for a desktop application

### API Quota Issues

The YouTube Data API has quota limits. If you encounter quota errors:

1. Check your quota usage in the Google Cloud Console
2. Consider creating a new project if you've exceeded your quota
3. Optimize your usage by scanning fewer comments at a time

### Application Errors

Check the logs in `%APPDATA%\Local\StopJudol\logs\` for detailed error information.

## Development Notes

### Project Structure

The application follows the structure outlined in the context document:

- `main.py`: Entry point
- `src/app.py`: Main window class
- `src/core/`: Core functionality (YouTube API, analysis, config)
- `src/auth/`: Authentication handling
- `src/utils/`: Utility functions
- `config/`: Configuration files
- `assets/`: Application assets
- `tests/`: Unit tests

### Running Tests

To run the unit tests:

```bash
python -m unittest discover tests
```

Or with pytest:

```bash
pytest tests/
```
