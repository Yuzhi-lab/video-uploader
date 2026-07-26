"""GitHub uploader module for handling file uploads to GitHub.

Provides GitHubUploader class for uploading video files to GitHub repository
and generating public jsDelivr CDN URLs.
"""

import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from github import Github, GithubException
from app.config import get_config, ConfigError

# Configure logging
logger = logging.getLogger(__name__)


class GitHubUploaderError(Exception):
    """Raised when GitHub upload operation fails."""
    pass


class GitHubUploader:
    """Handles uploading video files to GitHub and generating CDN URLs.
    
    This class manages:
    - Connection to GitHub API
    - File validation
    - Duplicate file detection
    - File upload with organized directory structure (videos/YYYY/MM/DD/)
    - jsDelivr CDN URL generation
    """
    
    def __init__(self):
        """Initialize GitHub uploader with authentication.
        
        Raises:
            ConfigError: If configuration is invalid
            GitHubUploaderError: If GitHub authentication fails
        """
        try:
            self.config = get_config()
        except ConfigError as e:
            raise GitHubUploaderError(f"Configuration error: {e}")
        
        try:
            # Create GitHub API instance with authentication
            self.github = Github(self.config.GITHUB_TOKEN, timeout=self.config.GITHUB_API_TIMEOUT)
            
            # Get repository object
            repo_full_name = self.config.get_github_repo_full_name()
            self.repo = self.github.get_repo(repo_full_name)
            
            # Verify repository access
            self.repo.get_commits(per_page=1)
            
            logger.info(f"GitHub uploader initialized for {repo_full_name}")
        except GithubException as e:
            logger.error(f"GitHub authentication failed: {e}")
            raise GitHubUploaderError(f"GitHub authentication failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during initialization: {e}")
            raise GitHubUploaderError(f"Initialization failed: {e}")
    
    def _generate_file_hash(self, file_path: str) -> str:
        """Generate SHA256 hash of file content for unique naming.
        
        Args:
            file_path: Path to the file
            
        Returns:
            First 12 characters of SHA256 hash in hexadecimal
            
        Raises:
            GitHubUploaderError: If file cannot be read
        """
        try:
            sha256_hash = hashlib.sha256()
            
            # Read file in chunks for memory efficiency
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(byte_block)
            
            # Return first 12 characters of hash (sufficient for uniqueness)
            return sha256_hash.hexdigest()[:12]
        except Exception as e:
            logger.error(f"Failed to generate file hash: {e}")
            raise GitHubUploaderError(f"Failed to generate file hash: {e}")
    
    def _get_upload_path(self, file_path: str) -> str:
        """Generate organized upload path with date structure.
        
        Format: videos/YYYY/MM/DD/{hash}.{extension}
        Example: videos/2026/07/26/a82fd91bc123.mp4
        
        Args:
            file_path: Path to the local file
            
        Returns:
            Upload path in repository
        """
        # Get file extension (lowercase)
        file_ext = Path(file_path).suffix.lower()
        
        # Generate hash for unique filename
        file_hash = self._generate_file_hash(file_path)
        
        # Get current date for directory structure
        now = datetime.now()
        date_path = f"{now.year:04d}/{now.month:02d}/{now.day:02d}"
        
        # Build complete upload path
        upload_path = f"videos/{date_path}/{file_hash}{file_ext}"
        
        logger.debug(f"Generated upload path: {upload_path}")
        return upload_path
    
    def _file_exists_in_repo(self, repo_path: str) -> bool:
        """Check if file already exists in repository.
        
        Args:
            repo_path: Path to check in repository
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.repo.get_contents(repo_path, ref=self.config.GITHUB_BRANCH)
            logger.debug(f"File already exists in repository: {repo_path}")
            return True
        except GithubException as e:
            # 404 means file doesn't exist, which is expected
            if e.status == 404:
                return False
            # Other errors should be logged but treated as file not found
            logger.warning(f"Unexpected error checking file existence: {e}")
            return False
    
    def _generate_jsdelivr_url(self, repo_path: str) -> str:
        """Generate public jsDelivr CDN URL for uploaded file.
        
        Args:
            repo_path: Path to file in repository
            
        Returns:
            Public jsDelivr CDN URL
        """
        username = self.config.GITHUB_USERNAME
        repository = self.config.GITHUB_REPOSITORY
        branch = self.config.GITHUB_BRANCH
        
        # Build jsDelivr CDN URL
        cdn_url = f"{self.config.JSDELIVR_BASE_URL}/{username}/{repository}@{branch}/{repo_path}"
        
        logger.debug(f"Generated jsDelivr URL: {cdn_url}")
        return cdn_url
    
    def upload_file(self, file_path: str) -> Tuple[str, bool]:
        """Upload a video file to GitHub repository.
        
        Process:
        1. Validates file path
        2. Generates organized upload path (videos/YYYY/MM/DD/)
        3. Checks if file already exists (by hash)
        4. Uploads file if new
        5. Returns jsDelivr CDN URL and upload status
        
        Args:
            file_path: Local path to video file
            
        Returns:
            Tuple of (jsDelivr_url, is_new_upload)
            - jsDelivr_url: Public URL to access file via CDN
            - is_new_upload: True if newly uploaded, False if already existed
            
        Raises:
            GitHubUploaderError: If upload fails
        """
        try:
            # Validate file exists
            local_path = Path(file_path)
            if not local_path.exists():
                raise GitHubUploaderError(f"File not found: {file_path}")
            
            if not local_path.is_file():
                raise GitHubUploaderError(f"Path is not a file: {file_path}")
            
            # Get file size for logging
            file_size_mb = local_path.stat().st_size / (1024 * 1024)
            
            # Generate repository path
            repo_path = self._get_upload_path(file_path)
            logger.info(f"Uploading file: {local_path.name} ({file_size_mb:.2f} MB) -> {repo_path}")
            
            # Check if file already exists
            if self._file_exists_in_repo(repo_path):
                logger.info(f"File already exists in repository: {repo_path}")
                cdn_url = self._generate_jsdelivr_url(repo_path)
                return cdn_url, False
            
            # Read file content in binary mode
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Create file in repository
            try:
                commit_message = f"Add {local_path.name}"
                self.repo.create_file(
                    path=repo_path,
                    message=commit_message,
                    content=file_content,
                    branch=self.config.GITHUB_BRANCH
                )
                logger.info(f"File uploaded successfully: {repo_path}")
            except GithubException as e:
                logger.error(f"GitHub API error during upload: {e}")
                raise GitHubUploaderError(f"Failed to upload file to GitHub: {e}")
            
            # Generate and return CDN URL
            cdn_url = self._generate_jsdelivr_url(repo_path)
            logger.info(f"Generated jsDelivr URL: {cdn_url}")
            
            return cdn_url, True
        
        except GitHubUploaderError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise GitHubUploaderError(f"Upload failed: {e}")
    
    def get_github_repo_url(self) -> str:
        """Get GitHub repository URL.
        
        Returns:
            Full GitHub repository URL
        """
        return self.config.get_github_repo_url()
    
    def __repr__(self) -> str:
        """String representation of uploader.
        
        Returns:
            Description string with repository info
        """
        return (
            f"GitHubUploader(\n"
            f"  Repository: {self.config.get_github_repo_full_name()}\n"
            f"  Branch: {self.config.GITHUB_BRANCH}\n"
            f"  CDN Base: {self.config.JSDELIVR_BASE_URL}\n"
            f")"
        )
