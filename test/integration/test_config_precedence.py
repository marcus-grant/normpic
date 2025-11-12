"""Integration tests for config precedence system."""

import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from src.manager.config_manager import load_config_with_env_override, load_config_with_full_precedence


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
    
    def test_cli_args_override_everything(self):
        """Test that CLI arguments override all other configuration sources."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create directories for all config sources
            file_source = temp_path / "file_source"
            file_dest = temp_path / "file_dest"
            env_source = temp_path / "env_source"
            env_dest = temp_path / "env_dest"
            cli_source = temp_path / "cli_source"
            cli_dest = temp_path / "cli_dest"
            
            for dir_path in [file_source, file_dest, env_source, env_dest, cli_source, cli_dest]:
                dir_path.mkdir()
            
            # Create config file
            config_file = temp_path / "config.json"
            config_data = {
                "collection_name": "file-collection",
                "source_dir": str(file_source),
                "dest_dir": str(file_dest)
            }
            config_file.write_text(json.dumps(config_data))
            
            # Mock environment variables
            with patch.dict('os.environ', {
                'NORMPIC_COLLECTION_NAME': 'env-collection',
                'NORMPIC_SOURCE_DIR': str(env_source),
                'NORMPIC_DEST_DIR': str(env_dest)
            }, clear=True):
                # CLI arguments should override everything
                cli_overrides = {
                    'collection_name': 'cli-collection',
                    'source_dir': str(cli_source),
                    'dest_dir': str(cli_dest)
                }
                
                config = load_config_with_full_precedence(
                    config_file=config_file,
                    cli_overrides=cli_overrides
                )
                
                # CLI args should win over everything
                assert config.collection_name == "cli-collection"
                assert str(config.source_dir) == str(cli_source)
                assert str(config.dest_dir) == str(cli_dest)
    
    def test_partial_cli_overrides(self):
        """Test partial CLI overrides leave other precedence intact."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create directories
            file_source = temp_path / "file_source"
            file_dest = temp_path / "file_dest"
            env_source = temp_path / "env_source"
            cli_dest = temp_path / "cli_dest"
            
            for dir_path in [file_source, file_dest, env_source, cli_dest]:
                dir_path.mkdir()
            
            # Config file
            config_file = temp_path / "config.json"
            config_data = {
                "collection_name": "file-collection",
                "source_dir": str(file_source),
                "dest_dir": str(file_dest)
            }
            config_file.write_text(json.dumps(config_data))
            
            # Environment override for source_dir only
            with patch.dict('os.environ', {
                'NORMPIC_SOURCE_DIR': str(env_source)
            }, clear=True):
                # CLI override for dest_dir only
                cli_overrides = {
                    'dest_dir': str(cli_dest)
                }
                
                config = load_config_with_full_precedence(
                    config_file=config_file,
                    cli_overrides=cli_overrides
                )
                
                # Each source should win for its field
                assert config.collection_name == "file-collection"  # From file
                assert str(config.source_dir) == str(env_source)    # From env
                assert str(config.dest_dir) == str(cli_dest)        # From CLI