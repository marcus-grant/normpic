# Manifest Consumption Guide

## Overview

This guide explains how to consume and work with NormPic manifest files in parent projects. NormPic manifests are JSON Schema-validated files containing comprehensive metadata about organized photo collections, designed for integration with gallery builders and site generators.

## Manifest Format

### Basic Structure

NormPic generates JSON manifests following a versioned schema:

```json
{
  "version": "0.1.0",
  "collection_name": "wedding",
  "collection_description": "Wedding photos from August 2025",
  "generated_at": "2025-11-12T23:25:18.447340",
  "pics": [
    {
      "source_path": "/home/marcus/Pictures/wedding/full/4F6A5096.JPG",
      "dest_path": "wedding-20250809T132034-r5a.JPG",
      "hash": "sha256--8511790490321378394",
      "size_bytes": 26786754,
      "mtime": 1756291891.0,
      "timestamp": "2025-08-09T13:20:34",
      "timestamp_source": "exif",
      "camera": "Canon EOS R5",
      "gps": null,
      "errors": []
    }
  ],
  "processing_status": "completed",
  "total_pics": 645,
  "total_errors": 0,
  "total_warnings": 0
}
```

### Field Descriptions

**Collection Metadata**:
- `version`: Schema version for compatibility checking
- `collection_name`: Collection identifier (used in filenames)
- `collection_description`: Human-readable description
- `generated_at`: ISO timestamp of manifest generation
- `processing_status`: Overall processing result

**Per-Photo Metadata**:
- `source_path`: Original photo file location (absolute path)
- `dest_path`: Normalized filename (relative to manifest directory)
- `hash`: SHA-256 file hash for change detection
- `size_bytes`: File size in bytes
- `mtime`: Last modified timestamp (Unix epoch)
- `timestamp`: Photo creation time (ISO format)
- `timestamp_source`: Source of timestamp ("exif", "filename", "filesystem")
- `camera`: Camera make/model from EXIF
- `gps`: GPS coordinates if available (lat/lon object or null)
- `errors`: Array of error objects for this photo

## Loading and Parsing Manifests

### Python Implementation

**manifest_loader.py**:
```python
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PhotoMetadata:
    """Structured representation of photo metadata."""
    source_path: str
    dest_path: str
    hash: str
    size_bytes: int
    mtime: float
    timestamp: str
    timestamp_source: str
    camera: Optional[str]
    gps: Optional[Dict[str, float]]
    errors: List[Dict]
    
    @property
    def timestamp_dt(self) -> datetime:
        """Parse timestamp as datetime object."""
        return datetime.fromisoformat(self.timestamp)
    
    @property
    def filename_stem(self) -> str:
        """Get filename without extension."""
        return Path(self.dest_path).stem
    
    @property
    def file_extension(self) -> str:
        """Get file extension."""
        return Path(self.dest_path).suffix.lower()

@dataclass 
class ManifestData:
    """Complete manifest with metadata and photos."""
    version: str
    collection_name: str
    collection_description: Optional[str]
    generated_at: str
    pics: List[PhotoMetadata]
    processing_status: str
    total_pics: int
    total_errors: int
    total_warnings: int
    
    @property
    def generated_dt(self) -> datetime:
        """Parse generation timestamp as datetime."""
        return datetime.fromisoformat(self.generated_at)
    
    def get_photos_by_camera(self) -> Dict[str, List[PhotoMetadata]]:
        """Group photos by camera."""
        cameras = {}
        for pic in self.pics:
            camera = pic.camera or "Unknown"
            if camera not in cameras:
                cameras[camera] = []
            cameras[camera].append(pic)
        return cameras
    
    def get_photos_by_timespan(self, hours: int = 1) -> List[List[PhotoMetadata]]:
        """Group photos by time spans for gallery pagination."""
        if not self.pics:
            return []
        
        sorted_pics = sorted(self.pics, key=lambda p: p.timestamp_dt)
        groups = []
        current_group = [sorted_pics[0]]
        
        for pic in sorted_pics[1:]:
            time_diff = (pic.timestamp_dt - current_group[-1].timestamp_dt).total_seconds()
            
            if time_diff <= hours * 3600:  # Within timespan
                current_group.append(pic)
            else:  # Start new group
                groups.append(current_group)
                current_group = [pic]
        
        if current_group:
            groups.append(current_group)
        
        return groups

def load_manifest(manifest_path: Path) -> ManifestData:
    """Load and parse NormPic manifest file."""
    
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    
    try:
        with open(manifest_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in manifest: {e}")
    
    # Validate required fields
    required_fields = ['version', 'collection_name', 'generated_at', 'pics']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    # Parse photo metadata
    pics = []
    for pic_data in data['pics']:
        pic = PhotoMetadata(
            source_path=pic_data['source_path'],
            dest_path=pic_data['dest_path'], 
            hash=pic_data['hash'],
            size_bytes=pic_data['size_bytes'],
            mtime=pic_data['mtime'],
            timestamp=pic_data['timestamp'],
            timestamp_source=pic_data['timestamp_source'],
            camera=pic_data.get('camera'),
            gps=pic_data.get('gps'),
            errors=pic_data.get('errors', [])
        )
        pics.append(pic)
    
    # Create manifest object
    manifest = ManifestData(
        version=data['version'],
        collection_name=data['collection_name'],
        collection_description=data.get('collection_description'),
        generated_at=data['generated_at'],
        pics=pics,
        processing_status=data.get('processing_status', 'unknown'),
        total_pics=data.get('total_pics', len(pics)),
        total_errors=data.get('total_errors', 0),
        total_warnings=data.get('total_warnings', 0)
    )
    
    return manifest

def validate_manifest_compatibility(manifest: ManifestData) -> bool:
    """Check if manifest version is compatible with current code."""
    
    # Support version 0.1.0 and compatible versions
    supported_versions = ['0.1.0']
    return manifest.version in supported_versions
```

