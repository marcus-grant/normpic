# Gallery Builder Integration Guide

## Overview

This guide explains how to build custom gallery generators that consume NormPic manifests and symlinked photos to create responsive HTML/CSS/JS galleries for static sites. The gallery builder integrates with Pelican while handling the specific requirements of photo gallery presentation.

## Gallery Builder Architecture

### Component Overview

```
NormPic Output → Gallery Builder → Pelican Integration → Static Site
     ↓               ↓                ↓                   ↓
Manifests +     HTML/CSS/JS      Gallery Pages      Complete Site
Symlinks        Templates        Integration        with Galleries
```

### Gallery Builder Responsibilities

1. **Manifest Processing**: Load and parse NormPic manifests
2. **Image Optimization**: Create thumbnails and web-optimized versions
3. **Template Rendering**: Generate HTML galleries from templates
4. **Asset Management**: Handle CSS, JavaScript, and image assets
5. **Pelican Integration**: Create Pelican-compatible content

## Basic Gallery Builder Implementation

### Core Gallery Generator

**gallery_builder/generator.py**:
```python
"""Core gallery generation functionality."""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image
from jinja2 import Environment, FileSystemLoader
from dataclasses import dataclass

from manifest_loader import load_manifest, ManifestData, PhotoMetadata

@dataclass
class GalleryConfig:
    """Gallery generation configuration."""
    manifest_path: Path
    photos_dir: Path
    output_dir: Path
    templates_dir: Path
    collection_name: str
    
    # Image processing settings
    thumbnail_size: tuple = (400, 400)
    medium_size: tuple = (1200, 800)
    jpeg_quality: int = 85
    webp_quality: int = 80
    
    # Gallery settings
    photos_per_page: int = 50
    enable_lightbox: bool = True
    enable_slideshow: bool = True
    enable_download: bool = False

class GalleryGenerator:
    """Generate static photo galleries from NormPic manifests."""
    
    def __init__(self, config: GalleryConfig):
        self.config = config
        self.manifest = load_manifest(config.manifest_path)
        
        # Set up Jinja2 templating
        self.jinja_env = Environment(
            loader=FileSystemLoader(config.templates_dir),
            autoescape=True
        )
        
        # Ensure output directories exist
        self.thumbnails_dir = config.output_dir / "thumbnails"
        self.medium_dir = config.output_dir / "medium"
        self.assets_dir = config.output_dir / "assets"
        
        for dir_path in [self.thumbnails_dir, self.medium_dir, self.assets_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def generate_gallery(self) -> Dict:
        """Generate complete gallery with all assets."""
        
        print(f"🖼️  Generating gallery for {self.config.collection_name}...")
        
        # Process images
        processed_photos = self._process_images()
        
        # Generate timeline and groupings
        timeline = self._generate_timeline(processed_photos)
        cameras = self._group_by_camera(processed_photos)
        
        # Create gallery pages
        gallery_data = {
            'collection_name': self.manifest.collection_name,
            'collection_description': self.manifest.collection_description,
            'generated_at': self.manifest.generated_at,
            'total_photos': len(processed_photos),
            'timeline': timeline,
            'cameras': cameras,
            'config': {
                'enable_lightbox': self.config.enable_lightbox,
                'enable_slideshow': self.config.enable_slideshow,
                'enable_download': self.config.enable_download
            }
        }
        
        # Generate HTML pages
        self._generate_index_page(gallery_data)
        self._generate_timeline_pages(timeline)
        self._generate_camera_pages(cameras)
        
        # Copy assets
        self._copy_assets()
        
        # Generate gallery metadata for Pelican
        gallery_metadata = self._create_pelican_metadata(gallery_data)
        
        print(f"✓ Gallery generated: {len(processed_photos)} photos")
        return gallery_metadata
    
    def _process_images(self) -> List[Dict]:
        """Process images to create thumbnails and optimized versions."""
        
        processed_photos = []
        
        for pic in self.manifest.pics:
            photo_path = self.config.photos_dir / pic.dest_path
            
            if not photo_path.exists():
                print(f"⚠️  Missing photo: {pic.dest_path}")
                continue
            
            try:
                # Process image
                processed = self._process_single_image(pic, photo_path)
                processed_photos.append(processed)
                
            except Exception as e:
                print(f"❌ Failed to process {pic.dest_path}: {e}")
                continue
        
        return processed_photos
    
    def _process_single_image(self, pic: PhotoMetadata, photo_path: Path) -> Dict:
        """Process a single image to create optimized versions."""
        
        stem = photo_path.stem
        
        # Output paths
        thumbnail_path = self.thumbnails_dir / f"{stem}.webp"
        medium_path = self.medium_dir / f"{stem}.webp"
        
        # Create thumbnail if it doesn't exist
        if not thumbnail_path.exists():
            self._create_thumbnail(photo_path, thumbnail_path)
        
        # Create medium version if it doesn't exist
        if not medium_path.exists():
            self._create_medium_version(photo_path, medium_path)
        
        # Create processed photo metadata
        return {
            'original': pic.dest_path,
            'thumbnail': f"thumbnails/{thumbnail_path.name}",
            'medium': f"medium/{medium_path.name}",
            'timestamp': pic.timestamp,
            'timestamp_dt': pic.timestamp_dt,
            'camera': pic.camera or 'Unknown',
            'size_mb': pic.size_bytes / 1024 / 1024,
            'metadata': {
                'timestamp_source': pic.timestamp_source,
                'gps': pic.gps,
                'errors': pic.errors
            }
        }
    
    def _create_thumbnail(self, source_path: Path, output_path: Path):
        """Create thumbnail image."""
        
        with Image.open(source_path) as img:
            # Convert to RGB if necessary (for WEBP output)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Create thumbnail maintaining aspect ratio
            img.thumbnail(self.config.thumbnail_size, Image.Resampling.LANCZOS)
            
            # Save as WEBP
            img.save(output_path, 'WEBP', quality=self.config.webp_quality)
    
    def _create_medium_version(self, source_path: Path, output_path: Path):
        """Create medium-sized version for gallery display."""
        
        with Image.open(source_path) as img:
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize to medium size maintaining aspect ratio
            img.thumbnail(self.config.medium_size, Image.Resampling.LANCZOS)
            
            img.save(output_path, 'WEBP', quality=self.config.webp_quality)
    
    def _generate_timeline(self, photos: List[Dict]) -> List[Dict]:
        """Generate chronological timeline."""
        
        # Group by date
        timeline = {}
        for photo in photos:
            date = photo['timestamp_dt'].date()
            if date not in timeline:
                timeline[date] = []
            timeline[date].append(photo)
        
        # Sort and format
        sorted_timeline = []
        for date in sorted(timeline.keys()):
            day_photos = sorted(timeline[date], key=lambda p: p['timestamp_dt'])
            
            sorted_timeline.append({
                'date': date.isoformat(),
                'display_date': date.strftime('%B %d, %Y'),
                'photo_count': len(day_photos),
                'photos': day_photos,
                'time_span': {
                    'start': day_photos[0]['timestamp'],
                    'end': day_photos[-1]['timestamp']
                }
            })
        
        return sorted_timeline
    
    def _group_by_camera(self, photos: List[Dict]) -> Dict[str, List[Dict]]:
        """Group photos by camera."""
        
        cameras = {}
        for photo in photos:
            camera = photo['camera']
            if camera not in cameras:
                cameras[camera] = []
            cameras[camera].append(photo)
        
        # Sort each camera's photos
        for camera in cameras:
            cameras[camera].sort(key=lambda p: p['timestamp_dt'])
        
        return cameras
    
    def _generate_index_page(self, gallery_data: Dict):
        """Generate main gallery index page."""
        
        template = self.jinja_env.get_template('gallery_index.html')
        
        # Recent photos for homepage
        recent_photos = sorted(
            [photo for day in gallery_data['timeline'] for photo in day['photos']],
            key=lambda p: p['timestamp_dt'],
            reverse=True
        )[:12]  # Show 12 most recent
        
        html_content = template.render(
            gallery=gallery_data,
            recent_photos=recent_photos
        )
        
        output_path = self.config.output_dir / "index.html"
        output_path.write_text(html_content)
    
    def _generate_timeline_pages(self, timeline: List[Dict]):
        """Generate timeline-based gallery pages."""
        
        template = self.jinja_env.get_template('gallery_timeline.html')
        
        # Generate page for each day
        for day in timeline:
            # Paginate photos if there are many
            photos = day['photos']
            page_size = self.config.photos_per_page
            
            if len(photos) <= page_size:
                # Single page
                html_content = template.render(
                    day=day,
                    photos=photos,
                    page=1,
                    total_pages=1
                )
                
                output_path = self.config.output_dir / f"timeline_{day['date']}.html"
                output_path.write_text(html_content)
            else:
                # Multiple pages
                total_pages = (len(photos) + page_size - 1) // page_size
                
                for page_num in range(total_pages):
                    start_idx = page_num * page_size
                    end_idx = start_idx + page_size
                    page_photos = photos[start_idx:end_idx]
                    
                    html_content = template.render(
                        day=day,
                        photos=page_photos,
                        page=page_num + 1,
                        total_pages=total_pages
                    )
                    
                    output_path = self.config.output_dir / f"timeline_{day['date']}_page_{page_num + 1}.html"
                    output_path.write_text(html_content)
    
    def _generate_camera_pages(self, cameras: Dict[str, List[Dict]]):
        """Generate camera-specific gallery pages."""
        
        template = self.jinja_env.get_template('gallery_camera.html')
        
        for camera, photos in cameras.items():
            html_content = template.render(
                camera_name=camera,
                photos=photos,
                photo_count=len(photos)
            )
            
            # Safe filename for camera
            safe_camera = "".join(c for c in camera if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_camera = safe_camera.replace(' ', '_').lower()
            
            output_path = self.config.output_dir / f"camera_{safe_camera}.html"
            output_path.write_text(html_content)
    
    def _copy_assets(self):
        """Copy CSS, JS, and other assets."""
        
        assets_source = self.config.templates_dir / "assets"
        if assets_source.exists():
            shutil.copytree(assets_source, self.assets_dir, dirs_exist_ok=True)
    
    def _create_pelican_metadata(self, gallery_data: Dict) -> Dict:
        """Create metadata for Pelican integration."""
        
        # Generate Pelican page metadata
        metadata_path = self.config.output_dir / "gallery_metadata.json"
        
        pelican_metadata = {
            'collection_name': gallery_data['collection_name'],
            'title': f"{gallery_data['collection_name'].title()} Photo Gallery",
            'slug': gallery_data['collection_name'],
            'template': 'gallery',
            'status': 'published',
            'total_photos': gallery_data['total_photos'],
            'generated_at': gallery_data['generated_at'],
            'gallery_url': f"galleries/{gallery_data['collection_name']}/",
            'thumbnail_url': f"galleries/{gallery_data['collection_name']}/thumbnails/",
            'timeline_pages': len(gallery_data['timeline']),
            'cameras': list(gallery_data['cameras'].keys())
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(pelican_metadata, f, indent=2)
        
        return pelican_metadata
```

