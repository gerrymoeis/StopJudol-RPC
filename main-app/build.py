#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Build Script
------------------------
This script builds the StopJudol application into an executable using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

def build_executable(onefile=True, console=False, clean=False):
    """
    Build the StopJudol application into an executable
    
    Args:
        onefile (bool): Whether to build as a single file or a directory
        console (bool): Whether to show console window
        clean (bool): Whether to clean build directories before building
    """
    print("Building StopJudol executable...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Clean build directories if requested
    if clean:
        print("Cleaning build directories...")
        build_dir = os.path.join(current_dir, 'build')
        dist_dir = os.path.join(current_dir, 'dist')
        
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
    
    # Build command
    cmd = [
        'pyinstaller',
        '--name=StopJudol',
        f'{"--onefile" if onefile else "--onedir"}',
        f'{"--console" if console else "--windowed"}',
        f'--icon={os.path.join(current_dir, "assets", "icons", "app_icon.ico")}',
        f'--add-data={os.path.join(current_dir, "config", "default_settings.json")};config',
        f'--add-data={os.path.join(current_dir, "assets")};assets',
        '--hidden-import=pkg_resources.py2_warn',
        os.path.join(current_dir, 'main.py')
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
    parser = argparse.ArgumentParser(description='Build StopJudol executable')
    parser.add_argument('--dir', action='store_true', help='Build as directory instead of single file')
    parser.add_argument('--console', action='store_true', help='Show console window')
    parser.add_argument('--clean', action='store_true', help='Clean build directories before building')
    
    args = parser.parse_args()
    
    build_executable(
        onefile=not args.dir,
        console=args.console,
        clean=args.clean
    )

if __name__ == '__main__':
    main()
