#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Build Script
------------------------
This script builds the StopJudol application into a standalone executable using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """Main build function"""
    print("Starting StopJudol build process...")
    
    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    icon_path = os.path.join(base_dir, 'assets', 'icons', 'app_icon.ico')
    config_dir = os.path.join(base_dir, 'config')
    assets_dir = os.path.join(base_dir, 'assets')
    main_script = os.path.join(base_dir, 'main.py')
    
    # Ensure icon exists
    if not os.path.exists(icon_path):
        print(f"Error: Icon file not found at {icon_path}")
        return False
    
    # Create dist and build directories if they don't exist
    dist_dir = os.path.join(base_dir, 'dist')
    build_dir = os.path.join(base_dir, 'build')
    
    os.makedirs(dist_dir, exist_ok=True)
    os.makedirs(build_dir, exist_ok=True)
    
    # Build command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=StopJudol',
        '--onefile',
        '--windowed',
        f'--icon={icon_path}',
        '--clean',
        f'--add-data={config_dir}{os.pathsep}config',
        f'--add-data={assets_dir}{os.pathsep}assets',
        '--hidden-import=google.auth.transport.requests',
        '--hidden-import=keyring.backends.Windows',
        '--hidden-import=src',
        '--hidden-import=src.core',
        '--hidden-import=src.auth',
        '--hidden-import=src.utils',
        '--hidden-import=src.core.youtube_api',
        '--hidden-import=src.core.analysis',
        '--hidden-import=src.core.config_manager',
        '--hidden-import=src.auth.oauth_handler',
        '--hidden-import=src.utils.logger_config',
        main_script
    ]
    
    # Run PyInstaller
    print("Running PyInstaller with the following command:")
    print(" ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild completed successfully!")
        print(f"Executable created at: {os.path.join(dist_dir, 'StopJudol.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