## Gallery Templates

### Base Template Structure

**templates/base.html**:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ gallery.collection_name | title }} Gallery{% endblock %}</title>
    
    <!-- CSS -->
    <link rel="stylesheet" href="assets/gallery.css">
    {% if gallery.config.enable_lightbox %}
    <link rel="stylesheet" href="assets/lightbox.css">
    {% endif %}
    
    <!-- Meta tags for social sharing -->
    <meta property="og:title" content="{% block og_title %}{{ gallery.collection_name | title }} Gallery{% endblock %}">
    <meta property="og:type" content="website">
    <meta property="og:description" content="{% block og_description %}Photo gallery from {{ gallery.collection_name }}{% endblock %}">
    
    {% block extra_head %}{% endblock %}
</head>
<body>
    <header class="gallery-header">
        <nav class="gallery-nav">
            <a href="../index.html" class="nav-home">← Back to Site</a>
            <h1 class="gallery-title">{{ gallery.collection_name | title }}</h1>
            <div class="nav-links">
                <a href="index.html">Gallery Home</a>
                {% if gallery.cameras | length > 1 %}
                <div class="dropdown">
                    <button class="dropdown-toggle">Cameras</button>
                    <div class="dropdown-menu">
                        {% for camera in gallery.cameras.keys() %}
                        <a href="camera_{{ camera | lower | replace(' ', '_') }}.html">{{ camera }}</a>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}
            </div>
        </nav>
    </header>

    <main class="gallery-main">
        {% block content %}{% endblock %}
    </main>

    <footer class="gallery-footer">
        <p>{{ gallery.total_photos }} photos • Generated {{ gallery.generated_at | strftime('%B %d, %Y') }}</p>
        {% if gallery.collection_description %}
        <p>{{ gallery.collection_description }}</p>
        {% endif %}
    </footer>

    <!-- JavaScript -->
    <script src="assets/gallery.js"></script>
    {% if gallery.config.enable_lightbox %}
    <script src="assets/lightbox.js"></script>
    {% endif %}
    {% if gallery.config.enable_slideshow %}
    <script src="assets/slideshow.js"></script>
    {% endif %}
    
    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

