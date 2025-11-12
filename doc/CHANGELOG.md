# NormPic Development Changelog

## 2025-11-12

### Enhanced Filesystem Operations and Environment Variable Support

- **Enhanced Symlink Detection**: Added performance optimizations for large directory trees
  - Recursive directory scanning with progress reporting callbacks
  - Added `scan_directory_symlinks()` for comprehensive file type analysis
  - Added `batch_validate_symlinks()` for efficient bulk validation
  - Graceful handling of permission errors and inaccessible files
  - Added 9 comprehensive tests for new enhanced functionality
- **Secure Environment Variable Support**: Implemented NORMPIC_* environment variable parsing
  - Whitelisted approach: only reads specific NORMPIC_SOURCE_DIR, NORMPIC_DEST_DIR, NORMPIC_COLLECTION_NAME, NORMPIC_CONFIG_PATH
  - Environment variables override file configuration (precedence system)
  - All environment variables fully mocked during testing for security
  - Added integration test for config precedence workflow
  - Added 21 unit tests with comprehensive mocking coverage
- **Status**: All 195 tests passing, ruff checks passing, commits 8-9 complete

## 2025-11-11

### Error Handling Documentation and Mock Filesystem Testing

- **Comprehensive Error Documentation**: Created user-friendly error handling guides
  - Added `doc/guides/errors.md` with error interpretation and troubleshooting
  - Updated `doc/guides/README.md` to include error handling guide
  - Enhanced `doc/modules/schema.md` with new error schema structure
  - Documented error types, severity levels, and processing status
- **Mock Filesystem Testing**: Added deterministic testing utilities
  - Created comprehensive mock filesystem implementation (MockPath, MockFilesystem)
  - Added 11 tests covering all filesystem operations
  - Enabled testing without real filesystem dependencies
- **Filesystem Utilities**: Completed core filesystem operations
  - Symlink creation and validation with atomic operations
  - Broken symlink detection with recursive scanning
  - File hash computation (SHA-256) with progress callbacks
- **Status**: All 164 tests passing, ruff checks passing, commits 6-7 complete

## 2025-11-10

### Error Handling Refactor and Test Suite Corrections

- **Error Handling Optimization**: Streamlined error handling implementation
  - Replaced complex `ErrorResult` objects with simple `ErrorEntry` dataclass
  - Removed redundant severity field (intrinsic to error type)
  - Simplified manifest schema, ~60% memory reduction
- **Test Suite Filename Format Corrections**: Fixed filename generation tests
- **Removed Handoff Section**: Cleaned up TODO.md after reviewing handoff instructions
- **Fixed Test Expectations**: Updated 7 failing tests to match corrected filename format
  - Single photos with unique timestamps: No `-0` counter (e.g., `ceremony-20241005T163000-i15.heic`)
  - Mixed cameras with different timestamps: No counters needed
  - Burst sequences (same timestamp + same camera): All get counters starting with `-0`
- **Burst Collision Detection Enhancement**: Implemented proper burst sequence handling
  - Modified `_create_ordered_pics()` in photo_manager.py to group by timestamp+camera
  - Photos with same timestamp to the second AND same camera get sequential counters
  - Different cameras at same timestamp remain separate (no counters)
- **File Extension Fix**: Corrected filename generation to preserve original extensions (.heic, .jpg)
- **Test Restructuring**: Updated burst sequence test to use complete workflow instead of incremental filename generation
- **Status**: All 153 tests passing, ruff checks passing

## Previous Entry - 2025-11-10

### Error Handling Implementation Complete (TDD GREEN Phase)

- **Critical Filename Generation Bug Fix**: Discovered and fixed systematic issue with counter logic
  - **Issue**: Filename generation always added `-0` suffix even for unique timestamps
  - **Root Cause**: Logic always called counter function instead of checking if base filename was available
  - **Fix**: Modified `generate_filename()` to only add counters when actual filename conflicts occur
  - **Impact**: Eliminates unnecessary `-0` suffixes in real photo collections
