# Module Documentation

## Overview

Technical documentation for each NormPic module,
covering implementation details, APIs, and design decisions.

## Schema & Data Models

- [JSON Schema](schema.md)
  - The schema artifact.
  - How it is loaded, and where the contract is defined.

## Core Processing  

- [EXIF Module](exif.md)
  - EXIF data extraction, structured models, and testing patterns
- [Photo Manager](photo-manager.md)
  - Complete photo organization workflow orchestration
- [Organization Algorithm](organization.md)
  - Photo ordering algorithm and burst preservation details
- [Manifest Operations](manifest.md)
  - Manifest management, validation, dry-run handling, and tool integrations

## System Operations

- [Filesystem Operations](filesystem.md) - Symlink creation, path handling, and file format support

## Coming Soon

- **Models** - Pic, Manifest, Config dataclass documentation
- **Filename Templates** - Template-based filename generation documentation
- **Serialization** - JSON serialization and validation layer
- **Utilities** - Filesystem operations and helper functions