### Gallery Index Template

**templates/gallery_index.html**:
```html
{% extends "base.html" %}

{% block content %}
<div class="gallery-overview">
    <div class="gallery-stats">
        <div class="stat">
            <span class="stat-number">{{ gallery.total_photos }}</span>
            <span class="stat-label">Photos</span>
        </div>
        <div class="stat">
            <span class="stat-number">{{ gallery.timeline | length }}</span>
            <span class="stat-label">Days</span>
        </div>
        <div class="stat">
            <span class="stat-number">{{ gallery.cameras | length }}</span>
            <span class="stat-label">{{ 'Camera' if gallery.cameras | length == 1 else 'Cameras' }}</span>
        </div>
    </div>

    <div class="recent-photos">
        <h2>Recent Photos</h2>
        <div class="photo-grid">
            {% for photo in recent_photos %}
            <div class="photo-item" data-timestamp="{{ photo.timestamp }}">
                <img src="{{ photo.thumbnail }}" 
                     alt="Photo from {{ photo.timestamp | strftime('%B %d, %Y at %I:%M %p') }}"
                     loading="lazy"
                     {% if gallery.config.enable_lightbox %}
                     data-lightbox="recent"
                     data-lightbox-src="{{ photo.medium }}"
                     {% endif %}>
                <div class="photo-info">
                    <time datetime="{{ photo.timestamp }}">{{ photo.timestamp | strftime('%b %d') }}</time>
                    <span class="camera">{{ photo.camera }}</span>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="timeline-navigation">
        <h2>Browse by Timeline</h2>
        <div class="timeline-days">
            {% for day in gallery.timeline %}
            <a href="timeline_{{ day.date }}.html" class="timeline-day">
                <div class="day-date">{{ day.display_date }}</div>
                <div class="day-count">{{ day.photo_count }} photos</div>
                <div class="day-time-span">
                    {{ day.time_span.start | strftime('%I:%M %p') }} - 
                    {{ day.time_span.end | strftime('%I:%M %p') }}
                </div>
            </a>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
```

