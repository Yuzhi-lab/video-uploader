#!/usr/bin/env python3
"""Main entry point for the video uploader application.

Handles CLI interaction and orchestrates the upload workflow.
Usage:
    python main.py video.mp4
    python main.py video.mp4 --verbose
"""

import logging
import sys
from pathlib import Path
from argparse import ArgumentParser

from app.config import get_config, ConfigError
from app.utils import validate_video_file, get_file_size_mb, UtilityError
from app.github_uploader import GitHubUploader, GitHubUploaderError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_parser() -> ArgumentParser:
    """Create and configure argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = ArgumentParser(
        description='Upload local video files to GitHub and get jsDelivr CDN URL',
        epilog='Example: python main.py demo.mp4'
    )
    
    parser.add_argument(
        'file_path',
        help='Path to the video file to upload (e.g., demo.mp4)'
    )
    
    parser.add_argument(
        '--max-size',
        type=int,
        default=100,
        help='Maximum file size in MB (default: 100)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging output'
    )
    
    return parser


def setup_logging(verbose: bool = False) -> None:
    """Configure logging level.
    
    Args:
        verbose: If True, enable DEBUG level logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Update root logger level
    logging.getLogger().setLevel(log_level)
    
    # Update main module logger
    logger.setLevel(log_level)


def print_success(cdn_url: str, github_url: str, is_new: bool) -> None:
    """Print upload success message.
    
    Args:
        cdn_url: Public jsDelivr CDN URL
        github_url: GitHub repository URL
        is_new: True if newly uploaded, False if already existed
    """
    status = "newly uploaded" if is_new else "already existed"
    
    print("\n" + "=" * 70)
    print("✓ Upload Successful!".center(70))
    print("=" * 70)
    print(f"Status: File {status}")
    print(f"\nPublic URL (jsDelivr CDN):")
    print(f"  {cdn_url}")
    print(f"\nRepository:")
    print(f"  {github_url}")
    print("=" * 70 + "\n")


def print_error(title: str, message: str, details: str = None) -> None:
    """Print error message in formatted way.
    
    Args:
        title: Error title
        message: Error message
        details: Optional detailed information
    """
    print("\n" + "=" * 70)
    print(f"✗ {title}".center(70))
    print("=" * 70)
    print(f"Error: {message}")
    if details:
        print(f"\nDetails:\n{details}")
    print("=" * 70 + "\n")


def handle_file_validation_error(file_path: str) -> None:
    """Handle file validation error with helpful message.
    
    Args:
        file_path: Path to the file that failed validation
    """
    path = Path(file_path)
    
    # Determine what went wrong
    if not path.exists():
        error_msg = f"File not found: {file_path}"
        details = "Please check the file path and try again."
    elif not path.is_file():
        error_msg = f"Path is not a file: {file_path}"
        details = "Please provide a file path, not a directory."
    else:
        # Likely a format or size issue - let validation provide details
        error_msg = "File validation failed"
        details = (
            "Supported formats: .mp4, .mov, .webm, .avi\n"
            "Maximum file size: 100 MB"
        )
    
    print_error("File Validation Failed", error_msg, details)


def handle_config_error(error: ConfigError) -> None:
    """Handle configuration error with helpful message.
    
    Args:
        error: ConfigError exception
    """
    error_msg = str(error)
    details = (
        "Please check your .env file:\n"
        "  GITHUB_TOKEN - Personal access token from GitHub\n"
        "  GITHUB_USERNAME - Your GitHub username\n"
        "  GITHUB_REPOSITORY - Name of the repository\n"
        "  GITHUB_BRANCH - Target branch (default: main)\n\n"
        "Get a GitHub token at: https://github.com/settings/tokens"
    )
    print_error("Configuration Error", error_msg, details)


def handle_uploader_error(error: GitHubUploaderError) -> None:
    """Handle uploader error with helpful message.
    
    Args:
        error: GitHubUploaderError exception
    """
    error_msg = str(error)
    details = (
        "This could be due to:\n"
        "  • Invalid GitHub token\n"
        "  • Repository doesn't exist or not accessible\n"
        "  • Network connection issues\n"
        "  • GitHub API rate limit exceeded"
    )
    print_error("Upload Failed", error_msg, details)


def main():
    """Main application entry point.
    
    Orchestrates the video upload workflow:
    1. Parse command line arguments
    2. Validate file
    3. Initialize uploader
    4. Upload file
    5. Print results or error
    
    Exit codes:
        0 - Success
        1 - Configuration error
        2 - File validation error
        3 - Upload error
        4 - Unexpected error
    """
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    
    logger.info(f"Video Uploader started")
    logger.debug(f"File path: {args.file_path}")
    logger.debug(f"Max size: {args.max_size} MB")
    
    try:
        # Step 1: Check file exists and is valid
        logger.info("Validating file...")
        if not validate_video_file(args.file_path, max_size_mb=args.max_size):
            handle_file_validation_error(args.file_path)
            sys.exit(2)
        
        file_path = Path(args.file_path)
        file_size_mb = get_file_size_mb(args.file_path)
        logger.info(f"File validation passed: {file_path.name} ({file_size_mb:.2f} MB)")
        
        # Step 2: Initialize uploader (validates config)
        logger.info("Initializing GitHub uploader...")
        uploader = GitHubUploader()
        logger.info(f"Connected to repository: {uploader.config.get_github_repo_full_name()}")
        
        # Step 3: Upload file
        logger.info(f"Uploading file: {file_path.name}")
        cdn_url, is_new = uploader.upload_file(args.file_path)
        
        # Step 4: Print success
        github_url = uploader.get_github_repo_url()
        print_success(cdn_url, github_url, is_new)
        
        logger.info("Upload completed successfully")
        sys.exit(0)
    
    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        handle_config_error(e)
        sys.exit(1)
    
    except GitHubUploaderError as e:
        logger.error(f"Upload error: {e}")
        handle_uploader_error(e)
        sys.exit(3)
    
    except UtilityError as e:
        logger.error(f"Utility error: {e}")
        print_error("Operation Failed", str(e))
        sys.exit(3)
    
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        print_error("Cancelled", "Upload cancelled by user")
        sys.exit(130)
    
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print_error(
            "Unexpected Error",
            str(e),
            "An unexpected error occurred. Please check the logs for details."
        )
        sys.exit(4)


if __name__ == "__main__":
    main()