### Usage Example

```python
from pathlib import Path
from manifest_loader import load_manifest, validate_manifest_compatibility

# Load manifest
manifest_path = Path("content/photos/wedding/full/manifest.json")
manifest = load_manifest(manifest_path)

# Validate compatibility
if not validate_manifest_compatibility(manifest):
    raise RuntimeError(f"Unsupported manifest version: {manifest.version}")

# Access collection metadata
print(f"Collection: {manifest.collection_name}")
print(f"Generated: {manifest.generated_dt}")
print(f"Total photos: {len(manifest.pics)}")

# Work with photo data
for pic in manifest.pics[:5]:  # First 5 photos
    print(f"📸 {pic.dest_path}")
    print(f"   📅 {pic.timestamp} ({pic.timestamp_source})")
    print(f"   📷 {pic.camera or 'Unknown camera'}")
    print(f"   📏 {pic.size_bytes / 1024 / 1024:.1f} MB")

# Group by camera
cameras = manifest.get_photos_by_camera()
for camera, pics in cameras.items():
    print(f"{camera}: {len(pics)} photos")
```

## Change Detection

### Manifest Comparison

Use manifest hashes to detect changes requiring gallery regeneration:

```python
def compare_manifests(old_manifest: ManifestData, new_manifest: ManifestData) -> Dict:
    """Compare two manifests to detect changes."""
    
    if old_manifest.collection_name != new_manifest.collection_name:
        raise ValueError("Cannot compare manifests from different collections")
    
    # Create lookup dictionaries by dest_path
    old_pics = {pic.dest_path: pic for pic in old_manifest.pics}
    new_pics = {pic.dest_path: pic for pic in new_manifest.pics}
    
    # Detect changes
    added = set(new_pics.keys()) - set(old_pics.keys())
    removed = set(old_pics.keys()) - set(new_pics.keys())
    
    # Check for content changes (hash comparison)
    modified = set()
    for path in old_pics.keys() & new_pics.keys():
        if old_pics[path].hash != new_pics[path].hash:
            modified.add(path)
    
    # Check for metadata changes (timestamp, camera, etc.)
    metadata_changed = set()
    for path in old_pics.keys() & new_pics.keys():
        old_pic = old_pics[path]
        new_pic = new_pics[path]
        
        if (old_pic.timestamp != new_pic.timestamp or 
            old_pic.camera != new_pic.camera or
            old_pic.gps != new_pic.gps):
            metadata_changed.add(path)
    
    return {
        'added': sorted(added),
        'removed': sorted(removed),
        'modified': sorted(modified),
        'metadata_changed': sorted(metadata_changed),
        'total_changes': len(added) + len(removed) + len(modified),
        'requires_rebuild': bool(added or removed or modified or metadata_changed),
        'old_total': len(old_manifest.pics),
        'new_total': len(new_manifest.pics)
    }

def should_rebuild_gallery(changes: Dict, threshold: float = 0.1) -> bool:
    """Determine if gallery should be rebuilt based on changes."""
    
    # Always rebuild if photos added/removed
    if changes['added'] or changes['removed']:
        return True
    
    # Rebuild if significant portion modified
    if changes['old_total'] > 0:
        change_ratio = changes['total_changes'] / changes['old_total']
        if change_ratio > threshold:
            return True
    
    # Rebuild if metadata changed (affects gallery organization)
    if changes['metadata_changed']:
        return True
    
    return False
```

