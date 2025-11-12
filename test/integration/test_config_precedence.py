"""Integration tests for config precedence system."""

import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from src.manager.config_manager import load_config_with_env_override


class TestConfigPrecedence:
    """Test configuration precedence: defaults < file < env < cli."""
    
    def test_env_overrides_file_config(self):
        """Test that environment variables override file configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create directories
            file_source = temp_path / "file_source" 
            file_dest = temp_path / "file_dest"
            env_source = temp_path / "env_source"
            env_dest = temp_path / "env_dest" 
            
            file_source.mkdir()
            file_dest.mkdir()
            env_source.mkdir()
            env_dest.mkdir()
            
            # Create config file
            config_file = temp_path / "config.json"
            config_data = {
                "collection_name": "file-collection",
                "source_dir": str(file_source),
                "dest_dir": str(file_dest)
            }
            config_file.write_text(json.dumps(config_data))
            
            # Mock environment to override file
            with patch.dict('os.environ', {
                'NORMPIC_COLLECTION_NAME': 'env-collection',
                'NORMPIC_SOURCE_DIR': str(env_source)
            }, clear=True):
                config = load_config_with_env_override(config_file)
                
                # Environment should win
                assert config.collection_name == "env-collection"
                assert str(config.source_dir) == str(env_source)
                # File value should remain for non-overridden fields
                assert str(config.dest_dir) == str(file_dest)