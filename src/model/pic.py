"""Photo data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List, Any


@dataclass
class Pic:
    """Photo metadata record."""
    
    # Required fields
    source_path: str
    dest_path: str
    hash: str
    size_bytes: int
    mtime: float  # File modification time for change detection
    
    # Optional fields
    timestamp: Optional[datetime] = None
    timestamp_source: Optional[str] = None
    camera: Optional[str] = None
    gps: Optional[Dict[str, float]] = None
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert Pic to dictionary for JSON serialization."""
        return {
            "source_path": self.source_path,
            "dest_path": self.dest_path,
            "hash": self.hash,
            "size_bytes": self.size_bytes,
            "mtime": self.mtime,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "timestamp_source": self.timestamp_source,
            "camera": self.camera,
            "gps": self.gps,
            "errors": self.errors
        }