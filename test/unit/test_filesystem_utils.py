"""Unit tests for filesystem utilities."""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from src.util.filesystem import (
    create_symlink,
    validate_symlink_integrity,
    detect_broken_symlinks, 
    compute_file_hash
)


class TestCreateSymlink:
    """Test symlink creation functionality."""
    
    def test_create_symlink_success(self):
        """Test successful symlink creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.jpg"
            dest = temp_path / "dest.jpg"
            source.write_bytes(b"test data")
            
            create_symlink(source, dest)
            
            assert dest.is_symlink()
            assert dest.readlink() == source
            assert dest.read_bytes() == b"test data"
    
    def test_create_symlink_existing_file(self):
        """Test symlink creation when destination exists.""" 
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.jpg"
            dest = temp_path / "dest.jpg"
            source.write_bytes(b"source data")
            dest.write_bytes(b"existing data")
            
            with pytest.raises(FileExistsError):
                create_symlink(source, dest)
    
    def test_create_symlink_nonexistent_source(self):
        """Test symlink creation with nonexistent source."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "nonexistent.jpg"
            dest = temp_path / "dest.jpg"
            
            with pytest.raises(FileNotFoundError):
                create_symlink(source, dest)
    
    def test_create_symlink_creates_parent_dirs(self):
        """Test symlink creation creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.jpg"
            dest = temp_path / "subdir" / "dest.jpg" 
            source.write_bytes(b"test data")
            
            create_symlink(source, dest)
            
            assert dest.is_symlink()
            assert dest.readlink() == source
    
    def test_create_symlink_atomic_operation(self):
        """Test atomic symlink creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.jpg"
            dest = temp_path / "dest.jpg"
            source.write_bytes(b"test data")
            
            create_symlink(source, dest, atomic=True)
            
            assert dest.is_symlink()
            assert dest.readlink() == source
            # Verify no temp files left behind
            temp_files = list(temp_path.glob(".tmp_*"))
            assert len(temp_files) == 0
    
    def test_create_symlink_non_atomic_operation(self):
        """Test non-atomic symlink creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.jpg"
            dest = temp_path / "dest.jpg"
            source.write_bytes(b"test data")
            
            create_symlink(source, dest, atomic=False)
            
            assert dest.is_symlink()
            assert dest.readlink() == source
    
    def test_create_symlink_progress_callback(self):
        """Test progress callback during symlink creation."""
        progress_messages = []
        
        def progress_callback(message):
            progress_messages.append(message)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.jpg"
            dest = temp_path / "dest.jpg"
            source.write_bytes(b"test data")
            
            create_symlink(source, dest, progress_callback=progress_callback)
            
            assert dest.is_symlink()
            assert len(progress_messages) == 1
            assert "Creating symlink: dest.jpg" in progress_messages[0]


class TestValidateSymlinkIntegrity:
    """Test symlink validation functionality."""
    
    def test_validate_symlink_integrity_valid(self):
        """Test validation of valid symlink."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.jpg"
            symlink = temp_path / "link.jpg"
            source.write_bytes(b"test data")
            symlink.symlink_to(source)
            
            assert validate_symlink_integrity(symlink)
    
    def test_validate_symlink_integrity_broken(self):
        """Test validation of broken symlink."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            source = temp_path / "source.jpg"  
            symlink = temp_path / "link.jpg"
            source.write_bytes(b"test data")
            symlink.symlink_to(source)
            
            # Break the symlink
            source.unlink()
            
            assert not validate_symlink_integrity(symlink)
    
    def test_validate_symlink_integrity_not_symlink(self):
        """Test validation of regular file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            regular_file = temp_path / "file.jpg"
            regular_file.write_bytes(b"test data")
            
            assert not validate_symlink_integrity(regular_file)
    
    def test_validate_symlink_integrity_nonexistent(self):
        """Test validation of nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            nonexistent = temp_path / "nonexistent.jpg"
            
            assert not validate_symlink_integrity(nonexistent)


class TestDetectBrokenSymlinks:
    """Test broken symlink detection functionality."""
    
    def test_detect_broken_symlinks_none(self):
        """Test detection when no broken symlinks exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create valid symlinks
            source1 = temp_path / "source1.jpg"
            source2 = temp_path / "source2.jpg"
            link1 = temp_path / "link1.jpg"
            link2 = temp_path / "link2.jpg"
            
            source1.write_bytes(b"data1")
            source2.write_bytes(b"data2")
            link1.symlink_to(source1)
            link2.symlink_to(source2)
            
            broken = detect_broken_symlinks(temp_path)
            assert broken == []
    
    def test_detect_broken_symlinks_some(self):
        """Test detection when some symlinks are broken.""" 
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create symlinks
            source1 = temp_path / "source1.jpg"
            source2 = temp_path / "source2.jpg"
            link1 = temp_path / "link1.jpg"
            link2 = temp_path / "link2.jpg"
            
            source1.write_bytes(b"data1")
            source2.write_bytes(b"data2")
            link1.symlink_to(source1)
            link2.symlink_to(source2)
            
            # Break one symlink
            source1.unlink()
            
            broken = detect_broken_symlinks(temp_path)
            assert len(broken) == 1
            assert link1 in broken
            assert link2 not in broken
    
    def test_detect_broken_symlinks_ignores_regular_files(self):
        """Test detection ignores regular files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mix of files and symlinks
            regular_file = temp_path / "regular.jpg"
            source = temp_path / "source.jpg"
            broken_link = temp_path / "broken.jpg"
            
            regular_file.write_bytes(b"regular data")
            source.write_bytes(b"source data")
            broken_link.symlink_to(temp_path / "nonexistent.jpg")
            
            broken = detect_broken_symlinks(temp_path)
            assert len(broken) == 1
            assert broken[0] == broken_link
    
    def test_detect_broken_symlinks_recursive(self):
        """Test detection works recursively in subdirectories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create subdirectory with broken symlink
            subdir = temp_path / "subdir" 
            subdir.mkdir()
            broken_link = subdir / "broken.jpg"
            broken_link.symlink_to(temp_path / "nonexistent.jpg")
            
            broken = detect_broken_symlinks(temp_path)
            assert len(broken) == 1
            assert broken[0] == broken_link


