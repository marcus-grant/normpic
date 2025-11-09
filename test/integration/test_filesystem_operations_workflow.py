"""Integration tests for filesystem operations workflow.

Tests complete workflow from source photos through symlink creation,
validation, and broken link detection.
"""

import tempfile
import pytest
from pathlib import Path

from src.util.filesystem import (
    create_symlink,
    validate_symlink_integrity, 
    detect_broken_symlinks,
    compute_file_hash
)


def test_symlink_creation_complete_workflow():
    """Test complete filesystem operations workflow.
    
    Workflow: source photos → symlink creation → validation → broken link detection
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Setup: Create source photos
        source_dir = temp_path / "source" 
        dest_dir = temp_path / "destination"
        source_dir.mkdir()
        dest_dir.mkdir()
        
        # Create test photo files
        photo1 = source_dir / "IMG_001.jpg"
        photo2 = source_dir / "IMG_002.jpg"
        photo1.write_bytes(b"fake photo data 1")
        photo2.write_bytes(b"fake photo data 2")
        
        # Phase 1: Create symlinks
        symlink1 = dest_dir / "2023-12-25T120000-r5a-1.jpg"
        symlink2 = dest_dir / "2023-12-25T120001-r5a-2.jpg"
        
        create_symlink(photo1, symlink1)
        create_symlink(photo2, symlink2)
        
        # Verify symlinks were created
        assert symlink1.is_symlink()
        assert symlink2.is_symlink()
        assert symlink1.readlink() == photo1
        assert symlink2.readlink() == photo2
        
        # Phase 2: Validate symlink integrity
        assert validate_symlink_integrity(symlink1)
        assert validate_symlink_integrity(symlink2)
        
        # Phase 3: Test hash computation
        hash1 = compute_file_hash(photo1)
        hash2 = compute_file_hash(photo2)
        assert hash1 != hash2  # Different files should have different hashes
        assert len(hash1) == 64  # SHA-256 produces 64 char hex string
        
        # Phase 4: Test broken symlink detection
        broken_links = detect_broken_symlinks(dest_dir)
        assert len(broken_links) == 0  # No broken links yet
        
        # Break a symlink by removing source
        photo1.unlink()
        
        broken_links = detect_broken_symlinks(dest_dir)
        assert len(broken_links) == 1
        assert broken_links[0] == symlink1
        
        # Verify remaining symlink still works
        assert validate_symlink_integrity(symlink2)


def test_symlink_error_handling_workflow():
    """Test error handling in filesystem operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        source_file = temp_path / "source.jpg"
        dest_file = temp_path / "dest.jpg"
        source_file.write_bytes(b"test data")
        
        # Test creating symlink when destination already exists
        dest_file.write_bytes(b"existing file")
        
        with pytest.raises(FileExistsError):
            create_symlink(source_file, dest_file)
        
        # Test validating non-existent symlink
        fake_symlink = temp_path / "fake.jpg"
        assert not validate_symlink_integrity(fake_symlink)
        
        # Test hash of non-existent file
        with pytest.raises(FileNotFoundError):
            compute_file_hash(temp_path / "nonexistent.jpg")