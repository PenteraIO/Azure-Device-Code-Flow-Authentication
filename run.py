#!/usr/bin/env python3
"""
Azure AD Token Utility Launcher
Choose between CLI and Web UI versions.
"""

import sys
import os
import subprocess

def main():
    print("🚀 Azure AD Token Utility Launcher")
    print("=" * 40)
    print("1. CLI Version (Interactive terminal)")
    print("2. Web UI Version (Browser interface)")
    print("3. Exit")
    print("=" * 40)
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            print("\nStarting CLI version...")
            try:
                subprocess.run([sys.executable, 'cli.py'], check=True)
            except KeyboardInterrupt:
                print("\n\nExiting CLI version.")
            except Exception as e:
                print(f"Error running CLI version: {e}")
            break
            
        elif choice == '2':
            print("\nStarting Web UI version...")
            print("The web interface will open at: http://localhost:5001")
            print("Press Ctrl+C to stop the web server.")
            try:
                subprocess.run([sys.executable, 'web_app.py'], check=True)
            except KeyboardInterrupt:
                print("\n\nStopping web server.")
            except Exception as e:
                print(f"Error running Web UI version: {e}")
            break
            
        elif choice == '3':
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main() 