### Timeline Template

**templates/gallery_timeline.html**:
```html
{% extends "base.html" %}

{% block title %}{{ day.display_date }} - {{ super() }}{% endblock %}

{% block content %}
<div class="timeline-gallery">
    <div class="timeline-header">
        <h2>{{ day.display_date }}</h2>
        <p>{{ day.photo_count }} photos from {{ day.time_span.start | strftime('%I:%M %p') }} 
           to {{ day.time_span.end | strftime('%I:%M %p') }}</p>
        
        {% if total_pages > 1 %}
        <div class="pagination">
            {% if page > 1 %}
            <a href="timeline_{{ day.date }}_page_{{ page - 1 }}.html" class="page-prev">← Previous</a>
            {% endif %}
            <span class="page-info">Page {{ page }} of {{ total_pages }}</span>
            {% if page < total_pages %}
            <a href="timeline_{{ day.date }}_page_{{ page + 1 }}.html" class="page-next">Next →</a>
            {% endif %}
        </div>
        {% endif %}
    </div>

    <div class="photo-gallery">
        {% for photo in photos %}
        <div class="photo-item" 
             data-timestamp="{{ photo.timestamp }}"
             data-camera="{{ photo.camera }}">
            <img src="{{ photo.thumbnail }}" 
                 alt="Photo from {{ photo.timestamp | strftime('%I:%M:%S %p') }}"
                 loading="lazy"
                 {% if gallery.config.enable_lightbox %}
                 data-lightbox="timeline"
                 data-lightbox-src="{{ photo.medium }}"
                 data-lightbox-caption="{{ photo.timestamp | strftime('%I:%M:%S %p') }} - {{ photo.camera }}"
                 {% endif %}>
            
            <div class="photo-overlay">
                <div class="photo-time">{{ photo.timestamp | strftime('%I:%M %p') }}</div>
                <div class="photo-camera">{{ photo.camera }}</div>
                {% if gallery.config.enable_download %}
                <a href="{{ photo.original }}" download class="photo-download">⬇</a>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>

    {% if total_pages > 1 %}
    <div class="pagination pagination-bottom">
        {% if page > 1 %}
        <a href="timeline_{{ day.date }}_page_{{ page - 1 }}.html" class="page-prev">← Previous</a>
        {% endif %}
        <span class="page-info">Page {{ page }} of {{ total_pages }}</span>
        {% if page < total_pages %}
        <a href="timeline_{{ day.date }}_page_{{ page + 1 }}.html" class="page-next">Next →</a>
        {% endif %}
    </div>
    {% endif %}
</div>
{% endblock %}
```

