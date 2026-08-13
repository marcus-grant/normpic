# Error Handling Guide

## Overview

NormPic handles per-file problems gracefully so photo processing
continues even when individual files have issues.
Diagnostics are emitted to the producer's runtime logs, not written
into the manifest.
The manifest is contract-pure: it describes only the collection's
pics and carries no error, warning, or status fields.
See [manifest-contract.md](../architecture/manifest-contract.md).

## Error categories and severity

Errors have intrinsic severity based on type.

### Info level

Files intentionally skipped; processing continues normally.

- `unsupported_format`: format not processed (e.g. `.pdf`, `.txt`,
  `.cr2`).
  Common in mixed-content directories.

### Warning level

Individual-file problems that do not stop overall processing.

- `corrupted_file`: corrupted or invalid image data.
  The file is skipped and processing continues.
- `exif_error`: EXIF extraction failed.
  NormPic falls back to a filesystem timestamp; the file may still be
  processed with reduced metadata accuracy.

### Error level

Serious issues that may halt processing.

- `filesystem_error`: permission denied, disk full, or I/O error.
  May indicate a broader system problem.
- `validation_error`: manifest or configuration validation failure.
  Processing typically cannot continue.

## Where diagnostics go

Diagnostics are written to the producer's logs at runtime.
They are not serialized into the manifest, and there is no
`errors`, `warnings`, or `processing_status` field in the manifest
schema.
A structured diagnostics sidecar may be added in a future version;
until then, the live log is the record.
See the anticipated-additions list in
[manifest-contract.md](../architecture/manifest-contract.md).

## Troubleshooting common issues

### "Permission denied"

- Check file and directory permissions.
- Ensure NormPic can read the source directory.
- Ensure NormPic can write the destination directory.

### "Corrupted file" warnings

- Files may be incomplete downloads.
- Re-download or recover from backup.
- Files are safely skipped; processing continues.

### "EXIF error" with fallback

- The file is processed using a filesystem timestamp instead.
- Temporal ordering may be less accurate.
- Repair EXIF data if accuracy is critical.

### Repeated "unsupported_format" messages

- Normal in directories with mixed file types.
- Point `source_dir` at a photo-only directory.
- Consider pre-filtering the source directory.

## Future enhancements

- CLI commands to filter and analyze diagnostics by type.
- A structured diagnostics sidecar alongside the manifest.
- Integration with photo-repair tools.