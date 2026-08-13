# Template/Util Split Architecture Pattern

## Decision

Split functionality between generic utilities (`normpic/util/`) and domain-specific templates (`normpic/template/`) rather than using catch-all service directories.

## Context

During EXIF extraction and filename generation implementation, we needed to decide how to organize code that handles both generic operations (EXIF reading) and domain-specific business rules (filename templates).

## Options Considered

1. **Single Service Directory**: Put everything in `normpic/service/`
2. **Functional Split**: Separate by generic vs domain-specific purpose
3. **Feature Modules**: Group by complete feature areas

## Decision Rationale

**Chosen: Functional Split (Option 2)**

### Benefits

- **Clear Responsibility**: Generic utilities have no domain knowledge
- **Reusability**: `normpic/util/exif.py` can be used in any photo project
- **Maintainability**: Business rules separated from technical utilities
- **Testability**: Clear boundaries for unit testing
- **Extensibility**: Easy to add new templates without affecting utilities

### Implementation

```
normpic/
├── util/           # Generic utilities (reusable)
│   └── exif.py     # EXIF extraction, no domain knowledge
├── template/       # Domain-specific templates
│   └── filename.py # NormPic filename generation rules
```

## Examples

### Generic Utility (`normpic/util/exif.py`)

```python
def extract_exif_data(photo_path: Path) -> ExifData:
    """Extract EXIF data from any photo file - pure utility."""
    # No knowledge of NormPic's business rules
    # Returns structured data that any project can use
```

### Domain Template (`normpic/template/filename.py`)

```python
def generate_filename(camera_info: CameraInfo, exif_data: ExifData, collection: str) -> str:
    """Apply NormPic's specific filename template rules."""
    # Knows about NormPic's naming conventions
    # Applies business rules: collection-YYYYMMDDTHHMMSS-camera-counter.ext
```

## Anti-Patterns Avoided

- `normpic/service/` - Vague "service" responsibility
- `normpic/core/` - Generic "core" dumping ground  
- Mixing generic and domain code in same module

## Future Applications

This pattern already appears across the codebase:

- `normpic/util/filesystem.py` - Generic file operations
- `normpic/util/hash.py` - Generic file hashing
- `normpic/serializer/manifest.py` - Manifest serialization
- `normpic/manager/photo_manager.py` - Photo ordering and burst
  preservation rules

## Validation

- 68 tests pass with clear separation
- EXIF utilities have no NormPic dependencies
- Template functions compose utilities with business rules
- Easy to test each layer independently

