"""Manifest management functionality."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, Union

from jsonschema import ValidationError

from normpic.util.hash import b2b120_hash

from ..model.manifest import Manifest
from ..model.pic import Pic
from ..serializer.manifest import ManifestSerializer
from ..util.manifest_validate import impl_validate


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
        try:
            return b2b120_hash(Path(file_path).read_bytes())
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
        
        # Check mtime change (faster than hash computation).
        # Normalize both sides to the manifest ISO format so the comparison is
        # at microsecond precision and not subject to sub-microsecond float drift.
        if previous_mtime is not None:
            current_mtime = source_path.stat().st_mtime
            _fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
            if (
                datetime.fromtimestamp(current_mtime, tz=timezone.utc).strftime(_fmt)
                != datetime.fromtimestamp(previous_mtime, tz=timezone.utc).strftime(_fmt)
            ):
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
    
    def needs_reprocessing_by_hash(
        self,
        current_hash: str,
        hash_index: Dict[str, "Pic"],
        current_mtime: float,
        dest_dir: Optional[Union[Path, str]] = None,
    ) -> bool:
        """Check if a photo needs reprocessing using a hash-keyed manifest index.

        Args:
            current_hash: b2b120 hash of the source file (caller-computed)
            hash_index: {hash: Pic} built from a prior manifest
            current_mtime: source file mtime as float timestamp (caller-computed)
            dest_dir: base directory for resolving matched_pic.relative_path; if
                None the dest-existence check is skipped

        Returns:
            True if file needs reprocessing (new or changed), False if unchanged
        """
        matched = hash_index.get(current_hash)
        if matched is None:
            return True

        if dest_dir is not None:
            dest_path = Path(dest_dir) / matched.relative_path
            if not dest_path.exists():
                return True

        _fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
        prev_mtime_float = datetime.fromisoformat(matched.mtime).timestamp()
        current_iso = datetime.fromtimestamp(current_mtime, tz=timezone.utc).strftime(_fmt)
        prev_iso = datetime.fromtimestamp(prev_mtime_float, tz=timezone.utc).strftime(_fmt)
        if current_iso != prev_iso:
            return True

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


def load_source_manifest(source_dir: Path) -> Optional[Manifest]:
    """Load and validate the source collection manifest, if present.

    Reads source_dir/manifest.json through both validation layers: schema
    (via ManifestManager.load_manifest) and impl (via impl_validate on the
    already-deserialized manifest dict). Returns None on any validation
    failure or if the file is absent.

    Args:
        source_dir: Source photo directory that may contain manifest.json

    Returns:
        Manifest object if present and valid at both layers, None otherwise
    """
    manifest_path = source_dir / "manifest.json"
    if not manifest_path.exists():
        return None

    manifest = ManifestManager(manifest_path).load_manifest()
    if manifest is None:
        return None

    errors = impl_validate(manifest.to_dict())
    if errors:
        return None

    return manifest


def build_source_manifest(source_dir: Path, collection_name: str) -> Manifest:
    """Scan source_dir and build a contract-shaped source Manifest.

    Args:
        source_dir: Source photo directory to scan
        collection_name: Name for the manifest's collection_name field

    Returns:
        Manifest covering all supported photos found in source_dir
    """
    photo_extensions = {".jpg", ".jpeg", ".png", ".heic", ".webp"}
    manager = ManifestManager()
    pics = []
    for f in sorted(source_dir.iterdir()):
        if not f.is_file() or f.suffix.lower() not in photo_extensions:
            continue
        stat = f.stat()
        file_hash = manager.compute_file_hash(f)
        mtime_str = datetime.fromtimestamp(
            stat.st_mtime, tz=timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        pics.append(Pic(
            hash=file_hash,
            size_bytes=stat.st_size,
            mtime=mtime_str,
            relative_path=f.name,
        ))
    return Manifest(
        version="0.1.0",
        collection_name=collection_name,
        generated_at=datetime.now(tz=timezone.utc),
        pic=pics,
        collection_root=".",
    )


def build_hash_keyed_source_index(manifest: Manifest) -> Dict[str, Pic]:
    """Build a hash-to-Pic index from a manifest's pic list.

    Args:
        manifest: Any Manifest whose pic list should be indexed by content hash

    Returns:
        {pic.hash: pic} mapping; on duplicate hash the first entry wins
    """
    index: Dict[str, Pic] = {}
    for pic in manifest.pic:
        if pic.hash not in index:
            index[pic.hash] = pic
    return index