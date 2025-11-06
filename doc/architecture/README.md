# Architecture Documentation

## Overview

NormPic follows a manifest-centric, TDD-driven architecture with clear separation of concerns across data models, processing logic, and serialization.

## Key Architectural Documents

### Schema & Data Management
- [Schema Versioning](schema-versioning.md) - Versioned schema approach using Python modules, serializer separation, and future migration system design
- [Data Models](data-models.md) - Dataclass architecture, TDD implementation, and serialization layer design

### Module Organization
- [Module Organization](module-organization.md) - Functional module patterns, avoiding catch-all anti-patterns, and template/utility separation
- [Template/Util Split](template-util-split.md) - Architecture pattern for separating generic utilities from domain-specific templates

## Architecture Principles

- **Manifest-Centric Design**: All decisions flow through JSON Schema-validated manifests
- **Protocol-Based Integration**: Parent projects provide implementations for external concerns  
- **TDD Approach**: Integration tests first, then unit tests following RED-GREEN-REFACTOR
- **Lazy Processing**: Skip unchanged photos based on timestamps and hashes

## System Structure

```
lib/
├── model/          # Data structures (Pic, Manifest, Config)
│   └── schema_v0.py # JSON Schema definitions as Python constants
├── serializer/     # JSON serialization/validation layer
├── util/           # Generic utilities (EXIF extraction, filesystem ops)
├── template/       # Template application (filename generation)
├── manager/        # High-level orchestration (manifest, config management)
└── [future modules organized by function]
```

This architecture enables clean testing, future schema evolution, and integration with external tools like Galleria.