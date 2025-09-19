# Image Resizing System

A Python-based image processing system that validates and resizes images to meet specific standards.

## Features

- **Format Validation**: Supports JPG and PNG formats only
- **Size Validation**: Ensures minimum width of 600px
- **Batch Processing**: Processes entire directories recursively
- **Caching**: Avoids reprocessing already converted images
- **Error Handling**: Comprehensive validation and error reporting
- **Auto-orientation**: Handles EXIF orientation data

## Requirements

- Python 3.7+
- PIL/Pillow for image processing
- python-dotenv for configuration

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the system:
```bash
python main.py
```

Or use the batch file on Windows:
```bash
run.bat
```

## Configuration

The system is configured to process images from:
`C:\Users\Victor Akello\Desktop\Jiji Items\Services 70\web design 15`

Processed images are saved to a `ready-images` folder in the same location as the original images.

## How It Works

1. **Validation**: Each image is checked for:
   - Supported format (JPG/PNG)
   - Minimum width of 600px
   - File size limits
   - Image integrity

2. **Processing**: Valid images are:
   - Converted to RGB format
   - Auto-oriented based on EXIF data
   - Saved as high-quality JPEG files

3. **Output**: Processed images are saved with `_processed.jpg` suffix

## Error Handling

The system provides detailed error messages for:
- Invalid file formats
- Images below minimum width
- Corrupted image files
- File access issues

## Caching

Processed images are cached to avoid reprocessing. To force reprocessing, delete the `cache` folder.
