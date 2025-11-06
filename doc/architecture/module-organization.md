# Module Organization Architecture

## Overview

NormPic organizes modules by function and responsibility rather than using generic catch-all directories like "core" or "services".

## Design Principles

### Avoid Catch-All Anti-Pattern
- **Problem**: Generic directories like `core/` become dumping grounds
- **Solution**: Organize by specific functional responsibility

### Split Generic vs Domain-Specific
- **Generic utilities**: Reusable across projects (`lib/util/`)
- **Domain logic**: NormPic-specific business rules (`lib/template/`, `lib/manager/`)

## Module Patterns

### Template Pattern (`lib/template/`)
- **Purpose**: Apply data to format templates
- **Example**: `filename.py` applies photo metadata to naming template
- **Template**: `{collection-?}{YY-MM-DDTHHMMSS}{-camera?}{-counter?}.ext`
- **Rationale**: Clear responsibility, supports future template variations

### Utility Pattern (`lib/util/`)
- **Purpose**: Generic, reusable helper functions
- **Example**: `exif.py` extracts metadata from any photo file
- **Rationale**: Pure functions, no domain knowledge, broadly useful

### Serialization Pattern (`lib/serializer/`)
- **Purpose**: Format conversion between internal and external representations
- **Example**: `manifest.py` converts Manifest objects ↔ JSON
- **Rationale**: Clean separation of data structures from formats

### Manager Pattern (`lib/manager/`)
- **Purpose**: High-level workflow orchestration and business logic coordination
- **Example**: `photo_manager.py` orchestrates the complete photo organization workflow
- **Implementation**: Coordinates EXIF extraction, temporal ordering, burst preservation, filename generation, symlink creation, and manifest generation
- **Rationale**: Clear entry point for complex workflows, coordinates multiple modules without becoming a catch-all

## Current Structure

```
lib/
├── model/          # Data structures & schema definitions
├── serializer/     # Format conversion (JSON, etc.)
├── util/           # Generic utilities (EXIF extraction)
├── template/       # Template application (filename generation)
├── manager/        # High-level orchestration
└── [future modules organized by function]
```

## Implemented Modules

### Current Implementation
- **`lib/util/exif.py`** - EXIF metadata extraction with piexif integration
- **`lib/template/filename.py`** - Template-based filename generation with camera mapping
- **`lib/manager/photo_manager.py`** - Complete photo organization workflow orchestration
- **`lib/serializer/manifest.py`** - JSON manifest serialization with schema validation

## Benefits

1. **Clear Responsibility**: Each module has a specific, describable purpose
2. **Maintainability**: Easy to find and modify functionality
3. **Testability**: Clear boundaries for unit testing
4. **Extensibility**: Natural place for new functionality
5. **No Catch-Alls**: Prevents code dumping grounds

## Anti-Patterns Avoided

- ❌ `core/` - Generic business logic dumping ground
- ❌ `service/` - Vague service responsibilities  
- ❌ `processing/` - Unclear processing boundaries

## Decision Process

When adding new modules, ask:
1. **What is the specific function?** (not "business logic")
2. **Is it generic or domain-specific?**
3. **Does it fit an existing pattern?**
4. **Does it need a new functional category?**

This approach scales better than generic organizational patterns.