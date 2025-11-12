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

## Filesystem Utilities Module

The `src/util/filesystem.py` module provides low-level filesystem operations for photo organization.

### Symlink Operations

#### `create_symlink(source, destination, atomic=True, progress_callback=None)`

Creates symlinks with atomic operations by default:

```python
from src.util.filesystem import create_symlink

# Basic usage
create_symlink(source_path, dest_path)

# With progress reporting
def progress_handler(message):
    print(f"Progress: {message}")

create_symlink(source_path, dest_path, progress_callback=progress_handler)

# Non-atomic operation (faster but not crash-safe)
create_symlink(source_path, dest_path, atomic=False)
```

**Features:**
- **Atomic operations**: Uses temporary file + rename for crash safety
- **Progress reporting**: Optional callback for UI integration
- **Parent directory creation**: Creates destination directories as needed
- **Error handling**: Clear exceptions for missing sources or existing destinations

#### `validate_symlink_integrity(symlink_path)`

Validates symlink targets exist:

```python
from src.util.filesystem import validate_symlink_integrity

is_valid = validate_symlink_integrity(symlink_path)
# Returns True if symlink exists and points to valid file
```

#### `detect_broken_symlinks(directory, progress_callback=None)`

Recursively finds broken symlinks with performance optimizations:

```python
from src.util.filesystem import detect_broken_symlinks

# Basic usage
broken_links = detect_broken_symlinks(dest_directory)
for broken_link in broken_links:
    print(f"Broken symlink: {broken_link}")

# With progress reporting for large directories
def scan_progress(scanned, total):
    print(f"Scanned {scanned}/{total} items")

broken_links = detect_broken_symlinks(dest_directory, progress_callback=scan_progress)
```

**Enhanced Features:**
- **Progress reporting**: Callback with scanned count and total items
- **Permission error handling**: Gracefully skips inaccessible files/directories
- **Performance optimization**: Two-pass scanning for accurate progress tracking

#### `scan_directory_symlinks(directory, progress_callback=None)`

Comprehensive directory analysis with file type categorization:

```python
from src.util.filesystem import scan_directory_symlinks

# Basic directory analysis
results = scan_directory_symlinks(directory)
print(f"Valid symlinks: {len(results['valid'])}")
print(f"Broken symlinks: {len(results['broken'])}")
print(f"Regular files: {len(results['regular_files'])}")
print(f"Directories: {len(results['directories'])}")

# With detailed progress reporting
def detailed_progress(status, current, total):
    print(f"{status} {current}/{total}")

results = scan_directory_symlinks(directory, progress_callback=detailed_progress)
```

**Return Format:**
```python
{
    'valid': [Path, ...],      # Working symlinks
    'broken': [Path, ...],     # Broken symlinks  
    'regular_files': [Path, ...], # Regular files
    'directories': [Path, ...]     # Subdirectories
}
```

#### `batch_validate_symlinks(symlinks, progress_callback=None)`

Efficient batch validation of multiple symlinks:

```python
from src.util.filesystem import batch_validate_symlinks

symlinks = [path1, path2, path3]

# Basic batch validation
results = batch_validate_symlinks(symlinks)
for symlink_path, is_valid in results.items():
    if not is_valid:
        print(f"Broken: {symlink_path}")

# With progress tracking
def validation_progress(completed, total):
    print(f"Validated {completed}/{total} symlinks")

results = batch_validate_symlinks(symlinks, progress_callback=validation_progress)
```

### File Hash Computation

#### `compute_file_hash(file_path, chunk_size=65536, progress_callback=None)`

Optimized SHA-256 hash computation:

```python
from src.util.filesystem import compute_file_hash

# Basic usage
file_hash = compute_file_hash(file_path)

# With progress reporting for large files
def hash_progress(bytes_read, total_size):
    percent = (bytes_read / total_size) * 100
    print(f"Hashing: {percent:.1f}%")

file_hash = compute_file_hash(file_path, progress_callback=hash_progress)

# Custom chunk size for performance tuning
file_hash = compute_file_hash(file_path, chunk_size=1024*1024)  # 1MB chunks
```

**Optimizations:**
- **64KB default chunks**: Optimal for most file sizes and storage types
- **Progress reporting**: Callback for long-running operations
- **Large file handling**: Efficient memory usage for multi-GB files
- **Configurable chunk size**: Tunable for specific performance requirements

## Current Limitations

1. **No recursion**: Photo manager only scans immediate source directory
2. **No nested structure handling**: Flat organization only  
3. **No file metadata preservation**: Only EXIF data extracted

## Filesystem Utilities vs Photo Manager

The filesystem utilities provide low-level operations, while photo manager provides high-level workflow:

| Component | Responsibility |
|-----------|---------------|
| `src/util/filesystem.py` | Atomic symlinks, hash computation, broken link detection |
| `src/manager/photo_manager.py` | Photo discovery, EXIF extraction, filename generation |

## Future Enhancements

**Recursive Directory Scanning:**
```python
def find_photos_recursive(source_dir: Path) -> List[Path]:
    """Recursively find photos in directory tree."""
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