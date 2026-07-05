"""Photo collection management and organization."""

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from ..model.manifest import Manifest
from ..model.pic import Pic
from ..util.exif import extract_exif_data, extract_camera_info
from ..template.filename import generate_filename
from ..serializer.manifest import ManifestSerializer
from .manifest_manager import (
    ManifestManager,
    load_source_manifest,
    build_source_manifest,
    build_hash_keyed_source_index,
)
from ..util.error_handling import ErrorHandler
from ..util.hash import b2b120_hash


def organize_photos(
    source_dir: Path,
    dest_dir: Path,
    collection_name: str,
    collection_description: Optional[str] = None,
    dry_run: bool = False,
    force: bool = False,
) -> Manifest:
    """Organize photos from source to destination with proper ordering and manifest generation.

    Args:
        source_dir: Source directory containing photos
        dest_dir: Destination directory for organized photos
        collection_name: Name of the photo collection
        collection_description: Optional description of the collection
        dry_run: If True, generate manifest without creating symlinks
        force: If True, bypass stat-skip and rehash every file

    Returns:
        Manifest object with organized photo information
    """
    # Initialize error handler
    error_handler = ErrorHandler()

    # Read or create the source collection manifest
    source_manifest = load_source_manifest(source_dir)
    if source_manifest is None:
        source_manifest = build_source_manifest(source_dir, collection_name)
        ManifestManager(source_dir / "manifest.json").save_manifest(source_manifest)

    # Load existing manifest for incremental processing
    manifest_filename = "manifest.dryrun.json" if dry_run else "manifest.json"
    manifest_path = dest_dir / manifest_filename
    manifest_manager = ManifestManager(manifest_path)
    existing_manifest = manifest_manager.load_manifest()

    # Hash-keyed index from dest manifest for reconciliation (content identity).
    hash_index = build_hash_keyed_source_index(existing_manifest) if existing_manifest else {}

    # Path-keyed index from source manifest for stat-based hash reuse only.
    # Keyed by relative_path (= f.name per build_source_manifest). No source_path
    # used here; stable through commit 5 field deletions.
    path_index = {pic.relative_path: pic for pic in source_manifest.pic}

    # Find all files in source directory and handle supported/unsupported formats
    photo_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.webp'}
    source_photos = []

    for file_path in source_dir.iterdir():
        if file_path.is_file():
            if file_path.suffix.lower() in photo_extensions:
                source_photos.append(file_path)
            else:
                error_handler.handle_unsupported_format(file_path)

    # Hash-keyed change detection with stat-skip for unchanged files.
    # When force=True the stat-skip is bypassed and every file is rehashed.
    _fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
    photos_to_process = []
    unchanged_pics = []

    for photo_path in source_photos:
        stat = photo_path.stat()
        current_mtime = stat.st_mtime
        current_mtime_str = datetime.fromtimestamp(
            current_mtime, tz=timezone.utc
        ).strftime(_fmt)

        prior_pic = path_index.get(photo_path.name)
        if (
            not force
            and prior_pic is not None
            and current_mtime_str == prior_pic.mtime
            and stat.st_size == prior_pic.size_bytes
        ):
            current_hash = prior_pic.hash
        else:
            current_hash = b2b120_hash(photo_path.read_bytes())

        if not manifest_manager.needs_reprocessing_by_hash(
            current_hash, hash_index, current_mtime, dest_dir
        ):
            unchanged_pics.append(hash_index[current_hash])
            continue
        photos_to_process.append(photo_path)
    
    # Extract EXIF and camera info for photos that need processing
    pics_with_metadata = []
    for photo_path in photos_to_process:
        try:
            exif_data = extract_exif_data(photo_path)
            camera_info = extract_camera_info(photo_path)
            pics_with_metadata.append((photo_path, exif_data, camera_info))
        except Exception as e:
            # Handle corrupted files and EXIF errors
            error_str = str(e).lower()
            if "corrupted" in error_str or "invalid" in error_str or "truncated" in error_str:
                error_handler.handle_corrupted_file(photo_path, str(e))
            else:
                # Try to use filesystem timestamp as fallback
                try:
                    fallback_timestamp = datetime.fromtimestamp(photo_path.stat().st_mtime).isoformat()
                    error_handler.handle_exif_extraction_failure(
                        photo_path, 
                        str(e), 
                        fallback_timestamp=fallback_timestamp
                    )
                    # Add with fallback data
                    pics_with_metadata.append((photo_path, None, None))
                except Exception:
                    # Complete failure - skip this file
                    error_handler.handle_filesystem_error(photo_path, f"Cannot access file: {e}")
            continue
    
    # Order by EXIF timestamp with burst sequence preservation
    ordered_pics = _order_photos_with_burst_preservation(pics_with_metadata)
    
    # Create Pic objects with proper filenames for newly processed photos
    newly_processed_pics = _create_ordered_pics(ordered_pics, collection_name, dest_dir)
    
    # Combine unchanged pics with newly processed pics
    # Note: This is simplified - proper ordering would require reordering all pics together
    all_pics = unchanged_pics + newly_processed_pics
    
    # Create symlinks for newly processed photos (unless dry-run)
    if not dry_run:
        pairs = resolve_symlink_pairs_by_hash(
            source_manifest, source_dir, newly_processed_pics, dest_dir
        )
        for source_resolved, dest_path in pairs:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            if not dest_path.exists():
                dest_path.symlink_to(source_resolved)
    
    # Create and save manifest
    manifest = Manifest(
        version="0.1.0",
        collection_name=collection_name,
        generated_at=datetime.now(tz=timezone.utc),
        pic=all_pics,
        collection_description=collection_description,
        config={"collection_name": collection_name},
    )
    
    # Save manifest (with .dryrun suffix in dry-run mode)
    manifest_filename = "manifest.dryrun.json" if dry_run else "manifest.json"
    manifest_file = dest_dir / manifest_filename
    serializer = ManifestSerializer()
    manifest_json = serializer.serialize(manifest, validate=True)
    manifest_file.write_text(manifest_json)
    
    return manifest


