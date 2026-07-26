"""Utility functions for video uploader.

Includes file validation, URL generation, and helper functions.
"""

import logging
from pathlib import Path
from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, JSDELIVR_BASE_URL

# Configure logging
logger = logging.getLogger(__name__)


def validate_video_file(file_path: str) -> bool:
    """Validate if the file is a valid video file.
    
    Args:
        file_path: Path to the video file
        
    Returns:
        True if valid, False otherwise
    """
    path = Path(file_path)
    
    # Check if file exists
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return False
    
    # Check if file is a file (not directory)
    if not path.is_file():
        logger.error(f"Path is not a file: {file_path}")
        return False
    
    # Check file extension
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        logger.error(f"Unsupported file extension: {path.suffix}")
        return False
    
    # Check file size
    file_size = path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        logger.error(f"File size exceeds limit: {file_size} > {MAX_FILE_SIZE}")
        return False
    
    logger.info(f"File validation passed: {file_path}")
    return True


def generate_jsdelivr_url(repo: str, branch: str, file_path: str) -> str:
    """Generate jsDelivr CDN URL for a GitHub file.
    
    Args:
        repo: Repository in format 'owner/repo'
        branch: Branch name
        file_path: Path to file in repository
        
    Returns:
        Public jsDelivr CDN URL
    """
    url = f"{JSDELIVR_BASE_URL}/{repo}@{branch}/{file_path}"
    logger.info(f"Generated jsDelivr URL: {url}")
    return url


def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    return Path(file_path).stat().st_size / (1024 * 1024)
