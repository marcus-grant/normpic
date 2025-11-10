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
    errors: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[Dict[str, Any]]] = None
    processing_status: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert Manifest to dictionary for JSON serialization."""
        result = {
            "version": self.version,
            "collection_name": self.collection_name,
            "generated_at": self.generated_at.isoformat(),
            "pics": [pic.to_dict() for pic in self.pics],
        }
        
        # Add optional fields only if they have values
        if self.collection_description is not None:
            result["collection_description"] = self.collection_description
        if self.config is not None:
            result["config"] = self.config
        if self.errors is not None:
            result["errors"] = self.errors
        if self.warnings is not None:
            result["warnings"] = self.warnings
        if self.processing_status is not None:
            result["processing_status"] = self.processing_status
            
        return result