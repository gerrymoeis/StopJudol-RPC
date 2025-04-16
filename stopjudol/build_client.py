#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Client Build Script
-------------------------------
This script builds the StopJudol client application into an executable using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

def build_executable(onefile=True, console=False, clean=False):
    """
    Build the StopJudol client application into an executable
    
    Args:
        onefile (bool): Whether to build as a single file or a directory
        console (bool): Whether to show console window
        clean (bool): Whether to clean build directories before building
    """
    print("Building StopJudol Client executable...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Clean build directories if requested
    if clean:
        print("Cleaning build directories...")
        build_dir = os.path.join(current_dir, 'client', 'build')
        dist_dir = os.path.join(current_dir, 'client', 'dist')
        
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
    
    # Create config directory if it doesn't exist
    config_dir = os.path.join(current_dir, 'client', 'config')
    os.makedirs(config_dir, exist_ok=True)
    
    # Ensure client_secret.json exists in config
    client_secret_src = os.path.join(current_dir, 'server', 'config', 'client_secret.json')
    client_secret_dst = os.path.join(config_dir, 'client_secret.json')
    if os.path.exists(client_secret_src) and not os.path.exists(client_secret_dst):
        shutil.copy(client_secret_src, client_secret_dst)
    
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
        '--name=StopJudol_Client',
        f'{"--onefile" if onefile else "--onedir"}',
        f'{"--console" if console else "--windowed"}',
        f'--icon={os.path.join(current_dir, "assets", "icons", "app_icon.ico")}',
        f'--add-data={os.path.join(config_dir)};config',
        '--hidden-import=pkg_resources.py2_warn',
        '--hidden-import=PyQt6',
        '--hidden-import=jsonrpcclient',
        '--hidden-import=google_auth_oauthlib',
        '--hidden-import=google.oauth2',
        os.path.join(current_dir, 'run_client.py')
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
    parser = argparse.ArgumentParser(description='Build StopJudol Client executable')
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
