# Parent Project Setup Guide

## Overview

This guide provides specific instructions for setting up a parent project (Pelican/Django site) that integrates with NormPic for photo management and gallery generation. Since NormPic is a separate uv-managed project, this guide covers the various integration approaches and their trade-offs.

## Integration Approaches

### Option 1: CLI Integration (Recommended)
Use NormPic as a command-line tool called from your parent project's build scripts.

**Pros**: Simple, clean separation, no dependency conflicts
**Cons**: Requires NormPic to be installed separately

### Option 2: Git Submodule Integration
Include NormPic as a git submodule for version-locked integration.

**Pros**: Version control integration, reproducible builds
**Cons**: More complex git management

### Option 3: Package Dependency
Include NormPic as a Python package dependency.

**Pros**: Standard Python dependency management
**Cons**: Requires NormPic to be published as a package

## Setup Instructions

### Option 1: CLI Integration Setup

This is the recommended approach for most parent projects.

#### Step 1: Install NormPic Separately

```bash
# Clone NormPic to a dedicated location
git clone https://github.com/your-username/normpic.git /opt/normpic
cd /opt/normpic

# Install NormPic with uv
uv sync
```

#### Step 2: Create Parent Project Structure

```bash
# Create your parent project
mkdir my-wedding-site
cd my-wedding-site

# Initialize with uv (or your preferred package manager)
uv init
```

#### Step 3: Parent Project Dependencies

**pyproject.toml**:
```toml
[project]
name = "my-wedding-site"
version = "0.1.0"
description = "Wedding website with photo galleries"
requires-python = ">=3.12"
dependencies = [
    "pelican>=4.8.0",
    "markdown>=3.4.0",
    "Pillow>=10.0.0",      # For gallery image processing
    "jinja2>=3.1.0",       # For gallery templates
]

[dependency-groups]
dev = [
    "ruff>=0.14.3",
    "pytest>=8.4.2",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### Step 4: Build Script Integration

**build.py**:
```python
#!/usr/bin/env python3
"""Parent project build script with NormPic integration."""

import subprocess
import json
import os
from pathlib import Path

# Configuration
NORMPIC_PATH = "/opt/normpic"
PROJECT_ROOT = Path(__file__).parent

