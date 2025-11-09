"""Manifest data model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

from .pic import Pic


@dataclass
class Manifest:
    """Photo collection manifest."""
    
    # Required fields
    version: str
    collection_name: str
    generated_at: datetime
    pics: List[Pic]
    
    # Optional fields
    collection_description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert Manifest to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "collection_name": self.collection_name,
            "generated_at": self.generated_at.isoformat(),
            "pics": [pic.to_dict() for pic in self.pics],
            "collection_description": self.collection_description,
            "config": self.config
        }