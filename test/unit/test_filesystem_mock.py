"""Unit tests for mock filesystem utilities."""

from unittest.mock import patch, mock_open
from typing import Dict, Any

from src.util.filesystem import (
    create_symlink,
    validate_symlink_integrity,
    detect_broken_symlinks,
    compute_file_hash
)


class MockPath:
    """Mock pathlib.Path for deterministic filesystem testing."""
    
    def __init__(self, path: str, filesystem: 'MockFilesystem'):
        self.path = str(path)
        self.fs = filesystem
    
    def __str__(self):
        return self.path
    
    def __truediv__(self, other):
        """Support path / other syntax."""
        if self.path.endswith('/'):
            new_path = self.path + str(other)
        else:
            new_path = self.path + '/' + str(other)
        return MockPath(new_path, self.fs)
    
    @property
    def name(self):
        """Get filename."""
        return self.path.split('/')[-1]
    
    @property
    def parent(self):
        """Get parent directory."""
        parts = self.path.rstrip('/').split('/')
        if len(parts) <= 1:
            return MockPath('/', self.fs)
        parent_path = '/'.join(parts[:-1])
        return MockPath(parent_path or '/', self.fs)
    
    def exists(self):
        """Check if path exists in mock filesystem."""
        return self.fs.exists(self.path)
    
    def is_symlink(self):
        """Check if path is a symlink."""
        entry = self.fs.entries.get(self.path)
        return entry and entry.get('type') == 'symlink'
    
    def is_file(self):
        """Check if path is a regular file."""
        entry = self.fs.entries.get(self.path)
        return entry and entry.get('type') == 'file'
    
    def is_dir(self):
        """Check if path is a directory.""" 
        entry = self.fs.entries.get(self.path)
        return entry and entry.get('type') == 'directory'
    
    def mkdir(self, parents=False, exist_ok=False):
        """Create directory."""
        if self.exists():
            if not exist_ok:
                raise FileExistsError(f"Directory exists: {self.path}")
            return
        
        if parents:
            # Create parent directories if needed
            parent = self.parent
            if not parent.exists():
                parent.mkdir(parents=True, exist_ok=True)
        
        self.fs.create_directory(self.path)
    
    def symlink_to(self, target):
        """Create symlink to target."""
        if self.exists():
            raise FileExistsError(f"File exists: {self.path}")
        
        self.fs.create_symlink(self.path, str(target))
    
    def readlink(self):
        """Read symlink target."""
        entry = self.fs.entries.get(self.path)
        if not entry or entry.get('type') != 'symlink':
            raise OSError(f"Not a symlink: {self.path}")
        
        target_path = entry.get('target')
        return MockPath(target_path, self.fs)
    
    def resolve(self, strict=False):
        """Resolve symlinks."""
        if not self.is_symlink():
            return self
        
        target = self.readlink()
        if strict and not target.exists():
            raise OSError(f"Symlink target does not exist: {target.path}")
        
        return target.resolve(strict=strict)
    
    def read_bytes(self):
        """Read file contents as bytes."""
        entry = self.fs.entries.get(self.path)
        if not entry or entry.get('type') != 'file':
            raise FileNotFoundError(f"File not found: {self.path}")
        
        content = entry.get('content', b'')
        return content if isinstance(content, bytes) else content.encode('utf-8')
    
    def write_bytes(self, data):
        """Write bytes to file."""
        # Create parent directories if needed
        parent = self.parent
        if not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
        
        self.fs.create_file(self.path, data)
    
    def write_text(self, text, encoding='utf-8'):
        """Write text to file."""
        self.write_bytes(text.encode(encoding))
    
    def stat(self):
        """Get file stats."""
        entry = self.fs.entries.get(self.path)
        if not entry:
            raise FileNotFoundError(f"File not found: {self.path}")
        
        return entry.get('stat', MockStat())
    
    def iterdir(self):
        """Iterate over directory contents."""
        if not self.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.path}")
        
        prefix = self.path.rstrip('/') + '/'
        for path in self.fs.entries:
            if path.startswith(prefix):
                # Get immediate children (not nested)
                relative = path[len(prefix):]
                if '/' not in relative and relative:  # Direct child
                    yield MockPath(path, self.fs)
    
    def rglob(self, pattern):
        """Recursively glob for pattern."""
        # Simple implementation for '*' pattern
        if pattern == '*':
            prefix = self.path.rstrip('/') + '/'
            for path in self.fs.entries:
                if path.startswith(prefix) and path != self.path:
                    yield MockPath(path, self.fs)
        else:
            raise NotImplementedError(f"Pattern {pattern} not implemented")
    
    def rename(self, target):
        """Rename file."""
        if not self.exists():
            raise FileNotFoundError(f"Source not found: {self.path}")
        
        entry = self.fs.entries[self.path]
        del self.fs.entries[self.path]
        self.fs.entries[str(target)] = entry
    
    def unlink(self):
        """Remove file."""
        if not self.exists():
            raise FileNotFoundError(f"File not found: {self.path}")
        
        del self.fs.entries[self.path]


