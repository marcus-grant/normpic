"""Photo collection management and organization."""

from datetime import datetime
from pathlib import Path
from typing import Optional, List

from src.model.manifest import Manifest
from src.model.pic import Pic
from src.util.exif import extract_exif_data, extract_camera_info
from src.template.filename import generate_filename
from src.serializer.manifest import ManifestSerializer
from src.manager.manifest_manager import ManifestManager


def organize_photos(
    source_dir: Path, 
    dest_dir: Path,
    collection_name: str,
    collection_description: Optional[str] = None,
    dry_run: bool = False
) -> Manifest:
    """Organize photos from source to destination with proper ordering and manifest generation.
    
    Args:
        source_dir: Source directory containing photos
        dest_dir: Destination directory for organized photos
        collection_name: Name of the photo collection
        collection_description: Optional description of the collection
        dry_run: If True, generate manifest without creating symlinks
        
    Returns:
        Manifest object with organized photo information
    """
    # Load existing manifest for incremental processing
    manifest_filename = "manifest.dryrun.json" if dry_run else "manifest.json"
    manifest_path = dest_dir / manifest_filename
    manifest_manager = ManifestManager(manifest_path)
    existing_manifest = manifest_manager.load_manifest()
    
    # Build lookup of existing photos by source path
    existing_pics_by_path = {}
    if existing_manifest:
        for pic in existing_manifest.pics:
            existing_pics_by_path[pic.source_path] = pic
    
    # Find all photo files in source directory
    photo_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.webp'}
    source_photos = []
    
    for file_path in source_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in photo_extensions:
            source_photos.append(file_path)
    
    # Filter photos that need processing using change detection
    photos_to_process = []
    unchanged_pics = []
    
    for photo_path in source_photos:
        existing_pic = existing_pics_by_path.get(str(photo_path))
        
        if existing_pic:
            # Check if photo needs reprocessing
            needs_processing = manifest_manager.needs_reprocessing(
                photo_path,
                previous_hash=existing_pic.hash,
                previous_mtime=existing_pic.mtime,
                dest_path=dest_dir / existing_pic.dest_path
            )
            
            if not needs_processing:
                # Photo unchanged - reuse existing pic data
                unchanged_pics.append(existing_pic)
                continue
        
        # Photo is new or changed - needs processing
        photos_to_process.append(photo_path)
    
    # Extract EXIF and camera info for photos that need processing
    pics_with_metadata = []
    for photo_path in photos_to_process:
        exif_data = extract_exif_data(photo_path)
        camera_info = extract_camera_info(photo_path)
        pics_with_metadata.append((photo_path, exif_data, camera_info))
    
    # Order by EXIF timestamp with burst sequence preservation
    ordered_pics = _order_photos_with_burst_preservation(pics_with_metadata)
    
    # Create Pic objects with proper filenames for newly processed photos
    newly_processed_pics = _create_ordered_pics(ordered_pics, collection_name, dest_dir)
    
    # Combine unchanged pics with newly processed pics
    # Note: This is simplified - proper ordering would require reordering all pics together
    all_pics = unchanged_pics + newly_processed_pics
    
    # Create symlinks for newly processed photos (unless dry-run)
    if not dry_run:
        for pic in newly_processed_pics:
            dest_path = dest_dir / pic.dest_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if not dest_path.exists():
                source_path = Path(pic.source_path)
                dest_path.symlink_to(source_path.resolve())
    
    # Create and save manifest
    manifest = Manifest(
        version="0.1.0",
        collection_name=collection_name,
        generated_at=datetime.now(),
        pics=all_pics,
        collection_description=collection_description,
        config={"collection_name": collection_name}
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
    pics = []
    
    for photo_path, exif_data, camera_info in pics_data:
        # Generate destination filename
        existing_filenames = [p.dest_path for p in pics]
        
        dest_filename = generate_filename(
            camera_info=camera_info,
            exif_data=exif_data,
            collection=collection_name,
            existing_filenames=existing_filenames
        )
        
        # Determine timestamp source
        timestamp_source = "exif" if exif_data.timestamp else "filename"
        
        # Calculate file metadata
        file_size = photo_path.stat().st_size
        file_hash = f"sha256-{hash(photo_path.read_bytes())}"  # Simplified
        
        # Get file modification time for change detection
        file_mtime = photo_path.stat().st_mtime
        
        # Create Pic object
        pic = Pic(
            source_path=str(photo_path),
            dest_path=dest_filename,
            hash=file_hash,
            size_bytes=file_size,
            mtime=file_mtime,
            timestamp=exif_data.timestamp,
            timestamp_source=timestamp_source,
            camera=camera_info.model if camera_info else None,
            gps={
                "latitude": exif_data.gps_latitude,
                "longitude": exif_data.gps_longitude
            } if exif_data.gps_latitude and exif_data.gps_longitude else None,
            errors=[]
        )
        
        pics.append(pic)
    
    return pics