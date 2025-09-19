"""Main application for image resizing system."""
import os
import sys
import time
from pathlib import Path

from config import Config
from image_service import ImageProcessor

def main():
    """Main application entry point."""
    print("=" * 60)
    print("Image Resizing System")
    print("=" * 60)
    
    # Initialize configuration
    config = Config()
    
    # Create necessary directories
    config.create_directories()
    
    # Initialize image processor
    processor = ImageProcessor(config)
    
    # Check if input directory exists
    if not os.path.exists(config.input_dir):
        print(f"Error: Input directory does not exist: {config.input_dir}")
        print("Please check the path in config.py")
        return
    
    print(f"Input directory: {config.input_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Minimum width requirement: {config.min_width}px")
    print(f"Supported formats: {', '.join(config.supported_formats)}")
    print("-" * 60)
    
    # Process images
    start_time = time.time()
    stats = processor.process_directory(config.input_dir)
    end_time = time.time()
    
    # Display results
    print("\n" + "=" * 60)
    print("PROCESSING RESULTS")
    print("=" * 60)
    print(f"Total files found: {stats['total']}")
    print(f"Successfully processed: {stats['processed']}")
    print(f"Skipped (cached): {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    print(f"Processing time: {end_time - start_time:.2f} seconds")
    
    if stats['processed'] > 0:
        print(f"\nProcessed images saved to: {os.path.abspath(config.output_dir)}")
    
    if stats['errors'] > 0:
        print(f"\n{stats['errors']} files had errors and were not processed.")
        print("Check the logs above for specific error messages.")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)

