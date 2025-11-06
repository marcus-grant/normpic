# Test Fixtures Documentation

## Overview

NormPic provides shared fixtures for creating synthetic photos with custom EXIF data. These fixtures ensure all file interactions use ephemeral, in-memory files.

## Primary Fixtures

### `create_photo_with_exif`

Factory fixture for creating test photos with custom EXIF data.

**Usage in Integration Tests:**
```python
def test_complete_workflow(create_photo_with_exif):
    """Test complete EXIF extraction → filename generation workflow."""
    photo = create_photo_with_exif(
        "canon_wedding.jpg",
        DateTimeOriginal="2024:10:05 14:30:45",
        SubSecTimeOriginal="123",
        Make="Canon",
        Model="EOS R5"
    )
    
    # Test complete workflow
    result = process_photo(photo)
    assert result.filename == "wedding-20241005T143045-r5a-0.jpg"
```

**Usage in Unit Tests:**
```python
def test_extract_timestamp(create_photo_with_exif):
    """Test timestamp extraction function."""
    photo = create_photo_with_exif(
        "test.jpg",
        DateTimeOriginal="2024:10:05 14:30:45"
    )
    
    # Test just the timestamp extraction
    timestamp = extract_timestamp(photo)
    assert timestamp == datetime(2024, 10, 5, 14, 30, 45)
```

**Supported EXIF Tags:**
- `DateTimeOriginal`: Photo creation timestamp  
- `SubSecTimeOriginal`: Subsecond precision
- `Make`: Camera manufacturer
- `Model`: Camera model
- `OffsetTimeOriginal`: Timezone offset
- `OffsetTimeDigitized`: Digitization timezone offset

### `sample_camera_data`

Provides common camera make/model combinations for testing.

**Usage:**
```python
def test_camera_codes(create_photo_with_exif, sample_camera_data):
    """Test camera code generation for various cameras."""
    canon_r5 = sample_camera_data["canon_r5"]
    photo = create_photo_with_exif("test.jpg", **canon_r5)
    
    camera_info = extract_camera_info(photo)
    assert camera_info.make == "Canon"
    assert camera_info.model == "EOS R5"
```

**Available Cameras:**
- `canon_r5`: Canon EOS R5
- `canon_r6`: Canon EOS R6  
- `nikon_d850`: Nikon D850
- `sony_a7r`: Sony A7R V
- `iphone_15`: Apple iPhone 15
- `iphone_14`: Apple iPhone 14
- `unknown`: No camera info

### `burst_sequence_timestamps`

Provides timestamp sequences for testing burst photo scenarios.

**Usage:**
```python
def test_burst_detection(create_photo_with_exif, burst_sequence_timestamps):
    """Test detection of burst photo sequences."""
    photos = []
    for i, timestamp in enumerate(burst_sequence_timestamps):
        photo = create_photo_with_exif(
            f"burst_{i}.jpg",
            DateTimeOriginal=timestamp,
            SubSecTimeOriginal=str(100 + i * 50),  # 100ms, 150ms, 200ms
            Make="Canon",
            Model="EOS R5"
        )
        photos.append(photo)
    
    bursts = detect_burst_sequences(photos)
    assert len(bursts) == 1
    assert len(bursts[0]) == 3
```

### `sample_gps_locations`

Provides GPS coordinates for testing location-based functionality.

**Usage:**
```python
def test_timezone_from_gps(sample_gps_locations):
    """Test timezone detection from GPS coordinates."""
    nyc = sample_gps_locations["nyc"]
    timezone = get_timezone_from_gps(nyc["lat"], nyc["lon"])
    assert timezone in ["-0400", "-0500"]  # EDT/EST
```

## Fixture Benefits

### Ephemeral Files
- All photos created in `tmp_path` directories
- Automatically cleaned up after each test
- No interference between tests

### Consistent Data
- Same fixture used across integration and unit tests
- Predictable EXIF data for reliable testing
- Easy to modify test scenarios

### Fast Execution
- Small 32x32 pixel synthetic images
- In-memory operations only
- No real file I/O overhead

### Type Safety
- Fixtures provide proper Path objects
- EXIF data properly encoded for piexif library
- Compatible with all EXIF extraction libraries

## Best Practices

### Naming Conventions
```python
# Good: Descriptive filename indicating test scenario
photo = create_photo_with_exif("canon_r5_burst_001.jpg", ...)

# Avoid: Generic names that don't indicate purpose  
photo = create_photo_with_exif("test.jpg", ...)
```

### EXIF Data
```python
# Good: Provide relevant EXIF for what you're testing
photo = create_photo_with_exif(
    "timestamp_test.jpg",
    DateTimeOriginal="2024:10:05 14:30:45"  # Only what's needed
)

# Avoid: Unnecessary EXIF data that doesn't relate to test
photo = create_photo_with_exif(
    "timestamp_test.jpg", 
    DateTimeOriginal="2024:10:05 14:30:45",
    Make="Canon",  # Not needed for timestamp test
    Model="EOS R5"
)
```

### Test Isolation
```python
# Good: Each test creates its own photos
def test_a(create_photo_with_exif):
    photo = create_photo_with_exif("test_a.jpg", ...)

def test_b(create_photo_with_exif):  
    photo = create_photo_with_exif("test_b.jpg", ...)

# Avoid: Sharing photos between tests
shared_photo = None
def test_a(create_photo_with_exif):
    global shared_photo
    shared_photo = create_photo_with_exif(...)
```