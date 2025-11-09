"""EXIF and camera data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class CameraInfo:
    """Camera make and model information."""
    
    make: Optional[str] = None
    model: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert CameraInfo to dictionary for JSON serialization."""
        return {
            "make": self.make,
            "model": self.model
        }


@dataclass
class ExifData:
    """Structured EXIF metadata from photo files."""
    
    timestamp: Optional[datetime] = None
    subsecond: Optional[int] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    timezone_offset: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ExifData to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "subsecond": self.subsecond,
            "gps_latitude": self.gps_latitude,
            "gps_longitude": self.gps_longitude,
            "timezone_offset": self.timezone_offset,
            "raw_data": self.raw_data
        }
    
    def has_gps(self) -> bool:
        """Check if GPS coordinates are available."""
        return (self.gps_latitude is not None and 
                self.gps_longitude is not None)
    
    def has_timestamp(self) -> bool:
        """Check if timestamp is available."""
        return self.timestamp is not None
    
    def has_subsecond_precision(self) -> bool:
        """Check if subsecond precision is available."""
        return self.subsecond is not None