def _order_photos_with_burst_preservation(pics_data):
    """Order photos by EXIF timestamp → filename → mtime, with burst preservation.
    
    When timestamps are shared between cameras, preserve burst sequences (no interleaving).
    """
    from collections import defaultdict
    
    # First, do normal temporal sorting
    temporally_sorted = _order_photos_temporally(pics_data)
    
    # Then group consecutive photos with same main timestamp and multiple cameras
    final_order = []
    i = 0
    
    while i < len(temporally_sorted):
        current_pic = temporally_sorted[i]
        photo_path, exif_data, camera_info = current_pic
        
        if not exif_data.timestamp:
            # No timestamp - just add and continue
            final_order.append(current_pic)
            i += 1
            continue
        
        # Check if next photos share the same main timestamp
        main_timestamp = exif_data.timestamp.replace(microsecond=0)
        same_timestamp_group = [current_pic]
        
        # Collect all photos with same main timestamp
        j = i + 1
        while j < len(temporally_sorted):
            next_photo_path, next_exif_data, next_camera_info = temporally_sorted[j]
            if (next_exif_data.timestamp and 
                next_exif_data.timestamp.replace(microsecond=0) == main_timestamp):
                same_timestamp_group.append(temporally_sorted[j])
                j += 1
            else:
                break
        
        # Check if multiple cameras are involved
        cameras_in_group = set()
        for _, _, cam_info in same_timestamp_group:
            cam_key = f"{cam_info.make or 'unknown'}-{cam_info.model or 'unknown'}"
            cameras_in_group.add(cam_key)
        
        if len(cameras_in_group) <= 1:
            # Single camera or no camera info - maintain temporal order
            final_order.extend(same_timestamp_group)
        else:
            # Multiple cameras - group by camera to prevent interleaving
            camera_groups = defaultdict(list)
            for pic_data in same_timestamp_group:
                _, _, cam_info = pic_data
                cam_key = f"{cam_info.make or 'unknown'}-{cam_info.model or 'unknown'}"
                camera_groups[cam_key].append(pic_data)
            
            # Sort camera groups by earliest photo's full timestamp
            def camera_earliest_sort_key(camera_item):
                cam_key, cam_pics = camera_item
                earliest_pic = cam_pics[0]
                _, earliest_exif, _ = earliest_pic
                timestamp_microsec = earliest_exif.timestamp.timestamp()
                if earliest_exif.subsecond:
                    timestamp_microsec += earliest_exif.subsecond / 1000.0
                return timestamp_microsec
            
            # Add camera groups in order of their earliest photo
            for cam_key, cam_pics in sorted(camera_groups.items(), key=camera_earliest_sort_key):
                final_order.extend(cam_pics)
        
        i = j
    
    return final_order


def _order_photos_temporally(pics_data):
    """Order photos by EXIF timestamp with subsecond precision, then filename."""
    def sort_key(pic_data):
        photo_path, exif_data, camera_info = pic_data
        
        if exif_data.timestamp:
            timestamp_microsec = exif_data.timestamp.timestamp()
            if exif_data.subsecond:
                # Has subsecond precision
                timestamp_microsec += exif_data.subsecond / 1000.0
                subsec_priority = 0  # Higher priority
            else:
                # No subsecond precision - add large offset to sort after
                subsec_priority = 1  # Lower priority
            return (0, timestamp_microsec, subsec_priority, photo_path.name)
        
        return (1, 0, 0, photo_path.name)
    
    return sorted(pics_data, key=sort_key)