class MockStat:
    """Mock stat result."""
    
    def __init__(self, size=1024, mtime=1699000000.0):
        self.st_size = size
        self.st_mtime = mtime


class MockFilesystem:
    """Mock filesystem for deterministic testing."""
    
    def __init__(self):
        self.entries: Dict[str, Dict[str, Any]] = {}
        self.reset()
    
    def reset(self):
        """Reset to empty filesystem."""
        self.entries.clear()
        # Always have root directory
        self.entries['/'] = {'type': 'directory'}
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return path in self.entries
    
    def create_file(self, path: str, content: bytes = b'', size: int = None):
        """Create a mock file."""
        if size is None:
            size = len(content)
        
        self.entries[path] = {
            'type': 'file',
            'content': content,
            'stat': MockStat(size=size)
        }
    
    def create_directory(self, path: str):
        """Create a mock directory."""
        self.entries[path] = {'type': 'directory'}
    
    def create_symlink(self, path: str, target: str):
        """Create a mock symlink."""
        self.entries[path] = {
            'type': 'symlink', 
            'target': target
        }
    
    def path(self, path_str: str) -> MockPath:
        """Create a MockPath for this filesystem."""
        return MockPath(path_str, self)


class TestMockFilesystem:
    """Test the mock filesystem utilities themselves."""
    
    def test_mock_filesystem_basic_operations(self):
        """Test basic filesystem operations work."""
        fs = MockFilesystem()
        
        # Test file creation and reading
        path = fs.path('/test.txt')
        path.write_text('hello world')
        
        assert path.exists()
        assert path.is_file()
        assert not path.is_dir()
        assert path.read_bytes() == b'hello world'
    
    def test_mock_filesystem_directories(self):
        """Test directory operations."""
        fs = MockFilesystem()
        
        # Test directory creation
        dir_path = fs.path('/test_dir')
        dir_path.mkdir()
        
        assert dir_path.exists()
        assert dir_path.is_dir()
        assert not dir_path.is_file()
    
    def test_mock_filesystem_symlinks(self):
        """Test symlink operations."""
        fs = MockFilesystem()
        
        # Create source file
        source = fs.path('/source.txt')
        source.write_text('source content')
        
        # Create symlink
        link = fs.path('/link.txt')
        link.symlink_to(source)
        
        assert link.exists()
        assert link.is_symlink()
        assert link.readlink().path == source.path
        assert link.resolve().path == source.path
    
    def test_mock_filesystem_parent_child_operations(self):
        """Test parent/child path operations."""
        fs = MockFilesystem()
        
        # Test path construction
        parent = fs.path('/parent')
        child = parent / 'child.txt'
        
        assert child.path == '/parent/child.txt'
        assert child.parent.path == '/parent'
        assert child.name == 'child.txt'


