"""Configuration management for image resizing system."""
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Centralized configuration management."""
    
    def __init__(self):
        self.min_width = int(os.getenv('MIN_WIDTH', 600))
        self.quality = int(os.getenv('QUALITY', 85))
        self.supported_formats = ['.jpg', '.jpeg', '.png']
        self.input_dir = r"C:\Users\Victor Akello\Desktop\Jiji Items\Services 70\web design 15"
        self.output_dir = os.path.join(self.input_dir, 'ready-images')
        self.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', 10))
        self.enable_caching = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
        self.cache_dir = os.getenv('CACHE_DIR', 'cache')
        self.retry_attempts = int(os.getenv('RETRY_ATTEMPTS', 3))
        self.retry_delay = int(os.getenv('RETRY_DELAY', 1))
    
    def is_valid_image_format(self, filename: str) -> bool:
        """Check if file has supported image format."""
        return any(filename.lower().endswith(ext) for ext in self.supported_formats)
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return self.supported_formats
    
    def create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [self.input_dir, self.output_dir]
        if self.enable_caching:
            directories.append(self.cache_dir)
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
