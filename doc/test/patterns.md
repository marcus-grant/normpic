# Test Patterns Documentation

## Integration vs Unit Test Patterns

### Integration Test Patterns

Integration tests verify complete workflows and reveal missing implementations.

**Complete Workflow Pattern:**
```python
def test_photo_processing_workflow(create_photo_with_exif):
    """Test: Source photo → EXIF extraction → filename generation → result."""
    
    # Arrange: Create test photo with specific scenario
    photo = create_photo_with_exif(
        "wedding_photo.jpg",
        DateTimeOriginal="2024:10:05 14:30:45",
        SubSecTimeOriginal="123",
        Make="Canon", 
        Model="EOS R5"
    )
    
    # Act: Execute complete workflow
    result = process_photo_complete_workflow(photo, collection="wedding")
    
    # Assert: Verify end-to-end behavior
    assert result.source_path == photo
    assert result.dest_filename == "wedding-20241005T143045-r5a-0.jpg"
    assert result.camera_info.make == "Canon"
    assert result.camera_info.model == "EOS R5"
```

**Multi-Photo Scenario Pattern:**
```python
def test_burst_sequence_workflow(create_photo_with_exif):
    """Test: Multiple photos → burst detection → sequential naming."""
    
    # Arrange: Create burst sequence
    photos = []
    for i in range(3):
        photo = create_photo_with_exif(
            f"burst_{i:03d}.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            SubSecTimeOriginal=str(100 + i * 50),  # 100ms intervals
            Make="Canon",
            Model="EOS R5"
        )
        photos.append(photo)
    
    # Act: Process as batch
    results = process_photo_batch(photos, collection="ceremony")
    
    # Assert: Verify burst handling
    assert len(results) == 3
    assert results[0].dest_filename.endswith("-0.jpg")
    assert results[1].dest_filename.endswith("-1.jpg") 
    assert results[2].dest_filename.endswith("-2.jpg")
```

### Unit Test Patterns

Unit tests focus on individual functions and components.

**Single Function Test Pattern:**
```python
def test_extract_camera_info(create_photo_with_exif):
    """Test: Photo → camera info extraction."""
    
    # Arrange: Create photo with camera EXIF
    photo = create_photo_with_exif(
        "camera_test.jpg",
        Make="Canon",
        Model="EOS R5"
    )
    
    # Act: Test specific function
    camera_info = extract_camera_info(photo)
    
    # Assert: Verify specific behavior
    assert camera_info.make == "Canon"
    assert camera_info.model == "EOS R5"
```

**Data Transformation Test Pattern:**
```python
def test_generate_camera_code():
    """Test: Camera info → camera code transformation."""
    
    # Arrange: Create data structure (no file needed)
    camera_info = CameraInfo(make="Canon", model="EOS R5")
    
    # Act: Test pure function
    code = generate_camera_code(camera_info)
    
    # Assert: Verify transformation
    assert code == "r5a"
```

**Edge Case Test Pattern:**
```python
def test_extract_timestamp_no_exif(create_photo_with_exif):
    """Test: Photo without EXIF → graceful handling."""
    
    # Arrange: Create photo with no EXIF data
    photo = create_photo_with_exif("no_exif.jpg")  # No kwargs = no EXIF
    
    # Act: Test function handles missing data
    timestamp = extract_timestamp(photo)
    
    # Assert: Verify graceful degradation
    assert timestamp is None
```

## TDD Discovery Pattern

### RED Phase: Write Failing Test
```python
def test_feature_that_doesnt_exist_yet(create_photo_with_exif):
    """Test for functionality that doesn't exist yet."""
    
    photo = create_photo_with_exif("test.jpg", DateTimeOriginal="2024:10:05 14:30:45")
    
    # This will fail - function doesn't exist
    result = function_that_doesnt_exist_yet(photo)
    
    assert result.expected_property == "expected_value"
```

**Expected Result:** ImportError or NameError - function doesn't exist

### GREEN Phase: Minimal Implementation
```python
# src/util/example.py
def function_that_doesnt_exist_yet(photo_path):
    """Minimal implementation to make test pass."""
    # Return just enough to satisfy the test
    return SimpleResult(expected_property="expected_value")
```

**Expected Result:** Test passes

### REFACTOR Phase: Improve Implementation
```python  
# src/util/example.py
def function_that_doesnt_exist_yet(photo_path):
    """Improved implementation with proper logic."""
    # Add real EXIF extraction, error handling, etc.
    exif_data = extract_exif_from_file(photo_path)
    return ProcessedResult(
        expected_property=process_exif_data(exif_data),
        additional_properties=...
    )
```

## Common Test Scenarios

### Camera Diversity Testing
```python
@pytest.mark.parametrize("camera_name", [
    "canon_r5", "canon_r6", "nikon_d850", "sony_a7r", "iphone_15"
])
def test_camera_support(create_photo_with_exif, sample_camera_data, camera_name):
    """Test camera code generation for various camera types."""
    camera_data = sample_camera_data[camera_name]
    photo = create_photo_with_exif("test.jpg", **camera_data)
    
    camera_info = extract_camera_info(photo)
    code = generate_camera_code(camera_info)
    
    # Verify each camera gets appropriate code
    assert len(code) == 3
    assert code.isalnum()
```

### Timestamp Edge Cases
```python
@pytest.mark.parametrize("timestamp,expected", [
    ("2024:01:01 00:00:00", datetime(2024, 1, 1, 0, 0, 0)),
    ("2024:12:31 23:59:59", datetime(2024, 12, 31, 23, 59, 59)),
    ("invalid:timestamp", None),  # Should handle gracefully
])
def test_timestamp_parsing(create_photo_with_exif, timestamp, expected):
    """Test timestamp parsing edge cases."""
    photo = create_photo_with_exif("test.jpg", DateTimeOriginal=timestamp)
    result = extract_timestamp(photo)
    assert result == expected
```

### Error Handling Pattern
```python
def test_corrupted_file_handling(tmp_path):
    """Test handling of corrupted or invalid files."""
    # Create invalid file 
    corrupted_file = tmp_path / "corrupted.jpg"
    corrupted_file.write_bytes(b"not a valid image")
    
    # Should handle gracefully without crashing
    result = extract_exif_data(corrupted_file)
    assert result.errors == ["corrupted_file"]
    assert result.camera_info is None
    assert result.timestamp is None
```

## Test Organization Best Practices

### File Naming
```
test/integration/
├── test_complete_workflows.py      # End-to-end scenarios
├── test_batch_processing.py        # Multi-photo workflows  
└── test_error_scenarios.py         # Error handling workflows

test/unit/
├── test_exif_extraction.py         # EXIF utility functions
├── test_filename_generation.py     # Filename template functions
├── test_camera_codes.py            # Camera code mapping
└── test_data_models.py             # Dataclass behavior
```

### Test Function Naming
```python
# Integration tests: describe complete scenario
def test_canon_r5_wedding_photo_complete_processing()
def test_iphone_burst_sequence_with_gps()
def test_mixed_camera_collection_ordering()

# Unit tests: describe specific function behavior  
def test_extract_timestamp_with_subsecond_precision()
def test_generate_camera_code_for_unknown_camera()
def test_format_filename_with_missing_collection()
```