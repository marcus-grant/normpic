"""Configuration management with secure environment variable support.

Provides secure parsing of NORMPIC_* environment variables with proper validation
and precedence handling. Only reads specific whitelisted environment variables.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

from src.model.config import Config


# Whitelisted environment variables for security
ALLOWED_ENV_VARS = {
    'NORMPIC_SOURCE_DIR',
    'NORMPIC_DEST_DIR', 
    'NORMPIC_COLLECTION_NAME',
    'NORMPIC_CONFIG_PATH'
}


def get_env_config() -> Dict[str, Any]:
    """Securely extract NORMPIC_* environment variables.
    
    Returns:
        Dictionary of environment configuration values
        
    Security:
        Only reads specific whitelisted variables, never enumerates all env vars
    """
    env_config = {}
    
    # Only read specific whitelisted environment variables
    for var_name in ALLOWED_ENV_VARS:
        value = os.environ.get(var_name)
        if value is not None:
            # Map environment variable names to config field names
            field_name = var_name.lower().replace('normpic_', '')
            env_config[field_name] = value
    
    return env_config


def validate_env_paths(env_config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and convert path strings to Path objects.
    
    Args:
        env_config: Raw environment configuration dictionary
        
    Returns:
        Validated configuration with Path objects
        
    Raises:
        ValueError: If paths are invalid or don't exist
    """
    validated_config = env_config.copy()
    
    # Validate source directory
    if 'source_dir' in validated_config:
        source_path = Path(validated_config['source_dir'])
        if not source_path.exists():
            raise ValueError(f"Source directory does not exist: {source_path}")
        if not source_path.is_dir():
            raise ValueError(f"Source path is not a directory: {source_path}")
        validated_config['source_dir'] = source_path
    
    # Validate destination directory (create if needed)
    if 'dest_dir' in validated_config:
        dest_path = Path(validated_config['dest_dir'])
        # Create destination directory if it doesn't exist
        dest_path.mkdir(parents=True, exist_ok=True)
        validated_config['dest_dir'] = dest_path
    
    # Validate config path
    if 'config_path' in validated_config:
        config_path = Path(validated_config['config_path'])
        if not config_path.exists():
            raise ValueError(f"Config file does not exist: {config_path}")
        if not config_path.is_file():
            raise ValueError(f"Config path is not a file: {config_path}")
        validated_config['config_path'] = config_path
    
    return validated_config


def load_config_with_env_override(config_path: Optional[Path] = None) -> Config:
    """Load configuration with environment variable overrides.
    
    Args:
        config_path: Optional path to JSON config file
        
    Returns:
        Config object with environment variable overrides applied
        
    Precedence:
        defaults < config file < environment variables < CLI arguments
    """
    # Start with config from file
    if config_path and config_path.exists():
        config = Config.from_json_file(config_path)
    else:
        # Create minimal default config
        config = Config(
            collection_name="",
            source_dir="",
            dest_dir=""
        )
    
    # Get environment configuration
    env_config = get_env_config()
    
    if env_config:
        # Apply environment overrides directly
        for field_name, value in env_config.items():
            if hasattr(config, field_name):
                setattr(config, field_name, value)
    
    return config