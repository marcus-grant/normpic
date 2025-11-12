# Parent Project Integration Guide

## Overview

This guide explains how to integrate NormPic into parent projects for building complete photo gallery websites. NormPic serves as the foundational photo management system that normalizes collections and generates manifests, which are then consumed by gallery builders and integrated into broader site generation workflows.

## Architecture Overview

### Integration Flow

```
Source Photos → NormPic → Gallery Builder → Pelican → Bunny CDN
     ↓            ↓           ↓            ↓         ↓
Raw Images → Normalized → HTML/CSS/JS → Full Site → Live Site
            Manifests    Galleries     Content
```

### Component Responsibilities

1. **NormPic** (this project): Photo organization and manifest generation
   - EXIF extraction and temporal ordering
   - Normalized filename generation 
   - Symlink creation with consistent naming
   - JSON manifest output with comprehensive metadata

2. **Gallery Builder** (custom parent project component): Static gallery generation
   - Consumes NormPic manifests and symlinked photos
   - Generates responsive HTML/CSS/JS galleries
   - Optimizes images for web delivery
   - Creates gallery-specific metadata

3. **Pelican** (static site generator): Standard page generation
   - Renders markdown content (landing, about, contact pages)
   - Applies templates and themes
   - Integrates gallery pages with main site structure
   - Generates final static site

4. **Bunny CDN** (deployment target): Content delivery
   - Photos bucket (separate, longer TTL)
   - Site bucket (frequent updates, shorter TTL)
   - Global content distribution

## Integration Benefits

### For Photo Management
- **Consistent naming**: Predictable photo URLs for gallery builders
- **Temporal accuracy**: EXIF-based timeline verification and ordering
- **Change detection**: Manifest comparison enables incremental processing
- **Performance optimization**: Symlinks avoid duplicate storage during development

### For Site Generation
- **Separation of concerns**: Photo management independent of site generation
- **Incremental builds**: Only regenerate changed galleries
- **Multi-format support**: Same source photos for full-res and web-optimized versions
- **Deployment efficiency**: Upload only modified content to CDN

### For Deployment Pipeline
- **Dual bucket strategy**: Photos vs site content with different cache settings
- **Selective uploads**: Hash-based change detection prevents unnecessary transfers
- **Rollback capability**: Versioned manifests enable deployment rollbacks
- **Performance monitoring**: Built-in metrics for optimization

## Integration Workflow

### Phase 1: Photo Organization
```bash
# Run NormPic to normalize photo collections
uv run --project /path/to/normpic python main.py \
    --source-dir ~/Photos/wedding/full \
    --dest-dir ./content/photos/wedding/full \
    --collection-name wedding \
    --verbose
```

**Output**: 
- Normalized symlinks: `content/photos/wedding/full/wedding-20250809T132034-r5a.JPG`
- Manifest: `content/photos/wedding/full/manifest.json`

### Phase 2: Gallery Generation
```python
# Custom gallery builder consumes NormPic output
from gallery_builder import GalleryGenerator

generator = GalleryGenerator(
    manifest_path="content/photos/wedding/full/manifest.json",
    photos_dir="content/photos/wedding/full/",
    output_dir="content/galleries/wedding/"
)
gallery_metadata = generator.generate()
```

**Output**:
- Gallery HTML: `content/galleries/wedding/index.html`
- Optimized images: `content/galleries/wedding/thumbnails/`
- Gallery manifest: `content/galleries/wedding/gallery.json`

### Phase 3: Site Generation
```bash
# Pelican generates complete site including galleries
pelican content/ -o output/ -s pelicanconf.py
```

**Output**:
- Complete static site: `output/`
- Gallery pages integrated with main site navigation
- All content ready for CDN deployment

### Phase 4: Deployment
```bash
# Deploy to Bunny CDN with dual bucket strategy
./deploy.sh --photos-only    # Upload only changed photos
./deploy.sh --site-only      # Upload only changed site content  
./deploy.sh --full           # Full deployment (initial setup)
```

## Change Detection Strategy

### Photo Collection Changes
NormPic manifests enable efficient change detection:

```python
def detect_photo_changes(old_manifest, new_manifest):
    """Compare manifests to identify changes requiring gallery rebuild."""
    
    old_pics = {pic['dest_path']: pic for pic in old_manifest['pics']}
    new_pics = {pic['dest_path']: pic for pic in new_manifest['pics']}
    
    added = set(new_pics.keys()) - set(old_pics.keys())
    removed = set(old_pics.keys()) - set(new_pics.keys())
    
    # Check for hash changes (modified photos)
    modified = {
        path for path in old_pics.keys() & new_pics.keys()
        if old_pics[path]['hash'] != new_pics[path]['hash']
    }
    
    return {
        'added': list(added),
        'removed': list(removed), 
        'modified': list(modified),
        'requires_rebuild': bool(added or removed or modified)
    }
```

