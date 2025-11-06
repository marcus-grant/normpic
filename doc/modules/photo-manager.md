# Photo Manager Module

## Overview

The `lib/manager/photo_manager.py` module provides complete photo collection organization workflow orchestration.

## Main Function

### `organize_photos(source_dir, dest_dir, collection_name, collection_description=None)`

**Purpose**: End-to-end photo organization workflow

**Process**:
1. Discovers photos in source directory (jpg, jpeg, png, heic, webp)
2. Extracts EXIF and camera metadata via `lib/util/exif.py`
3. Orders photos with burst preservation via `_order_photos_with_burst_preservation()`
4. Generates standardized filenames via `lib/template/filename.py`
5. Creates symlinks in destination directory
6. Generates and saves JSON manifest via `lib/serializer/manifest.py`

**Returns**: `Manifest` object with organized photo information

## Core Ordering Functions

### `_order_photos_with_burst_preservation(pics_data)`

**Purpose**: Main ordering algorithm preserving camera burst sequences

**Algorithm**:
- Groups photos by main timestamp (ignoring microseconds)
- For single-camera groups: maintains temporal order
- For multi-camera groups: groups by camera to prevent burst interleaving
- Orders camera groups by earliest photo's full timestamp

### `_order_photos_temporally(pics_data)`

**Purpose**: Basic temporal sorting with subsecond precision

**Sort Priority**:
1. EXIF timestamp availability
2. Full timestamp + subsecond precision  
3. Subsecond data availability
4. Filename lexical order

## Key Design Decisions

- **Burst Preservation**: Canon burst [A1,A3,A5] stays together despite iPhone [B2,B4] chronologically interrupting
- **Graceful Degradation**: Falls back to filename ordering when EXIF unavailable
- **Symlink Strategy**: Preserves originals while creating organized access layer
- **Schema Validation**: All manifests are JSON Schema validated

## Module Dependencies

- `lib/util/exif.py` - EXIF extraction
- `lib/template/filename.py` - Filename generation  
- `lib/serializer/manifest.py` - JSON serialization
- `lib/model/manifest.py` - Data structures