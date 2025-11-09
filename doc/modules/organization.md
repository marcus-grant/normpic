# Photo Organization Module

## Overview

The organization module (`src/manager/photo_manager.py`) implements the core photo ordering and organization workflow for NormPic. It ensures photos are arranged chronologically while preserving burst sequences from individual cameras.

## Ordering Algorithm

### Primary Ordering Hierarchy

Photos are ordered using a three-tier precedence system:

1. **EXIF timestamp** (highest priority)
2. **Filename sequence** (fallback)
3. **Filesystem mtime** (lowest priority)

### EXIF Timestamp Precedence

When EXIF timestamps are available:
- **Subsecond precision takes priority**: Photos with subsecond data sort before those without when main timestamp is identical
- **Full timestamp comparison**: Uses `timestamp.timestamp() + subsecond/1000.0` for precise ordering
- **Graceful degradation**: Photos without EXIF timestamps fall back to filename ordering

### Burst Sequence Preservation

The critical innovation is **burst preservation with no camera interleaving**:

#### Problem
When multiple cameras shoot simultaneously, naive timestamp ordering can interleave burst sequences:
```
Camera A: [photo1, photo3, photo5]  # burst sequence
Camera B: [photo2, photo4, photo6]  # burst sequence
Naive result: [A1, B2, A3, B4, A5, B6]  # broken bursts
```

#### Solution
The algorithm groups photos with shared main timestamps and preserves camera-specific burst sequences:

```python
def _order_photos_with_burst_preservation(pics_data):
    # 1. Sort all photos temporally first
    temporally_sorted = _order_photos_temporally(pics_data)
    
    # 2. Group consecutive photos with same main timestamp
    # 3. If multiple cameras in group, preserve burst sequences
    # 4. Order camera groups by earliest photo's full timestamp
```

#### Implementation Details

**Main Timestamp Grouping:**
- Groups photos by `timestamp.replace(microsecond=0)`
- Single camera groups maintain temporal order
- Multiple camera groups preserve burst sequences

**Camera Identification:**
- Uses `f"{camera.make}-{camera.model}"` as unique camera key
- Handles missing camera info gracefully with `"unknown-unknown"`

**Burst Sequence Ordering:**
- Each camera group is sorted by earliest photo's full timestamp (including subseconds)
- Camera groups are ordered relative to each other
- Within each camera group, photos maintain temporal order

## Result

Final photo order respects both temporal accuracy and burst integrity:
```
Desired result: [A1, A3, A5, B2, B4, B6]  # preserved bursts
```

## Key Functions

### `organize_photos()`
Main entry point that orchestrates the complete workflow:
- Photo discovery and filtering
- EXIF/camera metadata extraction  
- Temporal ordering with burst preservation
- Filename generation and symlink creation
- Manifest generation and serialization

### `_order_photos_with_burst_preservation()`
Implements the core burst preservation algorithm by:
- Temporal sorting first
- Grouping by main timestamp
- Camera-based burst grouping
- Ordered camera group arrangement

### `_order_photos_temporally()`
Handles basic temporal ordering with subsecond precision:
- EXIF timestamp priority
- Subsecond precision handling
- Filename fallback for missing timestamps

### `_create_ordered_pics()`
Creates final `Pic` objects with:
- Generated filenames via template system
- Metadata extraction and hash computation
- Proper timestamp source attribution

## Design Benefits

1. **Burst Integrity**: Photographers can review burst sequences without camera interleaving
2. **Temporal Accuracy**: Respects precise timestamps while preserving logical grouping
3. **Graceful Degradation**: Handles missing EXIF data appropriately
4. **Clear Algorithm**: Easy to test and verify behavior
5. **Performance**: Single-pass algorithm with minimal computational overhead