## CSS and JavaScript Assets

### Gallery Styles

**templates/assets/gallery.css**:
```css
/* Gallery Base Styles */
.gallery-header {
    background: #fff;
    border-bottom: 1px solid #e0e0e0;
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 100;
}

.gallery-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.gallery-title {
    font-size: 1.5rem;
    margin: 0;
    color: #333;
}

.nav-links {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.nav-links a {
    text-decoration: none;
    color: #666;
    font-weight: 500;
}

.nav-links a:hover {
    color: #333;
}

/* Photo Grid */
.photo-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    padding: 1rem;
}

.photo-item {
    position: relative;
    aspect-ratio: 1;
    overflow: hidden;
    border-radius: 8px;
    cursor: pointer;
    transition: transform 0.2s ease;
}

.photo-item:hover {
    transform: scale(1.02);
}

.photo-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: opacity 0.2s ease;
}

.photo-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(transparent, rgba(0,0,0,0.7));
    color: white;
    padding: 1rem;
    transform: translateY(100%);
    transition: transform 0.2s ease;
}

.photo-item:hover .photo-overlay {
    transform: translateY(0);
}

/* Timeline Navigation */
.timeline-days {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
    padding: 1rem;
}

.timeline-day {
    display: block;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 8px;
    text-decoration: none;
    color: inherit;
    transition: background-color 0.2s ease;
}

.timeline-day:hover {
    background: #e9ecef;
}

.day-date {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.day-count {
    color: #666;
    margin-bottom: 0.25rem;
}

.day-time-span {
    font-size: 0.9rem;
    color: #888;
}

/* Gallery Stats */
.gallery-stats {
    display: flex;
    justify-content: center;
    gap: 2rem;
    padding: 2rem 1rem;
    background: #f8f9fa;
}

.stat {
    text-align: center;
}

.stat-number {
    display: block;
    font-size: 2rem;
    font-weight: 700;
    color: #333;
}

.stat-label {
    font-size: 0.9rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Pagination */
.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    padding: 2rem 1rem;
}

.pagination a {
    padding: 0.5rem 1rem;
    background: #007bff;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    transition: background-color 0.2s ease;
}

.pagination a:hover {
    background: #0056b3;
}

/* Responsive Design */
@media (max-width: 768px) {
    .gallery-nav {
        flex-direction: column;
        gap: 1rem;
    }
    
    .photo-grid {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    }
    
    .gallery-stats {
        flex-direction: column;
        gap: 1rem;
    }
    
    .timeline-days {
        grid-template-columns: 1fr;
    }
}
```

