"""Manifest management functionality."""

import json
from pathlib import Path
from typing import Optional

from jsonschema import ValidationError

from src.model.manifest import Manifest
from src.serializer.manifest import ManifestSerializer


class ManifestManager:
    """Manages manifest file operations."""
    
    def __init__(self, manifest_path: Optional[Path] = None):
        """Initialize manifest manager.
        
        Args:
            manifest_path: Path to manifest file (default: manifest.json in current dir)
        """
        self.manifest_path = manifest_path or Path("manifest.json")
        self.serializer = ManifestSerializer()
    
    def load_manifest(self) -> Optional[Manifest]:
        """Load existing manifest from file.
        
        Returns:
            Manifest object if file exists and is valid, None otherwise
        """
        if not self.manifest_path.exists():
            return None
            
        try:
            manifest_json = self.manifest_path.read_text(encoding='utf-8')
            return self.serializer.deserialize(manifest_json)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            # Invalid JSON or encoding issues
            return None
        except ValidationError as e:
            # Schema validation failed
            return None
        except Exception as e:
            # Unexpected errors (file permissions, etc.)
            return None
    
    def save_manifest(self, manifest: Manifest, validate: bool = True) -> None:
        """Save manifest to file with atomic write.
        
        Args:
            manifest: Manifest object to save
            validate: Whether to validate against schema before saving
            
        Raises:
            ValidationError: If validate=True and manifest is invalid
            OSError: If file cannot be written
        """
        manifest_json = self.serializer.serialize(manifest, validate=validate)
        
        # Atomic write: write to temp file first, then rename
        temp_path = self.manifest_path.with_suffix('.tmp')
        try:
            temp_path.write_text(manifest_json, encoding='utf-8')
            temp_path.replace(self.manifest_path)
        except Exception:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise
    
    def manifest_exists(self) -> bool:
        """Check if manifest file exists."""
        return self.manifest_path.exists()


def load_existing_manifest(manifest_path: Path) -> Optional[Manifest]:
    """Load existing manifest from specified path.
    
    Standalone function for loading manifests from any path.
    
    Args:
        manifest_path: Path to manifest.json file
        
    Returns:
        Manifest object if file exists and is valid, None otherwise
    """
    manager = ManifestManager(manifest_path)
    return manager.load_manifest()