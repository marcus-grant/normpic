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
    "required": ["hash", "size_bytes", "mtime"],
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
        "original_filename": {
            "type": "string",
            "minLength": 1,
            "pattern": r"^[^/\\]+$",
            "description": "Original filename with no path component"
        },
        "size_bytes": {
            "type": "integer",
            "minimum": 0,
            "description": "File size in bytes"
        },
        "mtime": {
            "type": "string",
            "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z$",
            "description": "File modification time (ISO-8601 UTC with Z suffix)"
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
        "relative_path": {
            "type": "string",
            "minLength": 1,
            "if": {"type": "string"},
            "then": {
                "allOf": [
                    {"not": {"pattern": "^/"}},
                    {"not": {"pattern": "^[A-Za-z]:"}},
                    {"not": {"pattern": "/$"}},
                    {"not": {"pattern": "//"}},
                    {"not": {"pattern": "(?:^|/)\\.{1,2}(?:/|$)"}},
                    {"not": {"pattern": "\\\\"}},
                ]
            },
            "description": "Path relative to the collection root. No leading slash or Windows drive (no absolute paths). No trailing slash. No empty segments. No '.' or '..' segments anywhere. No backslashes. UTF-8, NFC normalized (NFC enforced by implementations, not the schema).",
        },
        "tag": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Flat tag strings"
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
    "required": ["version", "collection_name", "generated_at", "pic"],
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
        "collection_root": {
            "type": "string",
            "minLength": 1,
            "description": "Location of collection root relative to manifest"
        },
        "pic": {
            "type": "array",
            "items": PIC_SCHEMA,
            "description": "List of processed photos"
        },
    }
}