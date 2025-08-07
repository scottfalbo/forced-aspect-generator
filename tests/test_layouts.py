"""Tests for layout system."""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layouts.base_layout import (
    Panel, PanelDimensions, RoomDimensions, LayoutConfig, BaseLayout,
    create_standard_panel_dimensions, create_standard_room_dimensions
)
from layouts.three_panel import ThreePanelLayout, create_standard_3panel_config
from perspective.transforms import Point3D


class TestPanelDimensions:
    """Test PanelDimensions dataclass."""
    
    def test_creation(self):
        """Test PanelDimensions creation."""
        dims = PanelDimensions(6.0, 6.0, "inches")
        assert dims.width == 6.0
        assert dims.height == 6.0
        assert dims.units == "inches"
    
    def test_defaults(self):
        """Test default units."""
        dims = PanelDimensions(4.0, 4.0)
        assert dims.units == "inches"


class TestRoomDimensions:
    """Test RoomDimensions dataclass."""
    
    def test_creation(self):
        """Test RoomDimensions creation."""
        dims = RoomDimensions(12.0, 8.0, 10.0, "feet")
        assert dims.width == 12.0
        assert dims.height == 8.0
        assert dims.depth == 10.0
        assert dims.units == "feet"
    
    def test_defaults(self):
        """Test default units."""
        dims = RoomDimensions(12.0, 8.0, 10.0)
        assert dims.units == "feet"


class TestPanel:
    """Test Panel class."""
    
    def test_creation(self):
        """Test Panel creation."""
        corners = [
            Point3D(0.0, 0.0, 0.0),
            Point3D(1.0, 0.0, 0.0),
            Point3D(1.0, 1.0, 0.0),
            Point3D(0.0, 1.0, 0.0)
        ]
        normal = Point3D(0.0, 0.0, 1.0)
        
        panel = Panel("Test Panel", corners, normal, "wall")
        
        assert panel.label == "Test Panel"
        assert len(panel.corners) == 4
        assert panel.normal.z == 1.0
        assert panel.panel_type == "wall"
    
    def test_get_center(self):
        """Test center point calculation."""
        corners = [
            Point3D(0.0, 0.0, 0.0),
            Point3D(2.0, 0.0, 0.0),
            Point3D(2.0, 2.0, 0.0),
            Point3D(0.0, 2.0, 0.0)
        ]
        normal = Point3D(0.0, 0.0, 1.0)
        
        panel = Panel("Test Panel", corners, normal, "wall")
        center = panel.get_center()
        
        assert center.x == 1.0
        assert center.y == 1.0
        assert center.z == 0.0
    
    def test_get_center_invalid(self):
        """Test center calculation with invalid corner count."""
        corners = [Point3D(0.0, 0.0, 0.0)]  # Only one corner
        normal = Point3D(0.0, 0.0, 1.0)
        
        panel = Panel("Test Panel", corners, normal, "wall")
        
        with pytest.raises(ValueError):
            panel.get_center()
    
    def test_get_bounds(self):
        """Test bounding box calculation."""
        corners = [
            Point3D(-1.0, -2.0, -3.0),
            Point3D(1.0, -2.0, -3.0),
            Point3D(1.0, 2.0, -3.0),
            Point3D(-1.0, 2.0, -3.0)
        ]
        normal = Point3D(0.0, 0.0, 1.0)
        
        panel = Panel("Test Panel", corners, normal, "wall")
        bounds = panel.get_bounds()
        
        assert bounds["min_x"] == -1.0
        assert bounds["max_x"] == 1.0
        assert bounds["min_y"] == -2.0
        assert bounds["max_y"] == 2.0
        assert bounds["min_z"] == -3.0
        assert bounds["max_z"] == -3.0


