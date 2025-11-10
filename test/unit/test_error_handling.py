"""Unit tests for error handling scenarios."""

from pathlib import Path

# These imports will fail initially - that's the point of TDD
from src.util.error_handling import ErrorHandler


class TestErrorHandler:
    """Unit tests for error handling utilities."""

    def test_skip_corrupted_file_continue_processing(self):
        """Test: Corrupted file → skip with warning → processing continues."""
        
        # Arrange
        error_handler = ErrorHandler()
        corrupted_file = Path("/fake/corrupted.jpg")
        
        # Act
        result = error_handler.handle_corrupted_file(corrupted_file, "Invalid EXIF data")
        
        # Assert
        assert result.error_type == "corrupted_file"
        assert result.source_file == corrupted_file.name
        assert "Invalid EXIF data" in result.details
        assert len(error_handler.get_warnings()) == 1
        assert error_handler._files_skipped == 1

    def test_log_warnings_to_manifest(self):
        """Test: Multiple warnings → collected for manifest → proper formatting."""
        
        # Arrange
        error_handler = ErrorHandler()
        file1 = Path("/fake/corrupted.jpg")
        file2 = Path("/fake/unsupported.cr2")
        
        # Act
        error_handler.add_warning("corrupted_file", file1, "Invalid JPEG")
        error_handler.add_warning("unsupported_format", file2, "RAW not supported")
        
        warnings = error_handler.get_warnings()
        
        # Assert
        assert len(warnings) == 2
        
        warning1 = warnings[0]
        assert warning1.error_type == "corrupted_file"
        assert warning1.source_file == file1.name
        assert warning1.details == "Invalid JPEG"
        
        warning2 = warnings[1]
        assert warning2.error_type == "unsupported_format"
        assert warning2.source_file == file2.name
        assert warning2.details == "RAW not supported"

    def test_validate_manifest_before_write(self):
        """Test: Invalid manifest data → validation error → detailed message."""
        
        # Arrange
        error_handler = ErrorHandler()
        invalid_manifest_data = {
            "version": "0.1.0",
            "pics": [{"invalid": "structure"}],  # Missing required fields
            "errors": "should be list",  # Wrong type
        }
        
        # Act
        result = error_handler.validate_manifest_data(invalid_manifest_data)
        
        # Assert
        assert not result["is_valid"]
        assert len(result["validation_errors"]) > 0
        assert any("pics" in error for error in result["validation_errors"])

    def test_error_severity_levels(self):
        """Test: Different error types → appropriate severity levels → proper handling."""
        
        # Arrange
        error_handler = ErrorHandler()
        
        # Act & Assert - Test different severity levels
        
        # INFO level - should not affect processing
        info_result = error_handler.add_info("file_skipped", Path("/fake/skip.txt"), "Not a photo")
        assert info_result.error_type == "file_skipped"
        assert not error_handler.has_blocking_errors()
        assert len(error_handler.get_info()) == 1
        
        # WARNING level - should not block processing
        warning_result = error_handler.add_warning("corrupted_file", Path("/fake/bad.jpg"), "Corrupted")
        assert warning_result.error_type == "corrupted_file"
        assert not error_handler.has_blocking_errors()
        assert len(error_handler.get_warnings()) == 1
        
        # ERROR level - should block processing
        error_result = error_handler.add_error("filesystem_error", Path("/fake/path"), "Permission denied")
        assert error_result.error_type == "filesystem_error"
        assert error_handler.has_blocking_errors()
        assert len(error_handler.get_errors()) == 1

    def test_unsupported_file_format_handling(self):
        """Test: Unsupported format → skip with info → continue processing."""
        
        # Arrange
        error_handler = ErrorHandler()
        raw_file = Path("/fake/photo.CR2")
        
        # Act
        result = error_handler.handle_unsupported_format(raw_file)
        
        # Assert
        assert result.error_type == "unsupported_format"
        assert result.source_file == raw_file.name
        assert "CR2" in result.details
        assert "not supported" in result.details.lower()
        assert len(error_handler.get_info()) == 1
        assert error_handler._files_skipped == 1

    def test_exif_extraction_error_handling(self):
        """Test: EXIF extraction fails → fallback to filesystem → warning logged."""
        
        # Arrange
        error_handler = ErrorHandler()
        photo_file = Path("/fake/no_exif.jpg")
        
        # Act  
        result = error_handler.handle_exif_extraction_failure(
            photo_file, 
            "No EXIF data found",
            fallback_timestamp="2024-10-05T14:30:45"
        )
        
        # Assert
        assert result.error_type == "exif_error"
        assert result.source_file == photo_file.name
        assert "No EXIF data found" in result.details
        assert "fallback" in result.details.lower()
        assert len(error_handler.get_warnings()) == 1
        assert error_handler._files_skipped == 0  # Fallback means file wasn't skipped

    def test_filesystem_permission_error(self):
        """Test: Permission denied → error logged → processing may stop."""
        
        # Arrange
        error_handler = ErrorHandler()
        protected_file = Path("/fake/protected.jpg")
        
        # Act
        result = error_handler.handle_filesystem_error(
            protected_file,
            "Permission denied: cannot read file"
        )
        
        # Assert
        assert result.error_type == "filesystem_error"
        assert result.source_file == protected_file.name
        assert "permission denied" in result.details.lower()
        assert len(error_handler.get_errors()) == 1
        assert error_handler._files_skipped == 1

    def test_error_summary_statistics(self):
        """Test: Multiple errors → summary statistics → processing status."""
        
        # Arrange
        error_handler = ErrorHandler()
        
        # Act - Add various types of errors
        error_handler.add_info("file_skipped", Path("/fake/1.txt"), "Not photo")
        error_handler.add_warning("corrupted_file", Path("/fake/2.jpg"), "Bad EXIF")
        error_handler.add_warning("unsupported_format", Path("/fake/3.cr2"), "RAW")
        error_handler.add_error("filesystem_error", Path("/fake/4.jpg"), "No permission")
        
        summary = error_handler.get_processing_summary()
        
        # Assert
        assert summary["total_files_processed"] == 4
        assert summary["info_count"] == 1
        assert summary["warning_count"] == 2
        assert summary["error_count"] == 1
        assert summary["has_blocking_errors"]
        
        # Check categorization
        assert summary["files_skipped"] == 3  # info + warnings + errors all skip files
        assert summary["files_processed_successfully"] == 0  # none succeeded due to errors

    def test_error_entry_creation(self):
        """Test: Error entries contain required fields."""
        
        # Arrange
        error_handler = ErrorHandler()
        
        # Act
        result = error_handler.add_warning(
            "corrupted_file", 
            Path("/fake/test.jpg"), 
            "Test error"
        )
        
        # Assert
        assert result.error_type == "corrupted_file"
        assert result.source_file == "test.jpg"
        assert result.details == "Test error"

    def test_error_message_formatting(self):
        """Test: Error messages → consistent format → helpful details."""
        
        # Arrange
        error_handler = ErrorHandler()
        test_file = Path("/fake/photos/IMG_001.jpg")
        
        # Act
        result = error_handler.add_error(
            "corrupted_file",
            test_file,
            "EXIF data is corrupted or incomplete"
        )
        
        # Assert
        assert result.error_type == "corrupted_file"
        assert result.source_file == "IMG_001.jpg"
        assert result.details == "EXIF data is corrupted or incomplete"
        
        # Should format consistently
        assert isinstance(result.details, str)
        assert len(result.details) > 10  # Reasonable minimum length