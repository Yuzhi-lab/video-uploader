"""GitHub uploader module for handling file uploads to GitHub.

Handles GitHub API interactions including authentication, file uploads,
and commit creation.
"""

import logging
from pathlib import Path
from github import Github, GithubException
from app.config import GITHUB_TOKEN, GITHUB_REPO, GITHUB_BRANCH, GITHUB_API_TIMEOUT

logger = logging.getLogger(__name__)


class GitHubUploader:
    """Handles uploading files to GitHub."""
    
    def __init__(self):
        """Initialize GitHub uploader with authentication."""
        if not GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN not set in environment variables")
        if not GITHUB_REPO:
            raise ValueError("GITHUB_REPO not set in environment variables")
        
        self.github = Github(GITHUB_TOKEN, timeout=GITHUB_API_TIMEOUT)
        self.repo = self.github.get_repo(GITHUB_REPO)
        self.branch = GITHUB_BRANCH
        logger.info(f"GitHub uploader initialized for {GITHUB_REPO} on branch {self.branch}")
    
    def upload_file(self, file_path: str, target_path: str) -> str:
        """Upload a file to GitHub repository.
        
        Args:
            file_path: Local path to file
            target_path: Target path in repository (e.g., 'videos/sample.mp4')
            
        Returns:
            GitHub file URL
            
        Raises:
            FileNotFoundError: If file doesn't exist
            GithubException: If GitHub API call fails
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Check if file already exists
            try:
                existing = self.repo.get_contents(target_path, ref=self.branch)
                # File exists, update it
                self.repo.update_file(
                    target_path,
                    f"Update {path.name}",
                    content,
                    existing.sha,
                    branch=self.branch
                )
                logger.info(f"File updated in repository: {target_path}")
            except GithubException:
                # File doesn't exist, create it
                self.repo.create_file(
                    target_path,
                    f"Add {path.name}",
                    content,
                    branch=self.branch
                )
                logger.info(f"File created in repository: {target_path}")
            
            file_url = f"https://github.com/{GITHUB_REPO}/blob/{self.branch}/{target_path}"
            return file_url
        
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise
