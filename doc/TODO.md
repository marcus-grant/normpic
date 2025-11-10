# NormPic - Photo Organization & Manifest Generator TODO

## Current Status: Priority 3 COMPLETED

Complete MVP + Incremental Processing + Filesystem Utilities: 140 passing tests

**Critical Technical Details:**
- This is a uv-managed project: Use `uv run pytest` (NOT `python -m pytest`)
- Source code location: `src/` directory
- Test command: `uv run pytest test/` for full suite
- Linting: `uv run ruff check` (must pass before commits)

## Detailed Implementation Plan - Ready to Execute

The following 12 commits will complete all remaining MVP tasks. Each step includes validation requirements and commit messages.

### ✅ Commit 1: Error Handling E2E Test (RED Phase) - COMPLETED
**Files created**: `test/integration/test_error_handling_workflow.py`
**Task**: Create failing E2E test with comprehensive file format testing
- Test mix: JPEG/PNG (supported), RAW/GIF/MP4 (unsupported), corrupted files
- Test scenarios: mixed formats, all corrupted, partial processing with mixed scenarios
- Test assertions: supported files processed, unsupported skipped with warnings, processing continues
**Validation**: Tests fail as expected, `uv run ruff check` passes ✅
**Commit**: `Tst: Add error handling workflow tests (RED phase)` - a92859f

### ✅ Commit 2: Error Handling Unit Tests - COMPLETED
**Files created**: `test/unit/test_error_handling.py`
**Task**: Create unit tests for specific error scenarios
- `test_skip_corrupted_file_continue_processing()`, `test_log_warnings_to_manifest()`
- `test_validate_manifest_before_write()`, `test_error_severity_levels()`
- Mock all filesystem and EXIF operations for deterministic testing
**Validation**: Unit tests fail as expected, `uv run ruff check` passes ✅
**Commit**: `Tst: Add error handling unit tests` - b870276

### ✅ Commit 3: Schema Updates for Error Handling - COMPLETED
**Files modified**: `src/model/schema_v0.py`, `test/unit/test_schema.py`
**Task**: Add error/warning fields to manifest schema
- Added ERROR_SCHEMA with structured error information (type, severity, message, timestamp)
- Enhanced PIC_SCHEMA with `errors`, `warnings`, `processing_status` fields
- Added global error tracking and processing summary to MANIFEST_SCHEMA
- Updated existing test to use new structured error format
**Validation**: `uv run pytest` (existing tests pass, new tests still fail), `uv run ruff check` ✅
**Commit**: `Ft: Add error/warning fields to manifest schema` - 854cb66

### Commit 4: Error Handling Implementation (GREEN Phase)
**Files to create/modify**: `src/util/error_handling.py`, `src/manager/photo_manager.py`, data models
**Task**: Implement minimal error handling to make E2E test pass
- Create ErrorHandler class, ErrorSeverity/ErrorType enums
- Integrate error collection into photo processing workflow
- Use iterative test-driven approach: run test → implement minimum → repeat
**Validation**: `uv run pytest` (all tests including new ones pass), `uv run ruff check`
**Commit**: `Ft: Implement error handling throughout photo workflow`

### Commit 5: Error Handling Refactor
⚠️ **PAUSE FOR DESIGN REVIEW**: Consider simple string lists vs complex error objects
**Task**: Optimize error handling implementation based on actual usage
- Standardize error message formats, optimize performance
- Decide on final error representation format (strings vs objects)
**Validation**: `uv run pytest`, `uv run ruff check`
**Commit**: `Ref: Optimize error handling implementation`

### Commit 6: Error Handling Documentation
**Files to create/modify**: `doc/guides/errors.md`, `doc/guides/README.md`, `doc/modules/schema.md`, `doc/CHANGELOG.md`
**Task**: Create comprehensive error handling documentation
- User guide for interpreting errors, schema documentation updates
**Validation**: Documentation links work correctly
**Commit**: `Doc: Add comprehensive error handling documentation`

