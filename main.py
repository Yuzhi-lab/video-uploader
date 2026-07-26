#!/usr/bin/env python3
"""Main entry point for the video uploader application.

Handles CLI interaction and orchestrates the upload workflow.
"""

import logging
import sys
from pathlib import Path
from argparse import ArgumentParser

from app.config import UPLOAD_DIR
from app.utils import validate_video_file, generate_jsdelivr_url, get_file_size_mb
from app.github_uploader import GitHubUploader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    parser = ArgumentParser(description='Upload local video files to GitHub and get jsDelivr CDN URL')
    parser.add_argument('file_path', help='Path to the video file to upload')
    parser.add_argument('--target', help='Target path in repository (default: videos/filename)', default=None)
    
    args = parser.parse_args()
    
    try:
        # Validate file
        if not validate_video_file(args.file_path):
            logger.error("File validation failed")
            sys.exit(1)
        
        file_path = Path(args.file_path)
        file_size = get_file_size_mb(args.file_path)
        
        # Determine target path
        target_path = args.target or f"videos/{file_path.name}"
        
        logger.info(f"Starting upload: {file_path.name} ({file_size:.2f} MB)")
        
        # Initialize uploader
        uploader = GitHubUploader()
        
        # Upload file
        github_url = uploader.upload_file(args.file_path, target_path)
        logger.info(f"File uploaded to GitHub: {github_url}")
        
        # Generate jsDelivr CDN URL
        cdn_url = generate_jsdelivr_url(uploader.repo.full_name, uploader.branch, target_path)
        
        print("\n" + "="*60)
        print("Upload Successful!")
        print("="*60)
        print(f"GitHub URL: {github_url}")
        print(f"CDN URL: {cdn_url}")
        print("="*60 + "\n")
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
