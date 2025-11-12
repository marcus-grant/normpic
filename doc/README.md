# NormPic Documentation

## Overview

NormPic normalizes photo collections by:

- Extracting temporal and camera metadata from photos
- Generating standardized filenames based on timestamps
- Creating symlinks with consistent naming patterns
- Producing JSON manifests for integration with other tools

## Architecture Principles

- **Manifest-Centric Design**: All decisions flow through JSON Schema-validated manifests
- **Protocol-Based Integration**: Parent projects provide implementations for external concerns
- **TDD Approach**: Integration tests first, then unit tests following RED-GREEN-REFACTOR
- **Lazy Processing**: Skip unchanged photos based on timestamps and hashes

## Documentation Structure

This documentation follows a hierarchical linking structure:

- All documents link from project root README.md → doc/README.md
- Each doc/ subdirectory has its own README.md serving as an index
- Follow links: topic → subtopic → specific document (no direct deep linking)
- This ensures the entire documentation tree is discoverable systematically

## Documentation Index

### Project Management

- [TODO.md](TODO.md) - Development tasks and roadmap
- [CONTRIBUTE.md](CONTRIBUTE.md) - Contribution guidelines (MUST READ for developers)
- [CHANGELOG.md](CHANGELOG.md) - Daily development log

### Architecture

- [Architecture Overview](architecture/README.md) - System design and key decisions

### Modules

- [Module Documentation](modules/README.md) - Technical documentation for each module

### Testing

- [Testing Overview](test/README.md) - TDD approach, fixtures, and patterns

### Guides

- [User and Developer Guides](guides/README.md) - CLI usage, configuration, and basic workflows

### Integration

- [Parent Project Integration](guides/integration.md) - Complete workflow for integrating NormPic into static site projects
- [Parent Project Setup](guides/parent-project-setup.md) - Setup instructions for uv integration with parent projects
- [Manifest Integration](guides/manifest-integration.md) - Working with NormPic manifest data in custom applications  
- [Gallery Builder Integration](guides/gallery-builder-integration.md) - Building custom gallery generators that consume NormPic output

### Analysis

- [Performance and Timestamp Analysis](analysis/README.md) - Real-world performance benchmarks, timestamp accuracy analysis, and systematic offset documentation

## Project Status

**Complete MVP Implementation** with 109 passing tests:
- Full CLI interface with configuration system
- Photo organization workflow with temporal ordering and burst sequence preservation
- EXIF-based filename generation and symlink creation
- Manifest loading with validation and atomic file operations
- Comprehensive error handling and schema validation

**Current Development**: Change detection for incremental updates (Priority 2)

See [TODO.md](TODO.md) for next tasks and [CHANGELOG.md](CHANGELOG.md) for detailed development progress.

## Related Projects

- **Galleria** - Static gallery builder that consumes NormPic manifests
