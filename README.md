# Video Uploader

A Python project that uploads local video files to GitHub and returns a public URL using jsDelivr CDN.

## Features

- Upload video files to GitHub repository
- Automatic file validation (format, size)
- Generate public jsDelivr CDN URLs
- Clean, modular architecture
- Comprehensive error handling and logging

## Requirements

- Python 3.11+
- GitHub account with personal access token
- GitHub repository for storing videos

## Project Structure

```
project/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── github_uploader.py    # GitHub API interaction
│   ├── config.py             # Configuration management
│   └── utils.py              # Utility functions
├── uploads/                  # Local staging directory
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not committed)
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/video-uploader.git
   cd video-uploader
   ```

2. **Create virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Edit `.env` file
   - Add your GitHub token (create at: https://github.com/settings/tokens)
   - Specify target repository (format: `username/repo-name`)
   - Set branch (default: `main`)

   ```env
   GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
   GITHUB_REPO=your-username/your-repo-name
   GITHUB_BRANCH=main
   ```

## Usage

### Basic Usage

```bash
python main.py /path/to/video.mp4
```

### With Custom Target Path

```bash
python main.py /path/to/video.mp4 --target videos/my-folder/video.mp4
```

### Output Example

```
============================================================
Upload Successful!
============================================================
GitHub URL: https://github.com/username/repo/blob/main/videos/video.mp4
CDN URL: https://cdn.jsdelivr.net/gh/username/repo@main/videos/video.mp4
============================================================
```

## File Specifications

### Supported Video Formats
- `.mp4` - MPEG-4 Video
- `.avi` - Audio Video Interleave
- `.mov` - QuickTime Movie
- `.mkv` - Matroska Video
- `.webm` - WebM Video

### Constraints
- Maximum file size: 100 MB
- Files are validated before upload

## Module Overview

### `app/config.py`
Manages all configuration:
- GitHub credentials and repository settings
- File upload constraints
- jsDelivr CDN base URL
- API timeouts

### `app/utils.py`
Utility functions:
- `validate_video_file()` - Validates file format and size
- `generate_jsdelivr_url()` - Creates CDN URL
- `get_file_size_mb()` - Calculates file size
- Logging and error handling

### `app/github_uploader.py`
GitHub API wrapper:
- `GitHubUploader` class for file operations
- Authentication handling
- File creation/update operations
- Error management

### `main.py`
Application entry point:
- CLI argument parsing
- Orchestrates upload workflow
- Displays results to user

## Troubleshooting

### "GITHUB_TOKEN not set in environment variables"
- Ensure `.env` file exists in project root
- Check that `GITHUB_TOKEN` is set correctly
- Reload environment: `source venv/bin/activate`

### "GITHUB_REPO not set in environment variables"
- Verify `.env` contains `GITHUB_REPO=username/repo-name`
- Repository must exist on GitHub

### "File validation failed"
- Check file format is in supported list
- Verify file size is under 100 MB
- Ensure file path is correct and file exists

### "GitHub API error"
- Verify GitHub token has repository write permissions
- Check repository access and permissions
- Ensure target branch exists in repository

## Security Notes

- **Never commit `.env` file** - it contains sensitive tokens
- Use a personal access token with minimal required permissions
- Consider using GitHub token expiration
- Rotate tokens periodically for security

## Future Enhancements

- [ ] Batch upload multiple files
- [ ] Progress bar for large files
- [ ] Automatic video compression
- [ ] Metadata extraction
- [ ] Upload scheduling
- [ ] Webhook notifications

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
