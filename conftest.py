"""Global pytest configuration and fixture imports."""

# Import specific fixtures to make them available project-wide
# ruff: noqa: F401
from test.fixtures import (
    create_photo_with_exif,
    sample_camera_data,
    burst_sequence_timestamps,
    sample_gps_locations,
)