class TestComputeFileHash:
    """Test file hash computation functionality."""
    
    def test_compute_file_hash_sha256(self):
        """Test SHA-256 hash computation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            test_file = temp_path / "test.jpg"
            test_file.write_bytes(b"test data")
            
            hash_result = compute_file_hash(test_file)
            
            # SHA-256 of "test data" 
            expected = "916f0027a575074ce72a331777c3478d6513f786a591bd892da1a577bf2335f9"
            assert hash_result == expected
    
    def test_compute_file_hash_different_content(self):
        """Test different files produce different hashes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            file1 = temp_path / "file1.jpg"
            file2 = temp_path / "file2.jpg"
            file1.write_bytes(b"content one")
            file2.write_bytes(b"content two")
            
            hash1 = compute_file_hash(file1)
            hash2 = compute_file_hash(file2)
            
            assert hash1 != hash2
            assert len(hash1) == 64  # SHA-256 hex length
            assert len(hash2) == 64
    
    def test_compute_file_hash_empty_file(self):
        """Test hash computation for empty file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            empty_file = temp_path / "empty.jpg"
            empty_file.write_bytes(b"")
            
            hash_result = compute_file_hash(empty_file)
            
            # SHA-256 of empty string
            expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            assert hash_result == expected
    
    def test_compute_file_hash_nonexistent_file(self):
        """Test hash computation for nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            nonexistent = temp_path / "nonexistent.jpg"
            
            with pytest.raises(FileNotFoundError):
                compute_file_hash(nonexistent)
    
    def test_compute_file_hash_large_file(self):
        """Test hash computation for larger file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            large_file = temp_path / "large.jpg"
            # Create 1MB file
            large_data = b"x" * (1024 * 1024)
            large_file.write_bytes(large_data)
            
            hash_result = compute_file_hash(large_file)
            
            assert len(hash_result) == 64
            assert isinstance(hash_result, str)
    
    @patch("builtins.open", mock_open(read_data=b"mocked data"))
    def test_compute_file_hash_with_mock(self):
        """Test hash computation with mocked file I/O."""
        fake_path = Path("/fake/path.jpg")
        
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(Path, 'stat') as mock_stat:
            mock_stat.return_value.st_size = 11  # len("mocked data")
            hash_result = compute_file_hash(fake_path)
            
            # SHA-256 of "mocked data"
            expected = "e3a8081be79613ec801e399d3c0e41dd247e1b614b32c5427ebad8274f762129"
            assert hash_result == expected
    
    def test_compute_file_hash_custom_chunk_size(self):
        """Test hash computation with custom chunk size."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            test_file = temp_path / "test.jpg"
            test_file.write_bytes(b"test data")
            
            # Use small chunk size
            hash_result = compute_file_hash(test_file, chunk_size=4)
            
            # Should produce same hash regardless of chunk size
            expected = "916f0027a575074ce72a331777c3478d6513f786a591bd892da1a577bf2335f9"
            assert hash_result == expected
    
    def test_compute_file_hash_progress_callback(self):
        """Test progress callback during hash computation."""
        progress_updates = []
        
        def progress_callback(bytes_read, total_size):
            progress_updates.append((bytes_read, total_size))
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            test_file = temp_path / "test.jpg"
            test_data = b"test data for progress"
            test_file.write_bytes(test_data)
            
            hash_result = compute_file_hash(
                test_file, 
                chunk_size=8,  # Small chunks to trigger multiple updates
                progress_callback=progress_callback
            )
            
            assert len(hash_result) == 64
            assert len(progress_updates) > 0
            
            # Check progress updates
            final_update = progress_updates[-1]
            assert final_update[0] == len(test_data)  # bytes_read
            assert final_update[1] == len(test_data)  # total_size