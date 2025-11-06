# EXIF Module Documentation

## Overview

The EXIF module provides structured extraction of photo metadata using a combination of data models and utility functions.

## Components

### Data Models (`lib/model/exif.py`)

**CameraInfo**
```python
@dataclass
class CameraInfo:
    make: Optional[str] = None
    model: Optional[str] = None
```
- Structured camera make/model information
- Handles missing camera data gracefully
- Provides `to_dict()` for JSON serialization

**ExifData**
```python
@dataclass
class ExifData:
    timestamp: Optional[datetime] = None
    subsecond: Optional[int] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    timezone_offset: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
```
- Structured EXIF metadata container
- Helper methods: `has_gps()`, `has_timestamp()`, `has_subsecond_precision()`
- Preserves raw EXIF data for extensibility

### Extraction Utilities (`lib/util/exif.py`)

**extract_exif_data(photo_path) → ExifData**
- Extracts structured EXIF metadata from photo files
- Uses piexif library (project dependency)
- Graceful error handling for missing/corrupted files
- Converts EXIF timestamp format to Python datetime

**extract_camera_info(photo_path) → CameraInfo**  
- Extracts camera make/model from EXIF
- Handles whitespace and encoding issues
- Returns empty CameraInfo for missing data

## EXIF Tag Handling

### Supported Tags
- `EXIF DateTimeOriginal` → `ExifData.timestamp`
- `EXIF SubSecTimeOriginal` → `ExifData.subsecond` 
- `EXIF OffsetTimeOriginal` → `ExifData.timezone_offset`
- `EXIF OffsetTimeDigitized` → `ExifData.timezone_offset` (fallback)
- `Image Make` → `CameraInfo.make`
- `Image Model` → `CameraInfo.model`

### Raw Data Preservation
- All EXIF tags stored in `ExifData.raw_data`
- Excludes binary data (thumbnails, maker notes)
- UTF-8 encoding with error handling
- Enables future feature extension

## Error Handling Strategy

### Graceful Degradation
```python
try:
    exif_dict = piexif.load(str(photo_path))
    # Extract data...
except (FileNotFoundError, OSError, piexif.InvalidImageDataError, ValueError):
    # Return empty data structures
    pass
```

### Principles
- **Never crash** on missing/corrupted files
- **Return valid objects** with None values
- **Preserve partial data** when possible
- **Log errors** in raw_data for debugging

## Usage Patterns

### Basic Extraction
```python
from lib.util.exif import extract_exif_data, extract_camera_info

exif_data = extract_exif_data(photo_path)
camera_info = extract_camera_info(photo_path)

if exif_data.has_timestamp():
    print(f"Photo taken: {exif_data.timestamp}")
```

### Integration with Templates
```python
from lib.template.filename import generate_filename

filename = generate_filename(
    camera_info=camera_info,
    exif_data=exif_data,
    collection="wedding"
)
```

## Testing Strategy

### Test Fixtures
- `create_photo_with_exif` fixture creates synthetic photos
- Uses piexif to inject test EXIF data
- Ephemeral files in tmp_path directories

### Coverage Areas
- **Valid EXIF data** - timestamp, camera, subsecond
- **Missing data** - no EXIF, partial EXIF
- **Invalid data** - corrupted timestamps, bad formats
- **Edge cases** - whitespace, encoding issues
- **Multiple cameras** - various make/model combinations

## Performance Considerations

### Optimizations
- **Single file read** per extraction function
- **Selective tag loading** where possible
- **Efficient string handling** for large raw_data
- **Minimal memory footprint** for synthetic test photos

### Future Improvements
- EXIF caching for repeated access
- Batch processing optimizations
- Memory-mapped file reading for large collections

## Dependencies

### Required
- `piexif` - EXIF data extraction (project dependency)
- `PIL.Image` - Image validation (project dependency)
- `pathlib` - File path handling (standard library)
- `datetime` - Timestamp processing (standard library)

### Design Decision: piexif vs exifread
- **Chosen**: piexif (already in project dependencies)
- **Consistency** with test fixture patterns
- **Lighter weight** than alternatives
- **Active maintenance** and Python 3.12 compatibility