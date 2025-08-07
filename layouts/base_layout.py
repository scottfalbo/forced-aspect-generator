"""
Base layout class for panel configurations.

This module defines the abstract interface that all panel layouts must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
from perspective.transforms import Point3D


@dataclass
class PanelDimensions:
    """Physical dimensions of a panel."""
    width: float
    height: float
    units: str = "inches"


@dataclass
class RoomDimensions:
    """Dimensions of the room being represented."""
    width: float
    height: float
    depth: float
    units: str = "feet"


@dataclass 
class Panel:
    """
    Represents a single panel in the layout.
    
    A panel is defined by its corner points in 3D space and metadata.
    """
    label: str
    corners: List[Point3D]  # 4 corners in counter-clockwise order
    normal: Point3D         # Surface normal vector
    panel_type: str         # "floor", "wall", "ceiling"
    
    def get_center(self) -> Point3D:
        """Calculate the center point of the panel."""
        if len(self.corners) != 4:
            raise ValueError("Panel must have exactly 4 corners")
        
        x = sum(corner.x for corner in self.corners) / 4
        y = sum(corner.y for corner in self.corners) / 4
        z = sum(corner.z for corner in self.corners) / 4
        
        return Point3D(x, y, z)
    
    def get_bounds(self) -> Dict[str, float]:
        """Get bounding box of the panel."""
        if not self.corners:
            return {"min_x": 0, "max_x": 0, "min_y": 0, "max_y": 0, "min_z": 0, "max_z": 0}
        
        xs = [corner.x for corner in self.corners]
        ys = [corner.y for corner in self.corners]
        zs = [corner.z for corner in self.corners]
        
        return {
            "min_x": min(xs), "max_x": max(xs),
            "min_y": min(ys), "max_y": max(ys),
            "min_z": min(zs), "max_z": max(zs)
        }


@dataclass
class LayoutConfig:
    """Configuration for a panel layout."""
    panel_dimensions: PanelDimensions
    room_dimensions: RoomDimensions
    layout_type: str
    
    def validate(self) -> bool:
        """Validate the configuration."""
        if self.panel_dimensions.width <= 0 or self.panel_dimensions.height <= 0:
            return False
        if self.room_dimensions.width <= 0 or self.room_dimensions.height <= 0 or self.room_dimensions.depth <= 0:
            return False
        return True


class BaseLayout(ABC):
    """
    Abstract base class for all panel layout types.
    
    This class defines the interface that all specific layout implementations
    (3-panel, 4-panel, 5-panel) must follow.
    """
    
    def __init__(self, config: LayoutConfig):
        """
        Initialize layout with configuration.
        
        Args:
            config: Layout configuration specifying dimensions and type
        """
        if not config.validate():
            raise ValueError("Invalid layout configuration")
        
        self.config = config
        self._panels = None
        
    @abstractmethod
    def get_panels(self) -> List[Panel]:
        """
        Get list of panels in this layout.
        
        Returns:
            List of Panel objects defining the 3D geometry
        """
        pass
    
    @abstractmethod
    def get_layout_name(self) -> str:
        """
        Get the human-readable name of this layout.
        
        Returns:
            Layout name (e.g., "3-Panel Corner Room")
        """
        pass
    
    @abstractmethod
    def get_panel_count(self) -> int:
        """
        Get the number of panels in this layout.
        
        Returns:
            Number of panels
        """
        pass
    
    def get_total_bounds(self) -> Dict[str, float]:
        """
        Get bounding box that encompasses all panels.
        
        Returns:
            Dictionary with min/max coordinates for all axes
        """
        panels = self.get_panels()
        if not panels:
            return {"min_x": 0, "max_x": 0, "min_y": 0, "max_y": 0, "min_z": 0, "max_z": 0}
        
        all_corners = []
        for panel in panels:
            all_corners.extend(panel.corners)
        
        xs = [corner.x for corner in all_corners]
        ys = [corner.y for corner in all_corners]
        zs = [corner.z for corner in all_corners]
        
        return {
            "min_x": min(xs), "max_x": max(xs),
            "min_y": min(ys), "max_y": max(ys),
            "min_z": min(zs), "max_z": max(zs)
        }
    
    def get_center_point(self) -> Point3D:
        """
        Get the center point of the entire layout.
        
        Returns:
            Center point of all panels
        """
        bounds = self.get_total_bounds()
        
        center_x = (bounds["min_x"] + bounds["max_x"]) / 2
        center_y = (bounds["min_y"] + bounds["max_y"]) / 2
        center_z = (bounds["min_z"] + bounds["max_z"]) / 2
        
        return Point3D(center_x, center_y, center_z)
    
    def scale_to_units(self, target_units: str) -> float:
        """
        Get scaling factor to convert to target units.
        
        Args:
            target_units: Target unit system ("inches", "feet", "meters")
            
        Returns:
            Scaling factor
        """
        # Define conversion factors to inches
        to_inches = {
            "inches": 1.0,
            "feet": 12.0,
            "meters": 39.37,
            "cm": 0.3937,
            "mm": 0.0394
        }
        
        panel_to_inches = to_inches.get(self.config.panel_dimensions.units, 1.0)
        target_to_inches = to_inches.get(target_units, 1.0)
        
        return panel_to_inches / target_to_inches
    
    def get_description(self) -> str:
        """
        Get a description of the layout configuration.
        
        Returns:
            Human-readable description
        """
        panels = self.get_panels()
        panel_names = [panel.label for panel in panels]
        
        return f"{self.get_layout_name()}: {', '.join(panel_names)} " \
               f"({self.config.panel_dimensions.width}\" × {self.config.panel_dimensions.height}\")"


def create_standard_panel_dimensions(size_preset: str = "standard") -> PanelDimensions:
    """
    Create standard panel dimensions based on preset.
    
    Args:
        size_preset: "small", "standard", "large", or custom
        
    Returns:
        PanelDimensions with appropriate size
    """
    presets = {
        "small": PanelDimensions(4.0, 4.0, "inches"),
        "standard": PanelDimensions(6.0, 6.0, "inches"),
        "large": PanelDimensions(8.0, 8.0, "inches"),
    }
    
    return presets.get(size_preset, presets["standard"])


def create_standard_room_dimensions(room_preset: str = "standard") -> RoomDimensions:
    """
    Create standard room dimensions based on preset.
    
    Args:
        room_preset: "small", "standard", "large"
        
    Returns:
        RoomDimensions with appropriate size
    """
    presets = {
        "small": RoomDimensions(8.0, 6.0, 8.0, "feet"),
        "standard": RoomDimensions(12.0, 8.0, 12.0, "feet"),
        "large": RoomDimensions(16.0, 10.0, 16.0, "feet"),
    }
    
    return presets.get(room_preset, presets["standard"])
