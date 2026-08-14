# Package Structure and Import Architecture

## Overview

This document explains NormPic's package structure and the
architectural decisions behind the import system.

## Package Layout

### Current Structure (Post-Restructuring)

```text
normpic/                    # Root project directory
|-- normpic/                # Main package (conventional layout)
|   |-- __init__.py         # Clean API exports
|   |-- manager/            # Core business logic
|   |   |-- photo_manager.py      # Main organize_photos() function
|   |   |-- manifest_manager.py   # Manifest file operations
|   |   `-- config_manager.py     # Configuration handling
|   |-- model/              # Data models and schemas
|   |   |-- manifest.py     # Manifest data structure
|   |   |-- pic.py          # Photo metadata model
|   |   |-- config.py       # Configuration model
|   |   `-- exif.py         # EXIF data structures
|   |-- serializer/         # JSON serialization
|   |-- template/           # Filename generation
|   `-- util/               # Utilities (EXIF, filesystem, errors)
|-- test/                   # Test suite (unchanged)
|   |-- cli.py              # Click CLI interface
|   |-- __main__.py         # python -m normpic entry
|   |-- serializer/         # JSON serialization
|   |-- template/           # Filename generation
|   `-- util/               # Utilities (EXIF, filesystem, errors)
|-- test/                   # Test suite (unchanged)
`-- doc/                    # Documentation (unchanged)
```

### Previous Structure (Before Restructuring)

```text
normpic/                    # Root project directory
|-- src/                    # Source directory (non-conventional)
|   |-- manager/            # Business logic
|   |-- model/              # Data models
|   `-- ...
`-- ...
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

## Related documentation

- [module-organization.md](module-organization.md): how modules are
  grouped by responsibility.
- [template-util-split.md](template-util-split.md): the generic-vs-
  domain split within the package.
- [data-models.md](data-models.md): the data structures the package
  exposes.
