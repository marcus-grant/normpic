# Manifest Operations

## Overview

This document covers manifest file operations and management. For manifest structure and schema, see [schema.md](schema.md).

**⚠️ Note**: Integration patterns will evolve as more tools integrate with NormPic. This document will need updates.

## Manifest Operations

### Manifest Creation

Regular manifest creation (implemented in `lib/manager/photo_manager.py`):

```python
manifest = Manifest(
    version="0.1.0",
    collection_name=collection_name,
    generated_at=datetime.now(),
    pics=pics,
    collection_description=collection_description,
    config={"collection_name": collection_name}
)

# Save as manifest.json
manifest_file = dest_dir / "manifest.json"
serializer = ManifestSerializer()
manifest_json = serializer.serialize(manifest, validate=True)
manifest_file.write_text(manifest_json)
```

### Dry-Run Manifest Creation

When using `--dry-run` flag:

```python
# Same manifest creation, different filename
manifest_filename = "manifest.dryrun.json" if dry_run else "manifest.json"
manifest_file = dest_dir / manifest_filename
```

**Dry-run characteristics:**
- No symlinks created  
- Manifest shows what would be organized
- Useful for preview/validation before actual processing

### Manifest Loading (Future)

Planned functionality for incremental updates:

```python
# Load existing manifest with validation
def load_manifest(manifest_path: Path) -> Manifest:
    """Load and validate existing manifest."""
    pass

# Detect changes requiring reprocessing  
def detect_changes(manifest: Manifest, source_dir: Path) -> List[Change]:
    """Compare current state with manifest to find changes."""
    pass
```

**Change detection will check:**
- File hash changes (photo modified)
- Timestamp changes (EXIF data updated)
- Config changes (collection name, description)
- Missing destination files (broken symlinks)

### Atomic Manifest Updates (Future)

```python
# Write manifest atomically to prevent corruption
def write_manifest_atomic(manifest: Manifest, dest_path: Path) -> None:
    """Write manifest with atomic file replacement."""
    # Write to temp file first
    # Validate written content
    # Atomically replace existing manifest
    pass
```

## Integration with Other Tools

### Galleria (Static Gallery Builder)

Galleria consumes NormPic manifests to generate static photo galleries:

```json
{
  "version": "0.1.0",
  "collection_name": "wedding-photos",
  "generated_at": "2025-11-07T10:30:00Z",
  "pics": [
    {
      "source_path": "/photos/raw/IMG_001.jpg",
      "dest_path": "wedding-photos-25-11-07T103045-r5a.jpg", 
      "timestamp": "2025-11-07T10:30:45Z",
      "camera": "Canon EOS R5",
      "gps": {"lat": 40.7128, "lon": -74.0060}
    }
  ]
}
```

**Galleria usage pattern:**
1. NormPic organizes photos and creates manifest
2. Galleria reads manifest to understand photo metadata
3. Galleria generates HTML gallery with timeline, camera info, GPS data

### Future Integrations

**Photo Management Tools:**
- Import organized collections into Lightroom/Capture One
- Generate metadata sidecars for RAW processors
- Create albums/collections in photo management software

**Cloud Storage Sync:**
- S3/Google Cloud sync using manifest for metadata preservation
- Backup verification using manifest hashes
- Selective sync based on collection criteria

**Analysis Tools:**
- Photo statistics and analytics
- Timeline visualization 
- Camera usage analysis
- GPS track generation

## Manifest File Management

### File Locations

```
dest_directory/
├── manifest.json              # Regular processing result
├── manifest.dryrun.json       # Dry-run preview (temporary)
└── organized-photos/           # Symlinked photos
    ├── collection-25-11-07T103045-r5a.jpg
    └── collection-25-11-07T103047-r5a-1.jpg
```

### Cleanup Operations (Future)

```python
# Remove dry-run manifest after successful processing
def cleanup_dryrun_manifest(dest_dir: Path) -> None:
    """Remove manifest.dryrun.json after successful run."""
    dryrun_path = dest_dir / "manifest.dryrun.json" 
    if dryrun_path.exists():
        dryrun_path.unlink()
```

### Version Migration (Future)

```python
# Handle manifest schema version upgrades
def migrate_manifest(manifest_path: Path, target_version: str) -> Manifest:
    """Migrate manifest to newer schema version."""
    # Load current manifest
    # Detect schema version
    # Apply appropriate migration
    # Validate result
    pass
```

## Error Handling

### Validation Errors

```python
from jsonschema import ValidationError

try:
    serializer.serialize(manifest, validate=True)
except ValidationError as e:
    # Handle schema validation failure
    logger.error(f"Manifest validation failed: {e.message}")
```

### File System Errors

```python
try:
    manifest_file.write_text(manifest_json)
except PermissionError:
    # Handle write permission issues
    logger.error(f"Cannot write manifest: permission denied")
except OSError as e:
    # Handle disk space, path issues
    logger.error(f"Manifest write failed: {e}")
```

## Best Practices

1. **Always validate** manifest content before writing
2. **Use atomic writes** for manifest updates (when implemented)
3. **Clean up dry-run manifests** after successful processing
4. **Version manifests** with schema version for future compatibility
5. **Handle errors gracefully** with proper logging and recovery

## API Reference

See `lib/serializer/manifest.py` for current manifest serialization implementation.

Future manifest operations will be implemented in `lib/manager/manifest_manager.py`.