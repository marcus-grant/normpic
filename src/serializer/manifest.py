"""Manifest JSON serialization and validation."""

import json
from datetime import datetime

from jsonschema import validate

from src.model.manifest import Manifest
from src.model.pic import Pic
from src.model.schema_v0 import MANIFEST_SCHEMA


class ManifestSerializer:
    """Handles JSON serialization/deserialization and validation for manifests."""

    def serialize(self, manifest: Manifest, validate: bool = False) -> str:
        """Serialize Manifest to JSON string.
        
        Args:
            manifest: Manifest object to serialize
            validate: Whether to validate against schema before serializing
            
        Returns:
            JSON string representation
            
        Raises:
            ValidationError: If validate=True and manifest is invalid
        """
        if validate:
            self.validate(manifest)
            
        manifest_dict = manifest.to_dict()
        return json.dumps(manifest_dict, indent=2)

    def deserialize(self, json_str: str) -> Manifest:
        """Deserialize JSON string to Manifest object.
        
        Args:
            json_str: JSON string to deserialize
            
        Returns:
            Manifest object
            
        Raises:
            ValidationError: If JSON doesn't match manifest schema
            json.JSONDecodeError: If JSON is malformed
        """
        data = json.loads(json_str)
        
        # Validate against schema
        validate(instance=data, schema=MANIFEST_SCHEMA)
        
        # Convert to objects
        pics = []
        for pic_data in data["pics"]:
            # Parse timestamp if present
            timestamp = None
            if pic_data["timestamp"]:
                timestamp = datetime.fromisoformat(pic_data["timestamp"])
                
            pic = Pic(
                source_path=pic_data["source_path"],
                dest_path=pic_data["dest_path"],
                hash=pic_data["hash"],
                size_bytes=pic_data["size_bytes"],
                mtime=pic_data["mtime"],
                timestamp=timestamp,
                timestamp_source=pic_data["timestamp_source"],
                camera=pic_data["camera"],
                gps=pic_data["gps"],
                errors=pic_data["errors"] or []
            )
            pics.append(pic)
        
        # Parse generated_at timestamp
        generated_at = datetime.fromisoformat(data["generated_at"])
        
        manifest = Manifest(
            version=data["version"],
            collection_name=data["collection_name"],
            generated_at=generated_at,
            pics=pics,
            collection_description=data.get("collection_description"),
            config=data.get("config"),
            errors=data.get("errors"),
            warnings=data.get("warnings"),
            processing_status=data.get("processing_status")
        )
        
        return manifest

    def validate(self, manifest: Manifest) -> None:
        """Validate manifest against schema.
        
        Args:
            manifest: Manifest object to validate
            
        Raises:
            ValidationError: If manifest doesn't match schema
        """
        manifest_dict = manifest.to_dict()
        validate(instance=manifest_dict, schema=MANIFEST_SCHEMA)