def run_normpic(collection_name, source_dir, dest_dir):
    """Run NormPic CLI for photo organization."""
    
    cmd = [
        "uv", "run", 
        "--project", str(NORMPIC_PATH),
        "python", "main.py",
        "--source-dir", str(source_dir),
        "--dest-dir", str(dest_dir), 
        "--collection-name", collection_name,
        "--verbose"
    ]
    
    print(f"Running NormPic: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"NormPic failed: {result.stderr}")
        raise RuntimeError(f"NormPic processing failed")
    
    print(f"NormPic completed: {result.stdout}")
    return result

def build_galleries():
    """Build photo galleries using NormPic output."""
    
    collections = {
        "wedding": {
            "source_full": Path.home() / "Photos/wedding/full",
            "source_web": Path.home() / "Photos/wedding/web",
            "dest_full": PROJECT_ROOT / "content/photos/wedding/full",
            "dest_web": PROJECT_ROOT / "content/photos/wedding/web",
        }
    }
    
    for collection_name, paths in collections.items():
        print(f"\n=== Processing {collection_name} collection ===")
        
        # Ensure destination directories exist
        paths["dest_full"].mkdir(parents=True, exist_ok=True)
        paths["dest_web"].mkdir(parents=True, exist_ok=True)
        
        # Run NormPic for full resolution
        run_normpic(
            collection_name=collection_name,
            source_dir=paths["source_full"],
            dest_dir=paths["dest_full"]
        )
        
        # Run NormPic for web-optimized
        run_normpic(
            collection_name=collection_name, 
            source_dir=paths["source_web"],
            dest_dir=paths["dest_web"]
        )
        
        print(f"✓ {collection_name} collection organized")

def build_site():
    """Build complete site with Pelican."""
    
    cmd = ["pelican", "content/", "-o", "output/", "-s", "pelicanconf.py"]
    print(f"Building site: {' '.join(cmd)}")
    
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError("Site build failed")
    
    print("✓ Site build completed")

def main():
    """Main build workflow."""
    
    print("=== Parent Project Build ===")
    
    try:
        # Step 1: Organize photos with NormPic
        build_galleries()
        
        # Step 2: Build site with Pelican
        build_site()
        
        print("\n🎉 Build completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
```

#### Step 5: Make Build Script Executable

```bash
chmod +x build.py

# Add to pyproject.toml scripts section
```

**Updated pyproject.toml**:
```toml
[project.scripts]
build-site = "build:main"
```

#### Step 6: Development Workflow

```bash
# Install parent project dependencies
uv sync

# Run complete build
uv run build.py

# Or use the script entry point
uv run build-site
```

### Option 2: Git Submodule Integration

For projects requiring version-locked NormPic integration.

#### Step 1: Add NormPic as Submodule

```bash
# In your parent project directory
git submodule add https://github.com/your-username/normpic.git vendor/normpic
git submodule update --init --recursive
```

#### Step 2: Create Wrapper Script

**tools/normpic_wrapper.py**:
```python
#!/usr/bin/env python3
"""Wrapper for running NormPic from submodule."""

import subprocess
import sys
from pathlib import Path

# Path to NormPic submodule
NORMPIC_DIR = Path(__file__).parent.parent / "vendor/normpic"

def run_normpic(args):
    """Run NormPic CLI from submodule."""
    
    cmd = ["uv", "run", "--project", str(NORMPIC_DIR), "python", "main.py"] + args
    
    result = subprocess.run(cmd)
    return result.returncode

def main():
    """Pass through all arguments to NormPic."""
    return run_normpic(sys.argv[1:])

if __name__ == "__main__":
    exit(main())
```

#### Step 3: Build Script with Submodule

**build.py**:
```python
import subprocess
from pathlib import Path

def run_normpic(collection_name, source_dir, dest_dir):
    """Run NormPic via wrapper script."""
    
    wrapper = Path(__file__).parent / "tools/normpic_wrapper.py"
    
    cmd = [
        "python", str(wrapper),
        "--source-dir", str(source_dir),
        "--dest-dir", str(dest_dir),
        "--collection-name", collection_name,
        "--verbose"
    ]
    
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError("NormPic processing failed")
```

#### Step 4: Submodule Update Workflow

```bash
# Update NormPic submodule to latest version
cd vendor/normpic
git pull origin main
cd ../..
git add vendor/normpic
git commit -m "Update NormPic submodule"

# Initialize submodules on new clones
git clone --recurse-submodules https://github.com/you/parent-project.git
```

### Option 3: Package Dependency Integration

For when NormPic is published as a package.

#### Step 1: Package Installation

**pyproject.toml**:
```toml
dependencies = [
    "normpic>=0.1.0",
    "pelican>=4.8.0",
    # ... other dependencies
]
```

#### Step 2: Programmatic Integration

**build.py**:
```python
from normpic.manager.photo_manager import organize_photos
from normpic.model.config import Config
from pathlib import Path

def build_galleries():
    """Direct programmatic integration with NormPic."""
    
    # Create config programmatically
    config = Config(
        collection_name="wedding",
        source_dir=str(Path.home() / "Photos/wedding/full"),
        dest_dir="./content/photos/wedding/full"
    )
    
    # Run photo organization directly
    manifest = organize_photos(
        source_dir=Path(config.source_dir),
        dest_dir=Path(config.dest_dir), 
        collection_name=config.collection_name,
        collection_description="Wedding photo collection",
        dry_run=False
    )
    
    print(f"Processed {len(manifest.pics)} photos")
    return manifest
```

## Project Configuration

### Environment Variables

Create a `.env` file for local development:

```bash
# .env - Not tracked in git
NORMPIC_PATH=/opt/normpic
PHOTOS_SOURCE_DIR=/home/marcus/Pictures
PHOTOS_DEST_DIR=./content/photos
SITE_OUTPUT_DIR=./output
```

### Configuration Files

**config/normpic.json**:
```json
{
  "collections": {
    "wedding": {
      "collection_name": "wedding",
      "collection_description": "Wedding photos from August 2025",
      "source_dir": "${PHOTOS_SOURCE_DIR}/wedding/full",
      "dest_dir": "${PHOTOS_DEST_DIR}/wedding/full",
      "timestamp_offset_hours": 0,
      "force_reprocess": false
    }
  }
}
```

**pelicanconf.py**:
```python
# Pelican configuration
SITENAME = "Marcus & Partner's Wedding"
SITEURL = "https://www.example.com"

# Content paths
PATH = "content"
OUTPUT_PATH = "output"

# Static paths for galleries
STATIC_PATHS = ["photos", "galleries"]

# Gallery configuration
GALLERY_CONFIG = {
    "photos_url": "/photos/",
    "thumbnails_url": "/galleries/thumbnails/",
    "full_res_available": True
}

# Theme and plugin settings
THEME = "themes/wedding-theme"
PLUGINS = ["gallery_builder_plugin"]
```

## Development Workflow

### Complete Build Process

```bash
#!/bin/bash
# build.sh - Complete build script

set -e

echo "🏗️  Starting build process..."

# 1. Ensure dependencies are installed
echo "📦 Installing dependencies..."
uv sync

# 2. Organize photos with NormPic
echo "📸 Organizing photos with NormPic..."
uv run build.py --photos-only

# 3. Generate galleries
echo "🖼️  Generating galleries..."
uv run build.py --galleries-only

# 4. Build site with Pelican
echo "🌐 Building site..."
uv run build.py --site-only

# 5. Optional: Deploy to CDN
if [ "$1" = "--deploy" ]; then
    echo "🚀 Deploying to CDN..."
    uv run build.py --deploy
fi

echo "✅ Build completed!"
```

### Development Server

**dev_server.py**:
```python
#!/usr/bin/env python3
"""Development server with auto-rebuild."""

import subprocess
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class BuildHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(('.md', '.html', '.css', '.js')):
            print(f"🔄 Rebuilding due to change: {event.src_path}")
            subprocess.run(["uv", "run", "build.py", "--site-only"])

def main():
    """Run development server with auto-rebuild."""
    
    # Initial build
    subprocess.run(["uv", "run", "build.py"])
    
    # Start file watcher
    event_handler = BuildHandler()
    observer = Observer()
    observer.schedule(event_handler, "content/", recursive=True)
    observer.schedule(event_handler, "themes/", recursive=True)
    observer.start()
    
    # Start Pelican dev server
    try:
        print("🌐 Starting development server on http://localhost:8000")
        subprocess.run(["pelican", "--listen", "--autoreload"])
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
```

## CI/CD Integration

### GitHub Actions Example

**.github/workflows/build.yml**:
```yaml
name: Build and Deploy Site

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
      with:
        submodules: recursive  # If using git submodules
    
    - name: Install uv
      uses: astral-sh/setup-uv@v1
      with:
        version: "latest"
    
    - name: Set up Python
      run: uv python install 3.12
    
    - name: Install NormPic (CLI approach)
      run: |
        git clone https://github.com/your-username/normpic.git /opt/normpic
        cd /opt/normpic
        uv sync
    
    - name: Install project dependencies
      run: uv sync
    
    - name: Build site
      run: uv run build.py
    
    - name: Deploy to CDN
      if: github.ref == 'refs/heads/main'
      run: uv run build.py --deploy
      env:
        CDN_ACCESS_KEY: ${{ secrets.CDN_ACCESS_KEY }}
        CDN_SECRET_KEY: ${{ secrets.CDN_SECRET_KEY }}
```

## Troubleshooting

### Common Setup Issues

**Issue**: `uv run` fails to find NormPic
```bash
# Solution: Verify NormPic path and installation
ls -la /opt/normpic
cd /opt/normpic && uv sync
```

**Issue**: Permission errors with photo directories
```bash
# Solution: Check file permissions
chmod -R 755 ~/Photos/
```

**Issue**: Build script can't find executables
```bash
# Solution: Add paths to environment
export PATH="/opt/normpic/.venv/bin:$PATH"
```

### Integration Testing

**test_integration.py**:
```python
import unittest
import subprocess
from pathlib import Path

class TestNormPicIntegration(unittest.TestCase):
    
    def test_normpic_available(self):
        """Test that NormPic is accessible."""
        result = subprocess.run([
            "uv", "run", "--project", "/opt/normpic", 
            "python", "main.py", "--help"
        ], capture_output=True)
        self.assertEqual(result.returncode, 0)
    
    def test_build_process(self):
        """Test complete build process."""
        result = subprocess.run(["uv", "run", "build.py", "--dry-run"])
        self.assertEqual(result.returncode, 0)

if __name__ == "__main__":
    unittest.main()
```

## Next Steps

1. Choose your integration approach (CLI recommended for most cases)
2. Set up the build scripts and configuration files
3. Test the integration with a small photo collection
4. See [Manifest Integration Guide](manifest-integration.md) for working with NormPic output data
5. See [Gallery Builder Integration](gallery-builder-integration.md) for creating gallery generators

For additional help, consult the [Error Handling Guide](errors.md) and [Integration Guide](integration.md).