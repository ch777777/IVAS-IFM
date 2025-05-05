#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
IVAS-IFM (Intelligent Video Acquisition System - Intelligent File Management)
Main entry point for the application.

This module initializes the application and manages the execution context.
"""

import os
import sys
import logging
from pathlib import Path

# Add the src directory to the path so we can import modules
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from components.app import App
from config.settings import APP_CONFIG


def setup_logging():
    """Configure the logging system."""
    log_level = getattr(logging, APP_CONFIG['logging']['level'])
    log_format = APP_CONFIG['logging']['format']
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(APP_CONFIG['logging']['file'], encoding='utf-8')
        ]
    )
    
    return logging.getLogger(__name__)


def main():
    """Main entry point for the application."""
    logger = setup_logging()
    logger.info("Starting IVAS-IFM application...")
    
    try:
        app = App()
        app.run()
    except Exception as e:
        logger.exception(f"An error occurred during application execution: {e}")
        return 1
    
    logger.info("Application closed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
 
 