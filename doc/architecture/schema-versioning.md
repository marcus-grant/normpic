# Schema Versioning Architecture

## Overview

NormPic uses a versioned schema approach to enable manifest format evolution while maintaining backward compatibility.

## Design Decisions

### Python Module Approach

**Decision:** Store JSON schemas as Python constants in versioned modules rather than separate JSON files.

**Rationale:**
- No runtime file I/O or path resolution required
- Schemas are versioned with the code that uses them
- Easy imports: `from src.model.schema_v1 import MANIFEST_SCHEMA`
- Simplifies packaging and distribution
- Better testability - schemas are just Python objects

### Versioned Module Structure

```
src/model/
├── schema_v1.py    # Current schema (v1.0.0)
├── schema_v0.py    # Future: legacy compatibility
├── pic.py          # Data models
├── manifest.py
└── config.py
```

### Serializer Separation

**Decision:** Create `src/serializer/` as peer directory to `src/model/`.

**Rationale:**
- Serialization is a distinct architectural concern
- Models remain pure data structures
- Serializer can handle multiple formats (JSON, YAML, etc.)
- Cleaner separation of concerns for testing

### Migration System

**Future:** `src/migration/` will handle schema evolution:
- Automatic manifest version detection
- Migration scripts between versions
- Backward compatibility validation
- Rollback capability

## Implementation

Schema definitions use standard JSON Schema format stored as Python dictionaries with version constants for easy reference.