"""Error handling utilities for photo processing."""

from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any


class ErrorSeverity(Enum):
    """Severity levels for errors and warnings."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ErrorType(Enum):
    """Types of errors that can occur during processing."""
    CORRUPTED_FILE = "corrupted_file"
    UNSUPPORTED_FORMAT = "unsupported_format"
    EXIF_ERROR = "exif_error"
    FILESYSTEM_ERROR = "filesystem_error"
    VALIDATION_ERROR = "validation_error"
    FILE_SKIPPED = "file_skipped"


@dataclass
class ErrorResult:
    """Result of an error handling operation."""
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    timestamp: str
    source_file: Optional[str] = None
    action: str = "skip"
    details: Optional[Dict[str, Any]] = None
    fallback_data: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Result of manifest validation."""
    is_valid: bool
    error_type: Optional[ErrorType] = None
    validation_errors: List[str] = None

    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []


@dataclass
class ProcessingSummary:
    """Summary of processing results."""
    total_files_processed: int
    info_count: int
    warning_count: int
    error_count: int
    has_blocking_errors: bool
    files_skipped: int
    files_processed_successfully: int


class ErrorHandler:
    """Handles errors, warnings, and processing status during photo organization."""

    def __init__(self):
        self.errors: List[ErrorResult] = []
        self.warnings: List[ErrorResult] = []
        self.info_entries: List[ErrorResult] = []

    def _create_timestamp(self) -> str:
        """Create an ISO timestamp for error recording."""
        return datetime.now().isoformat()

    def _add_entry(self, error_type: ErrorType, severity: ErrorSeverity, 
                   source_file: Optional[Path], message: str, 
                   action: str = None, details: Optional[Dict[str, Any]] = None,
                   fallback_data: Optional[Dict[str, Any]] = None) -> ErrorResult:
        """Add an error entry and return the result."""
        # Set default action based on severity if not specified
        if action is None:
            if severity == ErrorSeverity.INFO:
                action = "processed"  # INFO entries don't skip files
            else:
                action = "skip"  # WARNING and ERROR entries skip files
                
        result = ErrorResult(
            error_type=error_type,
            severity=severity,
            message=message,
            timestamp=self._create_timestamp(),
            source_file=str(source_file) if source_file else None,
            action=action,
            details=details,
            fallback_data=fallback_data
        )
        
        if severity == ErrorSeverity.INFO:
            self.info_entries.append(result)
        elif severity == ErrorSeverity.WARNING:
            self.warnings.append(result)
        elif severity == ErrorSeverity.ERROR:
            self.errors.append(result)
            
        return result

    def handle_corrupted_file(self, file_path: Path, details: str) -> ErrorResult:
        """Handle a corrupted file error."""
        message = f"Corrupted file '{file_path.name}': {details}"
        return self._add_entry(
            ErrorType.CORRUPTED_FILE, 
            ErrorSeverity.WARNING, 
            file_path, 
            message
        )

    def handle_unsupported_format(self, file_path: Path) -> ErrorResult:
        """Handle an unsupported file format."""
        extension = file_path.suffix.upper()
        message = f"File format '{extension}' not supported for '{file_path.name}'"
        return self._add_entry(
            ErrorType.UNSUPPORTED_FORMAT,
            ErrorSeverity.INFO,  # Info level since it's expected
            file_path,
            message,
            action="skip"  # Unsupported formats are skipped even though they're INFO level
        )

    def handle_exif_extraction_failure(self, file_path: Path, details: str, 
                                     fallback_timestamp: Optional[str] = None) -> ErrorResult:
        """Handle EXIF extraction failure with optional fallback."""
        message = f"EXIF extraction failed for '{file_path.name}': {details}"
        if fallback_timestamp:
            message += " (using fallback timestamp)"
            action = "continue_with_fallback"
            fallback_data = {"timestamp": fallback_timestamp}
        else:
            action = "skip"
            fallback_data = None
            
        return self._add_entry(
            ErrorType.EXIF_ERROR,
            ErrorSeverity.WARNING,
            file_path,
            message,
            action=action,
            fallback_data=fallback_data
        )

    def handle_filesystem_error(self, file_path: Path, details: str) -> ErrorResult:
        """Handle filesystem-related errors."""
        message = f"Filesystem error for '{file_path.name}': {details}"
        return self._add_entry(
            ErrorType.FILESYSTEM_ERROR,
            ErrorSeverity.ERROR,
            file_path,
            message
        )

    def add_warning(self, error_type: ErrorType, file_path: Path, message: str) -> ErrorResult:
        """Add a warning-level error entry."""
        formatted_message = f"{error_type.value.upper()}: {message} (file: {file_path.name})"
        return self._add_entry(error_type, ErrorSeverity.WARNING, file_path, formatted_message)

    def add_error(self, error_type: ErrorType, file_path: Path, message: str) -> ErrorResult:
        """Add an error-level entry."""
        formatted_message = f"{error_type.value.upper()}: {message} (file: {file_path.name})"
        return self._add_entry(error_type, ErrorSeverity.ERROR, file_path, formatted_message)

    def add_info(self, error_type: ErrorType, file_path: Path, message: str) -> ErrorResult:
        """Add an info-level entry."""
        formatted_message = f"{error_type.value.upper()}: {message} (file: {file_path.name})"
        return self._add_entry(error_type, ErrorSeverity.INFO, file_path, formatted_message)

    def get_warnings(self) -> List[ErrorResult]:
        """Get all warning-level entries."""
        return self.warnings.copy()

    def get_errors(self) -> List[ErrorResult]:
        """Get all error-level entries."""
        return self.errors.copy()

    def get_info(self) -> List[ErrorResult]:
        """Get all info-level entries."""
        return self.info_entries.copy()

    def has_blocking_errors(self) -> bool:
        """Check if there are any blocking errors."""
        return len(self.errors) > 0

    def validate_manifest_data(self, manifest_data: Dict[str, Any]) -> ValidationResult:
        """Validate manifest data structure."""
        validation_errors = []
        
        # Basic structure validation
        if "pics" not in manifest_data:
            validation_errors.append("Missing required field 'pics'")
        elif not isinstance(manifest_data["pics"], list):
            validation_errors.append("Field 'pics' must be a list")
        else:
            # Validate pics structure
            for i, pic in enumerate(manifest_data["pics"]):
                if not isinstance(pic, dict):
                    validation_errors.append(f"pics[{i}] must be an object")
                elif "invalid" in pic:
                    validation_errors.append(f"pics[{i}] has invalid structure - missing required fields")
            
        if "errors" in manifest_data and not isinstance(manifest_data["errors"], list):
            validation_errors.append("Field 'errors' must be a list")
            
        is_valid = len(validation_errors) == 0
        error_type = None if is_valid else ErrorType.VALIDATION_ERROR
        
        return ValidationResult(
            is_valid=is_valid,
            error_type=error_type,
            validation_errors=validation_errors
        )

    def get_processing_summary(self) -> ProcessingSummary:
        """Get a summary of all processing results."""
        total_files = len(self.info_entries) + len(self.warnings) + len(self.errors)
        files_skipped = len([e for e in (self.info_entries + self.warnings + self.errors) 
                           if e.action == "skip"])
        
        # If there are blocking errors, no files count as "processed successfully"
        if self.has_blocking_errors():
            files_processed_successfully = 0
        else:
            files_processed_successfully = total_files - files_skipped
        
        return ProcessingSummary(
            total_files_processed=total_files,
            info_count=len(self.info_entries),
            warning_count=len(self.warnings),
            error_count=len(self.errors),
            has_blocking_errors=self.has_blocking_errors(),
            files_skipped=files_skipped,
            files_processed_successfully=files_processed_successfully
        )

    def get_all_entries_for_manifest(self) -> List[Dict[str, Any]]:
        """Get all error entries formatted for manifest inclusion."""
        all_entries = self.info_entries + self.warnings + self.errors
        
        manifest_entries = []
        for entry in all_entries:
            manifest_entry = {
                "error_type": entry.error_type.value,
                "severity": entry.severity.value,
                "message": entry.message,
                "timestamp": entry.timestamp,
            }
            
            if entry.source_file:
                manifest_entry["source_file"] = entry.source_file
                
            if entry.details:
                manifest_entry["details"] = entry.details
                
            manifest_entries.append(manifest_entry)
            
        return manifest_entries