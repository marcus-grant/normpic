# Architecture Documentation

## Overview

NormPic follows a manifest-centric, TDD-driven architecture with clear separation of concerns across data models, processing logic, and serialization.

## Key Architectural Documents

### Schema & Data Management
- [Schema Versioning](schema-versioning.md) - Versioned schema approach using Python modules, serializer separation, and future migration system design

## Architecture Principles

- **Manifest-Centric Design**: All decisions flow through JSON Schema-validated manifests
- **Protocol-Based Integration**: Parent projects provide implementations for external concerns  
- **TDD Approach**: Integration tests first, then unit tests following RED-GREEN-REFACTOR
- **Lazy Processing**: Skip unchanged photos based on timestamps and hashes

## System Structure

```
lib/
├── model/          # Data structures (Pic, Manifest, Config)
│   └── schema_v1.py # JSON Schema definitions as Python constants
├── serializer/     # JSON serialization/validation layer
├── core/           # Processing logic (EXIF, filename generation, organization)
├── manager/        # High-level orchestration (manifest, config management)
└── util/           # Filesystem utilities and helpers
```

This architecture enables clean testing, future schema evolution, and integration with external tools like Galleria.