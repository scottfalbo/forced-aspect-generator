"""Test configuration and utilities."""
import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config():
    """Provide a sample configuration for testing."""
    return {
        "preset_name": "test_config",
        "layout": {
            "type": "3panel",
            "panel_size": {"width": 6.0, "height": 6.0, "units": "inches"}
        },
        "camera": {
            "position": [0, 4, 8],
            "target": [0, 0, 0],
            "fov": 50,
            "units": "feet"
        },
        "grid": {
            "density": 0.5,
            "style": {
                "line_weight": 1,
                "color": "#333333",
                "opacity": 0.8
            }
        },
        "output": {
            "format": "svg",
            "size": {"width": 1920, "height": 1080, "units": "pixels"},
            "show_labels": True,
            "show_panels": True
        }
    }
