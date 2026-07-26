"""Utility functions for video uploader.

Provides helper functions for file operations, MIME type detection,
and video path generation.
"""

import hashlib
import logging
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

# Define supported video MIME types and their content types
VIDEO_MIME_TYPES = {
    '.mp4': 'video/mp4',
    '.mov': 'video/quicktime',
    '.webm': 'video/webm',
    '.avi': 'video/x-msvideo',
}


class UtilityError(Exception):
    """Raised when utility function encounters an error."""
    pass


def calculate_sha256(file_path: str, chunk_size: int = 8192) -> str:
    """Calculate SHA256 hash of a file safely.
    
    Reads files in chunks to handle large files efficiently without
    loading entire file into memory. This is critical for video files
    which can be hundreds of MB or larger.
    
    Args:
        file_path: Path to the file to hash
        chunk_size: Size of chunks to read (default: 8192 bytes = 8KB)
        
    Returns:
        Full SHA256 hash in hexadecimal format
        
    Raises:
        UtilityError: If file cannot be read or hashed
        
    Example:
        >>> hash_value = calculate_sha256('/path/to/video.mp4')
        >>> print(hash_value)
        'a82fd91bc123def456789abcdef012345678901'
    """
    try:
        # Validate file exists
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise UtilityError(f"File not found: {file_path}")
        
        if not file_path_obj.is_file():
            raise UtilityError(f"Path is not a file: {file_path}")
        
        # Create SHA256 hash object
        sha256_hash = hashlib.sha256()
        
        # Read file in chunks to avoid loading entire file into memory
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                sha256_hash.update(chunk)
        
        hash_value = sha256_hash.hexdigest()
        logger.debug(f"Calculated SHA256 for {file_path}: {hash_value[:12]}...")
        return hash_value
    
    except UtilityError:
        raise
    except IOError as e:
        logger.error(f"IO error while calculating hash: {e}")
        raise UtilityError(f"Cannot read file: {e}")
    except Exception as e:
        logger.error(f"Unexpected error calculating hash: {e}")
        raise UtilityError(f"Hash calculation failed: {e}")


def get_video_content_type(filename: str) -> str:
    """Detect MIME type for video file.
    
    Determines the correct Content-Type header for video files based
    on file extension. Supports common video formats with fallback
    to generic video MIME type.
    
    Supported formats:
    - .mp4  -> video/mp4
    - .mov  -> video/quicktime
    - .webm -> video/webm
    - .avi  -> video/x-msvideo
    
    Args:
        filename: Name of the video file (must include extension)
        
    Returns:
        MIME type string (e.g., 'video/mp4')
        
    Raises:
        UtilityError: If file extension is unsupported
        
    Example:
        >>> content_type = get_video_content_type('sample.mp4')
        >>> print(content_type)
        'video/mp4'
    """
    try:
        # Get file extension (lowercase)
        file_ext = Path(filename).suffix.lower()
        
        if not file_ext:
            raise UtilityError(f"No file extension found: {filename}")
        
        # Check if extension has known MIME type
        if file_ext in VIDEO_MIME_TYPES:
            mime_type = VIDEO_MIME_TYPES[file_ext]
            logger.debug(f"MIME type for {filename}: {mime_type}")
            return mime_type
        
        # Try system MIME type detection as fallback
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type and mime_type.startswith('video/'):
            logger.debug(f"Detected MIME type for {filename}: {mime_type}")
            return mime_type
        
        # If no video MIME type found, raise error
        raise UtilityError(
            f"Unsupported video format: {file_ext}\n"
            f"Supported formats: {', '.join(VIDEO_MIME_TYPES.keys())}"
        )
    
    except UtilityError:
        raise
    except Exception as e:
        logger.error(f"Error detecting MIME type: {e}")
        raise UtilityError(f"MIME type detection failed: {e}")


def generate_video_path(filename: str, base_date: Optional[datetime] = None) -> str:
    """Generate organized video path with date structure.
    
    Creates a path with current date organization for better file
    management and versioning. Format: videos/YYYY/MM/DD/filename
    
    Example:
        >>> path = generate_video_path('a82fd91bc123.mp4')
        >>> print(path)
        'videos/2026/07/26/a82fd91bc123.mp4'
    
    Args:
        filename: Name of the video file (typically the hash)
        base_date: Optional datetime for testing. Defaults to current datetime.
        
    Returns:
        Organized path string with date directories
        
    Raises:
        UtilityError: If filename is invalid
        
    Example:
        >>> from datetime import datetime
        >>> custom_date = datetime(2026, 7, 26)
        >>> path = generate_video_path('video.mp4', base_date=custom_date)
        >>> print(path)
        'videos/2026/07/26/video.mp4'
    """
    try:
        # Validate filename
        if not filename or not isinstance(filename, str):
            raise UtilityError(f"Invalid filename: {filename}")
        
        filename = filename.strip()
        if not filename:
            raise UtilityError("Filename cannot be empty")
        
        # Use provided date or current date
        date = base_date or datetime.now()
        
        # Build path with date organization: videos/YYYY/MM/DD/filename
        video_path = f"videos/{date.year:04d}/{date.month:02d}/{date.day:02d}/{filename}"
        
        logger.debug(f"Generated video path: {video_path}")
        return video_path
    
    except UtilityError:
        raise
    except Exception as e:
        logger.error(f"Error generating video path: {e}")
        raise UtilityError(f"Path generation failed: {e}")


def validate_video_file(file_path: str, max_size_mb: int = 100) -> bool:
    """Validate if the file is a valid video file.
    
    Performs comprehensive validation including:
    - File existence and readability
    - Correct file type (not directory)
    - Supported video format
    - File size limits
    
    Args:
        file_path: Path to the video file
        max_size_mb: Maximum allowed file size in MB (default: 100)
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> is_valid = validate_video_file('/path/to/video.mp4')
        >>> print(is_valid)
        True
    """
    try:
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        # Check if path is a file (not directory)
        if not path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            return False
        
        # Check file extension
        try:
            get_video_content_type(path.name)
        except UtilityError:
            logger.error(f"Unsupported video format: {path.suffix}")
            return False
        
        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            logger.error(
                f"File size exceeds limit: {file_size_mb:.2f} MB > {max_size_mb} MB"
            )
            return False
        
        logger.info(f"File validation passed: {file_path} ({file_size_mb:.2f} MB)")
        return True
    
    except Exception as e:
        logger.error(f"Error during file validation: {e}")
        return False


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB as float
        
    Raises:
        UtilityError: If file cannot be accessed
        
    Example:
        >>> size = get_file_size_mb('/path/to/video.mp4')
        >>> print(f"File size: {size:.2f} MB")
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise UtilityError(f"File not found: {file_path}")
        
        size_mb = path.stat().st_size / (1024 * 1024)
        logger.debug(f"File size for {file_path}: {size_mb:.2f} MB")
        return size_mb
    
    except UtilityError:
        raise
    except Exception as e:
        logger.error(f"Error getting file size: {e}")
        raise UtilityError(f"Cannot determine file size: {e}")
