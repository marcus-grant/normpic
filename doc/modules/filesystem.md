# Filesystem Operations

## Overview

NormPic performs minimal filesystem operations, primarily focused on symlink creation. This document covers the current filesystem interactions.

## Symlink Operations

### Symlink Creation

Current implementation in `src/manager/photo_manager.py`:

```python
# Create symlinks for organized photos
for pic in pics:
    dest_path = dest_dir / pic.dest_path
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not dest_path.exists():
        source_path = Path(pic.source_path)
        dest_path.symlink_to(source_path.resolve())
```

**Key behaviors:**
- Creates parent directories as needed
- Uses absolute path resolution for symlinks
- Skips existing symlinks (no overwrite)
- Preserves original files (read-only approach)

### Directory Structure

```
source/                          # Original photos
├── IMG_001.jpg
├── IMG_002.jpg
└── IMG_003.jpg

destination/
├── manifest.json                # Generated manifest
└── wedding-25-11-07T103045-r5a.jpg -> /full/path/to/source/IMG_001.jpg
└── wedding-25-11-07T103047-r5a.jpg -> /full/path/to/source/IMG_002.jpg
```

## File Format Support

### Supported Extensions

Case-insensitive matching:
- `.jpg`, `.jpeg` - JPEG images
- `.png` - PNG images  
- `.heic` - iPhone HEIC format
- `.webp` - WebP images

### File Discovery

```python
photo_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.webp'}
source_photos = []

for file_path in source_dir.iterdir():
    if file_path.is_file() and file_path.suffix.lower() in photo_extensions:
        source_photos.append(file_path)
```

**Characteristics:**
- Flat directory scanning only (no recursion)
- Filters by file extension
- Ignores non-photo files
- Processes files in directory iteration order

## Path Handling

### Source Directory Validation

```python
def validate_paths(self) -> None:
    source_path = Path(self.source_dir)
    dest_path = Path(self.dest_dir)
    
    if not source_path.exists():
        raise ValueError(f"Source directory does not exist: {source_path}")
        
    if not source_path.is_dir():
        raise ValueError(f"Source path is not a directory: {source_path}")
    
    # Create destination directory if it doesn't exist
    dest_path.mkdir(parents=True, exist_ok=True)
```

### Path Resolution

- Source paths are resolved to absolute paths for symlinks
- Destination directories created recursively if needed
- No modification of source directory structure

## Current Limitations

1. **No recursion**: Only scans immediate source directory
2. **No broken symlink detection**: Doesn't check for or clean up broken symlinks  
3. **No hash computation**: File integrity not verified
4. **No nested structure handling**: Flat organization only
5. **No file metadata preservation**: Only EXIF data extracted

## Future Filesystem Features

### Planned Enhancements

**Recursive Directory Scanning:**
```python
def find_photos_recursive(source_dir: Path) -> List[Path]:
    """Recursively find photos in directory tree."""
    pass
```

**Broken Symlink Detection:**
```python
def detect_broken_symlinks(dest_dir: Path) -> List[Path]:
    """Find symlinks that point to missing files."""
    pass
```

**File Hash Computation:**
```python
def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of file contents."""
    pass
```

**Flat Structure Validation:**
```python
def warn_nested_structure(source_dir: Path) -> List[str]:
    """Warn if source directory contains nested subdirectories."""
    pass
```

## Error Handling

### Permission Errors

```python
try:
    dest_path.symlink_to(source_path.resolve())
except PermissionError:
    logger.error(f"Permission denied creating symlink: {dest_path}")
except OSError as e:
    logger.error(f"Failed to create symlink: {e}")
```

### Path Validation Errors

- Source directory doesn't exist
- Source path is a file, not directory  
- Destination directory not writable
- Symlink target becomes invalid

## Testing Approach

Current filesystem operations are tested with:
- Real temporary directories (`tempfile.TemporaryDirectory`)
- Real file creation and symlink operations
- Path validation with actual filesystem checks

No mocking of filesystem operations in main test suite for integration confidence.

## Security Considerations

- Symlinks use absolute paths to prevent relative path issues
- No modification of source files (read-only approach)
- Destination directory creation respects user permissions
- No following of existing symlinks during source scanning