class TestLayoutConfig:
    """Test LayoutConfig class."""
    
    def test_creation(self):
        """Test LayoutConfig creation."""
        panel_dims = PanelDimensions(6.0, 6.0, "inches")
        room_dims = RoomDimensions(12.0, 8.0, 10.0, "feet")
        
        config = LayoutConfig(panel_dims, room_dims, "3panel")
        
        assert config.panel_dimensions.width == 6.0
        assert config.room_dimensions.height == 8.0
        assert config.layout_type == "3panel"
    
    def test_validation_valid(self):
        """Test validation with valid config."""
        panel_dims = PanelDimensions(6.0, 6.0, "inches")
        room_dims = RoomDimensions(12.0, 8.0, 10.0, "feet")
        
        config = LayoutConfig(panel_dims, room_dims, "3panel")
        
        assert config.validate() == True
    
    def test_validation_invalid_panel(self):
        """Test validation with invalid panel dimensions."""
        panel_dims = PanelDimensions(-1.0, 6.0, "inches")  # Negative width
        room_dims = RoomDimensions(12.0, 8.0, 10.0, "feet")
        
        config = LayoutConfig(panel_dims, room_dims, "3panel")
        
        assert config.validate() == False
    
    def test_validation_invalid_room(self):
        """Test validation with invalid room dimensions."""
        panel_dims = PanelDimensions(6.0, 6.0, "inches")
        room_dims = RoomDimensions(12.0, 0.0, 10.0, "feet")  # Zero height
        
        config = LayoutConfig(panel_dims, room_dims, "3panel")
        
        assert config.validate() == False


class TestThreePanelLayout:
    """Test ThreePanelLayout implementation."""
    
    def test_creation(self):
        """Test 3-panel layout creation."""
        config = create_standard_3panel_config()
        layout = ThreePanelLayout(config)
        
        assert layout.get_layout_name() == "3-Panel Corner Room"
        assert layout.get_panel_count() == 3
        assert layout.config.layout_type == "3panel"
    
    def test_panel_generation(self):
        """Test panel generation."""
        config = create_standard_3panel_config()
        layout = ThreePanelLayout(config)
        panels = layout.get_panels()
        
        assert len(panels) == 3
        
        # Check panel labels
        labels = [panel.label for panel in panels]
        assert "Floor" in labels
        assert "Left Wall" in labels
        assert "Right Wall" in labels
    
    def test_floor_panel_geometry(self):
        """Test floor panel geometry."""
        config = create_standard_3panel_config()
        layout = ThreePanelLayout(config)
        panels = layout.get_panels()
        
        floor_panel = next(panel for panel in panels if panel.label == "Floor")
        
        # Floor should be at Y=0
        for corner in floor_panel.corners:
            assert corner.y == 0.0
        
        # Floor normal should point up
        assert floor_panel.normal.y == 1.0
        assert floor_panel.panel_type == "floor"
    
    def test_wall_panel_geometry(self):
        """Test wall panel geometry."""
        config = create_standard_3panel_config()
        layout = ThreePanelLayout(config)
        panels = layout.get_panels()
        
        left_wall = next(panel for panel in panels if panel.label == "Left Wall")
        right_wall = next(panel for panel in panels if panel.label == "Right Wall")
        
        # Left wall should be at X=0
        for corner in left_wall.corners:
            assert corner.x == 0.0
        
        # Right wall should be at Z=0
        for corner in right_wall.corners:
            assert corner.z == 0.0
        
        # Check normals
        assert left_wall.normal.x == 1.0  # Points right
        assert right_wall.normal.z == 1.0  # Points forward
        
        # Both should be walls
        assert left_wall.panel_type == "wall"
        assert right_wall.panel_type == "wall"
    
    def test_panel_caching(self):
        """Test that panels are cached after first generation."""
        config = create_standard_3panel_config()
        layout = ThreePanelLayout(config)
        
        panels1 = layout.get_panels()
        panels2 = layout.get_panels()
        
        # Should be the same object (cached)
        assert panels1 is panels2
    
    def test_bounds_calculation(self):
        """Test total bounds calculation."""
        config = create_standard_3panel_config()
        layout = ThreePanelLayout(config)
        bounds = layout.get_total_bounds()
        
        # Should have positive extents
        assert bounds["max_x"] > bounds["min_x"]
        assert bounds["max_y"] > bounds["min_y"]
        assert bounds["max_z"] > bounds["min_z"]
        
        # Origin should be included
        assert bounds["min_x"] <= 0.0
        assert bounds["min_y"] <= 0.0
        assert bounds["min_z"] <= 0.0
    
    def test_center_point(self):
        """Test center point calculation."""
        config = create_standard_3panel_config()
        layout = ThreePanelLayout(config)
        center = layout.get_center_point()
        
        # Center should be in positive quadrant
        assert center.x >= 0.0
        assert center.y >= 0.0
        assert center.z >= 0.0
    
    def test_optimal_camera_positions(self):
        """Test optimal camera position suggestions."""
        config = create_standard_3panel_config()
        layout = ThreePanelLayout(config)
        
        camera_pos = layout.get_optimal_camera_position()
        camera_target = layout.get_optimal_camera_target()
        
        # Camera should be positioned away from origin
        assert camera_pos.x > 0.0
        assert camera_pos.y > 0.0
        assert camera_pos.z > 0.0
        
        # Target should be reasonable
        assert camera_target.x >= 0.0
        assert camera_target.y >= 0.0
        assert camera_target.z >= 0.0
    
    def test_description(self):
        """Test layout description generation."""
        config = create_standard_3panel_config()
        layout = ThreePanelLayout(config)
        description = layout.get_description()
        
        assert "3-Panel Corner Room" in description
        assert "Floor" in description
        assert "Wall" in description
        assert "6.0" in description  # Panel dimensions
    
    def test_invalid_config(self):
        """Test layout creation with invalid config."""
        panel_dims = PanelDimensions(-1.0, 6.0, "inches")  # Invalid
        room_dims = RoomDimensions(12.0, 8.0, 10.0, "feet")
        config = LayoutConfig(panel_dims, room_dims, "3panel")
        
        with pytest.raises(ValueError):
            ThreePanelLayout(config)


