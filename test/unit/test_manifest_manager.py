"""Tests for manifest manager functionality."""

import json


from src.manager.manifest_manager import ManifestManager, load_existing_manifest


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


class TestChangeDetection:
    """Test change detection functionality for incremental processing."""

    def test_detect_file_hash_changes(self, tmp_path, create_photo_with_exif):
        """Test detecting when file content changes via hash comparison."""
        # Arrange: Create a photo and get its initial hash
        photo_path = create_photo_with_exif(
            tmp_path / "test.jpg", 
            DateTimeOriginal="2024:10:05 14:30:45",
            Make="Canon",
            Model="EOS R5"
        )
        
        from src.manager.manifest_manager import ManifestManager
        manager = ManifestManager()
        
        # Get actual hash of the photo
        actual_hash = manager.compute_file_hash(photo_path)
        
        # Act: Check if needs reprocessing with same hash (should be False)
        needs_reprocessing_same = manager.needs_reprocessing(
            photo_path, 
            previous_hash=actual_hash
        )
        
        # Act: Check if needs reprocessing with different hash (should be True)
        needs_reprocessing_different = manager.needs_reprocessing(
            photo_path, 
            previous_hash="different_hash_value"
        )
        
        # Assert: Same hash = no reprocessing needed
        assert not needs_reprocessing_same, "Same hash should not trigger reprocessing"
        
        # Assert: Different hash = reprocessing needed  
        assert needs_reprocessing_different, "Different hash should trigger reprocessing"

    def test_detect_mtime_changes(self, tmp_path, create_photo_with_exif):
        """Test detecting filesystem modification time changes from previous manifest."""
        # Arrange: Create a photo
        photo_path = create_photo_with_exif(
            tmp_path / "test.jpg",
            DateTimeOriginal="2024:10:05 14:30:45"
        )
        
        original_mtime = photo_path.stat().st_mtime
        
        from src.manager.manifest_manager import ManifestManager
        manager = ManifestManager()
        
        # Act: Check with same mtime (should not need reprocessing)
        needs_reprocessing_same = manager.needs_reprocessing(
            photo_path, 
            previous_mtime=original_mtime
        )
        
        # Modify the file's mtime
        import time
        time.sleep(0.1)
        photo_path.touch()  # Updates mtime
        new_mtime = photo_path.stat().st_mtime
        
        # Verify mtime actually changed
        assert new_mtime > original_mtime
        
        # Act: Check with old mtime after file was touched (should need reprocessing)
        needs_reprocessing_changed = manager.needs_reprocessing(
            photo_path, 
            previous_mtime=original_mtime
        )
        
        # Assert: Same mtime = no reprocessing needed
        assert not needs_reprocessing_same, "Same mtime should not trigger reprocessing"
        
        # Assert: Different mtime = reprocessing needed
        assert needs_reprocessing_changed, "Changed mtime should trigger reprocessing"

    def test_detect_config_changes(self, tmp_path):
        """Test detecting when config changes affect processing requirements."""
        from src.manager.manifest_manager import ManifestManager
        manager = ManifestManager()
        
        # Test with same collection names (should not affect processing)
        same_config_old = {"collection_name": "wedding"}
        same_config_new = {"collection_name": "wedding"}
        
        # Test with different collection names (affects filename generation)
        old_config = {"collection_name": "old_collection"}
        new_config = {"collection_name": "new_collection"}
        
        # Test with unrelated config changes (should not affect processing)
        unrelated_old = {"collection_name": "wedding", "some_other_field": "old_value"}
        unrelated_new = {"collection_name": "wedding", "some_other_field": "new_value"}
        
        # Act: Test different scenarios
        no_change = manager.config_affects_reprocessing(same_config_old, same_config_new)
        collection_change = manager.config_affects_reprocessing(old_config, new_config)
        unrelated_change = manager.config_affects_reprocessing(unrelated_old, unrelated_new)
        
        # Assert: Same collection name = no reprocessing
        assert not no_change, "Same collection name should not trigger reprocessing"
        
        # Assert: Different collection name = reprocessing needed
        assert collection_change, "Different collection name should trigger reprocessing"
        
        # Assert: Unrelated config changes = no reprocessing
        assert not unrelated_change, "Unrelated config changes should not trigger reprocessing"

    def test_detect_missing_destination_files(self, tmp_path, create_photo_with_exif):
        """Test detecting when destination symlink files are missing."""
        # Arrange: Create source photo
        source_path = create_photo_with_exif(
            tmp_path / "source.jpg",
            DateTimeOriginal="2024:10:05 14:30:45"
        )
        
        # Expected destination path (symlink that should exist)
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()
        dest_path = dest_dir / "test-20241005T143045.jpg"
        
        from src.manager.manifest_manager import ManifestManager
        manager = ManifestManager()
        
        # Act: Test with missing destination file
        dest_missing_before = manager.destination_file_missing(source_path, dest_path)
        
        # Create symlink to source file
        dest_path.symlink_to(source_path)
        
        # Act: Test with existing correct symlink
        dest_missing_after = manager.destination_file_missing(source_path, dest_path)
        
        # Assert: Missing destination should be detected
        assert dest_missing_before, "Missing destination file should be detected"
        
        # Assert: Existing correct symlink should not be considered missing
        assert not dest_missing_after, "Existing correct symlink should not be considered missing"

    def test_unchanged_files_skipped(self, tmp_path, create_photo_with_exif):
        """Test that unchanged files are correctly identified as not needing reprocessing."""
        # Arrange: Create a photo
        photo_path = create_photo_with_exif(
            tmp_path / "unchanged.jpg",
            DateTimeOriginal="2024:10:05 14:30:45"
        )
        
        current_mtime = photo_path.stat().st_mtime
        
        from src.manager.manifest_manager import ManifestManager
        manager = ManifestManager()
        
        # Get the actual hash
        current_hash = manager.compute_file_hash(photo_path)
        
        # Act: Test with unchanged file (same mtime and hash)
        needs_reprocessing_unchanged = manager.needs_reprocessing(
            photo_path, 
            previous_mtime=current_mtime,
            previous_hash=current_hash
        )
        
        # Act: Test with no previous data (should need processing)
        needs_reprocessing_no_data = manager.needs_reprocessing(photo_path)
        
        # Assert: Unchanged file should not need reprocessing
        assert not needs_reprocessing_unchanged, "Unchanged file should not need reprocessing"
        
        # Assert: File with no previous data should need processing
        assert needs_reprocessing_no_data, "File with no previous data should need processing"
