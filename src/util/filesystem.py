"""Filesystem utilities for photo organization.

Provides symlink operations, file validation, and hash computation
for the NormPic photo processing pipeline.
"""

import hashlib
from pathlib import Path
from typing import List, Callable, Optional


def create_symlink(
    source: Path, 
    destination: Path, 
    atomic: bool = True,
    progress_callback: Optional[Callable[[str], None]] = None
) -> None:
    """Create a symlink from source to destination.
    
    Args:
        source: Path to source file (must exist)
        destination: Path for symlink (must not exist)
        atomic: If True, use atomic operation (temp + rename)
        progress_callback: Optional callback for progress reporting
        
    Raises:
        FileNotFoundError: If source file doesn't exist
        FileExistsError: If destination already exists
    """
    if progress_callback:
        progress_callback(f"Creating symlink: {destination.name}")
    
    if not source.exists():
        raise FileNotFoundError(f"Source file does not exist: {source}")
    
    if destination.exists():
        raise FileExistsError(f"Destination already exists: {destination}")
    
    # Create parent directories if needed
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    if atomic:
        # Atomic operation: create temp symlink then rename
        import os
        temp_dest = destination.parent / f".tmp_{destination.name}_{os.getpid()}"
        try:
            temp_dest.symlink_to(source)
            temp_dest.rename(destination)
        except Exception:
            # Clean up temp file if something went wrong
            if temp_dest.exists():
                temp_dest.unlink()
            raise
    else:
        # Direct symlink creation
        destination.symlink_to(source)


def validate_symlink_integrity(symlink_path: Path) -> bool:
    """Validate that a symlink points to an existing file.
    
    Args:
        symlink_path: Path to symlink to validate
        
    Returns:
        True if symlink is valid and target exists, False otherwise
    """
    if not symlink_path.exists():
        return False
    
    if not symlink_path.is_symlink():
        return False
    
    try:
        # Check if the target exists by resolving the symlink
        target = symlink_path.resolve(strict=True)
        return target.exists()
    except (OSError, RuntimeError):
        # OSError: broken symlink or permission issues
        # RuntimeError: circular symlink
        return False


def detect_broken_symlinks(directory: Path) -> List[Path]:
    """Find all broken symlinks in a directory tree.
    
    Args:
        directory: Directory to search recursively
        
    Returns:
        List of paths to broken symlinks
    """
    broken_links = []
    
    for item in directory.rglob("*"):
        if item.is_symlink() and not validate_symlink_integrity(item):
            broken_links.append(item)
    
    return broken_links


def compute_file_hash(
    file_path: Path, 
    chunk_size: int = 65536,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> str:
    """Compute SHA-256 hash of a file.
    
    Args:
        file_path: Path to file to hash
        chunk_size: Size of chunks to read (default 64KB for optimal performance)
        progress_callback: Optional callback(bytes_read, total_size) for progress
        
    Returns:
        Hexadecimal hash string (64 characters)
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")
    
    sha256_hash = hashlib.sha256()
    file_size = file_path.stat().st_size
    bytes_read = 0
    
    # Optimized chunk size for large files (64KB default)
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256_hash.update(chunk)
            bytes_read += len(chunk)
            
            if progress_callback:
                progress_callback(bytes_read, file_size)
    
    return sha256_hash.hexdigest()