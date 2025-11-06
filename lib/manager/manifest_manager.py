"""Manifest management functionality."""

from pathlib import Path
from typing import Optional

from lib.model.manifest import Manifest
from lib.serializer.manifest import ManifestSerializer


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
            manifest_json = self.manifest_path.read_text()
            return self.serializer.deserialize(manifest_json)
        except Exception:
            # Invalid manifest file
            return None
    
    def save_manifest(self, manifest: Manifest, validate: bool = True) -> None:
        """Save manifest to file.
        
        Args:
            manifest: Manifest object to save
            validate: Whether to validate against schema before saving
        """
        manifest_json = self.serializer.serialize(manifest, validate=validate)
        self.manifest_path.write_text(manifest_json)
    
    def manifest_exists(self) -> bool:
        """Check if manifest file exists."""
        return self.manifest_path.exists()