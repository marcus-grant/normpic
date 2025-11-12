# NormPic CLI Usage Guide

## Overview

NormPic provides a command-line interface for
organizing photo collections using JSON configuration files.

>**⚠️ Note**: This CLI is in rapid development and will change significantly.
>This guide will need frequent updates.

## Basic Usage

```bash
# Organize photos using default config (./config.json)
python main.py

# Use custom config file
python main.py --config /path/to/my-config.json

# Dry run mode (no symlinks created)
python main.py --dry-run

# Verbose output
python main.py --verbose

# Force reprocessing (ignore existing results)  
python main.py --force

# Override configuration with CLI arguments
python main.py --source-dir /path/to/photos --dest-dir /path/to/output --collection-name "my-photos"

# Mix config file and CLI overrides
python main.py --config my-config.json --collection-name "override-name"
```

## CLI Configuration Options

The following CLI options override configuration file and environment variables:

### --source-dir
Override source directory containing original photos.

```bash
python main.py --source-dir /path/to/raw/photos
```

### --dest-dir
Override destination directory for organized photos.

```bash
python main.py --dest-dir /path/to/organized/photos
```

### --collection-name
Override collection name used in generated filenames.

```bash
python main.py --collection-name "wedding-2024"
```

## Configuration Precedence

CLI arguments have the highest precedence and override all other configuration sources:

1. **Default values** (lowest)
2. **Configuration file** (--config)
3. **Environment variables** (NORMPIC_*)
4. **CLI arguments** (highest)

```bash
# Example: CLI argument overrides config file
# config.json contains: "collection_name": "from-file"
# ENV: NORMPIC_COLLECTION_NAME="from-env"
# CLI: --collection-name "from-cli"
# Result: "from-cli" is used
```

## Configuration File

Create a `config.json` file in your project directory:

```json
{
  "collection_name": "wedding-photos",
  "source_dir": "/path/to/raw/photos",
  "dest_dir": "/path/to/organized/photos",
  "collection_description": "John and Jane's Wedding",
  "timestamp_offset_hours": 0,
  "force_reprocess": false
}
```

## Basic Workflow Example

1. **Prepare photos**: Place all photos in a source directory
2. **Create config**: Write a `config.json` file specifying source and destination
3. **Test first**: Run with `--dry-run --verbose` to preview results
4. **Organize**: Run without flags to create organized symlinks and manifest

```bash
# Preview what will happen
python main.py --config wedding-config.json --dry-run --verbose

# Actually organize the photos
python main.py --config wedding-config.json --verbose
```

## CLI Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--config PATH` | Path to configuration file | `./config.json` |
| `--dry-run` | Generate manifest without creating symlinks | False |
| `--verbose` | Show detailed processing information | False |
| `--force` | Reprocess everything, ignoring cache | False |
| `--help` | Show help message | - |

## Output

NormPic displays a summary after processing:

```txt
Processed 42 pics, 3 warnings, 0 errors
```

In verbose mode, you'll see:

- Configuration loading details
- Source and destination directories
- Collection name and description
- Processing progress
- Manifest file location

## Future Development

- Additional output formats
- Batch processing multiple collections
- Integration with cloud storage
- Advanced filtering options

This guide will be updated as the CLI evolves.

