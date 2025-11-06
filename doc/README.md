# NormPic Documentation

## Overview

NormPic normalizes photo collections by:

- Extracting temporal and camera metadata from photos
- Generating standardized filenames based on timestamps
- Creating symlinks with consistent naming patterns
- Producing JSON manifests for integration with other tools

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

### Guides (Coming Soon)

- `guides/quickstart.md` - Getting started
- `guides/configuration.md` - Configuration reference

## Project Status

**Photo Organization Workflow**: Complete implementation with 78 passing tests
- Temporal ordering with burst sequence preservation
- EXIF-based filename generation 
- Symlink creation and manifest generation
- Ready for CLI implementation

See [TODO.md](TODO.md) for remaining tasks and [CHANGELOG.md](CHANGELOG.md) for detailed progress.

## Related Projects

- **Galleria** - Static gallery builder that consumes NormPic manifests
- **deleteme-normpic-modules** - Reference implementation to be superseded
