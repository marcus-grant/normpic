# Error Handling Guide

## Overview

NormPic provides comprehensive error handling to ensure photo processing continues gracefully even when individual files have issues. This guide explains how to interpret error messages, understand severity levels, and troubleshoot common problems.

## Error Categories and Severity

Errors in NormPic have intrinsic severity levels based on their type:

### Info Level Errors
These are informational messages about files that are intentionally skipped:

- **`unsupported_format`** - File formats not supported for photo processing (e.g., `.pdf`, `.txt`, `.cr2`)
  - Files are skipped but processing continues normally
  - Common with mixed-content directories

### Warning Level Errors  
These indicate problems with individual files that don't stop overall processing:

- **`corrupted_file`** - Photo files with corrupted or invalid data
  - File is skipped but processing continues
  - Often caused by incomplete downloads or storage corruption

- **`exif_error`** - EXIF metadata extraction failures
  - NormPic attempts fallback to filesystem timestamps
  - File may still be processed with reduced metadata accuracy

### Error Level Errors
These are serious issues that may halt processing:

- **`filesystem_error`** - File system access problems
  - Permission denied, disk full, or I/O errors
  - May indicate broader system issues requiring attention

- **`validation_error`** - Manifest or configuration validation failures
  - Usually indicates corrupted configuration or manifest files
  - Processing typically cannot continue

## Error Structure

Errors are stored in a simplified, structured format:

```json
{
  "error_type": "corrupted_file",
  "source_file": "photo.jpg",
  "details": "Invalid EXIF data: unexpected end of file"
}
```

### Fields

- **`error_type`** - The category of error (determines severity)
- **`source_file`** - Filename that caused the error (not full path for security)
- **`details`** - Optional additional context about the error

## Reading Error Output

### In Manifest Files

Errors are recorded in the generated `manifest.json` file:

```json
{
  "warnings": [
    {
      "error_type": "corrupted_file",
      "source_file": "IMG_001.jpg", 
      "details": "EXIF data corrupted"
    }
  ],
  "errors": [
    {
      "error_type": "filesystem_error",
      "source_file": "IMG_002.jpg",
      "details": "Permission denied"
    }
  ]
}
```

### Processing Status

The manifest includes overall processing status:

```json
{
  "processing_status": {
    "status": "completed_with_warnings",
    "total_files": 150,
    "processed_successfully": 147,
    "warnings_count": 3,
    "errors_count": 0,
    "files_skipped": 3
  }
}
```

Status values:
- **`completed`** - All files processed successfully
- **`completed_with_warnings`** - Some files skipped but processing completed
- **`failed`** - Critical errors prevented completion

## Troubleshooting Common Issues

### "Permission denied" errors
- Check file/directory permissions
- Ensure NormPic has read access to source directory
- Ensure NormPic has write access to destination directory

### "Corrupted file" warnings
- Files may be incomplete downloads
- Try re-downloading or recovering from backup
- Files are safely skipped, processing continues

### "EXIF error" with fallback
- File processed using filesystem timestamp instead
- Results may have less accurate temporal ordering
- Consider using tools to repair EXIF data if accuracy is critical

### Multiple "unsupported_format" messages
- Normal in directories with mixed file types
- Use `--source-dir` to point to photo-only directories
- Consider pre-filtering source directory

## Performance Considerations

The simplified error handling system provides:

- **Fast Processing** - Minimal overhead during photo organization
- **Memory Efficient** - ~60% reduction in memory usage vs. previous versions
- **Structured Data** - Enables future CLI tools for error filtering and analysis

## Future Enhancements

Planned error handling improvements:

- CLI commands for filtering and analyzing errors by type
- Automated error recovery suggestions
- Integration with photo repair tools
- Enhanced error context and debugging information