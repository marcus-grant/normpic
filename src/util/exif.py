"""Generic EXIF extraction utilities."""

from pathlib import Path
from datetime import datetime
from typing import Union
import piexif

from src.model.exif import CameraInfo, ExifData


def extract_exif_data(photo_path: Union[Path, str]) -> ExifData:
    """Extract EXIF data from photo file.
    
    Args:
        photo_path: Path to the photo file
        
    Returns:
        ExifData object with extracted metadata
    """
    photo_path = Path(photo_path)
    exif_data = ExifData()
    
    try:
        # Load EXIF data using piexif
        exif_dict = piexif.load(str(photo_path))
        
        # Extract timestamp from EXIF DateTimeOriginal
        if "Exif" in exif_dict and piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
            datetime_bytes = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]
            datetime_str = datetime_bytes.decode() if isinstance(datetime_bytes, bytes) else str(datetime_bytes)
            try:
                exif_data.timestamp = datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
            except ValueError:
                # Invalid timestamp format - leave as None
                pass
        
        # Extract subsecond precision
        if "Exif" in exif_dict and piexif.ExifIFD.SubSecTimeOriginal in exif_dict["Exif"]:
            subsec_bytes = exif_dict["Exif"][piexif.ExifIFD.SubSecTimeOriginal]
            subsec_str = subsec_bytes.decode() if isinstance(subsec_bytes, bytes) else str(subsec_bytes)
            try:
                exif_data.subsecond = int(subsec_str)
            except ValueError:
                # Invalid subsecond format - leave as None
                pass
        
        # Extract timezone offset
        if "Exif" in exif_dict and piexif.ExifIFD.OffsetTimeOriginal in exif_dict["Exif"]:
            offset_bytes = exif_dict["Exif"][piexif.ExifIFD.OffsetTimeOriginal]
            exif_data.timezone_offset = offset_bytes.decode() if isinstance(offset_bytes, bytes) else str(offset_bytes)
        elif "Exif" in exif_dict and piexif.ExifIFD.OffsetTimeDigitized in exif_dict["Exif"]:
            offset_bytes = exif_dict["Exif"][piexif.ExifIFD.OffsetTimeDigitized]
            exif_data.timezone_offset = offset_bytes.decode() if isinstance(offset_bytes, bytes) else str(offset_bytes)
        
        # Store simplified raw EXIF data
        raw_data = {}
        for ifd_name, ifd in exif_dict.items():
            if isinstance(ifd, dict):
                for tag, value in ifd.items():
                    # Convert to readable format
                    try:
                        if isinstance(value, bytes):
                            raw_data[f"{ifd_name}_{tag}"] = value.decode('utf-8', errors='ignore')
                        else:
                            raw_data[f"{ifd_name}_{tag}"] = str(value)
                    except Exception:
                        # Skip problematic tags
                        pass
        exif_data.raw_data = raw_data
        
    except (FileNotFoundError, OSError, piexif.InvalidImageDataError, ValueError):
        # File doesn't exist, can't be read, or has no EXIF - return empty ExifData
        pass
    
    return exif_data


def extract_camera_info(photo_path: Union[Path, str]) -> CameraInfo:
    """Extract camera make and model from photo file.
    
    Args:
        photo_path: Path to the photo file
        
    Returns:
        CameraInfo object with camera metadata
    """
    photo_path = Path(photo_path)
    camera_info = CameraInfo()
    
    try:
        # Load EXIF data using piexif
        exif_dict = piexif.load(str(photo_path))
        
        # Extract camera make
        if "0th" in exif_dict and piexif.ImageIFD.Make in exif_dict["0th"]:
            make_bytes = exif_dict["0th"][piexif.ImageIFD.Make]
            make = make_bytes.decode() if isinstance(make_bytes, bytes) else str(make_bytes)
            camera_info.make = make.strip() if make else None
        
        # Extract camera model
        if "0th" in exif_dict and piexif.ImageIFD.Model in exif_dict["0th"]:
            model_bytes = exif_dict["0th"][piexif.ImageIFD.Model]
            model = model_bytes.decode() if isinstance(model_bytes, bytes) else str(model_bytes)
            camera_info.model = model.strip() if model else None
            
    except (FileNotFoundError, OSError, piexif.InvalidImageDataError, ValueError):
        # File doesn't exist, can't be read, or has no EXIF - return empty CameraInfo
        pass
    
    return camera_info