### Lightbox JavaScript

**templates/assets/lightbox.js**:
```javascript
// Simple lightbox implementation
class GalleryLightbox {
    constructor() {
        this.currentIndex = 0;
        this.images = [];
        this.lightboxEl = null;
        
        this.init();
    }
    
    init() {
        this.createLightboxHTML();
        this.bindEvents();
        this.collectImages();
    }
    
    createLightboxHTML() {
        const lightboxHTML = `
            <div id="gallery-lightbox" class="lightbox">
                <div class="lightbox-content">
                    <img class="lightbox-image" src="" alt="">
                    <div class="lightbox-caption"></div>
                    <button class="lightbox-close">&times;</button>
                    <button class="lightbox-prev">&#8249;</button>
                    <button class="lightbox-next">&#8250;</button>
                    <div class="lightbox-counter">
                        <span class="lightbox-current">1</span> / <span class="lightbox-total">1</span>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', lightboxHTML);
        this.lightboxEl = document.getElementById('gallery-lightbox');
    }
    
    bindEvents() {
        // Close lightbox
        this.lightboxEl.querySelector('.lightbox-close').addEventListener('click', () => {
            this.close();
        });
        
        // Navigation
        this.lightboxEl.querySelector('.lightbox-prev').addEventListener('click', () => {
            this.prev();
        });
        
        this.lightboxEl.querySelector('.lightbox-next').addEventListener('click', () => {
            this.next();
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (!this.lightboxEl.classList.contains('active')) return;
            
            switch(e.key) {
                case 'Escape':
                    this.close();
                    break;
                case 'ArrowLeft':
                    this.prev();
                    break;
                case 'ArrowRight':
                    this.next();
                    break;
            }
        });
        
        // Click outside to close
        this.lightboxEl.addEventListener('click', (e) => {
            if (e.target === this.lightboxEl) {
                this.close();
            }
        });
    }
    
    collectImages() {
        const imageElements = document.querySelectorAll('[data-lightbox]');
        
        imageElements.forEach((el, index) => {
            const src = el.dataset.lightboxSrc || el.src;
            const caption = el.dataset.lightboxCaption || el.alt;
            
            this.images.push({ src, caption, element: el });
            
            el.addEventListener('click', (e) => {
                e.preventDefault();
                this.open(index);
            });
        });
    }
    
    open(index) {
        this.currentIndex = index;
        this.updateLightbox();
        this.lightboxEl.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    close() {
        this.lightboxEl.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    prev() {
        this.currentIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
        this.updateLightbox();
    }
    
    next() {
        this.currentIndex = (this.currentIndex + 1) % this.images.length;
        this.updateLightbox();
    }
    
    updateLightbox() {
        const image = this.images[this.currentIndex];
        
        this.lightboxEl.querySelector('.lightbox-image').src = image.src;
        this.lightboxEl.querySelector('.lightbox-caption').textContent = image.caption;
        this.lightboxEl.querySelector('.lightbox-current').textContent = this.currentIndex + 1;
        this.lightboxEl.querySelector('.lightbox-total').textContent = this.images.length;
    }
}

// Initialize lightbox when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new GalleryLightbox();
});
```

## Pelican Integration

### Gallery Plugin

**pelican_plugins/gallery_integration.py**:
```python
"""Pelican plugin for NormPic gallery integration."""

