# NormPic - Photo Organization & Manifest Generator TODO

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

### Existing Work Reference

- [ ] Review `deleteme-normpic-modules/README.md` for prior analysis
- [ ] Extract useful test specs from `deleteme-normpic-modules/test/`
  - Particularly timestamp and ordering logic
  - Adapt to current architecture improvements
- [ ] Reference `deleteme-normpic-modules/src/` for implementation patterns
- [ ] Consult `deleteme-normpic-modules/doc/` for documentation patterns
- [ ] Delete obsolete parts of deleteme directory as they're superseded
- [ ] Complete deletion of deleteme directory should coincide with MVP completion

## Current Implementation Plan

### Next Commit

#### Next Commit: "Ft: Add photo organization and processing"

## MVP Implementation Tasks

### Core Processing (`lib/core/`)

#### EXIF Extraction (`exif_extractor.py`)

- [ ] Review `deleteme-normpic-modules/test/` for EXIF test cases
- [ ] Extract timestamp with subsecond precision
- [ ] Extract camera make/model
- [ ] Extract GPS coordinates
- [ ] Handle missing EXIF gracefully
- [ ] Return structured metadata dict
- [ ] Document EXIF handling in `doc/modules/exif.md`

#### Filename Generation (`filename_generator.py`)

- [ ] Implement naming format: `{collection-?}{YY-MM-DDTHHMMSS}{-camera?}{-counter?}.ext`
- [ ] Use Base32 hex (0-9, a-v) for burst counter
- [ ] Handle timestamp conflicts with burst detection
- [ ] Normalize extensions (.jpeg \u2192 .jpg)
- [ ] Document naming conventions in `doc/guides/naming.md`

#### Pic Organization (`pic_organizer.py`)

- [ ] Review `deleteme-normpic-modules/test/` for ordering test specs
- [ ] Implement ordering algorithm:
  1. EXIF timestamp (with subsec)
  2. Filename sequence
  3. Filesystem mtime
- [ ] Handle burst sequences (don't interrupt by other cameras)
- [ ] Detect when processing needed (hash/timestamp changes)
- [ ] Document ordering logic in `doc/modules/organization.md`

### Managers (`lib/manager/`)

#### Manifest Manager

- [ ] Load existing manifest with validation
- [ ] Detect changes requiring reprocessing:
  - File hash changes
  - Timestamp changes
  - Config changes (collection name, etc.)
  - Missing destination files
- [ ] Update manifest with processing results
- [ ] Write manifest atomically
- [ ] Create dry-run manifests (`manifest.dryrun.json`)
- [ ] Delete dry-run manifest after successful run
- [ ] Document manifest operations in `doc/modules/manifest.md`

#### Config Manager

- [ ] Load config from JSON file
- [ ] Default config values
- [ ] Config validation
- [ ] Future: Environment variable override support (NORMPIC_*)
- [ ] Document configuration in `doc/guides/configuration.md`

### Utilities (`lib/util/`)

#### Filesystem Utilities

- [ ] Mock filesystem for testing
- [ ] Symlink creation and validation
- [ ] Detect broken symlinks
- [ ] Check for flat directory structure (warn if nested)
- [ ] File hash computation (SHA-256)
- [ ] Handle file formats: .jpg, .png, .heic, .webp
- [ ] Document filesystem operations in `doc/modules/filesystem.md`

### CLI Implementation (`cli/main.py`)

- [ ] Single command: `normpic`
- [ ] Flags:
  - `--dry-run`: Generate manifest without creating symlinks
  - `--verbose`: Show each pic being processed
  - `--force`: Reprocess everything ignoring cache
  - `--config`: Path to config file (default: `./config.json`)
- [ ] Output summary: "Processed X pics, Y warnings, Z errors"
- [ ] Distinguish warnings vs errors in output
- [ ] Return appropriate exit codes
- [ ] Create CLI usage guide in `doc/guides/cli.md`

### Testing Strategy

#### Integration Tests (`test/integration/`)

- [ ] Review and adapt tests from `deleteme-normpic-modules/test/`
- [ ] End-to-end test: source directory -> symlinks + manifest
- [ ] Test with mock filesystem
- [ ] Test dry-run mode
- [ ] Test force reprocessing
- [ ] Test incremental updates
- [ ] Document testing approach in `doc/CONTRIBUTE.md`

#### Unit Tests (`test/unit/`)

- [ ] EXIF extraction with various cameras
- [ ] Filename generation edge cases
- [ ] Timestamp parsing and ordering
- [ ] Burst detection
- [ ] Hash computation
- [ ] Config loading and validation
- [ ] Manifest serialization

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

**Active Tasks:** Ready for Commit 2 - Schema and data models implementation

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

- [ ] Processes 24GB photo collection efficiently
- [ ] Produces valid, schema-compliant manifests
- [ ] Maintains pic order with proper burst handling
- [ ] All tests pass before commits (except checkpoint branches)
- [ ] Ruff checks pass on all code
- [ ] Clear separation between library and CLI
- [ ] Documentation of performance improvements
- [ ] Complete documentation for all modules
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