class TestFilesystemWithMocks:
    """Test filesystem utilities using mock filesystem."""
    
    def setup_method(self):
        """Set up fresh mock filesystem for each test."""
        self.fs = MockFilesystem()
        # Patch pathlib.Path to use our mock
        self.path_patcher = patch('src.util.filesystem.Path', self.fs.path)
        self.path_patcher.start()
    
    def teardown_method(self):
        """Clean up after each test."""
        self.path_patcher.stop()
    
    def test_create_symlink_with_mock_filesystem(self):
        """Test symlink creation with mock filesystem."""
        # Arrange
        source = self.fs.path('/source.jpg')
        dest = self.fs.path('/dest.jpg')
        source.write_bytes(b'photo data')
        
        # Act
        create_symlink(source, dest, atomic=False)
        
        # Assert
        assert dest.exists()
        assert dest.is_symlink()
        assert dest.readlink().path == source.path
    
    def test_validate_symlink_with_mock_filesystem(self):
        """Test symlink validation with mock filesystem.""" 
        # Arrange - Valid symlink
        source = self.fs.path('/source.jpg')
        link = self.fs.path('/link.jpg')
        source.write_bytes(b'data')
        link.symlink_to(source)
        
        # Act & Assert
        assert validate_symlink_integrity(link) is True
        
        # Test broken symlink
        broken_link = self.fs.path('/broken.jpg')
        broken_link.symlink_to(self.fs.path('/nonexistent.jpg'))
        
        assert validate_symlink_integrity(broken_link) is False
    
    def test_detect_broken_symlinks_with_mock_filesystem(self):
        """Test broken symlink detection with mock filesystem."""
        # Arrange
        test_dir = self.fs.path('/test_dir')
        test_dir.mkdir()
        
        # Create valid symlink
        source = self.fs.path('/test_dir/source.jpg')
        valid_link = self.fs.path('/test_dir/valid_link.jpg')
        source.write_bytes(b'data')
        valid_link.symlink_to(source)
        
        # Create broken symlink
        broken_link = self.fs.path('/test_dir/broken_link.jpg')
        broken_link.symlink_to(self.fs.path('/nonexistent.jpg'))
        
        # Act
        broken_links = detect_broken_symlinks(test_dir)
        
        # Assert
        assert len(broken_links) == 1
        assert broken_links[0].path == broken_link.path
    
    def test_compute_file_hash_with_mock_filesystem(self):
        """Test file hash computation with mock filesystem."""
        # Arrange
        file_path = self.fs.path('/test.jpg')
        test_data = b'test photo data'
        file_path.write_bytes(test_data)
        
        # Mock the file opening for hash computation
        with patch('builtins.open', mock_open(read_data=test_data)):
            # Act
            hash_result = compute_file_hash(file_path)
            
            # Assert
            assert isinstance(hash_result, str)
            assert len(hash_result) == 64  # SHA-256 hex length
    
    def test_atomic_symlink_creation_with_mock_filesystem(self):
        """Test atomic symlink creation using mock filesystem."""
        # Arrange
        source = self.fs.path('/source.jpg')
        dest = self.fs.path('/dest.jpg')
        source.write_bytes(b'photo data')
        
        # Mock os.getpid for deterministic temp filename
        with patch('os.getpid', return_value=12345):
            # Act
            create_symlink(source, dest, atomic=True)
            
            # Assert
            assert dest.exists()
            assert dest.is_symlink()
            
            # Check that temp file was cleaned up
            temp_name = f'.tmp_{dest.name}_12345'
            temp_path = dest.parent / temp_name
            assert not temp_path.exists()
    
    def test_progress_callback_functionality(self):
        """Test progress callbacks work with mock filesystem."""
        # Arrange
        source = self.fs.path('/source.jpg')
        dest = self.fs.path('/dest.jpg')
        source.write_bytes(b'photo data')
        
        progress_calls = []
        
        def progress_callback(message):
            progress_calls.append(message)
        
        # Act
        create_symlink(source, dest, progress_callback=progress_callback)
        
        # Assert
        assert len(progress_calls) == 1
        assert 'Creating symlink: dest.jpg' in progress_calls[0]


class TestMockFilesystemIntegration:
    """Integration tests showing how to use mock filesystem in other tests."""
    
    def test_mock_filesystem_as_test_utility(self):
        """Demonstrate using mock filesystem as a test utility."""
        fs = MockFilesystem()
        
        # Set up test scenario
        fs.create_directory('/photos')
        fs.create_file('/photos/img001.jpg', b'jpeg data', size=12345)
        fs.create_file('/photos/img002.png', b'png data', size=6789)
        fs.create_symlink('/photos/link.jpg', '/photos/img001.jpg')
        
        # Test directory iteration
        photos_dir = fs.path('/photos')
        files = list(photos_dir.iterdir())
        
        assert len(files) == 3
        filenames = [f.name for f in files]
        assert 'img001.jpg' in filenames
        assert 'img002.png' in filenames
        assert 'link.jpg' in filenames
        
        # Test file properties
        img1 = fs.path('/photos/img001.jpg')
        assert img1.stat().st_size == 12345
        assert img1.read_bytes() == b'jpeg data'
        
        # Test symlink properties
        link = fs.path('/photos/link.jpg')
        assert link.is_symlink()
        assert link.resolve().path == '/photos/img001.jpg'