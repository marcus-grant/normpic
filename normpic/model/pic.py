"""Photo data model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

MISSING: object = object()

_TS_VALUES = frozenset({"exif", "filename", "filesystem", "unknown"})


@dataclass
class Pic:
    """Photo metadata record."""

    # Required fields
    hash: str
    size_bytes: int
    mtime: str
    relative_path: str

    # Optional fields
    timestamp: Optional[datetime] = None
    timestamp_source: Optional[str] = None
    camera: Optional[str] = None
    gps: Optional[Dict[str, float]] = None
    original_filename: Any = MISSING
    tag: Optional[List[str]] = None

    def __post_init__(self) -> None:
        """Validate fields at construction."""
        self.validate()

    def validate(self) -> None:
        """Validate field values; raise ValueError on any violation."""
        if self.original_filename is not MISSING:
            if self.original_filename is None:
                raise ValueError(
                    "original_filename cannot be None; omit the field if absent"
                )
            if self.original_filename == "":
                raise ValueError("original_filename must be a non-empty string")
            if "/" in self.original_filename or "\\" in self.original_filename:
                raise ValueError("original_filename must not contain path separators")
        if (
            self.timestamp_source is not None
            and self.timestamp_source not in _TS_VALUES
        ):
            raise ValueError(f"timestamp_source must be one of {sorted(_TS_VALUES)}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert Pic to dictionary for JSON serialization."""
        d: Dict[str, Any] = {
            "hash": self.hash,
            "relative_path": self.relative_path,
            "size_bytes": self.size_bytes,
            "mtime": self.mtime,
        }
        if self.timestamp is not None:
            d["timestamp"] = self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if self.timestamp_source is not None:
            d["timestamp_source"] = self.timestamp_source
        if self.camera is not None:
            d["camera"] = self.camera
        if self.gps is not None:
            d["gps"] = self.gps
        if self.original_filename is not MISSING:
            d["original_filename"] = self.original_filename
        if self.tag is not None:
            d["tag"] = self.tag
        return d
