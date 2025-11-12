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


def detect_broken_symlinks(
    directory: Path, 
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> List[Path]:
    """Find all broken symlinks in a directory tree.
    
    Args:
        directory: Directory to search recursively
        progress_callback: Optional callback(scanned_count, total_estimate) for progress
        
    Returns:
        List of paths to broken symlinks
    """
    broken_links = []
    
    if not directory.exists() or not directory.is_dir():
        return broken_links
    
    # First pass: count items for progress reporting
    if progress_callback:
        try:
            total_items = sum(1 for _ in directory.rglob("*"))
        except (OSError, PermissionError):
            # If we can't count, estimate or use unknown count
            total_items = 0
    else:
        total_items = 0
    
    scanned_count = 0
    
    try:
        for item in directory.rglob("*"):
            try:
                if item.is_symlink() and not validate_symlink_integrity(item):
                    broken_links.append(item)
                
                scanned_count += 1
                if progress_callback and total_items > 0:
                    progress_callback(scanned_count, total_items)
                    
            except (OSError, PermissionError):
                # Skip files we can't access
                scanned_count += 1
                if progress_callback and total_items > 0:
                    progress_callback(scanned_count, total_items)
                continue
    except (OSError, PermissionError):
        # Handle cases where we can't traverse the directory
        pass
    
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


def scan_directory_symlinks(
    directory: Path,
    progress_callback: Optional[Callable[[str, int, int], None]] = None
) -> dict[str, List[Path]]:
    """Scan directory for symlink analysis with performance optimizations.
    
    Args:
        directory: Directory to scan recursively
        progress_callback: Optional callback(status, current, total) for progress
        
    Returns:
        Dictionary with keys: 'valid', 'broken', 'regular_files', 'directories'
    """
    results = {
        'valid': [],
        'broken': [], 
        'regular_files': [],
        'directories': []
    }
    
    if not directory.exists() or not directory.is_dir():
        return results
    
    # Pre-scan for total count if progress reporting enabled
    total_items = 0
    if progress_callback:
        try:
            if progress_callback:
                progress_callback("Counting items...", 0, 0)
            total_items = sum(1 for _ in directory.rglob("*"))
        except (OSError, PermissionError):
            total_items = 0
    
    current_item = 0
    
    try:
        for item in directory.rglob("*"):
            try:
                current_item += 1
                
                if item.is_dir():
                    results['directories'].append(item)
                elif item.is_symlink():
                    if validate_symlink_integrity(item):
                        results['valid'].append(item)
                    else:
                        results['broken'].append(item)
                else:
                    results['regular_files'].append(item)
                
                if progress_callback and total_items > 0:
                    progress_callback("Scanning...", current_item, total_items)
                    
            except (OSError, PermissionError):
                # Skip inaccessible files/directories
                continue
                
    except (OSError, PermissionError):
        # Handle cases where directory traversal fails
        pass
    
    return results


def batch_validate_symlinks(
    symlinks: List[Path],
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> dict[Path, bool]:
    """Validate multiple symlinks efficiently.
    
    Args:
        symlinks: List of symlink paths to validate
        progress_callback: Optional callback(completed, total) for progress
        
    Returns:
        Dictionary mapping symlink path to validity (True=valid, False=broken)
    """
    results = {}
    
    for i, symlink in enumerate(symlinks):
        try:
            results[symlink] = validate_symlink_integrity(symlink)
        except (OSError, PermissionError):
            results[symlink] = False
            
        if progress_callback:
            progress_callback(i + 1, len(symlinks))
    
    return results