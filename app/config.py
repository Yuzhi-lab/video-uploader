"""Configuration management for the video uploader.

Loads environment variables and defines constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# GitHub Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')  # Format: owner/repo
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'main')

# jsDelivr Configuration
JSDELIVR_BASE_URL = "https://cdn.jsdelivr.net/gh"

# File Configuration
UPLOAD_DIR = Path(__file__).parent.parent / 'uploads'
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}

# API Configuration
GITHUB_API_TIMEOUT = 30  # seconds
