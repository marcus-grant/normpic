# NormPic - Photo Organization & Manifest Generator TODO

## Current Status: Commits 5-7 COMPLETED

Complete MVP + Error Handling + Mock Testing: 164 passing tests

**Critical Technical Details:**
- This is a uv-managed project: Use `uv run pytest` (NOT `python -m pytest`)
- Source code location: `src/` directory
- Test command: `uv run pytest test/` for full suite
- Linting: `uv run ruff check` (must pass before commits)


## Remaining MVP Implementation Tasks

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

- [ ] Check for flat directory structure (warn if nested)


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

