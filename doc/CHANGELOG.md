# NormPic Development Changelog

## 2025-11-06

### EXIF Extraction and Filename Generation Implementation (TDD)

- **Architecture Decision**: Implemented template/util split pattern
  - `lib/util/exif.py` - Generic EXIF extraction utilities (reusable)
  - `lib/template/filename.py` - Domain-specific filename template application
- **Data Models**: Created structured EXIF data models
  - `CameraInfo` dataclass for camera make/model
  - `ExifData` dataclass for structured EXIF metadata
- **EXIF Utilities**: Comprehensive EXIF extraction
  - Extract timestamp, subsecond precision, camera info, timezone offset
  - Graceful handling of missing/corrupted EXIF data
  - Compatible with piexif library (existing project dependency)
- **Filename Templates**: Template-based filename generation
  - Format: `{collection-?}{YYYYMMDDTHHMMSS}{-camera?}{-counter?}.ext`
  - Camera code mapping (Canon R5→r5a, iPhone 15→i15, etc.)
  - Base32 counter system for burst sequences (0-V, 32 photos max)
- **TDD Implementation**: Integration-first approach
  - 5 integration tests for complete workflows
  - 48 unit tests for individual components
  - 68 total tests passing (100% success rate)
- **Test Infrastructure**: Shared fixtures and documentation
  - `create_photo_with_exif` fixture for ephemeral test photos
  - Comprehensive test documentation in `doc/test/`
  - Project-wide fixture availability via conftest.py
- **Specifications**: Adapted from deleteme-normpic-modules reference
  - Extracted specs from existing tests, not direct code copy
  - Modern implementation with structured data models
  - Clean separation of concerns (template vs utility functions)

### Earlier Today

- Project structure initialization with uv, Python 3.12+, ruff
- Added dependencies: click, Pillow, piexif, jsonschema, pytest  
- Created lib/ directory structure with model/, core/, manager/, util/, serializer/
- Installed pre-commit hook for commit message validation
- Added deleteme folder cleanup rules to CONTRIBUTE.md
- Designed versioned schema architecture with schema_v1.py approach
- Planned serializer pattern as peer directory to models
- Updated TODO.md with 3-commit implementation plan and migration system design
- Established pre-commit documentation process in CONTRIBUTE.md
- Added JSON schema v0.1.0 and data models (TDD approach)
- Created Pic, Manifest, Config dataclasses with validation
- Implemented ManifestSerializer with JSON serialization and schema validation
- Added comprehensive unit tests (20 passing tests)
- Established versioned schema architecture (schema_v0.py approach)
- Implemented serializer separation pattern (lib/serializer/ peer to lib/model/)
- Documented data models architecture and schema design decisions