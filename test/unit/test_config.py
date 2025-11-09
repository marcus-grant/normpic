"""Tests for config JSON loading and validation."""

import json
import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

from src.model.config import Config


class TestConfigFromJsonFile:
    """Tests for Config.from_json_file method."""

    def test_load_valid_config_file(self):
        """Should load valid JSON config file successfully."""
        config_data = {
            "collection_name": "test-collection",
            "source_dir": "/tmp/source",
            "dest_dir": "/tmp/dest",
        }

        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)

        try:
            config = Config.from_json_file(config_path)

            assert config.collection_name == "test-collection"
            assert config.source_dir == "/tmp/source"
            assert config.dest_dir == "/tmp/dest"
            assert config.collection_description is None
            assert config.timestamp_offset_hours == 0
            assert config.force_reprocess is False
        finally:
            config_path.unlink()

    def test_load_config_with_optional_fields(self):
        """Should load config with all optional fields set."""
        config_data = {
            "collection_name": "wedding-photos",
            "source_dir": "/photos/raw",
            "dest_dir": "/photos/organized",
            "collection_description": "Sarah & John Wedding",
            "timestamp_offset_hours": -5,
            "force_reprocess": True,
        }

        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)

        try:
            config = Config.from_json_file(config_path)

            assert config.collection_name == "wedding-photos"
            assert config.collection_description == "Sarah & John Wedding"
            assert config.timestamp_offset_hours == -5
            assert config.force_reprocess is True
        finally:
            config_path.unlink()

    def test_file_not_found_raises_error(self):
        """Should raise FileNotFoundError for non-existent file."""
        non_existent_path = Path("/does/not/exist/config.json")

        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            Config.from_json_file(non_existent_path)

    def test_invalid_json_raises_error(self):
        """Should raise JSONDecodeError for malformed JSON."""
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"collection_name": "test", invalid json}')
            config_path = Path(f.name)

        try:
            with pytest.raises(json.JSONDecodeError):
                Config.from_json_file(config_path)
        finally:
            config_path.unlink()


class TestConfigFromDict:
    """Tests for Config.from_dict method."""

    def test_valid_minimal_config(self):
        """Should create config from minimal valid dictionary."""
        data = {
            "collection_name": "test",
            "source_dir": "/tmp/source",
            "dest_dir": "/tmp/dest",
        }

        config = Config.from_dict(data)

        assert config.collection_name == "test"
        assert config.source_dir == "/tmp/source"
        assert config.dest_dir == "/tmp/dest"
        assert config.collection_description is None
        assert config.timestamp_offset_hours == 0
        assert config.force_reprocess is False

    def test_missing_required_field_raises_error(self):
        """Should raise ValueError when required fields are missing."""
        data = {
            "collection_name": "test",
            # Missing source_dir and dest_dir
        }

        with pytest.raises(ValueError, match="Missing required configuration fields"):
            Config.from_dict(data)

    def test_empty_string_fields_raise_error(self):
        """Should raise ValueError for empty string required fields."""
        test_cases = [
            {
                "collection_name": "",
                "source_dir": "/tmp/source",
                "dest_dir": "/tmp/dest",
            },
            {"collection_name": "test", "source_dir": "", "dest_dir": "/tmp/dest"},
            {"collection_name": "test", "source_dir": "/tmp/source", "dest_dir": ""},
        ]

        for data in test_cases:
            with pytest.raises(ValueError):
                Config.from_dict(data)

    def test_invalid_type_fields_raise_error(self):
        """Should raise ValueError for invalid field types."""
        base_data = {
            "collection_name": "test",
            "source_dir": "/tmp/source",
            "dest_dir": "/tmp/dest",
        }

        test_cases = [
            {**base_data, "timestamp_offset_hours": "not_int"},
            {**base_data, "force_reprocess": "not_bool"},
            {**base_data, "collection_description": 123},
        ]

        for data in test_cases:
            with pytest.raises(ValueError):
                Config.from_dict(data)


class TestConfigDefaultPath:
    """Tests for Config.get_default_config_path method."""

    def test_default_config_path(self):
        """Should return ./config.json as default path."""
        default_path = Config.get_default_config_path()
        assert default_path == Path("./config.json")


class TestConfigValidatePaths:
    """Tests for Config.validate_paths method."""

    def test_validate_existing_source_directory(self):
        """Should succeed when source directory exists."""
        with TemporaryDirectory() as temp_dir:
            dest_dir = Path(temp_dir) / "dest"

            config = Config(
                collection_name="test", source_dir=temp_dir, dest_dir=str(dest_dir)
            )

            config.validate_paths()  # Should not raise
            assert dest_dir.exists()  # Should create dest dir

    def test_validate_non_existent_source_raises_error(self):
        """Should raise ValueError when source directory doesn't exist."""
        config = Config(
            collection_name="test", source_dir="/does/not/exist", dest_dir="/tmp/dest"
        )

        with pytest.raises(ValueError, match="Source directory does not exist"):
            config.validate_paths()

    def test_validate_source_file_not_directory_raises_error(self):
        """Should raise ValueError when source path is a file, not directory."""
        with NamedTemporaryFile() as temp_file:
            config = Config(
                collection_name="test", source_dir=temp_file.name, dest_dir="/tmp/dest"
            )

            with pytest.raises(ValueError, match="Source path is not a directory"):
                config.validate_paths()
