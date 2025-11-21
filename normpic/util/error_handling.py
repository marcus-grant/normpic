"""Streamlined error handling utilities for photo processing."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class ErrorEntry:
    """Minimal error entry with structured data."""
    error_type: str
    source_file: str
    details: Optional[str] = None




class ErrorHandler:
    """Streamlined error handling with structured data and intrinsic severity."""

    def __init__(self):
        self.errors: List[ErrorEntry] = []
        self.warnings: List[ErrorEntry] = []
        self.info_entries: List[ErrorEntry] = []
        self._files_skipped = 0

    def handle_corrupted_file(self, file_path: Path, details: str) -> ErrorEntry:
        """Handle a corrupted file error."""
        entry = ErrorEntry(
            error_type="corrupted_file",
            source_file=file_path.name,
            details=details
        )
        self.warnings.append(entry)
        self._files_skipped += 1
        return entry

    def handle_unsupported_format(self, file_path: Path) -> ErrorEntry:
        """Handle an unsupported file format."""
        extension = file_path.suffix.upper()
        entry = ErrorEntry(
            error_type="unsupported_format",
            source_file=file_path.name,
            details=f"Format {extension} not supported"
        )
        self.info_entries.append(entry)
        self._files_skipped += 1
        return entry

    def handle_exif_extraction_failure(self, file_path: Path, details: str, 
                                     fallback_timestamp: Optional[str] = None) -> ErrorEntry:
        """Handle EXIF extraction failure with optional fallback."""
        details_text = details
        if fallback_timestamp:
            details_text += " (using fallback timestamp)"
        
        entry = ErrorEntry(
            error_type="exif_error",
            source_file=file_path.name,
            details=details_text
        )
        self.warnings.append(entry)
        
        if not fallback_timestamp:
            self._files_skipped += 1
            
        return entry

    def handle_filesystem_error(self, file_path: Path, details: str) -> ErrorEntry:
        """Handle filesystem-related errors."""
        entry = ErrorEntry(
            error_type="filesystem_error",
            source_file=file_path.name,
            details=details
        )
        self.errors.append(entry)
        self._files_skipped += 1
        return entry

    def add_warning(self, error_type: str, file_path: Path, details: str) -> ErrorEntry:
        """Add a warning-level error entry."""
        entry = ErrorEntry(
            error_type=error_type,
            source_file=file_path.name,
            details=details
        )
        self.warnings.append(entry)
        self._files_skipped += 1
        return entry

    def add_error(self, error_type: str, file_path: Path, details: str) -> ErrorEntry:
        """Add an error-level entry."""
        entry = ErrorEntry(
            error_type=error_type,
            source_file=file_path.name,
            details=details
        )
        self.errors.append(entry)
        self._files_skipped += 1
        return entry

    def add_info(self, error_type: str, file_path: Path, details: str) -> ErrorEntry:
        """Add an info-level entry."""
        entry = ErrorEntry(
            error_type=error_type,
            source_file=file_path.name,
            details=details
        )
        self.info_entries.append(entry)
        return entry

    def get_warnings(self) -> List[ErrorEntry]:
        """Get all warning-level entries."""
        return self.warnings.copy()

    def get_errors(self) -> List[ErrorEntry]:
        """Get all error-level entries."""
        return self.errors.copy()

    def get_info(self) -> List[ErrorEntry]:
        """Get all info-level entries."""
        return self.info_entries.copy()

    def has_blocking_errors(self) -> bool:
        """Check if there are any blocking errors."""
        return len(self.errors) > 0

    def validate_manifest_data(self, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate manifest data structure."""
        validation_errors = []
        
        if "pics" not in manifest_data:
            validation_errors.append("Missing required field 'pics'")
        elif not isinstance(manifest_data["pics"], list):
            validation_errors.append("Field 'pics' must be a list")
        else:
            for i, pic in enumerate(manifest_data["pics"]):
                if not isinstance(pic, dict):
                    validation_errors.append(f"pics[{i}] must be an object")
                elif "invalid" in pic:
                    validation_errors.append(f"pics[{i}] has invalid structure")
        
        if "errors" in manifest_data and not isinstance(manifest_data["errors"], list):
            validation_errors.append("Field 'errors' must be a list")
        
        return {
            "is_valid": len(validation_errors) == 0,
            "validation_errors": validation_errors
        }

    def get_processing_summary(self) -> Dict[str, Any]:
        """Get a summary of all processing results."""
        total_files = len(self.info_entries) + len(self.warnings) + len(self.errors)
        files_processed_successfully = total_files - self._files_skipped if not self.has_blocking_errors() else 0
        
        return {
            "total_files_processed": total_files,
            "info_count": len(self.info_entries),
            "warning_count": len(self.warnings),
            "error_count": len(self.errors),
            "has_blocking_errors": self.has_blocking_errors(),
            "files_skipped": self._files_skipped,
            "files_processed_successfully": files_processed_successfully
        }

    def get_errors_for_manifest(self) -> List[Dict[str, Any]]:
        """Get error entries formatted for manifest inclusion."""
        return [{
            "error_type": entry.error_type,
            "source_file": entry.source_file,
            "details": entry.details
        } for entry in self.errors]
    
    def get_warnings_for_manifest(self) -> List[Dict[str, Any]]:
        """Get warning and info entries formatted for manifest inclusion."""
        all_warnings = self.warnings + self.info_entries
        return [{
            "error_type": entry.error_type,
            "source_file": entry.source_file,
            "details": entry.details
        } for entry in all_warnings]