class TestLayoutFactories:
    """Test layout factory functions."""
    
    def test_standard_panel_dimensions(self):
        """Test standard panel dimension presets."""
        small = create_standard_panel_dimensions("small")
        standard = create_standard_panel_dimensions("standard")
        large = create_standard_panel_dimensions("large")
        
        assert small.width == 4.0
        assert standard.width == 6.0
        assert large.width == 8.0
        
        # All should be square
        assert small.width == small.height
        assert standard.width == standard.height
        assert large.width == large.height
    
    def test_standard_room_dimensions(self):
        """Test standard room dimension presets."""
        small = create_standard_room_dimensions("small")
        standard = create_standard_room_dimensions("standard")
        large = create_standard_room_dimensions("large")
        
        assert small.width == 8.0
        assert standard.width == 12.0
        assert large.width == 16.0
        
        # All should have reasonable proportions
        assert small.height > 0
        assert standard.height > 0
        assert large.height > 0
    
    def test_standard_3panel_config(self):
        """Test 3-panel config factory."""
        config = create_standard_3panel_config()
        
        assert config.layout_type == "3panel"
        assert config.validate() == True
        assert config.panel_dimensions.width == 6.0
        assert config.room_dimensions.width == 12.0
    
    def test_3panel_config_with_presets(self):
        """Test 3-panel config with different presets."""
        config = create_standard_3panel_config("large", "small")
        
        assert config.panel_dimensions.width == 8.0
        assert config.room_dimensions.width == 8.0


if __name__ == "__main__":
    # Run tests if executed directly
    import subprocess
    subprocess.run(["python", "-m", "pytest", __file__, "-v"])
