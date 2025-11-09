# Manifest Operations

## Overview

This document covers manifest file operations and management. For manifest structure and schema, see [schema.md](schema.md).

**⚠️ Note**: Integration patterns will evolve as more tools integrate with NormPic. This document will need updates.

## Manifest Operations

### Manifest Creation

Regular manifest creation (implemented in `src/manager/photo_manager.py`):

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

### Manifest Loading

Loading existing manifests for validation and reuse (implemented in `src/manager/manifest_manager.py`):

```python
from src.manager.manifest_manager import load_existing_manifest, ManifestManager
from pathlib import Path

# Using standalone function (recommended for one-time loading)
manifest_path = Path("dest_dir/manifest.json")
manifest = load_existing_manifest(manifest_path)

if manifest is not None:
    print(f"Loaded manifest for collection: {manifest.collection_name}")
    print(f"Contains {len(manifest.pics)} photos")
    print(f"Generated at: {manifest.generated_at}")
else:
    print("Manifest not found or invalid")

# Using ManifestManager class (recommended for multiple operations)
manager = ManifestManager(manifest_path)
if manager.manifest_exists():
    manifest = manager.load_manifest()
    # Process manifest...
```

**Loading behavior:**
- Returns `None` if file doesn't exist
- Returns `None` if JSON is malformed or schema validation fails  
- Supports full schema validation against current version (0.1.0)
- Handles encoding issues gracefully
- Safe error handling for file permission problems

**Error Handling:**
- JSON parsing errors → returns `None`
- Schema validation failures → returns `None`  
- File encoding issues → returns `None`
- File permission errors → returns `None`

This enables incremental processing workflows where existing manifests can be loaded and compared against current source files.

### Atomic Manifest Updates

Safe manifest writing to prevent corruption (implemented in `ManifestManager.save_manifest()`):

```python
from src.manager.manifest_manager import ManifestManager

manager = ManifestManager(manifest_path)

# Atomic write with temp file + rename
try:
    manager.save_manifest(manifest, validate=True)
    print("Manifest saved successfully")
except ValidationError as e:
    print(f"Manifest validation failed: {e}")
except OSError as e:
    print(f"Failed to write manifest: {e}")
```

**Atomic write process:**
1. Serialize manifest to JSON with validation
2. Write to temporary file (`manifest.tmp`)
3. Atomically rename temp file to final name
4. Clean up temp file on any errors

This prevents manifest corruption from interrupted writes or system crashes.

### Change Detection (Priority 2 - Future)

Planned functionality for incremental updates:

```python
# Detect changes requiring reprocessing  
def detect_changes(manifest: Manifest, source_dir: Path) -> List[Change]:
    """Compare current state with manifest to find changes."""
    # Will check:
    # - File hash changes (photo modified)
    # - Timestamp changes (EXIF data updated) 
    # - Config changes (collection name, description)
    # - Missing destination files (broken symlinks)
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

**Manifest Operations:**
- `src/manager/manifest_manager.py` - ManifestManager class and load_existing_manifest() function
- `src/serializer/manifest.py` - ManifestSerializer for JSON serialization/validation

**Current Implementation:**
- Manifest loading with validation ✓
- Atomic manifest writing ✓ 
- Error handling for common failure modes ✓

**Coming Next (Priority 2):**
- Change detection for incremental updates
- Dry-run manifest cleanup
- Manifest version migration system