"""Manifest management functionality."""

import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any, Union

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
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Invalid JSON or encoding issues
            return None
        except ValidationError:
            # Schema validation failed
            return None
        except Exception:
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
    
    def compute_file_hash(self, file_path: Union[Path, str]) -> str:
        """Compute SHA-256 hash of file contents.
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA-256 hash as string
        """
        file_path = Path(file_path)
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                # Read in chunks for memory efficiency with large files
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256_hash.update(chunk)
            
            return f"sha256-{sha256_hash.hexdigest()}"
        except (FileNotFoundError, OSError) as e:
            # Return error indicator for missing/unreadable files
            return f"error-{str(e)}"
    
    def needs_reprocessing(
        self, 
        source_path: Union[Path, str], 
        previous_hash: Optional[str] = None,
        previous_mtime: Optional[float] = None,
        dest_path: Optional[Union[Path, str]] = None
    ) -> bool:
        """Check if a photo needs reprocessing based on changes.
        
        Args:
            source_path: Path to source photo file
            previous_hash: Hash from previous manifest (if available)
            previous_mtime: Modification time from previous manifest (if available) 
            dest_path: Path to destination file to check if it exists
            
        Returns:
            True if file needs reprocessing, False if unchanged
        """
        source_path = Path(source_path)
        
        # File doesn't exist - can't process
        if not source_path.exists():
            return False
        
        # Check if destination file is missing
        if dest_path:
            dest_path = Path(dest_path)
            if not dest_path.exists():
                return True
        
        # Check mtime change (faster than hash computation)
        if previous_mtime is not None:
            current_mtime = source_path.stat().st_mtime
            if abs(current_mtime - previous_mtime) > 0.001:  # Allow for small float precision differences
                return True
        
        # Check hash change (more thorough but slower)
        if previous_hash is not None:
            current_hash = self.compute_file_hash(source_path)
            if current_hash != previous_hash:
                return True
        
        # If we have no previous data, assume it needs processing
        if previous_hash is None and previous_mtime is None:
            return True
        
        # No changes detected
        return False
    
    def config_affects_reprocessing(self, old_config: Dict[str, Any], new_config: Dict[str, Any]) -> bool:
        """Check if config changes affect photo processing results.
        
        Args:
            old_config: Previous configuration
            new_config: Current configuration
            
        Returns:
            True if config changes require reprocessing
        """
        # Check fields that affect filename generation
        filename_affecting_fields = ["collection_name"]
        
        for field in filename_affecting_fields:
            if old_config.get(field) != new_config.get(field):
                return True
        
        return False
    
    def destination_file_missing(self, source_path: Union[Path, str], dest_path: Union[Path, str]) -> bool:
        """Check if destination file (symlink) is missing.
        
        Args:
            source_path: Path to source photo
            dest_path: Expected path to destination symlink
            
        Returns:
            True if destination file is missing or broken
        """
        dest_path = Path(dest_path)
        
        # Destination doesn't exist
        if not dest_path.exists():
            return True
        
        # For symlinks, check if target still exists and is correct
        if dest_path.is_symlink():
            try:
                # Check if symlink target exists and points to correct source
                target = dest_path.resolve()
                expected_source = Path(source_path).resolve()
                return target != expected_source
            except (OSError, RuntimeError):
                # Broken symlink
                return True
        
        return False


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