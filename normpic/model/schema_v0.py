"""JSON Schema definitions for NormPic manifest v0.1.0."""

VERSION = "0.1.0"

ERROR_SCHEMA = {
    "type": "object",
    "required": ["error_type", "source_file"],
    "properties": {
        "error_type": {
            "type": "string",
            "enum": [
                "corrupted_file", 
                "unsupported_format", 
                "exif_error",
                "filesystem_error",
                "validation_error",
                "file_skipped"
            ],
            "description": "Type of error encountered (severity is intrinsic to type)"
        },
        "source_file": {
            "type": "string",
            "description": "Filename that caused the error"
        },
        "details": {
            "type": ["string", "null"],
            "description": "Additional error-specific details"
        }
    }
}

PIC_SCHEMA = {
    "type": "object",
    "required": ["source_path", "dest_path", "hash", "size_bytes", "mtime"],
    "properties": {
        "source_path": {
            "type": "string",
            "description": "Path to original photo file"
        },
        "dest_path": {
            "type": "string", 
            "description": "Path to organized/renamed photo file"
        },
        "hash": {
            "type": "string",
            "description": "SHA-256 hash of photo file"
        },
        "size_bytes": {
            "type": "integer",
            "minimum": 0,
            "description": "File size in bytes"
        },
        "mtime": {
            "type": "number",
            "description": "File modification time (Unix timestamp) for change detection"
        },
        "timestamp": {
            "type": ["string", "null"],
            "format": "date-time",
            "description": "Photo creation timestamp (ISO 8601)"
        },
        "timestamp_source": {
            "type": ["string", "null"],
            "enum": ["exif", "filename", "filesystem", "unknown", None],
            "description": "Source of timestamp information"
        },
        "camera": {
            "type": ["string", "null"],
            "description": "Camera make/model string"
        },
        "gps": {
            "type": ["object", "null"],
            "properties": {
                "lat": {
                    "type": "number",
                    "minimum": -90,
                    "maximum": 90
                },
                "lon": {
                    "type": "number", 
                    "minimum": -180,
                    "maximum": 180
                }
            },
            "required": ["lat", "lon"],
            "description": "GPS coordinates if available"
        },
        "errors": {
            "type": "array",
            "items": ERROR_SCHEMA,
            "description": "Processing errors encountered for this photo"
        },
        "warnings": {
            "type": "array", 
            "items": ERROR_SCHEMA,
            "description": "Processing warnings encountered for this photo"
        },
        "processing_status": {
            "type": "string",
            "enum": ["processed", "skipped", "failed", "processed_with_warnings"],
            "description": "Status of processing this photo"
        }
    }
}

MANIFEST_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object", 
    "required": ["version", "collection_name", "generated_at", "pics"],
    "properties": {
        "version": {
            "type": "string",
            "const": VERSION,
            "description": "Manifest schema version"
        },
        "collection_name": {
            "type": "string",
            "description": "Name of the photo collection"
        },
        "collection_description": {
            "type": ["string", "null"],
            "description": "Optional description of the collection"
        },
        "generated_at": {
            "type": "string", 
            "format": "date-time",
            "description": "When this manifest was generated (ISO 8601)"
        },
        "config": {
            "type": ["object", "null"],
            "description": "Configuration used to generate this manifest"
        },
        "pics": {
            "type": "array",
            "items": PIC_SCHEMA,
            "description": "List of processed photos"
        },
        "errors": {
            "type": "array",
            "items": ERROR_SCHEMA,
            "description": "Global processing errors not tied to specific photos"
        },
        "warnings": {
            "type": "array", 
            "items": ERROR_SCHEMA,
            "description": "Global processing warnings not tied to specific photos"
        },
        "processing_status": {
            "type": "object",
            "required": ["status", "total_files", "processed_successfully"],
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["completed", "completed_with_warnings", "failed"],
                    "description": "Overall processing status"
                },
                "total_files": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Total number of files encountered"
                },
                "processed_successfully": {
                    "type": "integer", 
                    "minimum": 0,
                    "description": "Number of files processed successfully"
                },
                "warnings_count": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Total number of warnings"
                },
                "errors_count": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Total number of errors"
                },
                "files_skipped": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Number of files skipped due to errors/warnings"
                }
            },
            "description": "Summary of processing results"
        }
    }
}