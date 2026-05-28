"""
Logging Utility Module
Provides unified logger for the job agent, printing to stdout and writing to doc/scraping.log
"""

import logging
import os
import sys

def setup_logger(name: str = "JobAgent") -> logging.Logger:
    """
    Setup and configure the logger.
    
    Args:
        name (str): Name of the logger
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers if logger is already initialized
    if logger.handlers:
        return logger
        
    log_format = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    
    # File Handler - write to doc/scraping.log
    log_dir = "doc"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "scraping.log")
    
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create file logger at {log_file} ({e}). Console logging only.")
        
    return logger

# Create a default logger instance
logger = setup_logger()
