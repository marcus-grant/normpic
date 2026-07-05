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
    pic: List[Pic]
    
    # Optional fields
    collection_description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    collection_root: str = "."

    def to_dict(self) -> Dict[str, Any]:
        """Convert Manifest to dictionary for JSON serialization."""
        result = {
            "version": self.version,
            "collection_name": self.collection_name,
            "generated_at": self.generated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "collection_root": self.collection_root,
            "pic": [p.to_dict() for p in self.pic],
        }
        
        # Add optional fields only if they have values
        if self.collection_description is not None:
            result["collection_description"] = self.collection_description
        if self.config is not None:
            result["config"] = self.config
        return result