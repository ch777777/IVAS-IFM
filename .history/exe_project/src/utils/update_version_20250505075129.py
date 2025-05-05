#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Version updater utility.

Updates the version number in the configuration files.
"""

import os
import re
import sys
import argparse
from pathlib import Path

# Add the src directory to the path so we can import modules
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir.parent.parent))


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Update version number in configuration files')
    parser.add_argument('--version', required=True, help='New version number (e.g. 1.2.0)')
    return parser.parse_args()


def update_version(version):
    """
    Update the version number in the configuration files.
    
    Args:
        version: New version number
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Path to settings.py
        settings_file = current_dir.parent / 'config' / 'settings.py'
        
        if not settings_file.exists():
            print(f"Error: Settings file not found at {settings_file}")
            return False
        
        # Read the file content
        with open(settings_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Update the version number
        pattern = r'"app_version":\s*"[^"]*"'
        replacement = f'"app_version": "{version}"'
        new_content = re.sub(pattern, replacement, content)
        
        # Update the release date
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        pattern = r'"app_release_date":\s*"[^"]*"'
        replacement = f'"app_release_date": "{today}"'
        new_content = re.sub(pattern, replacement, new_content)
        
        # Write the updated content back to the file
        with open(settings_file, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print(f"Version updated to {version} and release date to {today}")
        return True
    
    except Exception as e:
        print(f"Error updating version: {e}")
        return False


def main():
    """Main entry point."""
    args = parse_args()
    success = update_version(args.version)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 
 
 