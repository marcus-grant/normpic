"""Configuration data model."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any


@dataclass
class Config:
    """Collection configuration."""
    
    # Required fields
    collection_name: str
    source_dir: str
    dest_dir: str
    
    # Optional fields
    collection_description: Optional[str] = None
    timestamp_offset_hours: int = 0
    force_reprocess: bool = False
    
    @classmethod
    def from_json_file(cls, config_path: Path) -> 'Config':
        """Load configuration from JSON file.
        
        Args:
            config_path: Path to JSON configuration file
            
        Returns:
            Config object loaded from JSON
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If JSON is malformed
            ValueError: If required fields are missing or invalid
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in config file {config_path}: {e.msg}", e.doc, e.pos)
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create Config from dictionary with validation.
        
        Args:
            data: Configuration dictionary
            
        Returns:
            Config object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Check required fields
        required_fields = ['collection_name', 'source_dir', 'dest_dir']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required configuration fields: {missing_fields}")
        
        # Validate types
        if not isinstance(data['collection_name'], str) or not data['collection_name'].strip():
            raise ValueError("collection_name must be a non-empty string")
        
        if not isinstance(data['source_dir'], str) or not data['source_dir'].strip():
            raise ValueError("source_dir must be a non-empty string")
            
        if not isinstance(data['dest_dir'], str) or not data['dest_dir'].strip():
            raise ValueError("dest_dir must be a non-empty string")
        
        # Extract optional fields with defaults
        collection_description = data.get('collection_description')
        timestamp_offset_hours = data.get('timestamp_offset_hours', 0)
        force_reprocess = data.get('force_reprocess', False)
        
        # Validate optional fields
        if collection_description is not None and not isinstance(collection_description, str):
            raise ValueError("collection_description must be a string if provided")
            
        if not isinstance(timestamp_offset_hours, int):
            raise ValueError("timestamp_offset_hours must be an integer")
            
        if not isinstance(force_reprocess, bool):
            raise ValueError("force_reprocess must be a boolean")
        
        return cls(
            collection_name=data['collection_name'],
            source_dir=data['source_dir'],
            dest_dir=data['dest_dir'],
            collection_description=collection_description,
            timestamp_offset_hours=timestamp_offset_hours,
            force_reprocess=force_reprocess
        )
    
    @classmethod
    def get_default_config_path(cls) -> Path:
        """Get default configuration file path."""
        return Path('./config.json')
    
    def validate_paths(self) -> None:
        """Validate that source and destination paths are valid.
        
        Raises:
            ValueError: If paths are invalid
        """
        source_path = Path(self.source_dir)
        dest_path = Path(self.dest_dir)
        
        if not source_path.exists():
            raise ValueError(f"Source directory does not exist: {source_path}")
            
        if not source_path.is_dir():
            raise ValueError(f"Source path is not a directory: {source_path}")
        
        # Create destination directory if it doesn't exist
        dest_path.mkdir(parents=True, exist_ok=True)