### Commit 7: Mock Filesystem Testing
**Files to create**: `test/unit/test_filesystem_mock.py`
**Task**: Add mock filesystem utilities for deterministic testing
- Create comprehensive filesystem mocking for all filesystem operations
**Validation**: `uv run pytest test/unit/test_filesystem_mock.py -v`, full suite, `uv run ruff check`
**Commit**: `Tst: Add mock filesystem utilities for deterministic testing`

### Commit 8: Enhanced Symlink Detection
**Files to modify**: `src/util/filesystem.py`
**Task**: Enhance broken symlink detection with performance optimizations
- Add recursive directory scanning, progress reporting for large trees
**Validation**: `uv run pytest test/unit/test_filesystem_utils.py -v`, full suite, `uv run ruff check`
**Commit**: `Ft: Enhance broken symlink detection with performance optimizations`

### Commit 9: Environment Variable Support
⚠️ **SECURITY WARNING**: Only read specific NORMPIC_* variables, never shell enumeration
**Files to create**: `src/manager/config_manager.py`
**Task**: Add secure environment variable parsing
- Only read: NORMPIC_SOURCE_DIR, NORMPIC_DEST_DIR, NORMPIC_COLLECTION_NAME, NORMPIC_CONFIG_PATH
- Mock all environment variables during testing (use `unittest.mock.patch.dict`)
**Validation**: `uv run pytest test/unit/test_config_manager.py -v`, full suite, `uv run ruff check`
**Commit**: `Ft: Add secure NORMPIC_* environment variable support`

### Commit 10: Config Precedence System
**Files to modify**: `src/manager/config_manager.py`, `src/cli/main.py`
**Task**: Implement config precedence system
- Precedence order: defaults < config file < environment variables < CLI arguments
- Create integration tests for all precedence combinations
**Validation**: `uv run pytest test/integration/test_config_precedence.py -v`, full suite, `uv run ruff check`
**Commit**: `Ft: Implement config precedence system (defaults < file < env < cli)`

### Commit 11: Performance Documentation
**Files to create**: `doc/analysis/performance.md`
**Task**: Create performance baselines with reproducibility information
- Record exact commit hash and complete hardware specifications
- Document CPU, RAM, storage, OS details for benchmark reproduction
- Include benchmark reproduction guide and hardware comparison template
**📋 REMINDER**: Ask user about parent project's real-world timestamped photo document
**Validation**: Documentation links work correctly
**Commit**: `Doc: Add performance baseline with hardware specs and reproducible benchmarks`

### Commit 12: Timestamp Analysis Documentation
**Files to create**: `doc/analysis/timestamps.md`
**Task**: Document timestamp analysis and systematic offset findings
- Camera-specific timestamp accuracy, systematic offset patterns
- Configuration examples for common camera corrections
**Validation**: Documentation links work correctly
**Commit**: `Doc: Add timestamp analysis and systematic offset documentation`

### Commit 13: Final Cleanup
**Task**: Remove obsolete deleteme directory after verification
- Review `deleteme-normpic-modules/` content, verify all specs adapted
- Remove entire directory, update documentation references
**Validation**: No broken links, `uv run pytest`, `uv run ruff check`
**Commit**: `Cleanup: Remove obsolete deleteme directory after successful adaptation`

## Reference Information (Historical Context)

## Current Implementation Plan

## MVP Implementation Tasks


### Managers (`src/manager/`)

#### Manifest Manager

- [ ] Detect changes requiring reprocessing:
  - File hash changes
  - Timestamp changes
  - Config changes (collection name, etc.)
  - Missing destination files
- [ ] Update manifest with processing results
- [ ] Delete dry-run manifest after successful run

#### Config Manager (Future Enhancements)

- [ ] Environment variable override support (NORMPIC_*)
- [ ] Implement config precedence system (defaults < local config < env vars < cli args)

### Utilities (`src/util/`)

#### Filesystem Utilities

- [ ] Mock filesystem for testing
- [ ] Symlink creation and validation
- [ ] Detect broken symlinks
- [ ] Check for flat directory structure (warn if nested)
- [ ] File hash computation (SHA-256)


### Testing Strategy (Remaining)

#### Integration Tests (`test/integration/`)

- [ ] Review and adapt tests from `deleteme-normpic-modules/test/`
- [ ] Test incremental updates

#### Unit Tests (`test/unit/`)