- **Comprehensive Error Handling Implementation**: Full TDD GREEN phase completion
  - `src/util/error_handling.py`: Complete ErrorHandler with severity levels and processing status
  - `src/manager/photo_manager.py`: Integrated error handling throughout photo organization workflow
  - `src/model/manifest.py`: Enhanced with error/warning/processing_status fields
  - `src/serializer/manifest.py`: Updated deserializer to handle new optional fields
- **Error Processing Features**: Production-ready error handling capabilities
  - Graceful handling of unsupported formats (RAW/GIF/MP4) with INFO-level logging
  - Corrupted file detection with WARNING-level logging and continued processing
  - EXIF extraction failures with fallback to filesystem timestamps
  - Comprehensive processing status tracking in manifest output
  - Proper error categorization and summary statistics
- **Test Suite Updates**: Updated all tests to match corrected filename format
  - Fixed filename generation unit tests to expect no counters for unique timestamps
  - Updated integration tests to match corrected behavior
  - All error handling E2E tests passing with comprehensive coverage

## 2025-11-09

### Filesystem Utilities Implementation (Priority 3 TDD)

- **Filesystem Module**: Created `src/util/filesystem.py` with comprehensive utilities
  - `create_symlink()`: Atomic symlink creation with progress reporting
  - `validate_symlink_integrity()`: Symlink validation and target checking  
  - `detect_broken_symlinks()`: Recursive broken symlink detection
  - `compute_file_hash()`: Optimized SHA-256 computation with progress callbacks
- **Atomic Operations**: Symlinks use temporary file + rename for crash safety
- **Performance Optimizations**: 64KB chunk size for optimal hash computation
- **Progress Reporting**: Callback hooks for UI integration
- **Comprehensive Testing**: 23 unit tests + 2 integration tests
  - Full TDD RED-GREEN-REFACTOR cycle implementation
  - E2E workflow testing: symlink creation → validation → broken link detection
  - Error handling tests for edge cases and invalid inputs
- **Documentation Update**: Enhanced `doc/modules/filesystem.md` with usage examples
  - Added API documentation for all new functions
  - Performance optimization details and configuration options
  - Clear separation of concerns vs photo manager responsibilities

## 2025-11-07

### Manifest Loading Functionality (TDD Implementation)

- **Manifest Manager Enhancement**: Added `load_existing_manifest()` function
  - Implemented standalone function for loading manifests from any path
  - Added comprehensive unit tests with schema validation scenarios
  - Improved error handling with specific exception types (ValidationError, JSONDecodeError)
  - Enhanced `save_manifest()` with atomic write operations for data safety
  - Added UTF-8 encoding specification for better file handling
- **Integration Testing**: Created manifest loading workflow tests
  - Added `test/integration/test_manifest_loading_workflow.py`
  - E2E test validates manifest loading, validation, and reuse in photo organization
  - Verified compatibility with existing photo organization workflow
- **TDD Process**: Followed complete RED-GREEN-REFACTOR cycle
  - RED: Created failing E2E and unit tests
  - GREEN: Implemented minimal functionality to pass tests
  - REFACTOR: Added error handling, atomic writes, and better validation

### CLI Implementation (Complete MVP Feature)

- **CLI Implementation**: Full command-line interface for photo organization
  - Implemented `cli/main.py` using Click framework with all operational flags
  - Added `--dry-run`, `--verbose`, `--force`, `--config` flags  
  - Wire CLI to existing photo_manager workflow
  - Updated `main.py` to call CLI interface
- **Configuration Management**: JSON-based configuration system
  - Extended `src/model/config.py` with source_dir/dest_dir fields
  - Added JSON file loading with comprehensive validation
  - Implemented path validation and directory creation
  - Default config path: `./config.json`
