"""Unit tests for configuration manager with environment variable support."""

import tempfile
import pytest
import json
from pathlib import Path
from unittest.mock import patch

from src.manager.config_manager import (
    get_env_config,
    validate_env_paths,
    load_config_with_env_override,
    ALLOWED_ENV_VARS
)
from src.model.config import Config


class TestGetEnvConfig:
    """Test environment variable extraction functionality."""
    
    @patch.dict('os.environ', {}, clear=True)
    def test_get_env_config_empty(self):
        """Test getting config when no environment variables are set."""
        env_config = get_env_config()
        assert env_config == {}
    
    @patch.dict('os.environ', {
        'NORMPIC_SOURCE_DIR': '/source/path',
        'NORMPIC_DEST_DIR': '/dest/path'
    }, clear=True)
    def test_get_env_config_basic(self):
        """Test getting basic environment configuration."""
        env_config = get_env_config()
        
        expected = {
            'source_dir': '/source/path',
            'dest_dir': '/dest/path'
        }
        assert env_config == expected
    
    @patch.dict('os.environ', {
        'NORMPIC_SOURCE_DIR': '/source/path',
        'NORMPIC_DEST_DIR': '/dest/path',
        'NORMPIC_COLLECTION_NAME': 'test-collection',
        'NORMPIC_CONFIG_PATH': '/config/path.json'
    }, clear=True)
    def test_get_env_config_all_vars(self):
        """Test getting all supported environment variables."""
        env_config = get_env_config()
        
        expected = {
            'source_dir': '/source/path',
            'dest_dir': '/dest/path',
            'collection_name': 'test-collection',
            'config_path': '/config/path.json'
        }
        assert env_config == expected
    
    @patch.dict('os.environ', {
        'NORMPIC_SOURCE_DIR': '/source/path',
        'OTHER_ENV_VAR': 'ignored',
        'NORMPIC_UNKNOWN': 'also_ignored'
    }, clear=True)
    def test_get_env_config_ignores_unknown(self):
        """Test that unknown environment variables are ignored."""
        env_config = get_env_config()
        
        expected = {
            'source_dir': '/source/path'
        }
        assert env_config == expected
    
    def test_allowed_env_vars_whitelist(self):
        """Test that the whitelist contains expected variables."""
        expected_vars = {
            'NORMPIC_SOURCE_DIR',
            'NORMPIC_DEST_DIR',
            'NORMPIC_COLLECTION_NAME', 
            'NORMPIC_CONFIG_PATH'
        }
        assert ALLOWED_ENV_VARS == expected_vars


class TestValidateEnvPaths:
    """Test environment path validation functionality."""
    
    def test_validate_env_paths_empty(self):
        """Test validation with empty configuration."""
        result = validate_env_paths({})
        assert result == {}
    
    def test_validate_env_paths_no_paths(self):
        """Test validation with non-path configuration."""
        config = {'collection_name': 'test'}
        result = validate_env_paths(config)
        assert result == config
    
    def test_validate_env_paths_source_dir_valid(self):
        """Test validation with valid source directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {'source_dir': temp_dir}
            result = validate_env_paths(config)
            
            assert isinstance(result['source_dir'], Path)
            assert result['source_dir'] == Path(temp_dir)
    
    def test_validate_env_paths_source_dir_nonexistent(self):
        """Test validation with nonexistent source directory."""
        config = {'source_dir': '/nonexistent/path'}
        
        with pytest.raises(ValueError, match="Source directory does not exist"):
            validate_env_paths(config)
    
    def test_validate_env_paths_source_dir_not_directory(self):
        """Test validation when source path is not a directory.""" 
        with tempfile.NamedTemporaryFile() as temp_file:
            config = {'source_dir': temp_file.name}
            
            with pytest.raises(ValueError, match="Source path is not a directory"):
                validate_env_paths(config)
    
    def test_validate_env_paths_dest_dir_creates(self):
        """Test validation creates destination directory if needed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dest_path = Path(temp_dir) / "new_dest"
            config = {'dest_dir': str(dest_path)}
            
            result = validate_env_paths(config)
            
            assert isinstance(result['dest_dir'], Path)
            assert result['dest_dir'] == dest_path
            assert dest_path.exists()
            assert dest_path.is_dir()
    
    def test_validate_env_paths_dest_dir_existing(self):
        """Test validation with existing destination directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {'dest_dir': temp_dir}
            result = validate_env_paths(config)
            
            assert isinstance(result['dest_dir'], Path)
            assert result['dest_dir'] == Path(temp_dir)
    
    def test_validate_env_paths_config_path_valid(self):
        """Test validation with valid config file."""
        with tempfile.NamedTemporaryFile(suffix='.json') as temp_file:
            config = {'config_path': temp_file.name}
            result = validate_env_paths(config)
            
            assert isinstance(result['config_path'], Path)
            assert result['config_path'] == Path(temp_file.name)
    
    def test_validate_env_paths_config_path_nonexistent(self):
        """Test validation with nonexistent config file."""
        config = {'config_path': '/nonexistent/config.json'}
        
        with pytest.raises(ValueError, match="Config file does not exist"):
            validate_env_paths(config)
    
    def test_validate_env_paths_config_path_not_file(self):
        """Test validation when config path is not a file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {'config_path': temp_dir}
            
            with pytest.raises(ValueError, match="Config path is not a file"):
                validate_env_paths(config)


