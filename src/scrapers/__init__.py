"""
Scrapers Module

This module contains all job scrapers for different platforms.
"""

from .base import BaseScraper
from .naukri import NaukriScraper
from .remoteok import RemoteOKScraper
from .wellfound import WellfoundScraper

__all__ = [
    'BaseScraper',
    'NaukriScraper',
    'RemoteOKScraper',
    'WellfoundScraper'
]