### Incremental Processing

```python
def get_changed_photos(changes: Dict, manifest_dir: Path) -> List[Path]:
    """Get list of photo files that need reprocessing."""
    
    changed_photos = []
    
    # New and modified photos need processing
    for dest_path in changes['added'] + changes['modified']:
        photo_path = manifest_dir / dest_path
        if photo_path.exists():
            changed_photos.append(photo_path)
    
    return changed_photos

def cleanup_removed_photos(changes: Dict, gallery_dir: Path):
    """Clean up gallery files for removed photos."""
    
    for dest_path in changes['removed']:
        # Remove thumbnails
        thumb_path = gallery_dir / "thumbnails" / dest_path
        if thumb_path.exists():
            thumb_path.unlink()
        
        # Remove any other generated assets
        stem = Path(dest_path).stem
        for asset_file in gallery_dir.glob(f"{stem}.*"):
            asset_file.unlink()
```

## Gallery Integration Patterns

### Photo Timeline Generation

```python
def generate_timeline(manifest: ManifestData) -> List[Dict]:
    """Generate chronological timeline for gallery display."""
    
    # Group photos by date
    timeline = {}
    for pic in manifest.pics:
        date = pic.timestamp_dt.date()
        if date not in timeline:
            timeline[date] = []
        timeline[date].append(pic)
    
    # Sort and format for gallery
    sorted_timeline = []
    for date in sorted(timeline.keys()):
        photos = sorted(timeline[date], key=lambda p: p.timestamp_dt)
        
        sorted_timeline.append({
            'date': date.isoformat(),
            'display_date': date.strftime('%B %d, %Y'),
            'photo_count': len(photos),
            'photos': [
                {
                    'filename': pic.dest_path,
                    'timestamp': pic.timestamp,
                    'camera': pic.camera,
                    'size_mb': pic.size_bytes / 1024 / 1024
                } for pic in photos
            ],
            'time_span': {
                'start': photos[0].timestamp,
                'end': photos[-1].timestamp
            }
        })
    
    return sorted_timeline
```

### Camera-Based Organization

```python
def generate_camera_galleries(manifest: ManifestData) -> Dict[str, List]:
    """Organize photos by camera for multi-photographer events."""
    
    galleries = {}
    cameras = manifest.get_photos_by_camera()
    
    for camera, pics in cameras.items():
        # Sort by timestamp
        sorted_pics = sorted(pics, key=lambda p: p.timestamp_dt)
        
        galleries[camera] = {
            'camera_name': camera,
            'photo_count': len(pics),
            'time_span': {
                'start': sorted_pics[0].timestamp,
                'end': sorted_pics[-1].timestamp
            },
            'photos': [
                {
                    'filename': pic.dest_path,
                    'timestamp': pic.timestamp,
                    'size_mb': pic.size_bytes / 1024 / 1024
                } for pic in sorted_pics
            ]
        }
    
    return galleries
```

### Burst Sequence Detection

```python
from datetime import timedelta

def detect_burst_sequences(manifest: ManifestData, max_gap_seconds: int = 5) -> List[List[PhotoMetadata]]:
    """Detect burst sequences for gallery grouping."""
    
    # Sort photos by timestamp
    sorted_pics = sorted(manifest.pics, key=lambda p: p.timestamp_dt)
    
    sequences = []
    current_sequence = []
    
    for pic in sorted_pics:
        if not current_sequence:
            current_sequence.append(pic)
            continue
        
        # Check if photo continues current sequence
        time_gap = pic.timestamp_dt - current_sequence[-1].timestamp_dt
        same_camera = pic.camera == current_sequence[-1].camera
        
        if time_gap <= timedelta(seconds=max_gap_seconds) and same_camera:
            current_sequence.append(pic)
        else:
            # Save current sequence if it has multiple photos
            if len(current_sequence) > 1:
                sequences.append(current_sequence)
            current_sequence = [pic]
    
    # Don't forget the last sequence
    if len(current_sequence) > 1:
        sequences.append(current_sequence)
    
    return sequences
```

