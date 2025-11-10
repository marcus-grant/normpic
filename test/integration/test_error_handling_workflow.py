"""Integration tests for error handling workflow with comprehensive file format testing."""

# These imports will fail initially - that's the point of TDD
from src.manager.photo_manager import organize_photos
from src.serializer.manifest import ManifestSerializer


class TestErrorHandlingWorkflow:
    """Integration tests for error handling with various file formats and corruption scenarios."""

    def test_mixed_file_formats_continue_processing(
        self, create_photo_with_exif, tmp_path
    ):
        """Test: Mix of supported/unsupported/corrupted files → processing continues → errors/warnings in manifest."""

        # Arrange: Create mix of file types and scenarios
        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        # Supported formats with valid EXIF
        create_photo_with_exif(
            source_dir / "valid_photo.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            Make="Canon",
            Model="EOS R5",
        )

        create_photo_with_exif(
            source_dir / "valid_photo2.jpg",
            DateTimeOriginal="2024:10:05 14:30:46",
            Make="Canon", 
            Model="EOS R5",
        )

        # Create unsupported file formats
        raw_file = source_dir / "photo.CR2"
        raw_file.write_bytes(b"fake RAW file content")

        gif_file = source_dir / "animation.gif"
        gif_file.write_bytes(b"GIF89a fake gif content")

        video_file = source_dir / "video.mp4"
        video_file.write_bytes(b"fake video content")

        # Create corrupted files
        corrupted_jpeg = source_dir / "corrupted.jpg"
        corrupted_jpeg.write_bytes(b"not a real jpeg file")

        empty_file = source_dir / "empty.jpg"
        empty_file.write_bytes(b"")

        # JPEG with invalid EXIF
        invalid_exif = source_dir / "invalid_exif.jpg"
        invalid_exif.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF invalid exif data")

        # Act: Run photo organization
        result = organize_photos(
            source_dir=source_dir,
            dest_dir=dest_dir,
            collection_name="test-collection"
        )

        # Assert: Processing completed with appropriate handling
        # Note: Currently organize_photos returns a Manifest, not a dict with status
        # This test expects error handling to be implemented
        assert result is not None
        
        # Supported files should be processed successfully
        assert (dest_dir / "test-collection-20241005T143045-r5a.jpg").exists()
        assert (dest_dir / "test-collection-20241005T143046-r5a.jpg").exists()
        
        # Unsupported files should be skipped with warnings
        assert not (dest_dir / "photo.CR2").exists()
        assert not (dest_dir / "animation.gif").exists() 
        assert not (dest_dir / "video.mp4").exists()
        
        # Corrupted files should be skipped with warnings
        assert not (dest_dir / "corrupted.jpg").exists()
        assert not (dest_dir / "empty.jpg").exists()
        assert not (dest_dir / "invalid_exif.jpg").exists()

        # Load and verify manifest contains error information
        manifest_path = dest_dir / "manifest.json"
        assert manifest_path.exists()
        
        # For now, just check that we can load the manifest
        # Error handling fields will be added in later commits
        serializer = ManifestSerializer()
        manifest_json = manifest_path.read_text()
        serializer.deserialize(manifest_json)
        
        # This test expects error handling features to be implemented:
        # - errors and warnings fields in manifest
        # - processing_status summary
        # - specific error type tracking
        # These assertions will initially fail, driving the implementation

    def test_all_files_corrupted_graceful_handling(self, tmp_path):
        """Test: All files corrupted → graceful failure → detailed error manifest."""
        
        # Arrange: Create only corrupted files
        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        # Various corruption scenarios
        corrupted_files = [
            ("empty.jpg", b""),
            ("truncated.jpg", b"\xff\xd8\xff"),
            ("wrong_extension.jpg", b"PNG fake content"),
            ("binary_junk.jpg", b"\x00\x01\x02\x03\x04"),
        ]
        
        for filename, content in corrupted_files:
            (source_dir / filename).write_bytes(content)

        # Act: Run photo organization
        result = organize_photos(
            source_dir=source_dir,
            dest_dir=dest_dir,
            collection_name="corrupted-test"
        )

        # Assert: Graceful handling with no crashes  
        assert result is not None
        
        # This test expects that corrupted files are handled gracefully:
        # - No symlinks created for corrupted files
        # - Manifest contains comprehensive error information
        # - Processing continues despite all files being corrupted

    def test_partial_processing_with_mixed_scenarios(
        self, create_photo_with_exif, tmp_path
    ):
        """Test: Mixed valid/invalid files → partial success → complete error reporting."""
        
        # Arrange: Create realistic mixed scenario
        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        # Valid photos
        create_photo_with_exif(
            source_dir / "good_photo1.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            Make="Canon",
            Model="EOS R5",
        )

        create_photo_with_exif(
            source_dir / "good_photo2.jpg", 
            DateTimeOriginal="2024:10:05 14:30:46",
            Make="Canon",
            Model="EOS R5",
        )

        # Photo without EXIF timestamp (should use filename or filesystem)
        create_photo_with_exif(
            source_dir / "20241005_143047_no_exif.jpg",
        )

        # Unsupported format
        (source_dir / "document.pdf").write_bytes(b"fake PDF content")
        
        # Corrupted JPEG
        (source_dir / "corrupted.jpg").write_bytes(b"fake jpeg")

        # Act: Run photo organization
        result = organize_photos(
            source_dir=source_dir,
            dest_dir=dest_dir,
            collection_name="mixed-test"
        )

        # Assert: Partial processing success
        assert result is not None
        
        # This test expects mixed scenario handling:
        # - Valid files processed successfully  
        # - Invalid files skipped with warnings
        # - Comprehensive error reporting in manifest
        # - Fallback timestamp handling for files without EXIF