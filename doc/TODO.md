# NormPic - Photo Organization & Manifest Generator TODO


## Current Status: MVP COMPLETE ✅

**Ready for parent project integration**
- Core photo organization workflow complete (200 passing tests)
- Performance and timestamp analysis documentation complete
- Integration documentation complete with all guides indexed
- CLI interface with full configuration system
- All MVP requirements satisfied

**Critical Technical Details:**
- This is a uv-managed project: Use `uv run pytest` (NOT `python -m pytest`)
- Source code location: `src/` directory
- Test command: `uv run pytest test/` for full suite
- Linting: `uv run ruff check` (must pass before commits)

## Remaining Tasks

### Critical MVP: Packaging Fix ✅ COMPLETED
**ENABLES PARENT PROJECT INTEGRATION** - Package now supports `from normpic import organize_photos`

**✅ COMPLETED - All Goals Achieved:**
- ✅ Restructured to conventional `PROJECT_ROOT/normpic/` layout (was `src/`)
- ✅ All 26 files with imports successfully updated
- ✅ Clean API entry point with `organize_photos`, `Manifest`, `Pic`, `Config`
- ✅ Package properly installable for parent projects

**✅ Implementation Completed** (6 commits on `fix/packaging` branch):
- ✅ **Commit 1**: Fixed all 6 core modules (relative imports `from ..X`)
- ✅ **Commit 2**: Fixed unit test imports (kept `src.` for development)
- ✅ **Commit 3**: Integration tests worked without changes
- ✅ **Commit 4**: Fixed CLI imports + created API entry point
- ✅ **Commit 5**: Restructured to `normpic/` package layout
- ✅ **Commit 6**: Updated all test imports to use `normpic.*`

**✅ Success Criteria Met:**
- ✅ `from normpic import organize_photos` works after `uv pip install -e .`
- ✅ All 200 tests pass with new structure
- ✅ Ruff linting passes on all code
- ✅ CLI functional with `uv run python cli/main.py`

**Ready for integration into parent projects!**

### Final Cleanup
**Task**: Remove obsolete deleteme directory after verification
- Review `deleteme-normpic-modules/` content, verify all specs adapted
- **S3 storage features confirmed as post-MVP** - can be removed safely
- Remove entire directory, update documentation references

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
- [x] Environment variable config overrides
- [x] CLI argument overrides
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

