# NormPic - Photo Organization & Manifest Generator TODO

## Next Development Phase - Detailed TDD Implementation Cycles

### Priority 1: Manifest Manager - Load Existing Manifest

**RED Phase - Write Failing E2E Test:**
1. Create `test/integration/test_manifest_loading_workflow.py`
2. Write `test_load_existing_manifest_complete_workflow()`
   - Setup: Create existing manifest.json in destination
   - Act: Run photo organization on same source
   - Assert: Existing manifest loaded, validated, used for processing decisions

**GREEN Phase - Unit Tests & Implementation:**
1. Test fails (ImportError: function doesn't exist)
2. Write unit tests in `test/unit/test_manifest_manager.py`:
   - `test_load_manifest_file_exists()`
   - `test_load_manifest_invalid_json()`
   - `test_load_manifest_schema_validation()`
3. Implement minimal `manifest_manager.load_existing_manifest()` to pass tests
4. Run `uv run pytest test/unit/test_manifest_manager.py -v` until green

**REFACTOR Phase:**
1. Improve implementation with proper error handling
2. Add logging, validation checks
3. Optimize file loading performance if needed

**DOCUMENTATION Phase:**
1. Update `doc/CHANGELOG.md` with H2 date header + bullet points
2. Update `doc/modules/manifest.md` with load functionality
3. Ensure link chain: doc/README.md → doc/modules/README.md → manifest.md

**COMMIT Phase:**
1. Run full test suite: `uv run pytest`
2. Run linting: `ruff check` and `ruff format`
3. Commit with format: `Ft: Add manifest loading with validation`
4. Mark TODO item [x] complete

### Priority 2: Manifest Manager - Change Detection

**RED Phase - Write Failing E2E Test:**
1. Create `test_incremental_processing_workflow()` in same file
2. Test scenario: modify source file, verify only changed files reprocessed
3. Assert: unchanged files skipped, changed files reprocessed

**GREEN Phase - Unit Tests & Implementation:**
1. Unit tests for change detection:
   - `test_detect_file_hash_changes()`
   - `test_detect_timestamp_changes()`
   - `test_detect_config_changes()`
   - `test_detect_missing_destination_files()`
2. Implement change detection logic in `manifest_manager.py`
3. Iterate RED-GREEN until all tests pass

**REFACTOR Phase:**
1. Optimize hash computation for large files
2. Add efficient timestamp comparison logic
3. Consider lazy evaluation strategies

**DOCUMENTATION Phase:**
1. Update `doc/CHANGELOG.md` with date header
2. Document change detection algorithm in `doc/modules/manifest.md`
3. Add performance notes in `doc/analysis/` if significant optimizations made

**COMMIT Phase:**
1. Full test suite + linting checks
2. Commit: `Ft: Add incremental change detection for manifests`

### Priority 3: Filesystem Utilities - Symlink Operations

**RED Phase - Write Failing E2E Test:**
1. Create `test/integration/test_filesystem_operations_workflow.py`
2. Write `test_symlink_creation_complete_workflow()`
3. Test: source photos → symlink creation → validation → broken link detection

**GREEN Phase - Unit Tests & Implementation:**
1. Create `test/unit/test_filesystem_utils.py`:
   - `test_create_symlink_success()`
   - `test_create_symlink_existing_file()`
   - `test_validate_symlink_integrity()`
   - `test_detect_broken_symlinks()`
   - `test_compute_file_hash_sha256()`
2. Implement `lib/util/filesystem.py` utilities
3. Mock filesystem operations for deterministic testing

**REFACTOR Phase:**
1. Add atomic symlink creation (temp + rename)
2. Optimize hash computation for large files
3. Add progress reporting hooks

**DOCUMENTATION Phase:**
1. Update `doc/CHANGELOG.md`
2. Expand `doc/modules/filesystem.md` with new operations
3. Link from doc/modules/README.md

**COMMIT Phase:**
1. Full suite + linting
2. Commit: `Ft: Add symlink operations and file hash utilities`

### Priority 4: Error Handling Framework

**RED Phase - Write Failing E2E Test:**
1. Create `test/integration/test_error_handling_workflow.py`
2. Write `test_corrupted_file_complete_error_handling()`
3. Test: corrupted files → graceful handling → continue processing → error logging

**GREEN Phase - Unit Tests & Implementation:**
1. Unit tests for error scenarios:
   - `test_skip_corrupted_file_continue_processing()`
   - `test_log_warnings_to_manifest()`
   - `test_validate_manifest_before_write()`
2. Implement error handling throughout processing pipeline
3. Add error logging to manifest schema

**REFACTOR Phase:**
1. Standardize error message formats
2. Add error severity levels (warning vs error)
3. Implement error reporting utilities

**DOCUMENTATION Phase:**
1. Create `doc/guides/errors.md` with error handling guide
2. Link from `doc/guides/README.md`
3. Update `doc/CHANGELOG.md`
4. Document error schema in `doc/modules/schema.md`

**COMMIT Phase:**
1. Full suite + linting
2. Commit: `Ft: Add comprehensive error handling framework`

## Project Overview

NormPic is a photo organization tool that normalizes photo collections by
renaming files based on temporal and camera metadata,
creating symlinks with standardized names,
and generating JSON manifests for interoperability with
other tools like Galleria (gallery builder).

## Architecture Overview

- **Manifest-Centric Design**: All decisions flow through JSON Schema-validated manifests
- **Protocol-Based Integration**:
  - Parent projects provide implementations for external concerns
- **TDD Approach**: Integration tests first, then unit tests following RED-GREEN-REFACTOR
- **Lazy Processing**: Skip unchanged photos based on timestamps and hashes

## Documentation Strategy

### Documentation Structure

```txt
normpic/
|-- README.md           -> Links to doc/README.md
|-- doc/
    |-- README.md       # Index and overview
    |-- TODO.md         # This file
    |-- CONTRIBUTE.md   # Contribution guidelines (must read)
    |-- CHANGELOG.md    # Daily updates with H2 date headers
    |-- architecture/   # System design documents
    |-- modules/        # Module-specific documentation
    |-- guides/         # User and developer guides
    |-- analysis/       # Performance metrics, timestamp statistics
```

### Documentation Requirements

- [ ] Every commit must consider documentation updates
- [ ] Features/fixes must be documented in appropriate locations
- [ ] Daily changes logged in CHANGELOG.md under date headers
- [ ] Major changes require guide/module documentation updates
- [ ] Performance discoveries documented in analysis/
- [ ] Architecture decisions documented as they're made

## Current Implementation Plan

## MVP Implementation Tasks


### Managers (`lib/manager/`)

#### Manifest Manager

- [x] Load existing manifest with validation
- [ ] Detect changes requiring reprocessing:
  - File hash changes
  - Timestamp changes
  - Config changes (collection name, etc.)
  - Missing destination files
- [ ] Update manifest with processing results
- [ ] Write manifest atomically
- [x] Create dry-run manifests (`manifest.dryrun.json`)
- [ ] Delete dry-run manifest after successful run
- [x] Document manifest operations in `doc/modules/manifest.md`

#### Config Manager (Future Enhancements)

- [ ] Environment variable override support (NORMPIC_*)
- [ ] Implement config precedence system (defaults < local config < env vars < cli args)

### Utilities (`lib/util/`)

#### Filesystem Utilities

- [ ] Mock filesystem for testing
- [ ] Symlink creation and validation
- [ ] Detect broken symlinks
- [ ] Check for flat directory structure (warn if nested)
- [ ] File hash computation (SHA-256)
- [x] Handle file formats: .jpg, .png, .heic, .webp
- [x] Document filesystem operations in `doc/modules/filesystem.md`


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

- [ ] Architecture overview in `doc/architecture/overview.md`
- [ ] Module interaction diagrams
- [ ] Usage guide for end users
- [ ] Developer setup guide
- [ ] Performance baseline measurements
- [ ] Timestamp analysis from test collections
- [ ] Document any systematic offsets discovered
- [ ] Complete CHANGELOG.md with all development history
- [ ] Verify all deleteme content is obsolete and remove directory

### Current Status

**COMPLETED:** CLI implementation with comprehensive configuration system

**Next Tasks:** Performance improvements and incremental updates

## Post-MVP Features (Future)

### Schema Evolution Architecture

**Migration System Design:**
- `lib/migration/` directory for schema version migrations
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
- [ ] **Schema Migration System** (`lib/migration/`)
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

