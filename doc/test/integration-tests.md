# Integration Test Documentation

## Overview

Complex end-to-end test scenarios in `test/integration/test_photo_organization_workflow.py` validate complete workflow behavior with realistic photo collections.

## Test Scenarios

### `test_mixed_cameras_temporal_ordering_with_manifest()`

**Validates**: Multi-camera temporal ordering with complete manifest generation

**Test Setup**:
- Canon R5 photos: 14:30:45.123, 14:30:47.456 
- iPhone 15 Pro: 14:30:46.789
- Nikon D850: 14:30:47 (no subseconds)

**Expected Order**:
```
wedding-20241005T143045-r5a-0.jpg  # Canon early
wedding-20241005T143046-i15-0.jpg  # iPhone middle  
wedding-20241005T143047-d85-0.jpg  # Nikon (no subsec, filename DSC < IMG)
wedding-20241005T143047-r5a-0.jpg  # Canon late
```

**Assertions**:
- Proper temporal ordering despite filename differences
- Complete manifest with 4 photos
- Symlinks created correctly
- Manifest JSON round-trip serialization

### `test_burst_sequence_preservation()`

**Validates**: Burst sequences remain adjacent despite chronological interrupts

**Test Setup**:
- Canon burst: 14:30:45.100, 14:30:45.300, 14:30:45.400
- iPhone interrupt: 14:30:45.200 (chronologically between burst photos)

**Expected Behavior**:
- Canon photos stay consecutive: positions [0,1,2] or [1,2,3]
- iPhone does NOT interleave: [Canon, iPhone, Canon, Canon] ❌
- Burst counters increment: -0.jpg, -1.jpg, -2.jpg

### `test_fallback_ordering_without_exif()`

**Validates**: Graceful degradation when EXIF data unavailable

**Test Setup**:
- Files: photo_z_last.jpg, photo_a_first.jpg, photo_m_middle.jpg
- No EXIF metadata (raw bytes only)
- Reverse modification times vs filename order

**Expected Behavior**:
- Filename lexical order takes precedence over mtime
- Order: photo_a_first → photo_m_middle → photo_z_last  
- All photos have `timestamp_source="filename"`

## Test Infrastructure

**Fixtures Used**:
- `create_photo_with_exif()` - Creates realistic photos with controlled EXIF
- `tmp_path` - Isolated test directories
- Mock filesystem operations for deterministic testing

**Coverage Focus**:
- Complete workflow integration
- Edge case handling (missing EXIF, timestamp conflicts)
- Multi-camera coordination scenarios