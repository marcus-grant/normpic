# Architecture Documentation

## Overview

NormPic follows a manifest-centric, TDD-driven architecture with clear
separation of concerns across data models, processing logic, and
serialization.

## Key Architectural Documents

### Schema and Data Management

- [Manifest Contract](manifest-contract.md): the durable v0.1.0
  manifest contract that consumers and reimplementations depend on.
  Implementation-agnostic; source of truth for fields, semantics,
  canonical forms, and forward-compatibility rules.
- [Conformance Requirement](conformance.md): defines what an
  implementation must demonstrate to claim v0.1.0 conformance.
  Specifies the two-layer validation model, fixture categories and
  inventory, producer and consumer responsibilities, and acceptance
  criteria.
- [Schema Versioning](schema-versioning.md): versioned schema approach
  using Python modules, serializer separation, and future migration
  system design.
- [Data Models](data-models.md): dataclass architecture, TDD
  implementation, and serialization layer design.

### Module Organization

- [Module Organization](module-organization.md): functional module
  patterns, avoiding catch-all anti-patterns, and template/utility
  separation.
- [Template/Util Split](template-util-split.md): architecture pattern
  for separating generic utilities from domain-specific templates.
- [Package Structure](package-structure.md): import architecture,
  conventional package layout, and restructuring decisions.

## Architecture Principles

- **Manifest-Centric Design**: all decisions flow through JSON
  Schema-validated manifests.
- **Protocol-Based Integration**: parent projects provide
  implementations for external concerns.
- **TDD Approach**: integration tests first, then unit tests following
  RED-GREEN-REFACTOR.
- **Lazy Processing**: skip unchanged photos based on timestamps and
  hashes.

## System Structure

```
normpic/                  # Main package (conventional layout)
|-- __init__.py           # Clean API exports
|-- model/                # Data structures (Pic, Manifest, Config)
|   `-- schema_v0.py      # JSON Schema definitions as Python constants
|-- serializer/           # JSON serialization/validation layer
|-- util/                 # Generic utilities (EXIF, filesystem ops)
|-- template/             # Template application (filename generation)
|-- manager/              # High-level workflow orchestration
|   `-- photo_manager.py  # Complete photo organization workflow
`-- [future modules organized by function]
```

## Implemented Workflows

### Photo Organization (normpic/manager/photo_manager.py)

Complete photo collection processing workflow:

- **Temporal Ordering**: EXIF timestamp -> filename -> mtime
  precedence with subsecond precision.
- **Burst Preservation**: no camera interleaving on shared timestamps
  to maintain burst sequence integrity.
- **Symlink Generation**: creates standardized chronological filenames
  while preserving originals.
- **Manifest Production**: schema-validated JSON with complete photo
  metadata for tool integration.

This architecture enables clean testing, future schema evolution, and
integration with external tools like Galleria.