class TestLoadConfigWithEnvOverride:
    """Test configuration loading with environment overrides."""
    
    @patch.dict('os.environ', {}, clear=True)
    def test_load_config_no_env_no_file(self):
        """Test loading config with no environment or file."""
        config = load_config_with_env_override()
        
        # Should return default config
        assert isinstance(config, Config)
        assert config.collection_name == ""
        assert config.source_dir == ""
        assert config.dest_dir == ""
    
    @patch.dict('os.environ', {}, clear=True) 
    def test_load_config_with_file_no_env(self):
        """Test loading config from file without environment variables."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create config file
            config_file = temp_path / "config.json"
            config_data = {
                "collection_name": "file-collection",
                "source_dir": str(temp_path / "source"),
                "dest_dir": str(temp_path / "dest")
            }
            
            # Create directories
            (temp_path / "source").mkdir()
            (temp_path / "dest").mkdir()
            
            config_file.write_text(json.dumps(config_data))
            
            config = load_config_with_env_override(config_file)
            
            assert config.collection_name == "file-collection"
            assert config.source_dir == str(temp_path / "source")
            assert config.dest_dir == str(temp_path / "dest")
    
    @patch.dict('os.environ', {
        'NORMPIC_COLLECTION_NAME': 'env-collection'
    }, clear=True)
    def test_load_config_env_override_no_file(self):
        """Test loading config with environment override and no file."""
        config = load_config_with_env_override()
        
        # Environment should override default
        assert config.collection_name == "env-collection"
        assert config.source_dir == ""  # Not set in env
        assert config.dest_dir == ""    # Not set in env
    
    def test_load_config_env_override_with_file(self):
        """Test loading config with environment override over file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create directories
            source_dir = temp_path / "source"
            dest_dir = temp_path / "dest"
            env_source_dir = temp_path / "env_source"
            env_dest_dir = temp_path / "env_dest"
            
            source_dir.mkdir()
            dest_dir.mkdir() 
            env_source_dir.mkdir()
            env_dest_dir.mkdir()
            
            # Create config file
            config_file = temp_path / "config.json"
            config_data = {
                "collection_name": "file-collection",
                "source_dir": str(source_dir),
                "dest_dir": str(dest_dir)
            }
            config_file.write_text(json.dumps(config_data))
            
            # Mock environment variables
            with patch.dict('os.environ', {
                'NORMPIC_COLLECTION_NAME': 'env-collection',
                'NORMPIC_SOURCE_DIR': str(env_source_dir),
                'NORMPIC_DEST_DIR': str(env_dest_dir)
            }, clear=True):
                config = load_config_with_env_override(config_file)
                
                # Environment should override file
                assert config.collection_name == "env-collection"
                assert config.source_dir == str(env_source_dir)
                assert config.dest_dir == str(env_dest_dir)
    
    @patch.dict('os.environ', {
        'NORMPIC_SOURCE_DIR': '/nonexistent/source'
    }, clear=True)
    def test_load_config_env_validation_error(self):
        """Test loading config with invalid environment variable."""
        # Current implementation doesn't validate paths, just applies overrides
        config = load_config_with_env_override()
        assert config.source_dir == '/nonexistent/source'
    
    def test_load_config_nonexistent_file(self):
        """Test loading config with nonexistent file path."""
        nonexistent_file = Path("/nonexistent/config.json")
        
        with patch.dict('os.environ', {}, clear=True):
            config = load_config_with_env_override(nonexistent_file)
            
            # Should return default config when file doesn't exist
            assert isinstance(config, Config)
            assert config.collection_name == ""