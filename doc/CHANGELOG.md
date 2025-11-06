# NormPic Development Changelog

## 2025-11-06

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