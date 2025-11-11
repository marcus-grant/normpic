# JSON Schema v0.1.0

## Overview

NormPic uses JSON Schema to validate manifest structure, ensuring consistency and enabling interoperability with other tools like Galleria.

## Schema Design Decisions

### MVP Versioning (0.x)
- **Version**: `0.1.0` for MVP development
- **Rationale**: 0.x versions indicate pre-stable, personal project phase
- **Future**: v1.x will mark public-ready, stable API

### Schema as Python Constants
- **Location**: `src/model/schema_v0.py`
- **Format**: Python dictionaries using JSON Schema specification
- **Benefits**: No runtime file I/O, schemas versioned with code, easy imports

### Required vs Optional Fields
- **Manifest Required**: `version`, `collection_name`, `generated_at`, `pics`
- **Manifest Optional**: `collection_description`, `config`, `errors`, `warnings`, `processing_status` (all nullable)
- **Pic Required**: `source_path`, `dest_path`, `hash`, `size_bytes`, `mtime`
- **Pic Optional**: `timestamp`, `timestamp_source`, `camera`, `gps`, `errors` (all nullable)
- **Error Entry Required**: `error_type`, `source_file`
- **Error Entry Optional**: `details`

## Schema Structure

### Manifest Schema
```json
{
  "version": "0.1.0",
  "collection_name": "string",
  "generated_at": "2025-11-06T19:30:00Z",
  "pics": [...],
  "collection_description": "string|null",
  "config": "object|null",
  "errors": [...],
  "warnings": [...],
  "processing_status": {...}
}
```

### Pic Schema
```json
{
  "source_path": "/path/to/original.jpg",
  "dest_path": "/path/to/organized.jpg", 
  "hash": "sha256-hex-string",
  "size_bytes": 1024,
  "timestamp": "2025-11-06T19:30:00Z|null",
  "timestamp_source": "exif|filename|filesystem|unknown|null",
  "camera": "Canon EOS R5|null",
  "gps": {"lat": 40.7128, "lon": -74.0060}|null,
  "errors": []
}
```

### Error Entry Schema
```json
{
  "error_type": "corrupted_file",
  "source_file": "photo.jpg", 
  "details": "Invalid EXIF data: unexpected end of file"
}
```

### Processing Status Schema
```json
{
  "status": "completed_with_warnings",
  "total_files": 150,
  "processed_successfully": 147,
  "warnings_count": 3,
  "errors_count": 0,
  "files_skipped": 3
}
```

## Timestamp Source Hierarchy
1. **exif**: EXIF timestamp with subsecond precision
2. **filename**: Extracted from filename patterns
3. **filesystem**: File modification time
4. **unknown**: Unable to determine timestamp

## Error Types and Severity

### Info Level (Processing Continues)
- **`unsupported_format`**: File format not supported for photo processing
- **`file_skipped`**: File intentionally skipped for other reasons

### Warning Level (File Skipped, Processing Continues)  
- **`corrupted_file`**: File is damaged, corrupted, or unreadable
- **`exif_error`**: EXIF metadata extraction failed (may use fallback timestamp)

### Error Level (May Halt Processing)
- **`filesystem_error`**: File system access problems (permissions, I/O errors)
- **`validation_error`**: Manifest or configuration validation failures

Note: Severity level is intrinsic to error type - no separate severity field needed.

## Usage
```python
from src.model.schema_v0 import MANIFEST_SCHEMA, PIC_SCHEMA, ERROR_SCHEMA, VERSION
from jsonschema import validate

# Validate manifest
validate(instance=manifest_dict, schema=MANIFEST_SCHEMA)

# Validate individual error entries
for error in manifest_dict.get("errors", []):
    validate(instance=error, schema=ERROR_SCHEMA)

# Check version
assert manifest["version"] == VERSION  # "0.1.0"
```

## Future Evolution
- Schema v1.x will add features like UTC offsets, multiple cameras per timestamp
- Migration system (`src/migration/`) will handle version upgrades
- Backward compatibility maintained through versioned schema modules