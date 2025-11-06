# Template/Util Split Architecture Pattern

## Decision

Split functionality between generic utilities (`lib/util/`) and domain-specific templates (`lib/template/`) rather than using catch-all service directories.

## Context

During EXIF extraction and filename generation implementation, we needed to decide how to organize code that handles both generic operations (EXIF reading) and domain-specific business rules (filename templates).

## Options Considered

1. **Single Service Directory**: Put everything in `lib/service/` 
2. **Functional Split**: Separate by generic vs domain-specific purpose
3. **Feature Modules**: Group by complete feature areas

## Decision Rationale

**Chosen: Functional Split (Option 2)**

### Benefits
- **Clear Responsibility**: Generic utilities have no domain knowledge
- **Reusability**: `lib/util/exif.py` can be used in any photo project
- **Maintainability**: Business rules separated from technical utilities
- **Testability**: Clear boundaries for unit testing
- **Extensibility**: Easy to add new templates without affecting utilities

### Implementation

```
lib/
├── util/           # Generic utilities (reusable)
│   └── exif.py     # EXIF extraction, no domain knowledge
├── template/       # Domain-specific templates
│   └── filename.py # NormPic filename generation rules
```

## Examples

### Generic Utility (`lib/util/exif.py`)
```python
def extract_exif_data(photo_path: Path) -> ExifData:
    """Extract EXIF data from any photo file - pure utility."""
    # No knowledge of NormPic's business rules
    # Returns structured data that any project can use
```

### Domain Template (`lib/template/filename.py`)
```python
def generate_filename(camera_info: CameraInfo, exif_data: ExifData, collection: str) -> str:
    """Apply NormPic's specific filename template rules."""
    # Knows about NormPic's naming conventions
    # Applies business rules: collection-YYYYMMDDTHHMMSS-camera-counter.ext
```

## Anti-Patterns Avoided

- ❌ `lib/service/` - Vague "service" responsibility
- ❌ `lib/core/` - Generic "core" dumping ground  
- ❌ Mixing generic and domain code in same module

## Future Applications

This pattern scales to other functionality:
- `lib/util/filesystem.py` - Generic file operations
- `lib/template/manifest.py` - Domain-specific manifest generation
- `lib/util/hash.py` - Generic file hashing
- `lib/template/organization.py` - Domain-specific photo ordering rules

## Validation

- ✅ 68 tests pass with clear separation
- ✅ EXIF utilities have no NormPic dependencies
- ✅ Template functions compose utilities with business rules
- ✅ Easy to test each layer independently