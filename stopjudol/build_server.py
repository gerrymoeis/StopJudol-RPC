#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Server Build Script
-------------------------------
This script builds the StopJudol server application into an executable using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

def build_executable(onefile=True, console=True, clean=False):
    """
    Build the StopJudol server application into an executable
    
    Args:
        onefile (bool): Whether to build as a single file or a directory
        console (bool): Whether to show console window (recommended for server)
        clean (bool): Whether to clean build directories before building
    """
    print("Building StopJudol Server executable...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Clean build directories if requested
    if clean:
        print("Cleaning build directories...")
        build_dir = os.path.join(current_dir, 'server', 'build')
        dist_dir = os.path.join(current_dir, 'server', 'dist')
        
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
    
    # Ensure .env file exists
    env_file = os.path.join(current_dir, '.env')
    if not os.path.exists(env_file):
        print("Warning: .env file not found. Creating a template .env file...")
        with open(env_file, 'w') as f:
            f.write("""# StopJudol Server Environment Variables

# API Authentication
API_USERNAME=admin
API_PASSWORD=password

# JWT Authentication
JWT_SECRET_KEY=StopJudol_Secret_Key_Change_This_In_Production
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=5000

# YouTube API
YOUTUBE_API_KEY=

# Logging
LOG_LEVEL=INFO
""")
    
    # Gunakan python dari venv untuk menjalankan PyInstaller
    venv_python = os.path.join(current_dir, 'venv', 'Scripts', 'python.exe')
    if not os.path.exists(venv_python):
        venv_python = os.path.join(current_dir, '..', 'venv', 'Scripts', 'python.exe')
        
    if not os.path.exists(venv_python):
        print(f"ERROR: Python tidak ditemukan di venv. Pastikan virtual environment sudah dibuat dengan benar.")
        sys.exit(1)
    
    # Build command menggunakan modul PyInstaller melalui Python
    cmd = [
        venv_python, 
        '-m', 'PyInstaller',
        '--name=StopJudol_Server',
        f'{"--onefile" if onefile else "--onedir"}',
        f'{"--console" if console else "--windowed"}',
        f'--icon={os.path.join(current_dir, "assets", "icons", "app_icon.ico")}',
        f'--add-data={os.path.join(current_dir, ".env")};.',
        f'--add-data={os.path.join(current_dir, "server", "config")};config',
        '--hidden-import=pkg_resources.py2_warn',
        '--hidden-import=jsonrpcserver',
        '--hidden-import=aiohttp',
        '--hidden-import=dotenv',
        '--hidden-import=jwt',
        '--hidden-import=google_auth_oauthlib',
        '--hidden-import=google.oauth2',
        os.path.join(current_dir, 'run_server.py')
    ]
    
    # Execute the command
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Build successful!")
        print(f"Executable created in {os.path.join(current_dir, 'dist')}")
        
        # Print stdout and stderr
        if result.stdout:
            print("\nOutput:")
            print(result.stdout)
    else:
        print("Build failed!")
        print("\nError:")
        print(result.stderr)
        
        if result.stdout:
            print("\nOutput:")
            print(result.stdout)
        
        sys.exit(1)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Build StopJudol Server executable')
    parser.add_argument('--dir', action='store_true', help='Build as directory instead of single file')
    parser.add_argument('--no-console', action='store_true', help='Hide console window (not recommended for server)')
    parser.add_argument('--clean', action='store_true', help='Clean build directories before building')
    
    args = parser.parse_args()
    
    build_executable(
        onefile=not args.dir,
        console=not args.no_console,
        clean=args.clean
    )

if __name__ == '__main__':
    main()
