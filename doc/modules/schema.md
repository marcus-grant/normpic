# JSON Schema v0.1.0

## Overview

NormPic uses JSON Schema to validate manifest structure, ensuring consistency and enabling interoperability with other tools like Galleria.

## Schema Design Decisions

### MVP Versioning (0.x)
- **Version**: `0.1.0` for MVP development
- **Rationale**: 0.x versions indicate pre-stable, personal project phase
- **Future**: v1.x will mark public-ready, stable API

### Schema as Python Constants
- **Location**: `lib/model/schema_v0.py`
- **Format**: Python dictionaries using JSON Schema specification
- **Benefits**: No runtime file I/O, schemas versioned with code, easy imports

### Required vs Optional Fields
- **Manifest Required**: `version`, `collection_name`, `generated_at`, `pics`
- **Manifest Optional**: `collection_description`, `config` (both nullable)
- **Pic Required**: `source_path`, `dest_path`, `hash`, `size_bytes`
- **Pic Optional**: `timestamp`, `timestamp_source`, `camera`, `gps`, `errors` (all nullable)

## Schema Structure

### Manifest Schema
```json
{
  "version": "0.1.0",
  "collection_name": "string",
  "generated_at": "2025-11-06T19:30:00Z",
  "pics": [...],
  "collection_description": "string|null",
  "config": "object|null"
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
  "errors": ["no_exif", "corrupted_file", "unsupported_format"]
}
```

## Timestamp Source Hierarchy
1. **exif**: EXIF timestamp with subsecond precision
2. **filename**: Extracted from filename patterns
3. **filesystem**: File modification time
4. **unknown**: Unable to determine timestamp

## Error Types
- **no_exif**: Photo lacks EXIF metadata
- **corrupted_file**: File is damaged or unreadable
- **unsupported_format**: File format not supported

## Usage
```python
from lib.model.schema_v0 import MANIFEST_SCHEMA, PIC_SCHEMA, VERSION
from jsonschema import validate

# Validate manifest
validate(instance=manifest_dict, schema=MANIFEST_SCHEMA)

# Check version
assert manifest["version"] == VERSION  # "0.1.0"
```

## Future Evolution
- Schema v1.x will add features like UTC offsets, multiple cameras per timestamp
- Migration system (`lib/migration/`) will handle version upgrades
- Backward compatibility maintained through versioned schema modules