## Error Handling

### Manifest Validation

```python
def validate_manifest_integrity(manifest: ManifestData, photos_dir: Path) -> List[str]:
    """Validate manifest against actual files."""
    
    errors = []
    
    for pic in manifest.pics:
        photo_path = photos_dir / pic.dest_path
        
        # Check if symlinked photo exists
        if not photo_path.exists():
            errors.append(f"Missing photo: {pic.dest_path}")
            continue
        
        # Verify file size matches
        actual_size = photo_path.stat().st_size
        if actual_size != pic.size_bytes:
            errors.append(f"Size mismatch for {pic.dest_path}: "
                         f"expected {pic.size_bytes}, got {actual_size}")
        
        # Check for symlink validity
        if photo_path.is_symlink() and not photo_path.readlink().exists():
            errors.append(f"Broken symlink: {pic.dest_path}")
    
    return errors

def handle_manifest_errors(manifest: ManifestData) -> bool:
    """Check for and handle photos with processing errors."""
    
    error_count = 0
    for pic in manifest.pics:
        if pic.errors:
            error_count += 1
            print(f"❌ Error in {pic.dest_path}:")
            for error in pic.errors:
                print(f"   {error}")
    
    if error_count > 0:
        print(f"\n⚠️  {error_count} photos had processing errors")
        return False
    
    return True
```

### Graceful Degradation

```python
def create_fallback_gallery(manifest: ManifestData, photos_dir: Path) -> List[Dict]:
    """Create simple gallery when complex processing fails."""
    
    valid_photos = []
    
    for pic in manifest.pics:
        photo_path = photos_dir / pic.dest_path
        
        # Only include photos that actually exist
        if photo_path.exists():
            valid_photos.append({
                'filename': pic.dest_path,
                'timestamp': pic.timestamp,
                'camera': pic.camera or 'Unknown',
                'has_errors': bool(pic.errors)
            })
    
    # Sort by filename if timestamp parsing fails
    try:
        valid_photos.sort(key=lambda p: p['timestamp'])
    except:
        valid_photos.sort(key=lambda p: p['filename'])
    
    return valid_photos
```

## Performance Optimization

### Lazy Loading

```python
class LazyManifest:
    """Manifest wrapper with lazy loading for large collections."""
    
    def __init__(self, manifest_path: Path):
        self.manifest_path = manifest_path
        self._manifest = None
        self._pics_by_camera = None
        self._timeline = None
    
    @property
    def manifest(self) -> ManifestData:
        if self._manifest is None:
            self._manifest = load_manifest(self.manifest_path)
        return self._manifest
    
    @property
    def pics_by_camera(self) -> Dict[str, List[PhotoMetadata]]:
        if self._pics_by_camera is None:
            self._pics_by_camera = self.manifest.get_photos_by_camera()
        return self._pics_by_camera
    
    def get_photos_page(self, page: int, page_size: int = 50) -> List[PhotoMetadata]:
        """Get paginated photos for large collections."""
        start_idx = page * page_size
        end_idx = start_idx + page_size
        return self.manifest.pics[start_idx:end_idx]
    
    def get_photo_count(self) -> int:
        """Get total photo count without loading full manifest."""
        return self.manifest.total_pics
```

### Caching

```python
import pickle
from hashlib import sha256

def cache_manifest_analysis(manifest_path: Path, analysis_func, cache_dir: Path):
    """Cache expensive manifest analysis results."""
    
    # Create cache key from manifest content hash
    manifest_hash = sha256(manifest_path.read_bytes()).hexdigest()[:16]
    cache_file = cache_dir / f"{analysis_func.__name__}_{manifest_hash}.pkl"
    
    # Return cached result if available
    if cache_file.exists():
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    # Compute and cache result
    manifest = load_manifest(manifest_path)
    result = analysis_func(manifest)
    
    cache_dir.mkdir(exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(result, f)
    
    return result

# Usage
timeline = cache_manifest_analysis(
    manifest_path, 
    generate_timeline, 
    cache_dir=Path(".cache/manifests")
)
```

## Next Steps

1. Implement manifest loading for your gallery builder
2. Add change detection to your build pipeline
3. See [Gallery Builder Integration Guide](gallery-builder-integration.md) for complete gallery generation
4. See [Deployment Integration Guide](deployment-integration.md) for CDN deployment strategies

For troubleshooting manifest issues, see the [Error Handling Guide](errors.md) and [Integration Guide](integration.md).