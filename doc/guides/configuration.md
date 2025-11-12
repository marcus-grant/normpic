# Configuration Reference

## Overview

NormPic uses JSON configuration files to specify photo collection settings and processing parameters. Configuration follows a strict precedence hierarchy: **defaults < config file < environment variables < CLI arguments**.

## Configuration Precedence

The configuration system applies settings in this order (later sources override earlier ones):

1. **Default values** (lowest priority)
2. **JSON configuration file** 
3. **Environment variables** (NORMPIC_*)
4. **CLI arguments** (highest priority)

This allows flexible deployment scenarios while maintaining predictable overrides.

## Configuration File Format

### Basic Example

```json
{
  "collection_name": "wedding-photos",
  "source_dir": "/Users/photographer/raw-photos",
  "dest_dir": "/Users/photographer/organized-photos"
}
```

### Complete Example

```json
{
  "collection_name": "vacation-crete-2025",
  "source_dir": "/home/photos/vacation/raw",
  "dest_dir": "/home/photos/vacation/organized",
  "collection_description": "Family vacation to Crete, June 2025",
  "timestamp_offset_hours": 2,
  "force_reprocess": false
}
```

## Required Fields

### `collection_name` (string)
- Name used in generated filenames
- Must be non-empty
- Recommended: kebab-case format (e.g., `wedding-photos`, `graduation-2025`)

**Examples:**
```json
"collection_name": "wedding-photos"
"collection_name": "vacation-italy" 
"collection_name": "graduation-2025"
```

### `source_dir` (string)  
- Path to directory containing original photos
- Must exist and be readable
- Can be absolute or relative path

**Examples:**
```json
"source_dir": "/Users/john/Photos/Wedding"
"source_dir": "./raw-photos"
"source_dir": "/mnt/camera-sd-card/DCIM"
```

### `dest_dir` (string)
- Path where organized photos and manifest will be created
- Will be created if it doesn't exist
- Must be writable

**Examples:**
```json
"dest_dir": "/Users/john/Photos/Organized/Wedding"
"dest_dir": "./organized"
"dest_dir": "/backup/photos/wedding-organized"
```

## Optional Fields

### `collection_description` (string, nullable)
- Human-readable description of the collection
- Stored in manifest for documentation
- Default: `null`

```json
"collection_description": "Sarah and John's wedding ceremony and reception"
```

### `timestamp_offset_hours` (integer)
- Hour offset for timestamp correction
- Useful for camera timezone errors
- Default: `0`

```json
"timestamp_offset_hours": -5  // Camera was 5 hours ahead
```

### `force_reprocess` (boolean)
- Whether to reprocess all photos ignoring existing results
- Can be overridden with `--force` CLI flag
- Default: `false`

```json
"force_reprocess": true
```

## Path Validation

### Source Directory Requirements
- Must exist before running NormPic
- Must be a directory (not a file)
- Must be readable by the user
- Should contain supported photo formats (jpg, jpeg, png, heic, webp)

### Destination Directory Behavior
- Created automatically if it doesn't exist
- Parent directories created as needed
- Must be writable by the user

## Supported Photo Formats

- `.jpg`, `.jpeg` (JPEG images)
- `.png` (PNG images) 
- `.heic` (iPhone HEIC format)
- `.webp` (WebP images)

Case-insensitive matching (e.g., `.JPG`, `.PNG` work too).

## Default Configuration Path

- Default: `./config.json` (current directory)
- Override with `--config` CLI flag
- File must exist (no automatic creation)

## Validation Errors

Common configuration errors:

```bash
# Missing required fields
"Missing required configuration fields: ['source_dir', 'dest_dir']"

# Empty required fields  
"collection_name must be a non-empty string"

# Invalid types
"timestamp_offset_hours must be an integer"

# Path issues
"Source directory does not exist: /invalid/path"
"Source path is not a directory: /path/to/file.jpg"
```

## Future Configuration Features

The following features are planned for future releases:

### Configuration Precedence System
Priority order (highest to lowest):
1. CLI arguments
2. Environment variables (`NORMPIC_*`)
3. Local config file
4. Default values

### Environment Variables
```bash
NORMPIC_SOURCE_DIR="/default/source"
NORMPIC_DEST_DIR="/default/dest"  
NORMPIC_COLLECTION_NAME="default-collection"
```

### Extended Configuration
- Multiple source directories
- Output format options
- Custom filename templates
- Cloud storage integration settings
- Advanced timestamp handling

## Best Practices

1. **Use absolute paths** for source/dest directories to avoid confusion
2. **Test with dry-run** before processing large collections
3. **Keep source photos read-only** to prevent accidental modifications
4. **Use descriptive collection names** that will make sense later
5. **Back up important photos** before processing