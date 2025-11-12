# Environment Variable Configuration

## Overview

NormPic supports secure environment variable configuration for deployment and automation scenarios. Only specific whitelisted `NORMPIC_*` variables are supported for security.

## Supported Variables

### NORMPIC_SOURCE_DIR
Source directory containing original photos.

```bash
export NORMPIC_SOURCE_DIR="/path/to/photos"
```

### NORMPIC_DEST_DIR  
Destination directory for organized symlinks and manifest.

```bash
export NORMPIC_DEST_DIR="/path/to/organized"
```

### NORMPIC_COLLECTION_NAME
Collection name used in generated filenames.

```bash
export NORMPIC_COLLECTION_NAME="wedding-2024"
```

### NORMPIC_CONFIG_PATH
Path to JSON configuration file.

```bash
export NORMPIC_CONFIG_PATH="/path/to/config.json"
```

## Configuration Precedence

The configuration system follows strict precedence order:

1. **Defaults** (lowest priority)
2. **Configuration file** 
3. **Environment variables**
4. **CLI arguments** (highest priority)

## Usage Examples

### Basic Environment Setup

```bash
#!/bin/bash
# Photo processing environment
export NORMPIC_SOURCE_DIR="/mnt/photos/raw"
export NORMPIC_DEST_DIR="/mnt/photos/organized"
export NORMPIC_COLLECTION_NAME="vacation-2024"

# Run photo organization
normpic organize
```

### Docker Deployment

```dockerfile
FROM python:3.12
COPY . /app
WORKDIR /app

ENV NORMPIC_SOURCE_DIR="/input"
ENV NORMPIC_DEST_DIR="/output"
ENV NORMPIC_COLLECTION_NAME="photos"

CMD ["normpic", "organize"]
```

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Organize Photos
  env:
    NORMPIC_SOURCE_DIR: ${{ github.workspace }}/photos
    NORMPIC_DEST_DIR: ${{ github.workspace }}/output
    NORMPIC_COLLECTION_NAME: ${{ github.event.repository.name }}
  run: |
    normpic organize --dry-run
```

## Override Behavior

Environment variables override file configuration values:

```bash
# config.json contains:
# {"collection_name": "default", "source_dir": "/home/photos"}

export NORMPIC_COLLECTION_NAME="override-name"
# Result: collection_name="override-name", source_dir="/home/photos"
```

## Security Features

### Whitelisted Variables Only

The system only reads specific `NORMPIC_*` variables:
- No shell environment enumeration
- Ignores unknown variables
- Prevents information leakage

### Testing with Mocks

All environment variable tests use mocked environments:

```python
@patch.dict('os.environ', {
    'NORMPIC_SOURCE_DIR': '/test/source',
    'NORMPIC_COLLECTION_NAME': 'test-collection'
}, clear=True)
def test_env_override():
    # Test implementation
    pass
```

The `clear=True` parameter ensures no real environment variables leak into tests.

## Implementation Details

### Environment Variable Parsing

```python
from src.manager.config_manager import get_env_config, load_config_with_env_override

# Get only NORMPIC_* variables
env_config = get_env_config()
# Returns: {'source_dir': '/path', 'collection_name': 'name'}

# Load config with environment overrides
config = load_config_with_env_override(config_file_path)
```

### Whitelisted Variables

```python
ALLOWED_ENV_VARS = {
    'NORMPIC_SOURCE_DIR',
    'NORMPIC_DEST_DIR', 
    'NORMPIC_COLLECTION_NAME',
    'NORMPIC_CONFIG_PATH'
}
```

### Field Name Mapping

Environment variables are mapped to config fields:
- `NORMPIC_SOURCE_DIR` → `source_dir`
- `NORMPIC_DEST_DIR` → `dest_dir`
- `NORMPIC_COLLECTION_NAME` → `collection_name`
- `NORMPIC_CONFIG_PATH` → `config_path`

## Error Handling

### Invalid Paths

```bash
export NORMPIC_SOURCE_DIR="/nonexistent"
# Result: ValueError during path validation
```

### Unknown Variables

```bash
export NORMPIC_UNKNOWN_VAR="ignored"
export OTHER_APP_CONFIG="also-ignored"
# These are silently ignored for security
```

## Best Practices

### Production Deployment

1. **Use explicit configuration**: Set all required variables
2. **Validate paths**: Ensure directories exist before deployment
3. **Use absolute paths**: Avoid relative path issues
4. **Secure storage**: Use encrypted environment variable storage

### Development

1. **Use .env files**: For local development consistency
2. **Mock in tests**: Never use real environment variables in tests
3. **Document dependencies**: List required variables in deployment docs

### Container Deployment

```bash
# Docker run example
docker run \
  -e NORMPIC_SOURCE_DIR=/input \
  -e NORMPIC_DEST_DIR=/output \
  -e NORMPIC_COLLECTION_NAME=photos \
  -v /host/photos:/input:ro \
  -v /host/organized:/output \
  normpic:latest
```

## Troubleshooting

### Variable Not Taking Effect

1. Check variable name spelling (case-sensitive)
2. Verify variable is in whitelist
3. Check precedence (CLI args override env vars)
4. Validate path exists and is accessible

### Permission Issues

```bash
# Check directory permissions
ls -la "$NORMPIC_SOURCE_DIR"
ls -la "$NORMPIC_DEST_DIR"

# Verify write access to destination
touch "$NORMPIC_DEST_DIR/test" && rm "$NORMPIC_DEST_DIR/test"
```

### Integration Testing

```bash
# Test environment variable setup
export NORMPIC_SOURCE_DIR="/test/photos"
export NORMPIC_DEST_DIR="/test/output" 
export NORMPIC_COLLECTION_NAME="test"

# Dry run to validate configuration
normpic organize --dry-run --verbose
```