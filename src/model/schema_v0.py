"""JSON Schema definitions for NormPic manifest v0.1.0."""

VERSION = "0.1.0"

PIC_SCHEMA = {
    "type": "object",
    "required": ["source_path", "dest_path", "hash", "size_bytes"],
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
            "items": {
                "type": "string",
                "enum": ["no_exif", "corrupted_file", "unsupported_format"]
            },
            "description": "Processing errors encountered"
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
        }
    }
}