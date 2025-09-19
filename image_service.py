"""Image processing service with validation and resizing capabilities."""
import os
import time
import hashlib
from typing import List, Tuple, Optional
from PIL import Image, ImageOps
import logging

from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageProcessor:
    """Handles image processing, validation, and resizing operations."""
    
    def __init__(self, config: Config):
        self.config = config
        self.processed_count = 0
        self.skipped_count = 0
        self.error_count = 0
    
    def validate_image(self, image_path: str) -> Tuple[bool, str, bool]:
        """
        Validate image file for format and minimum width requirements.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (is_valid, error_message, needs_borders)
        """
        try:
            # Check file extension
            if not self.config.is_valid_image_format(image_path):
                return False, f"Invalid image extension. Supported formats are {', '.join(self.config.supported_formats)}", False
            
            # Check if file exists
            if not os.path.exists(image_path):
                return False, "File does not exist", False
            
            # Check file size
            file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
            if file_size_mb > self.config.max_file_size_mb:
                return False, f"File too large ({file_size_mb:.1f}MB). Maximum allowed: {self.config.max_file_size_mb}MB", False
            
            # Open and validate image
            with Image.open(image_path) as img:
                width, height = img.size
                
                # Check if image can be processed
                img.verify()
                
                # Check minimum width requirement
                needs_borders = width < self.config.min_width
                if needs_borders:
                    logger.info(f"Image {os.path.basename(image_path)} is {width}px wide, will add dark borders to meet {self.config.min_width}px requirement")
                
            return True, "", needs_borders
            
        except Exception as e:
            return False, f"Error validating image: {str(e)}", False
    
    def process_image(self, input_path: str, output_path: str, add_borders: bool = False) -> bool:
        """
        Process and save image with proper formatting.
        
        Args:
            input_path: Path to input image
            output_path: Path to save processed image
            add_borders: Whether to add dark borders to meet minimum width
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if necessary (for JPEG output)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparent images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Auto-orient image based on EXIF data
                img = ImageOps.exif_transpose(img)
                
                # Add dark borders if needed to meet minimum width
                if add_borders:
                    img = self._add_dark_borders(img)
                
                # Save with specified quality
                img.save(output_path, 'JPEG', quality=self.config.quality, optimize=True)
                
            return True
            
        except Exception as e:
            logger.error(f"Error processing image {input_path}: {str(e)}")
            return False
    
    def _add_dark_borders(self, img: Image.Image) -> Image.Image:
        """
        Add dark borders to image to meet minimum width requirement.
        
        Args:
            img: PIL Image object
            
        Returns:
            Image with dark borders added
        """
        width, height = img.size
        
        if width >= self.config.min_width:
            return img
        
        # Calculate new dimensions maintaining aspect ratio
        new_width = self.config.min_width
        new_height = int((new_width * height) / width)
        
        # Resize image to new dimensions
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create dark background (black)
        dark_background = Image.new('RGB', (new_width, new_height), (0, 0, 0))
        
        # Paste resized image onto dark background
        # Center the image
        x_offset = 0
        y_offset = 0
        dark_background.paste(resized_img, (x_offset, y_offset))
        
        return dark_background
    
    def get_cache_key(self, file_path: str) -> str:
        """Generate cache key for file."""
        stat = os.stat(file_path)
        return hashlib.md5(f"{file_path}_{stat.st_mtime}_{stat.st_size}".encode()).hexdigest()
    
    def is_cached(self, file_path: str) -> bool:
        """Check if file is already processed and cached."""
        if not self.config.enable_caching:
            return False
        
        cache_key = self.get_cache_key(file_path)
        cache_file = os.path.join(self.config.cache_dir, f"{cache_key}.txt")
        return os.path.exists(cache_file)
    
    def mark_as_cached(self, file_path: str):
        """Mark file as processed in cache."""
        if not self.config.enable_caching:
            return
        
        cache_key = self.get_cache_key(file_path)
        cache_file = os.path.join(self.config.cache_dir, f"{cache_key}.txt")
        os.makedirs(self.config.cache_dir, exist_ok=True)
        
        with open(cache_file, 'w') as f:
            f.write(f"Processed: {file_path}\nTimestamp: {time.time()}")
    
    def process_single_image(self, input_path: str) -> bool:
        """
        Process a single image file.
        
        Args:
            input_path: Path to the input image
            
        Returns:
            True if successful, False otherwise
        """
        # Check if already cached
        if self.is_cached(input_path):
            logger.info(f"Skipping cached file: {input_path}")
            self.skipped_count += 1
            return True
        
        # Validate image
        is_valid, error_msg, needs_borders = self.validate_image(input_path)
        if not is_valid:
            logger.warning(f"Invalid image {input_path}: {error_msg}")
            self.error_count += 1
            return False
        
        # Generate output path
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        suffix = "_processed_with_borders" if needs_borders else "_processed"
        output_filename = f"{name}{suffix}.jpg"
        output_path = os.path.join(self.config.output_dir, output_filename)
        
        # Process image
        if self.process_image(input_path, output_path, add_borders=needs_borders):
            self.mark_as_cached(input_path)
            self.processed_count += 1
            border_info = " (with dark borders)" if needs_borders else ""
            logger.info(f"Successfully processed: {input_path} -> {output_path}{border_info}")
            return True
        else:
            self.error_count += 1
            return False
    
    def process_directory(self, directory_path: str) -> dict:
        """
        Process all valid images in a directory.
        
        Args:
            directory_path: Path to directory containing images
            
        Returns:
            Dictionary with processing statistics
        """
        logger.info(f"Starting batch processing of directory: {directory_path}")
        
        # Reset counters
        self.processed_count = 0
        self.skipped_count = 0
        self.error_count = 0
        
        # Create output directory
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        # Find all image files
        image_files = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if self.config.is_valid_image_format(file):
                    image_files.append(os.path.join(root, file))
        
        logger.info(f"Found {len(image_files)} image files to process")
        
        # Process each image
        for image_path in image_files:
            self.process_single_image(image_path)
        
        # Return statistics
        stats = {
            'processed': self.processed_count,
            'skipped': self.skipped_count,
            'errors': self.error_count,
            'total': len(image_files)
        }
        
        logger.info(f"Processing complete. Processed: {stats['processed']}, "
                   f"Skipped: {stats['skipped']}, Errors: {stats['errors']}")
        
        return stats

