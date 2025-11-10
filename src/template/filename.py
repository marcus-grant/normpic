"""Domain-specific filename template generation."""

from datetime import datetime
from typing import Optional, Set
from src.model.exif import CameraInfo, ExifData

# Base32 alphabet for counter system (lexically ordered)
BASE32_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUV"


def generate_filename(
    camera_info: CameraInfo,
    exif_data: ExifData,
    collection: str,
    file_extension: str = ".jpg",
    existing_filenames: Optional[Set[str]] = None
) -> str:
    """Generate standardized filename from photo metadata.
    
    Format: {collection-?}{YYYYMMDDTHHMMSS}{-camera?}{-counter?}.ext
    
    Args:
        camera_info: Camera make/model information
        exif_data: EXIF metadata including timestamp
        collection: Collection name (can be empty)
        file_extension: File extension (default: .jpg)
        existing_filenames: Set of existing filenames to avoid collisions
        
    Returns:
        Generated filename string
    """
    # Build filename components
    parts = []
    
    # Collection prefix (optional)
    if collection:
        parts.append(collection)
    
    # Timestamp (required - use current time if missing)
    timestamp = exif_data.timestamp or datetime.now()
    timestamp_str = format_timestamp(timestamp)
    parts.append(timestamp_str)
    
    # Camera code (optional but defaults to 'unk')
    camera_code = get_camera_code(camera_info)
    parts.append(camera_code)
    
    # Build base filename
    base_filename = "-".join(parts)
    
    # Check if base filename is available (no counter needed)
    candidate_filename = f"{base_filename}{file_extension}"
    if not existing_filenames or candidate_filename not in existing_filenames:
        return candidate_filename
    
    # Base filename conflicts, need to add counter
    counter = find_available_counter(base_filename, file_extension, existing_filenames)
    counter_char = BASE32_ALPHABET[counter]
    
    # Final filename with counter
    return f"{base_filename}-{counter_char}{file_extension}"


def get_camera_code(camera_info: CameraInfo) -> str:
    """Generate 3-character camera code from camera info.
    
    Args:
        camera_info: Camera make and model information
        
    Returns:
        3-character lowercase camera code
    """
    if not camera_info.make and not camera_info.model:
        return "unk"
    
    # Combine make and model
    combined = f"{camera_info.make or ''} {camera_info.model or ''}".strip()
    
    # Known camera mappings
    camera_mappings = {
        "canon eos r5": "r5a",
        "canon eos r6": "r6a",
        "canon eos 5d": "5da", 
        "canon eos 6d": "6da",
        "nikon d850": "d85",
        "nikon d750": "d75",
        "sony a7r": "a7r",
        "sony a7 iii": "a73",
        "iphone 15": "i15",
        "iphone 14": "i14",
        "iphone 13": "i13",
        "iphone 12": "i12",
        "iphone": "iph",
    }
    
    combined_lower = combined.lower()
    
    # Check for exact matches first
    for pattern, code in camera_mappings.items():
        if pattern in combined_lower:
            return code
    
    # Fallback: take first 3 alphanumeric characters
    clean = ''.join(c for c in combined_lower if c.isalnum())
    if len(clean) >= 3:
        return clean[:3]
    elif len(clean) > 0:
        return clean.ljust(3, 'x')[:3]
    else:
        return "unk"


def format_timestamp(dt: datetime) -> str:
    """Format datetime as filename-safe timestamp.
    
    Args:
        dt: Datetime object
        
    Returns:
        Timestamp in format YYYYMMDDTHHMMSS
    """
    return dt.strftime("%Y%m%dT%H%M%S")


def find_available_counter(
    base_filename: str,
    file_extension: str,
    existing_filenames: Optional[Set[str]] = None
) -> int:
    """Find the next available counter for filename collision avoidance.
    
    Args:
        base_filename: Base filename without counter and extension
        file_extension: File extension
        existing_filenames: Set of existing filenames to check against
        
    Returns:
        Counter index (0-31 for Base32)
    """
    if not existing_filenames:
        return 0
    
    for counter in range(32):  # Base32 has 32 characters
        counter_char = BASE32_ALPHABET[counter]
        filename = f"{base_filename}-{counter_char}{file_extension}"
        if filename not in existing_filenames:
            return counter
    
    # If all 32 counters are taken, raise an error
    raise ValueError(f"Too many files with same timestamp and camera: {base_filename}")