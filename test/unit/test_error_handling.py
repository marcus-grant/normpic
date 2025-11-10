"""Unit tests for error handling scenarios."""

from unittest.mock import patch
from pathlib import Path

# These imports will fail initially - that's the point of TDD
from src.util.error_handling import ErrorHandler, ErrorSeverity, ErrorType


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
        assert result.action == "skip"
        assert result.severity == ErrorSeverity.WARNING
        assert result.error_type == ErrorType.CORRUPTED_FILE
        assert corrupted_file.name in result.message
        assert "Invalid EXIF data" in result.message
        assert result.source_file == str(corrupted_file)

    def test_log_warnings_to_manifest(self):
        """Test: Multiple warnings → collected for manifest → proper formatting."""
        
        # Arrange
        error_handler = ErrorHandler()
        file1 = Path("/fake/corrupted.jpg")
        file2 = Path("/fake/unsupported.cr2")
        
        # Act
        error_handler.add_warning(ErrorType.CORRUPTED_FILE, file1, "Invalid JPEG")
        error_handler.add_warning(ErrorType.UNSUPPORTED_FORMAT, file2, "RAW not supported")
        
        warnings = error_handler.get_warnings()
        
        # Assert
        assert len(warnings) == 2
        
        warning1 = warnings[0]
        assert warning1.error_type == ErrorType.CORRUPTED_FILE
        assert warning1.severity == ErrorSeverity.WARNING
        assert warning1.source_file == str(file1)
        assert "Invalid JPEG" in warning1.message
        
        warning2 = warnings[1]
        assert warning2.error_type == ErrorType.UNSUPPORTED_FORMAT
        assert warning2.severity == ErrorSeverity.WARNING
        assert warning2.source_file == str(file2)
        assert "RAW not supported" in warning2.message

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
        assert not result.is_valid
        assert result.error_type == ErrorType.VALIDATION_ERROR
        assert len(result.validation_errors) > 0
        assert any("pics" in error for error in result.validation_errors)

    def test_error_severity_levels(self):
        """Test: Different error types → appropriate severity levels → proper handling."""
        
        # Arrange
        error_handler = ErrorHandler()
        
        # Act & Assert - Test different severity levels
        
        # INFO level - should not affect processing
        info_result = error_handler.add_info(ErrorType.FILE_SKIPPED, Path("/fake/skip.txt"), "Not a photo")
        assert info_result.severity == ErrorSeverity.INFO
        assert not error_handler.has_blocking_errors()
        
        # WARNING level - should not block processing
        warning_result = error_handler.add_warning(ErrorType.CORRUPTED_FILE, Path("/fake/bad.jpg"), "Corrupted")
        assert warning_result.severity == ErrorSeverity.WARNING
        assert not error_handler.has_blocking_errors()
        
        # ERROR level - should potentially block processing
        error_result = error_handler.add_error(ErrorType.FILESYSTEM_ERROR, Path("/fake/path"), "Permission denied")
        assert error_result.severity == ErrorSeverity.ERROR
        assert error_handler.has_blocking_errors()

    def test_unsupported_file_format_handling(self):
        """Test: Unsupported format → skip with info → continue processing."""
        
        # Arrange
        error_handler = ErrorHandler()
        raw_file = Path("/fake/photo.CR2")
        
        # Act
        result = error_handler.handle_unsupported_format(raw_file)
        
        # Assert
        assert result.action == "skip"
        assert result.severity == ErrorSeverity.INFO  # Info level since it's expected
        assert result.error_type == ErrorType.UNSUPPORTED_FORMAT
        assert "CR2" in result.message
        assert "not supported" in result.message.lower()

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
        assert result.action == "continue_with_fallback"
        assert result.severity == ErrorSeverity.WARNING
        assert result.error_type == ErrorType.EXIF_ERROR
        assert result.fallback_data["timestamp"] == "2024-10-05T14:30:45"
        assert "fallback" in result.message.lower()

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
        assert result.action == "skip"
        assert result.severity == ErrorSeverity.ERROR
        assert result.error_type == ErrorType.FILESYSTEM_ERROR
        assert "permission denied" in result.message.lower()

    def test_error_summary_statistics(self):
        """Test: Multiple errors → summary statistics → processing status."""
        
        # Arrange
        error_handler = ErrorHandler()
        
        # Act - Add various types of errors
        error_handler.add_info(ErrorType.FILE_SKIPPED, Path("/fake/1.txt"), "Not photo")
        error_handler.add_warning(ErrorType.CORRUPTED_FILE, Path("/fake/2.jpg"), "Bad EXIF")
        error_handler.add_warning(ErrorType.UNSUPPORTED_FORMAT, Path("/fake/3.cr2"), "RAW")
        error_handler.add_error(ErrorType.FILESYSTEM_ERROR, Path("/fake/4.jpg"), "No permission")
        
        summary = error_handler.get_processing_summary()
        
        # Assert
        assert summary.total_files_processed == 4
        assert summary.info_count == 1
        assert summary.warning_count == 2
        assert summary.error_count == 1
        assert summary.has_blocking_errors
        
        # Check categorization
        assert summary.files_skipped == 3  # info + warnings + errors all skip files
        assert summary.files_processed_successfully == 0  # none succeeded due to errors

    @patch('src.util.error_handling.datetime')
    def test_error_timestamp_recording(self, mock_datetime):
        """Test: Errors include timestamps → proper ISO format → timezone handling."""
        
        # Arrange
        error_handler = ErrorHandler()
        mock_datetime.now.return_value.isoformat.return_value = "2024-10-05T14:30:45.123456"
        
        # Act
        result = error_handler.add_warning(
            ErrorType.CORRUPTED_FILE, 
            Path("/fake/test.jpg"), 
            "Test error"
        )
        
        # Assert
        assert result.timestamp == "2024-10-05T14:30:45.123456"
        mock_datetime.now.assert_called_once()

    def test_error_message_formatting(self):
        """Test: Error messages → consistent format → helpful details."""
        
        # Arrange
        error_handler = ErrorHandler()
        test_file = Path("/fake/photos/IMG_001.jpg")
        
        # Act
        result = error_handler.add_error(
            ErrorType.CORRUPTED_FILE,
            test_file,
            "EXIF data is corrupted or incomplete"
        )
        
        # Assert
        message = result.message
        assert "CORRUPTED_FILE" in message or "corrupted" in message.lower()
        assert "IMG_001.jpg" in message
        assert "EXIF data is corrupted" in message
        
        # Should include error type for debugging
        assert result.error_type == ErrorType.CORRUPTED_FILE
        
        # Should format consistently
        assert isinstance(message, str)
        assert len(message) > 10  # Reasonable minimum length