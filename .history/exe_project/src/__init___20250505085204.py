"""
IVAS-IFM: Intelligent Video Acquisition System - Intelligent File Management

This package provides tools for intelligent video acquisition, processing, and management
from multiple video platforms.
"""

__version__ = '1.1.0'

# For direct imports
try:
    from .modules.vca import CrawlerManager
    from .config.settings import APP_CONFIG, PLATFORM_CONFIGS, MESSAGES
except ImportError:
    # We'll handle these imports in the specific modules
    pass 