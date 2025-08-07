"""
3-Panel corner room layout implementation.

This layout creates a corner room with floor and two walls meeting at a corner.
Perfect for simple forced perspective compositions.
"""

from typing import List
from .base_layout import BaseLayout, Panel, LayoutConfig
from perspective.transforms import Point3D


class ThreePanelLayout(BaseLayout):
    """
    3-Panel corner room layout: Floor + Left Wall + Right Wall.
    
    This is the most common layout for forced perspective art. The panels
    form a corner where two walls meet the floor, creating a natural
    3D environment for artwork.
    
    Coordinate system:
    - Origin at the corner where walls meet the floor
    - X-axis: along the right wall
    - Y-axis: vertical (floor to ceiling)
    - Z-axis: along the left wall
    """
    
    def __init__(self, config: LayoutConfig):
        """Initialize 3-panel layout."""
        config.layout_type = "3panel"
        super().__init__(config)
    
    def get_panels(self) -> List[Panel]:
        """Generate the three panels: floor, left wall, right wall."""
        if self._panels is None:
            self._panels = self._create_panels()
        return self._panels
    
    def get_layout_name(self) -> str:
        """Get layout name."""
        return "3-Panel Corner Room"
    
    def get_panel_count(self) -> int:
        """Get panel count."""
        return 3
    
    def _create_panels(self) -> List[Panel]:
        """Create the three panel geometries."""
        panels = []
        
        # Use room dimensions to define the 3D space
        room_width = self.config.room_dimensions.width
        room_height = self.config.room_dimensions.height
        room_depth = self.config.room_dimensions.depth
        
        # Scale factor from room units to panel units
        scale = self._get_scale_factor()
        
        # Convert room dimensions to working units (typically same as panel units)
        width = room_width * scale
        height = room_height * scale
        depth = room_depth * scale
        
        # Create floor panel
        floor_panel = self._create_floor_panel(width, depth)
        panels.append(floor_panel)
        
        # Create left wall panel (along Z axis)
        left_wall_panel = self._create_left_wall_panel(depth, height)
        panels.append(left_wall_panel)
        
        # Create right wall panel (along X axis)
        right_wall_panel = self._create_right_wall_panel(width, height)
        panels.append(right_wall_panel)
        
        return panels
    
    def _create_floor_panel(self, width: float, depth: float) -> Panel:
        """
        Create the floor panel.
        
        The floor lies in the XZ plane (Y=0) and extends from the origin.
        """
        corners = [
            Point3D(0.0, 0.0, 0.0),      # Origin corner
            Point3D(width, 0.0, 0.0),    # Right edge
            Point3D(width, 0.0, depth),  # Far right corner
            Point3D(0.0, 0.0, depth)     # Far left corner
        ]
        
        # Floor normal points up (positive Y)
        normal = Point3D(0.0, 1.0, 0.0)
        
        return Panel(
            label="Floor",
            corners=corners,
            normal=normal,
            panel_type="floor"
        )
    
    def _create_left_wall_panel(self, depth: float, height: float) -> Panel:
        """
        Create the left wall panel.
        
        The left wall lies in the YZ plane (X=0) and extends upward from the floor.
        Corner order: [bottom-near, bottom-far, top-far, top-near]
        """
        corners = [
            Point3D(0.0, 0.0, 0.0),      # Bottom corner at origin (bottom-near)
            Point3D(0.0, 0.0, depth),    # Bottom corner at far end (bottom-far)
            Point3D(0.0, height, depth), # Top corner at far end (top-far)
            Point3D(0.0, height, 0.0)    # Top corner at origin (top-near)
        ]
        
        # Left wall normal points right (positive X)
        normal = Point3D(1.0, 0.0, 0.0)
        
        return Panel(
            label="Left Wall",
            corners=corners,
            normal=normal,
            panel_type="wall"
        )
    
    def _create_right_wall_panel(self, width: float, height: float) -> Panel:
        """
        Create the right wall panel.
        
        The right wall lies in the XY plane (Z=0) and extends upward from the floor.
        Corner order: [bottom-near, bottom-far, top-far, top-near]
        """
        corners = [
            Point3D(0.0, 0.0, 0.0),      # Bottom corner at origin (bottom-near)
            Point3D(width, 0.0, 0.0),    # Bottom corner at far end (bottom-far)
            Point3D(width, height, 0.0), # Top corner at far end (top-far)
            Point3D(0.0, height, 0.0)    # Top corner at origin (top-near)
        ]
        
        # Right wall normal points forward (positive Z)
        normal = Point3D(0.0, 0.0, 1.0)
        
        return Panel(
            label="Right Wall", 
            corners=corners,
            normal=normal,
            panel_type="wall"
        )
    
    def _get_scale_factor(self) -> float:
        """
        Get scale factor to convert room units to panel units.
        
        Returns:
            Scale factor for unit conversion
        """
        # Define conversion factors to inches
        to_inches = {
            "inches": 1.0,
            "feet": 12.0,
            "meters": 39.37,
            "cm": 0.3937,
            "mm": 0.0394
        }
        
        room_units = self.config.room_dimensions.units
        panel_units = self.config.panel_dimensions.units
        
        room_to_inches = to_inches.get(room_units, 1.0)
        panel_to_inches = to_inches.get(panel_units, 1.0)
        
        # Convert room units to panel units
        return room_to_inches / panel_to_inches
    
    def get_optimal_camera_position(self) -> Point3D:
        """
        Get an optimal camera position for viewing this layout.
        
        Returns:
            Suggested camera position for good perspective view
        """
        bounds = self.get_total_bounds()
        
        # Position camera at corner diagonal, elevated, and back from the scene
        distance_factor = 1.5  # Multiplier for viewing distance
        
        x = bounds["max_x"] * distance_factor
        y = bounds["max_y"] * 0.6  # Slightly below top for good angle
        z = bounds["max_z"] * distance_factor
        
        return Point3D(x, y, z)
    
    def get_optimal_camera_target(self) -> Point3D:
        """
        Get optimal camera target point for this layout.
        
        Returns:
            Point to aim camera at for good composition
        """
        bounds = self.get_total_bounds()
        
        # Target the center of the floor area, slightly elevated
        x = bounds["max_x"] * 0.4
        y = bounds["max_y"] * 0.2
        z = bounds["max_z"] * 0.4
        
        return Point3D(x, y, z)


def create_standard_3panel_config(panel_size: str = "standard", room_size: str = "standard") -> LayoutConfig:
    """
    Create a standard 3-panel layout configuration.
    
    Args:
        panel_size: "small", "standard", or "large"
        room_size: "small", "standard", or "large"
        
    Returns:
        LayoutConfig for 3-panel setup
    """
    from .base_layout import create_standard_panel_dimensions, create_standard_room_dimensions
    
    panel_dims = create_standard_panel_dimensions(panel_size)
    room_dims = create_standard_room_dimensions(room_size)
    
    return LayoutConfig(
        panel_dimensions=panel_dims,
        room_dimensions=room_dims,
        layout_type="3panel"
    )
