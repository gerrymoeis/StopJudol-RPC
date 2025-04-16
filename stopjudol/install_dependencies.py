#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StopJudol - Dependency Installer
-------------------------------
This script installs all required dependencies for both client and server components.
"""

import os
import sys
import subprocess
import platform

def print_section(title):
    """Print a section title with formatting"""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50, "="))
    print("=" * 50 + "\n")

def run_pip_install(requirements_file, venv=None):
    """Run pip install with the specified requirements file"""
    print(f"Installing dependencies from {requirements_file}...")
    
    # Determine pip command based on platform and venv
    if platform.system() == "Windows":
        pip_cmd = "pip"
    else:
        pip_cmd = "pip3"
    
    # Build the command
    cmd = [pip_cmd, "install", "-r", requirements_file]
    
    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def main():
    """Main function to install dependencies"""
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Print welcome message
    print_section("StopJudol Dependency Installer")
    print("This script will install all required dependencies for StopJudol.")
    print("Make sure you have pip installed and properly configured.")
    
    # Install client dependencies
    print_section("Installing Client Dependencies")
    client_req = os.path.join(script_dir, "client", "requirements.txt")
    if not os.path.exists(client_req):
        print(f"❌ Client requirements file not found at {client_req}")
        return False
    
    client_success = run_pip_install(client_req)
    
    # Install server dependencies
    print_section("Installing Server Dependencies")
    server_req = os.path.join(script_dir, "server", "requirements.txt")
    if not os.path.exists(server_req):
        print(f"❌ Server requirements file not found at {server_req}")
        return False
    
    server_success = run_pip_install(server_req)
    
    # Print summary
    print_section("Installation Summary")
    if client_success and server_success:
        print("✅ All dependencies installed successfully!")
        print("\nYou can now run the StopJudol application:")
        print("1. Start the server: python -m server.main")
        print("2. Start the client: python -m client.main")
    else:
        print("❌ Some dependencies could not be installed.")
        print("Please check the error messages above and try again.")
    
    return client_success and server_success

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