- **Dry-run Support**: Added dry-run mode throughout photo workflow
  - Updated `src/manager/photo_manager.py` with dry_run parameter
  - Skip symlink creation in dry-run mode  
  - Generate `manifest.dryrun.json` instead of `manifest.json`
- **Comprehensive Testing**: Full TDD approach for new functionality
  - Added 12 unit tests for config JSON loading/validation (`test/unit/test_config.py`)
  - Added 11 CLI integration tests (`test/integration/test_cli.py`)  
  - All 101 tests passing, including existing photo workflow tests
- **Code Quality**: Clean implementation following project standards
  - Proper error handling and exit codes
  - Summary output: "Processed X pics, Y warnings, Z errors"
  - Ruff linting compliance

## 2025-11-06

### Documentation Update & Cleanup (Post-Feature)

- **Implementation Documentation**: Focused on actual code and complex tests
  - Created `doc/modules/photo-manager.md` - Documents photo_manager.py functions and orchestration
  - Created `doc/test/integration-tests.md` - Documents complex test scenarios and expected behaviors
  - Updated `doc/architecture/module-organization.md` with implemented modules list
- **Architecture Documentation**: Comprehensive updates for photo organization workflow
  - Updated `doc/architecture/README.md` with implemented photo_manager.py workflow
  - Added Manager Pattern documentation for `src/manager/photo_manager.py` 
  - Documented temporal ordering, burst preservation, and workflow orchestration
  - Updated system structure diagram to reflect actual implementation
- **Organization Algorithm Documentation**: Created detailed ordering algorithm docs
  - Created `doc/modules/organization.md` with EXIF timestamp → filename → mtime precedence hierarchy
  - Document burst sequence preservation (no camera interleaving)
  - Explain subsecond precision handling and temporal ordering algorithms
- **Documentation Index Updates**: Linked all new documentation properly
  - Updated `doc/README.md` project status to reflect completed photo organization workflow
  - Updated `doc/modules/README.md` and `doc/test/README.md` with new documentation links
  - Document 78 passing tests and readiness for CLI implementation
- **Cleanup Superseded Content**: Removed obsolete ordering logic from deleteme directory
  - Deleted `test_file_processing_dual.py` (complex batch processing superseded)
  - Deleted `file_processing.py` (dual collection logic superseded by simple workflow)
  - Focused cleanup on organization/ordering content replaced by new implementation

### Photo Organization and Processing Workflow (TDD)

- **Architecture Decision**: Implemented proper module organization in `src/manager/`
  - `src/manager/photo_manager.py` - High-level photo organization workflow orchestration
  - Follows documented architecture patterns (manager for orchestration, not catch-all core)
- **Ordering Algorithm**: EXIF timestamp → filename → mtime precedence
  - Subsecond precision handling for fine-grained temporal ordering
  - Graceful fallback when EXIF data unavailable
- **Burst Sequence Preservation**: No camera interleaving on shared timestamps  
  - Same camera photos stay together: [A1,A3,A5,B2,B4,B6] not [A1,B2,A3,B4,A5,B6]
  - Critical for maintaining burst shot continuity
- **Complete Workflow**: Source photos → organized symlinks + manifest.json
  - Integrates EXIF extraction, filename generation, and manifest serialization
  - Schema-validated JSON manifest with full photo metadata
- **Test Coverage**: 78 tests passing (integration + unit tests)
  - Integration tests for complete workflows with burst preservation
  - Unit tests for ordering algorithms and filename generation
  - Mock-based testing for file I/O isolation

## 2025-11-06 (Earlier)

### EXIF Extraction and Filename Generation Implementation (TDD)

- **Architecture Decision**: Implemented template/util split pattern
  - `src/util/exif.py` - Generic EXIF extraction utilities (reusable)
  - `src/template/filename.py` - Domain-specific filename template application
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
- Created src/ directory structure with model/, core/, manager/, util/, serializer/
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
- Implemented serializer separation pattern (src/serializer/ peer to src/model/)
- Documented data models architecture and schema design decisions