import json
from pathlib import Path
from pelican import signals
from pelican.contents import Page

def generate_gallery_pages(generator):
    """Generate Pelican pages from gallery metadata."""
    
    galleries_dir = Path(generator.settings['PATH']) / 'galleries'
    
    if not galleries_dir.exists():
        return
    
    for gallery_dir in galleries_dir.iterdir():
        if not gallery_dir.is_dir():
            continue
        
        metadata_file = gallery_dir / 'gallery_metadata.json'
        if not metadata_file.exists():
            continue
        
        # Load gallery metadata
        with open(metadata_file) as f:
            gallery_metadata = json.load(f)
        
        # Create Pelican page
        page_content = f"""
Title: {gallery_metadata['title']}
Slug: gallery-{gallery_metadata['slug']}
Template: gallery_page
Status: {gallery_metadata['status']}
Gallery-Path: {gallery_dir.relative_to(Path(generator.settings['PATH']))}

# {gallery_metadata['title']}

{gallery_metadata.get('description', 'Photo gallery')}

<div class="gallery-embed">
    <iframe src="{gallery_metadata['gallery_url']}" 
            width="100%" 
            height="600px" 
            frameborder="0">
    </iframe>
    <p><a href="{gallery_metadata['gallery_url']}" target="_blank">View Full Gallery</a></p>
</div>
        """
        
        # Create page object
        page = Page(
            content=page_content,
            metadata=gallery_metadata,
            source_path=str(metadata_file),
            context=generator.context,
            base_dir=generator.path
        )
        
        generator.pages.append(page)

def register():
    """Register the plugin with Pelican."""
    signals.page_generator_finalized.connect(generate_gallery_pages)
```

## Usage Example

### Complete Gallery Builder Script

**build_galleries.py**:
```python
#!/usr/bin/env python3
"""Build all galleries from NormPic manifests."""

import sys
from pathlib import Path
from gallery_builder.generator import GalleryGenerator, GalleryConfig

def main():
    """Build all configured galleries."""
    
    # Gallery configurations
    galleries = [
        {
            'name': 'wedding',
            'manifest_path': Path('content/photos/wedding/full/manifest.json'),
            'photos_dir': Path('content/photos/wedding/full'),
            'output_dir': Path('content/galleries/wedding'),
            'templates_dir': Path('gallery_templates')
        }
    ]
    
    for gallery_config in galleries:
        if not gallery_config['manifest_path'].exists():
            print(f"⚠️  Skipping {gallery_config['name']}: manifest not found")
            continue
        
        config = GalleryConfig(**gallery_config)
        generator = GalleryGenerator(config)
        
        try:
            metadata = generator.generate_gallery()
            print(f"✓ Generated {gallery_config['name']} gallery")
            
        except Exception as e:
            print(f"❌ Failed to generate {gallery_config['name']}: {e}")
            return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

## Next Steps

1. Implement the gallery builder for your specific design requirements
2. Create custom templates matching your site's theme
3. See [Deployment Integration Guide](deployment-integration.md) for CDN deployment
4. Test with your NormPic manifests and photo collections

For troubleshooting gallery generation issues, see the [Error Handling Guide](errors.md) and [Integration Guide](integration.md).