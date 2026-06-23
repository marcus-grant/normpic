"""Photo data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

MISSING: object = object()


@dataclass
class Pic:
    """Photo metadata record."""

    # Required fields
    source_path: str
    dest_path: str
    hash: str
    size_bytes: int
    mtime: float

    # Optional fields
    timestamp: Optional[datetime] = None
    timestamp_source: Optional[str] = None
    camera: Optional[str] = None
    gps: Optional[Dict[str, float]] = None
    errors: List[str] = field(default_factory=list)
    original_filename: Any = MISSING

    def __post_init__(self) -> None:
        """Validate fields at construction."""
        if self.original_filename is not MISSING:
            if self.original_filename is None:
                raise ValueError(
                    "original_filename cannot be None; omit the field if absent"
                )
            if self.original_filename == "":
                raise ValueError("original_filename must be a non-empty string")
            if "/" in self.original_filename or "\\" in self.original_filename:
                raise ValueError(
                    "original_filename must not contain path separators"
                )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Pic to dictionary for JSON serialization."""
        d: Dict[str, Any] = {
            "source_path": self.source_path,
            "dest_path": self.dest_path,
            "hash": self.hash,
            "size_bytes": self.size_bytes,
            "mtime": self.mtime,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "timestamp_source": self.timestamp_source,
            "camera": self.camera,
            "gps": self.gps,
            "errors": self.errors,
        }
        if self.original_filename is not MISSING:
            d["original_filename"] = self.original_filename
        return d