### Incremental Build Pipeline
```bash
#!/bin/bash
# Smart rebuild script

# 1. Run NormPic to update photo organization
uv run --project /path/to/normpic python main.py --config config.json

# 2. Detect changes using manifest comparison
if python detect_changes.py --old-manifest old/manifest.json --new-manifest new/manifest.json; then
    echo "Photo changes detected, rebuilding galleries..."
    
    # 3. Regenerate affected galleries only
    python gallery_builder.py --incremental
    
    # 4. Regenerate site with updated galleries
    pelican content/ -o output/ -s pelicanconf.py
    
    # 5. Deploy only changed content
    ./deploy.sh --incremental
else
    echo "No photo changes detected, skipping rebuild"
fi
```

## Deployment Configurations

### Dual Bucket Strategy

**Photos Bucket** (`photos.example.com`):
```json
{
    "name": "photos-bucket",
    "purpose": "Photo content managed by NormPic",
    "ttl": "30 days",
    "cache_control": "public, max-age=2592000",
    "update_frequency": "Infrequent (collection updates)",
    "content_types": ["image/jpeg", "image/png", "image/webp"]
}
```

**Site Bucket** (`www.example.com`):
```json
{
    "name": "site-bucket", 
    "purpose": "HTML/CSS/JS and site content",
    "ttl": "1 hour",
    "cache_control": "public, max-age=3600",
    "update_frequency": "Frequent (content updates)",
    "content_types": ["text/html", "text/css", "application/javascript"]
}
```

### Benefits of Separation
- **Performance**: Photos cached longer, reducing CDN costs
- **Flexibility**: Update site content without affecting photo URLs
- **Scalability**: Photo bucket can use different optimization settings
- **Security**: Different access controls for photos vs site content

## Integration Examples

### Example Parent Project Structure
```
my-wedding-site/
├── pyproject.toml              # Parent project dependencies
├── requirements/
│   └── normpic.txt            # NormPic integration requirements
├── content/
│   ├── pages/                 # Pelican markdown content
│   │   ├── about.md
│   │   └── contact.md
│   ├── photos/                # NormPic managed photos
│   │   ├── wedding/full/      # Full resolution symlinks + manifest
│   │   └── wedding/web/       # Web optimized symlinks + manifest
│   └── galleries/             # Generated gallery content
│       └── wedding/           # Gallery HTML/CSS/JS
├── tools/
│   ├── gallery_builder.py     # Custom gallery generator
│   ├── detect_changes.py      # Change detection script
│   └── deploy.sh              # Deployment automation
├── themes/                    # Pelican theme customizations
└── config/
    ├── normpic.json           # NormPic configuration
    └── pelicanconf.py         # Pelican configuration
```

### Integration Configuration Example
```json
{
  "normpic": {
    "collections": {
      "wedding": {
        "source_full": "~/Photos/wedding/full",
        "source_web": "~/Photos/wedding/web", 
        "dest_full": "./content/photos/wedding/full",
        "dest_web": "./content/photos/wedding/web",
        "collection_name": "wedding"
      }
    }
  },
  "gallery_builder": {
    "input_manifests": [
      "./content/photos/wedding/full/manifest.json",
      "./content/photos/wedding/web/manifest.json"
    ],
    "output_dir": "./content/galleries/wedding/"
  },
  "deployment": {
    "photos_bucket": "photos.example.com",
    "site_bucket": "www.example.com", 
    "cdn_endpoint": "https://cdn.example.com"
  }
}
```

## Next Steps

For detailed implementation guidance, see:

1. [Parent Project Setup Guide](parent-project-setup.md) - Specific setup instructions including uv integration
2. [Manifest Consumption Guide](manifest-integration.md) - Working with NormPic manifest data
3. [Gallery Builder Integration](gallery-builder-integration.md) - Building custom gallery generators  
4. [Deployment Integration](deployment-integration.md) - CDN deployment strategies

## Troubleshooting Integration Issues

### Common Integration Problems

**Problem**: NormPic not found in parent project
**Solution**: See [Parent Project Setup Guide](parent-project-setup.md) for proper uv integration

**Problem**: Manifest changes not detected
**Solution**: Verify manifest file locations and implement proper change detection logic

**Problem**: Gallery rebuild performance issues
**Solution**: Use incremental building and manifest comparison for selective updates

**Problem**: CDN deployment conflicts
**Solution**: Implement dual bucket strategy with proper cache headers

For additional support, see the [Error Handling Guide](errors.md) and project documentation.