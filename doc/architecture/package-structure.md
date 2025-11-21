# Package Structure and Import Architecture

## Overview

This document explains NormPic's package structure and the architectural decisions behind the import system, including the major restructuring completed in November 2025.

## Package Layout

### Current Structure (Post-Restructuring)

```
normpic/                    # Root project directory
├── normpic/               # Main package (conventional layout)
│   ├── __init__.py       # Clean API exports
│   ├── manager/          # Core business logic
│   │   ├── photo_manager.py      # Main organize_photos() function
│   │   ├── manifest_manager.py   # Manifest file operations
│   │   └── config_manager.py     # Configuration handling
│   ├── model/            # Data models and schemas
│   │   ├── manifest.py   # Manifest data structure
│   │   ├── pic.py        # Photo metadata model
│   │   ├── config.py     # Configuration model
│   │   ├── exif.py       # EXIF data structures
│   │   └── schema_v0.py  # JSON schema definitions
│   ├── serializer/       # JSON serialization
│   ├── template/         # Filename generation
│   └── util/            # Utilities (EXIF, filesystem, errors)
├── test/                # Test suite (unchanged)
├── cli/                 # CLI interface (unchanged)
└── doc/                 # Documentation (unchanged)
```

### Previous Structure (Before Restructuring)

```
normpic/                    # Root project directory  
├── src/                   # Source directory (non-conventional)
│   ├── manager/          # Business logic
│   ├── model/            # Data models
│   └── ...
└── ...
```

## Import Architecture

### External API (Parent Projects)

**Canonical Import Pattern:**
```python
from normpic import organize_photos, Manifest, Pic, Config
```

**API Exports (`normpic/__init__.py`):**
```python
from .manager.photo_manager import organize_photos
from .model.manifest import Manifest  
from .model.pic import Pic
from .model.config import Config

__all__ = ['organize_photos', 'Manifest', 'Pic', 'Config']
```

### Internal Imports (Within Package)

**Relative Imports:**
- All internal package modules use relative imports
- Example: `from ..model.manifest import Manifest`
- Enables proper package isolation and prevents import conflicts

### Development/Test Imports

**Package Imports for Tests:**
- All test files use absolute package imports: `from normpic.model.config import Config`
- Ensures tests verify the actual installed package structure
- CLI also uses package imports for consistency

## Architectural Decisions

### 1. Conventional Package Layout

**Decision:** Use `PROJECT_ROOT/normpic/` instead of `PROJECT_ROOT/src/normpic/`

**Rationale:**
- More conventional Python package structure
- Simpler setuptools configuration
- Easier package discovery and installation
- Clearer separation between package code and project metadata

**Benefits:**
- Standard layout expected by Python packaging tools
- Reduces configuration complexity in pyproject.toml
- Familiar structure for Python developers

### 2. Relative Imports for Internal Modules

**Decision:** Use `from ..module import Class` for intra-package imports

**Rationale:**
- Prevents import path conflicts
- Enables package renaming without breaking internal imports
- Standard practice for Python packages
- Supports proper package encapsulation

### 3. Clean API Surface

**Decision:** Export only essential functions and classes in `__init__.py`

**Exports:**
- `organize_photos` - Primary function for photo organization
- `Manifest`, `Pic`, `Config` - Essential data structures

**Non-exports:**
- Internal utilities and implementation details remain private
- Prevents API pollution and maintains clean interface

### 4. Package vs. Development Import Separation

**Decision:** Different import patterns for different contexts

**Package Imports (Tests, CLI):**
```python
from normpic.manager.photo_manager import organize_photos
```

**Relative Imports (Internal):**
```python
from ..manager.photo_manager import organize_photos  
```

**Benefits:**
- Tests verify actual package structure
- Internal code remains properly encapsulated
- Clear distinction between public API and implementation

## Implementation History

### Phase 1: Internal Import Fixes
- Converted `from src.X` to `from ..X` in all core modules
- Fixed relative import issues within the package
- Maintained test compatibility during transition

### Phase 2: Structure Reorganization  
- Moved `src/` directory to `normpic/` for conventional layout
- Updated pyproject.toml package discovery configuration
- Simplified build system requirements

### Phase 3: Test Import Updates
- Updated all test files from `from src.X` to `from normpic.X`
- Verified package installation and import resolution
- Validated CLI functionality with new structure

### Phase 4: API Finalization
- Created clean API exports in `normpic/__init__.py`
- Tested parent project integration patterns
- Documented canonical import syntax

## Validation Results

**Package Installation:**
- ✅ `uv pip install -e .` successful
- ✅ `from normpic import organize_photos` functional
- ✅ All main exports accessible

**Quality Assurance:**
- ✅ All 200 tests pass with new structure
- ✅ Ruff linting clean on all code
- ✅ CLI functional with `uv run python cli/main.py`

**Integration Ready:**
- ✅ Package structure supports parent project import
- ✅ API surface appropriate for external consumption  
- ✅ Documentation reflects new structure

## Migration Guide for Contributors

### For New Development
- Use relative imports (`from ..module`) for intra-package references
- Use package imports (`from normpic.module`) in tests and CLI
- Follow the established pattern in existing modules

### For External Projects
- Install with `uv pip install -e path/to/normpic` or similar
- Import with `from normpic import organize_photos`
- Refer to integration guides for complete workflow examples

## Related Documentation

- [Integration Guide](../guides/integration.md) - Complete parent project setup
- [Module Documentation](../modules/README.md) - Individual module details  
- [Testing Patterns](../test/README.md) - Test structure and conventions