- [ ] Hash computation

#### Test Fixtures (`test/fixture/`)

- [ ] Sample EXIF data for different cameras
- [ ] Mock pics with various metadata combinations
- [ ] Invalid/corrupted file examples
- [ ] Config examples

### Error Handling

- [ ] Skip pics with warnings, continue processing
- [ ] Log all warnings/errors to manifest
- [ ] Validate manifest before updates
- [ ] Handle corrupted files gracefully
- [ ] Report broken symlinks
- [ ] Document error handling in `doc/guides/errors.md`

### MVP Documentation Completion

- [ ] Performance baseline measurements
- [ ] Timestamp analysis from test collections
- [ ] Document any systematic offsets discovered
- [ ] Verify all deleteme content is obsolete and remove directory

### Current Status

**COMPLETED:** 
- CLI implementation with comprehensive configuration system
- Manifest loading with validation (Priority 1)

**Next Tasks:** Change detection for incremental updates (Priority 2)

## Post-MVP Features (Future)

### Schema Evolution Architecture

**Migration System Design:**
- `src/migration/` directory for schema version migrations
- Migration scripts handle manifest format evolution
- Versioned schemas (`schema_v1.py`, `schema_v2.py`, etc.) support multiple formats
- Automatic detection and upgrade of legacy manifests
- Rollback capability for failed migrations

### Near-term Enhancements

- [ ] Configurable symlink vs copy behavior
- [ ] S3-compatible adapter implementation
- [ ] Rich CLI with Textual TUI
- [ ] UTC offset support (EXIF/GPS/config)
- [ ] Timestamp systematic correction via config
- [ ] SSH/SFTP adapter
- [ ] Proton Drive integration
- [ ] Environment variable config overrides
- [ ] CLI argument overrides
- [ ] Subdirectory handling with tagging
- [ ] RAW format support
- [ ] Performance: Multithreading with speedup documentation in `doc/analysis/`
- [ ] Performance: EXIF caching with speedup documentation
- [ ] Deletion detection and safe cleanup
- [ ] Ignore file for excluding pics

### Medium-term Features

- [ ] Mirror variant handling (web-optimized versions)
- [ ] EXIF modification and copy creation
- [ ] Camera name mapping configuration
- [ ] Multiple error tracking per pic
- [ ] **Schema Migration System** (`src/migration/`)
  - [ ] Automatic manifest version detection
  - [ ] Migration scripts between schema versions
  - [ ] Backward compatibility validation
  - [ ] Migration rollback capability
- [ ] Resume capability for failed builds
- [ ] Webhook notifications on completion

### Long-term Features

- [ ] Additional metadata tagging systems
- [ ] Popularity tracking from CDN stats
- [ ] Progressive loading variant generation
- [ ] Automated CI/CD integration
- [ ] Git hooks for automatic processing

## Integration Points

### For Galleria (Gallery Builder)

- Manifest provides all pic metadata
- Standardized filenames enable consistent URLs
- Schema validation ensures compatibility

### For Parent Site Project

- Can orchestrate NormPic + Galleria
- Manifest enables incremental builds
- JSON Schema allows tool independence

## Success Criteria

**✅ Completed:**
- Produces valid, schema-compliant manifests
- Maintains pic order with proper burst handling  
- All tests pass before commits (except checkpoint branches)
- Ruff checks pass on all code
- Clear separation between library and CLI
- Complete documentation for all modules

**🚧 Remaining:**
- [ ] Processes 24GB photo collection efficiently
- [ ] Documentation of performance improvements
- [ ] Deletion of deleteme directory indicates MVP completion

## Development Rules

1. TDD: Write integration test ->
    fail -> write unit tests -> implement -> green -> refactor
2. No commits without passing tests (except checkpoint branches: "Chk: [description]")
3. All code must pass ruff checks
4. Use mocked filesystem in tests
5. Lazy processing by default (skip unchanged pics)
6. Warnings continue, errors stop
7. JSON Schema validation for all manifest operations
8. Update documentation with every commit
9. Log changes in CHANGELOG.md daily
10. Reference and adapt useful specs from deleteme directory
11. Delete obsolete deleteme content as it's replaced

