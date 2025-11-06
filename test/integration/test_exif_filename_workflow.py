"""Integration tests for complete EXIF extraction → filename generation workflows."""

from datetime import datetime

# These imports will fail initially - that's the point of TDD
from lib.util.exif import extract_exif_data, extract_camera_info
from lib.template.filename import generate_filename
from lib.model.exif import CameraInfo, ExifData


class TestCompleteWorkflows:
    """Integration tests for end-to-end photo processing workflows."""
    
    def test_canon_r5_wedding_photo_complete_workflow(self, create_photo_with_exif):
        """Test: Canon R5 wedding photo → EXIF extraction → filename generation."""
        
        # Arrange: Create Canon R5 wedding photo with full EXIF
        photo = create_photo_with_exif(
            "wedding_ceremony.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            SubSecTimeOriginal="123", 
            Make="Canon",
            Model="EOS R5"
        )
        
        # Act: Extract EXIF data (will fail - function doesn't exist)
        exif_data = extract_exif_data(photo)
        camera_info = extract_camera_info(photo)
        
        # Act: Generate filename (will fail - function doesn't exist)
        filename = generate_filename(
            camera_info=camera_info,
            exif_data=exif_data, 
            collection="wedding"
        )
        
        # Assert: Verify complete workflow produces expected filename
        assert filename == "wedding-20241005T143045-r5a-0.jpg"
        
        # Assert: Verify extracted data structures
        assert isinstance(camera_info, CameraInfo)
        assert camera_info.make == "Canon"
        assert camera_info.model == "EOS R5"
        
        assert isinstance(exif_data, ExifData)
        assert exif_data.timestamp == datetime(2024, 10, 5, 14, 30, 45)
        assert exif_data.subsecond == 123
        
    def test_iphone_ceremony_photo_with_gps_workflow(self, create_photo_with_exif):
        """Test: iPhone photo with GPS → EXIF extraction → filename generation."""
        
        # Arrange: Create iPhone photo with GPS data  
        photo = create_photo_with_exif(
            "ceremony_moment.heic",
            DateTimeOriginal="2024:10:05 16:30:00",
            Make="Apple",
            Model="iPhone 15"
            # TODO: Add GPS EXIF tags when fixture supports them
        )
        
        # Act: Extract data and generate filename
        exif_data = extract_exif_data(photo)
        camera_info = extract_camera_info(photo)
        filename = generate_filename(
            camera_info=camera_info,
            exif_data=exif_data,
            collection="ceremony",
            file_extension=".heic"
        )
        
        # Assert: Verify iPhone workflow
        assert filename == "ceremony-20241005T163000-i15-0.heic"
        assert camera_info.make == "Apple"
        assert camera_info.model == "iPhone 15"
        assert exif_data.timestamp == datetime(2024, 10, 5, 16, 30, 0)
        
    def test_photo_without_exif_graceful_handling(self, create_photo_with_exif):
        """Test: Photo without EXIF → graceful fallback behavior."""
        
        # Arrange: Create photo with no EXIF data
        photo = create_photo_with_exif("no_exif_photo.jpg")  # No EXIF kwargs
        
        # Act: Extract data (should handle missing EXIF gracefully)
        exif_data = extract_exif_data(photo)
        camera_info = extract_camera_info(photo)
        filename = generate_filename(
            camera_info=camera_info,
            exif_data=exif_data,
            collection="unknown"
        )
        
        # Assert: Verify graceful handling of missing data
        assert camera_info.make is None
        assert camera_info.model is None
        assert exif_data.timestamp is None
        assert exif_data.subsecond is None
        
        # Should still generate a filename with fallback values
        assert filename.startswith("unknown-")
        assert filename.endswith("-unk-0.jpg")
        
    def test_burst_sequence_workflow(self, create_photo_with_exif):
        """Test: Burst sequence → EXIF extraction → sequential filename generation."""
        
        # Arrange: Create 3-photo burst sequence
        photos = []
        for i in range(3):
            photo = create_photo_with_exif(
                f"burst_{i:03d}.jpg",
                DateTimeOriginal="2024:10:05 14:30:45",  # Same second
                SubSecTimeOriginal=str(100 + i * 50),    # 100ms, 150ms, 200ms
                Make="Canon",
                Model="EOS R5"
            )
            photos.append(photo)
            
        # Act: Process each photo in the burst
        filenames = []
        existing_filenames = set()
        
        for photo in photos:
            exif_data = extract_exif_data(photo)
            camera_info = extract_camera_info(photo)
            filename = generate_filename(
                camera_info=camera_info,
                exif_data=exif_data,
                collection="reception",
                existing_filenames=existing_filenames
            )
            filenames.append(filename)
            existing_filenames.add(filename)
        
        # Assert: Verify burst sequence gets sequential counters
        assert len(filenames) == 3
        assert filenames[0] == "reception-20241005T143045-r5a-0.jpg"
        assert filenames[1] == "reception-20241005T143045-r5a-1.jpg"
        assert filenames[2] == "reception-20241005T143045-r5a-2.jpg"
        
        # Assert: All filenames are unique
        assert len(set(filenames)) == 3
        
    def test_mixed_camera_collection_workflow(self, create_photo_with_exif, sample_camera_data):
        """Test: Mixed camera types → consistent processing workflow."""
        
        # Arrange: Create photos from different cameras
        camera_types = ["canon_r5", "nikon_d850", "iphone_15"]
        photos = []
        
        for i, camera_type in enumerate(camera_types):
            camera_data = sample_camera_data[camera_type]
            photo = create_photo_with_exif(
                f"mixed_{i:03d}.jpg",
                DateTimeOriginal=f"2024:10:05 14:3{i}:00",  # Different times
                **camera_data
            )
            photos.append(photo)
            
        # Act: Process mixed camera collection
        results = []
        for photo in photos:
            exif_data = extract_exif_data(photo)
            camera_info = extract_camera_info(photo)
            filename = generate_filename(
                camera_info=camera_info,
                exif_data=exif_data,
                collection="portfolio"
            )
            results.append({
                "photo": photo,
                "camera_info": camera_info,
                "exif_data": exif_data, 
                "filename": filename
            })
            
        # Assert: Verify each camera type processed correctly
        assert len(results) == 3
        
        # Canon R5
        assert results[0]["camera_info"].make == "Canon"
        assert results[0]["filename"].endswith("-r5a-0.jpg")
        
        # Nikon D850  
        assert results[1]["camera_info"].make == "Nikon"
        assert results[1]["filename"].endswith("-d85-0.jpg")
        
        # iPhone 15
        assert results[2]["camera_info"].make == "Apple"
        assert results[2]["filename"].endswith("-i15-0.jpg")
        
        # All should have same collection prefix
        for result in results:
            assert result["filename"].startswith("portfolio-")