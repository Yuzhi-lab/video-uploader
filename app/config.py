"""Configuration management for the video uploader.

Loads and validates environment variables using python-dotenv.
Provides a Config class with comprehensive validation.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when configuration is invalid or incomplete."""
    pass


class Config:
    """Configuration manager for the video uploader.
    
    Loads environment variables from .env file and validates them.
    Provides access to configuration through class attributes.
    """
    
    # GitHub Configuration
    GITHUB_TOKEN: str
    GITHUB_USERNAME: str
    GITHUB_REPOSITORY: str
    GITHUB_BRANCH: str
    
    # jsDelivr Configuration
    JSDELIVR_BASE_URL: str = "https://cdn.jsdelivr.net/gh"
    
    # File Configuration
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB
    ALLOWED_EXTENSIONS: set = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
    UPLOAD_DIR: Path
    
    # API Configuration
    GITHUB_API_TIMEOUT: int = 30  # seconds
    
    def __init__(self, env_path: Optional[Path] = None):
        """Initialize configuration by loading and validating environment variables.
        
        Args:
            env_path: Path to .env file. Defaults to project root.
            
        Raises:
            ConfigError: If required environment variables are missing or invalid.
        """
        # Determine .env path
        if env_path is None:
            env_path = Path(__file__).parent.parent / '.env'
        
        # Load environment variables
        if env_path.exists():
            load_dotenv(env_path)
        else:
            # If no .env file, still load from system environment
            load_dotenv()
        
        # Set upload directory
        self.UPLOAD_DIR = Path(__file__).parent.parent / 'uploads'
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        
        # Validate and set GitHub configuration
        self._validate_and_load_github_config()
    
    def _validate_and_load_github_config(self) -> None:
        """Validate and load GitHub configuration from environment variables.
        
        Raises:
            ConfigError: If required GitHub configuration is missing.
        """
        # Load GITHUB_TOKEN
        self.GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '').strip()
        if not self.GITHUB_TOKEN:
            raise ConfigError(
                "Missing required configuration: GITHUB_TOKEN\n"
                "Please add GITHUB_TOKEN to your .env file.\n"
                "Get a token at: https://github.com/settings/tokens"
            )
        
        # Load GITHUB_USERNAME
        self.GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', '').strip()
        if not self.GITHUB_USERNAME:
            raise ConfigError(
                "Missing required configuration: GITHUB_USERNAME\n"
                "Please add GITHUB_USERNAME to your .env file.\n"
                "Example: GITHUB_USERNAME=your-github-username"
            )
        
        # Load GITHUB_REPOSITORY
        self.GITHUB_REPOSITORY = os.getenv('GITHUB_REPOSITORY', '').strip()
        if not self.GITHUB_REPOSITORY:
            raise ConfigError(
                "Missing required configuration: GITHUB_REPOSITORY\n"
                "Please add GITHUB_REPOSITORY to your .env file.\n"
                "Example: GITHUB_REPOSITORY=video-uploader"
            )
        
        # Load GITHUB_BRANCH (has default)
        self.GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'main').strip()
        if not self.GITHUB_BRANCH:
            raise ConfigError(
                "Invalid configuration: GITHUB_BRANCH cannot be empty.\n"
                "Default is 'main'. Set GITHUB_BRANCH in .env file."
            )
        
        # Validate token format (basic check)
        if not self._is_valid_github_token(self.GITHUB_TOKEN):
            raise ConfigError(
                "Invalid GITHUB_TOKEN format.\n"
                "GitHub tokens typically start with 'ghp_' or 'github_pat_'.\n"
                "Verify your token at: https://github.com/settings/tokens"
            )
    
    @staticmethod
    def _is_valid_github_token(token: str) -> bool:
        """Validate GitHub token format.
        
        Args:
            token: The token to validate
            
        Returns:
            True if token has valid format, False otherwise
        """
        if not token:
            return False
        # GitHub tokens typically start with specific prefixes
        valid_prefixes = ('ghp_', 'gho_', 'ghu_', 'github_pat_')
        return any(token.startswith(prefix) for prefix in valid_prefixes) or len(token) > 20
    
    def get_github_repo_full_name(self) -> str:
        """Get full GitHub repository name (username/repository).
        
        Returns:
            Repository full name in format: username/repository
        """
        return f"{self.GITHUB_USERNAME}/{self.GITHUB_REPOSITORY}"
    
    def get_github_repo_url(self) -> str:
        """Get GitHub repository URL.
        
        Returns:
            Full GitHub repository URL
        """
        return f"https://github.com/{self.get_github_repo_full_name()}"
    
    def __repr__(self) -> str:
        """String representation of configuration (without sensitive data).
        
        Returns:
            Configuration summary with masked token
        """
        token_masked = f"{self.GITHUB_TOKEN[:10]}..." if len(self.GITHUB_TOKEN) > 10 else "***"
        return (
            f"Config(\n"
            f"  GitHub Token: {token_masked}\n"
            f"  Repository: {self.get_github_repo_full_name()}\n"
            f"  Branch: {self.GITHUB_BRANCH}\n"
            f"  Max File Size: {self.MAX_FILE_SIZE / (1024 * 1024):.0f} MB\n"
            f"  Allowed Extensions: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}\n"
            f")"
        )


# Global configuration instance
# This is initialized when the module is imported
try:
    config = Config()
except ConfigError as e:
    # Store the error for later handling
    config = None
    _config_error = str(e)


def get_config() -> Config:
    """Get the global configuration instance.
    
    Returns:
        Global Config instance
        
    Raises:
        ConfigError: If configuration failed to initialize
    """
    if config is None:
        raise ConfigError(f"Configuration not initialized:\n{_config_error}")
    return config