def _create_ordered_pics(pics_data, collection_name: str, dest_dir: Path) -> List[Pic]:
    """Create Pic objects with proper filenames and metadata."""
    from datetime import datetime
    from collections import defaultdict
    
    # Group photos by (timestamp_to_second, camera_model) to detect bursts
    burst_groups = defaultdict(list)
    
    for i, (photo_path, exif_data, camera_info) in enumerate(pics_data):
        # Get timestamp rounded to the second
        timestamp = exif_data.timestamp or datetime.now()
        timestamp_key = timestamp.replace(microsecond=0)  # Round to second
        
        # Group by timestamp and camera
        camera_model = camera_info.model if camera_info else "unknown"
        group_key = (timestamp_key, camera_model)
        burst_groups[group_key].append((i, photo_path, exif_data, camera_info))
    
    # Generate filenames with burst counters when needed
    pics = [None] * len(pics_data)  # Pre-allocate with correct order
    
    for group_key, group_photos in burst_groups.items():
        if len(group_photos) == 1:
            # Single photo - no counter needed
            i, photo_path, exif_data, camera_info = group_photos[0]
            
            file_extension = photo_path.suffix
            dest_filename = generate_filename(
                camera_info=camera_info,
                exif_data=exif_data,
                collection=collection_name,
                file_extension=file_extension,
                existing_filenames=None  # No collision check needed for single photos
            )
        else:
            # Multiple photos at same timestamp+camera - all need counters
            from ..template.filename import BASE32_ALPHABET, get_camera_code, format_timestamp
            
            # Generate base filename components
            parts = []
            if collection_name:
                parts.append(collection_name)
            
            # Use first photo's data for base filename
            _, first_photo_path, first_exif_data, first_camera_info = group_photos[0]
            timestamp = first_exif_data.timestamp or datetime.now()
            parts.append(format_timestamp(timestamp))
            parts.append(get_camera_code(first_camera_info))
            
            base_filename = "-".join(parts)

        # Create Pic objects for this group
        for j, (i, photo_path, exif_data, camera_info) in enumerate(group_photos):
            if len(group_photos) > 1:
                # Use the counter filename generated above
                file_extension = photo_path.suffix
                counter_char = BASE32_ALPHABET[j]
                dest_filename = f"{base_filename}-{counter_char}{file_extension}"
            # else: dest_filename already set for single photos
            
            # Calculate file metadata
            timestamp_source = "exif" if exif_data.timestamp else "filename"
            stat = photo_path.stat()
            file_size = stat.st_size
            file_hash = b2b120_hash(photo_path.read_bytes())
            file_mtime = datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            
            # Create Pic object
            pic = Pic(
                source_path=str(photo_path),
                dest_path=dest_filename,
                relative_path=dest_filename,
                hash=file_hash,
                size_bytes=file_size,
                mtime=file_mtime,
                timestamp=exif_data.timestamp,
                timestamp_source=timestamp_source,
                camera=camera_info.model if camera_info else None,
                gps={
                    "lat": exif_data.gps_latitude,
                    "lon": exif_data.gps_longitude
                } if exif_data.gps_latitude and exif_data.gps_longitude else None,
                errors=[]
            )
            
            pics[i] = pic  # Maintain original order
    
    return [pic for pic in pics if pic is not None]


def resolve_symlink_pairs_by_hash(
    source_manifest: Manifest,
    source_dir: Path,
    copy_pics: List[Pic],
    dest_dir: Path,
) -> List[Tuple[Path, Path]]:
    """Resolve (source, dest) path pairs for symlink creation via hash reconciliation.

    Implements the contract resolution algorithm for both manifests:
    full location = directory_of(manifest) / collection_root / relative_path.

    Args:
        source_manifest: Source collection manifest with hash-indexed pics.
        source_dir: Directory containing the source manifest file.
        copy_pics: Pics from the copy manifest to resolve.
        dest_dir: Directory containing the copy manifest file.

    Returns:
        List of (source_resolved, dest_path) tuples, one per copy pic.

    Raises:
        RuntimeError: If any copy pic's hash is absent from the source manifest.
    """
    index = build_hash_keyed_source_index(source_manifest)
    pairs: List[Tuple[Path, Path]] = []
    for pic in copy_pics:
        source_pic = index.get(pic.hash)
        if source_pic is None:
            raise RuntimeError(f"no source match for hash: {pic.hash}")
        if source_pic.relative_path is None:
            raise RuntimeError(
                f"source pic has no relative_path: {source_pic.hash}"
            )
        source_resolved = (
            source_dir / source_manifest.collection_root / source_pic.relative_path
        ).resolve()
        if pic.relative_path is None:
            raise RuntimeError(f"copy pic has no relative_path: {pic.dest_path}")
        dest = dest_dir / pic.relative_path
        pairs.append((source_resolved, dest))
    return pairs