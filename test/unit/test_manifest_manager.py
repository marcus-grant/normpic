"""Tests for manifest manager functionality."""

import json


from lib.manager.manifest_manager import ManifestManager, load_existing_manifest


class TestManifestManager:
    """Test ManifestManager class functionality."""

    def test_load_manifest_file_exists(self, tmp_path):
        """Test loading manifest when file exists and is valid."""
        # Arrange
        manifest_path = tmp_path / "manifest.json"
        valid_manifest_data = {
            "version": "0.1.0",
            "collection_name": "test",
            "generated_at": "2024-10-05T14:00:00Z",
            "collection_description": None,
            "config": None,
            "pics": [],
        }

        with open(manifest_path, "w") as f:
            json.dump(valid_manifest_data, f)

        manager = ManifestManager(manifest_path)

        # Act
        result = manager.load_manifest()

        # Assert
        assert result is not None
        assert result.version == "0.1.0"
        assert result.collection_name == "test"
        assert len(result.pics) == 0

    def test_load_manifest_file_not_exists(self, tmp_path):
        """Test loading manifest when file doesn't exist."""
        # Arrange
        manifest_path = tmp_path / "nonexistent.json"
        manager = ManifestManager(manifest_path)

        # Act
        result = manager.load_manifest()

        # Assert
        assert result is None

    def test_load_manifest_invalid_json(self, tmp_path):
        """Test loading manifest with invalid JSON."""
        # Arrange
        manifest_path = tmp_path / "invalid.json"
        with open(manifest_path, "w") as f:
            f.write("invalid json content")

        manager = ManifestManager(manifest_path)

        # Act
        result = manager.load_manifest()

        # Assert
        assert result is None

    def test_load_manifest_schema_validation_failure(self, tmp_path):
        """Test loading manifest that fails schema validation."""
        # Arrange
        manifest_path = tmp_path / "invalid_schema.json"
        invalid_manifest_data = {
            "version": "0.1.0",
            # Missing required fields: collection_name, generated_at
            "pics": [],
        }

        with open(manifest_path, "w") as f:
            json.dump(invalid_manifest_data, f)

        manager = ManifestManager(manifest_path)

        # Act
        result = manager.load_manifest()

        # Assert
        assert result is None


class TestLoadExistingManifestFunction:
    """Test standalone load_existing_manifest function."""

    def test_load_existing_manifest_success(self, tmp_path):
        """Test load_existing_manifest function with valid manifest."""
        # Arrange
        manifest_path = tmp_path / "test_manifest.json"
        valid_manifest_data = {
            "version": "0.1.0",
            "collection_name": "wedding",
            "generated_at": "2024-10-05T14:00:00Z",
            "collection_description": None,
            "config": None,
            "pics": [],
        }

        with open(manifest_path, "w") as f:
            json.dump(valid_manifest_data, f)

        # Act
        result = load_existing_manifest(manifest_path)

        # Assert
        assert result is not None
        assert result.version == "0.1.0"
        assert result.collection_name == "wedding"

    def test_load_existing_manifest_file_not_found(self, tmp_path):
        """Test load_existing_manifest with non-existent file."""
        # Arrange
        nonexistent_path = tmp_path / "does_not_exist.json"

        # Act
        result = load_existing_manifest(nonexistent_path)

        # Assert
        assert result is None

    def test_load_existing_manifest_invalid_format(self, tmp_path):
        """Test load_existing_manifest with corrupted file."""
        # Arrange
        corrupt_path = tmp_path / "corrupt.json"
        with open(corrupt_path, "w") as f:
            f.write("not valid json at all")

        # Act
        result = load_existing_manifest(corrupt_path)

        # Assert
        assert result is None
