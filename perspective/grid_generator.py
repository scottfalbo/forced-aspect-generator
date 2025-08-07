"""
Grid generation for perspective layouts.

This module creates perspective-accurate grid lines for each panel in a layout.
"""

import numpy as np
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from .transforms import Point3D, Point2D, project_to_screen
from .camera import Camera
from layouts.base_layout import Panel


@dataclass
class GridLine:
    """Represents a single grid line in 2D screen space."""
    start: Point2D
    end: Point2D
    panel_label: str
    line_type: str  # "horizontal", "vertical", "boundary"


@dataclass
class GridConfig:
    """Configuration for grid generation."""
    density: float = 0.5          # Grid spacing (0.1 = fine, 1.0 = coarse)
    show_panel_boundaries: bool = True
    show_panel_labels: bool = True
    min_line_length: float = 5.0  # Minimum line length in pixels
    max_lines_per_panel: int = 100


class GridGenerator:
    """Generates perspective grids for panel layouts."""
    
    def __init__(self, config: GridConfig = None):
        """
        Initialize grid generator.
        
        Args:
            config: Grid generation configuration
        """
        self.config = config or GridConfig()
    
    def generate_grid(self, panels: List[Panel], camera: Camera, 
                     screen_width: int, screen_height: int) -> List[GridLine]:
        """
        Generate perspective grid lines for all panels.
        
        Args:
            panels: List of panels to generate grids for
            camera: Camera for perspective projection
            screen_width: Output image width in pixels
            screen_height: Output image height in pixels
            
        Returns:
            List of grid lines in screen coordinates
        """
        all_lines = []
        
        # Get camera matrices
        view_matrix = camera.get_view_matrix()
        aspect_ratio = screen_width / screen_height
        projection_matrix = camera.get_projection_matrix(aspect_ratio)
        
        for panel in panels:
            # Generate grid for this panel
            panel_lines = self._generate_panel_grid(
                panel, view_matrix, projection_matrix, screen_width, screen_height
            )
            all_lines.extend(panel_lines)
        
        # Filter out very short lines
        filtered_lines = [
            line for line in all_lines 
            if self._calculate_line_length(line) >= self.config.min_line_length
        ]
        
        return filtered_lines
    
    def _generate_panel_grid(self, panel: Panel, view_matrix, projection_matrix,
                            screen_width: int, screen_height: int) -> List[GridLine]:
        """Generate grid lines for a single panel."""
        lines = []
        
        # Add panel boundary if requested
        if self.config.show_panel_boundaries:
            boundary_lines = self._generate_panel_boundary(
                panel, view_matrix, projection_matrix, screen_width, screen_height
            )
            lines.extend(boundary_lines)
        
        # Generate interior grid lines
        interior_lines = self._generate_interior_grid(
            panel, view_matrix, projection_matrix, screen_width, screen_height
        )
        lines.extend(interior_lines)
        
        return lines
    
    def _generate_panel_boundary(self, panel: Panel, view_matrix, projection_matrix,
                                screen_width: int, screen_height: int) -> List[GridLine]:
        """Generate boundary lines for a panel."""
        lines = []
        corners = panel.corners
        
        if len(corners) != 4:
            return lines
        
        # Create lines between adjacent corners
        for i in range(4):
            start_3d = corners[i]
            end_3d = corners[(i + 1) % 4]
            
            # Project and clip line
            line = self._project_and_clip_line(
                start_3d, end_3d, view_matrix, projection_matrix,
                screen_width, screen_height, panel.label, "boundary"
            )
            
            if line:
                lines.append(line)
        
        return lines
    
    def _generate_interior_grid(self, panel: Panel, view_matrix, projection_matrix,
                               screen_width: int, screen_height: int) -> List[GridLine]:
        """Generate interior grid lines for a panel."""
        lines = []
        
        if len(panel.corners) != 4:
            return lines
        
        # Determine panel orientation and generate appropriate grid
        if panel.panel_type == "floor":
            lines.extend(self._generate_floor_grid(
                panel, view_matrix, projection_matrix, screen_width, screen_height
            ))
        elif panel.panel_type == "wall":
            lines.extend(self._generate_wall_grid(
                panel, view_matrix, projection_matrix, screen_width, screen_height
            ))
        
        return lines
    
    def _generate_floor_grid(self, panel: Panel, view_matrix, projection_matrix,
                            screen_width: int, screen_height: int) -> List[GridLine]:
        """Generate uniform square grid for floor panel."""
        lines = []
        corners = panel.corners
        
        # Floor corners: [origin, right_edge, far_right, far_left]
        origin = corners[0]      # (0, 0, 0)
        right_edge = corners[1]  # (width, 0, 0)  
        far_right = corners[2]   # (width, 0, depth)
        far_left = corners[3]    # (0, 0, depth)
        
        # Calculate dimensions
        width = abs(right_edge.x - origin.x)
        depth = abs(far_left.z - origin.z)
        
        # Use consistent square grid spacing
        grid_spacing = self._calculate_grid_spacing(min(width, depth))
        
        # Generate horizontal lines (parallel to X-axis, spaced in Z direction)
        num_z_lines = int(depth / grid_spacing)
        for i in range(1, num_z_lines):  # Skip boundaries, start from 1
            z_pos = origin.z + (i * grid_spacing)
            if z_pos >= far_left.z:
                break
                
            start_3d = Point3D(origin.x, origin.y, z_pos)
            end_3d = Point3D(right_edge.x, origin.y, z_pos)
            
            line = self._project_and_clip_line(
                start_3d, end_3d, view_matrix, projection_matrix,
                screen_width, screen_height, panel.label, "horizontal"
            )
            
            if line:
                lines.append(line)
        
        # Generate vertical lines (parallel to Z-axis, spaced in X direction)
        num_x_lines = int(width / grid_spacing)
        for i in range(1, num_x_lines):  # Skip boundaries, start from 1
            x_pos = origin.x + (i * grid_spacing)
            if x_pos >= right_edge.x:
                break
                
            start_3d = Point3D(x_pos, origin.y, origin.z)
            end_3d = Point3D(x_pos, origin.y, far_left.z)
            
            line = self._project_and_clip_line(
                start_3d, end_3d, view_matrix, projection_matrix,
                screen_width, screen_height, panel.label, "vertical"
            )
            
            if line:
                lines.append(line)
        
        return lines
    
    def _generate_wall_grid(self, panel: Panel, view_matrix, projection_matrix,
                           screen_width: int, screen_height: int) -> List[GridLine]:
        """Generate uniform square grid for wall panels."""
        lines = []
        corners = panel.corners
        
        # Wall corners: [near-bottom, far-bottom, far-top, near-top]
        near_bottom = corners[0]
        far_bottom = corners[1]
        far_top = corners[2]
        near_top = corners[3]
        
        # Calculate dimensions
        if panel.label == "Left Wall":
            # Left wall: varies in Z (depth) and Y (height)
            width = abs(far_bottom.z - near_bottom.z)
            height = abs(near_top.y - near_bottom.y)
        else:  # Right Wall
            # Right wall: varies in X (width) and Y (height)
            width = abs(far_bottom.x - near_bottom.x)
            height = abs(near_top.y - near_bottom.y)
        
        # Skip panels with zero dimensions
        if width == 0 or height == 0:
            return lines
        
        # Use same square grid spacing as floor
        grid_spacing = self._calculate_grid_spacing(min(width, height))
        
        # Generate horizontal lines (constant height) - same spacing as floor
        num_h_lines = int(height / grid_spacing)
        for i in range(1, num_h_lines):  # Skip boundaries
            y_pos = near_bottom.y + (i * grid_spacing)
            if y_pos >= near_top.y:
                break
            
            if panel.label == "Left Wall":
                start_3d = Point3D(near_bottom.x, y_pos, near_bottom.z)
                end_3d = Point3D(far_bottom.x, y_pos, far_bottom.z)
            else:  # Right Wall
                start_3d = Point3D(near_bottom.x, y_pos, near_bottom.z)
                end_3d = Point3D(far_bottom.x, y_pos, far_bottom.z)
            
            line = self._project_and_clip_line(
                start_3d, end_3d, view_matrix, projection_matrix,
                screen_width, screen_height, panel.label, "horizontal"
            )
            
            if line:
                lines.append(line)
        
        # Generate vertical lines - same spacing as floor
        num_v_lines = int(width / grid_spacing)
        for i in range(1, num_v_lines):  # Skip boundaries
            if panel.label == "Left Wall":
                z_pos = near_bottom.z + (i * grid_spacing)
                if z_pos >= far_bottom.z:
                    break
                start_3d = Point3D(near_bottom.x, near_bottom.y, z_pos)
                end_3d = Point3D(near_top.x, near_top.y, z_pos)
            else:  # Right Wall
                x_pos = near_bottom.x + (i * grid_spacing)
                if x_pos >= far_bottom.x:
                    break
                start_3d = Point3D(x_pos, near_bottom.y, near_bottom.z)
                end_3d = Point3D(x_pos, near_top.y, near_top.z)
            
            line = self._project_and_clip_line(
                start_3d, end_3d, view_matrix, projection_matrix,
                screen_width, screen_height, panel.label, "vertical"
            )
            
            if line:
                lines.append(line)
        
        return lines
    
    def _calculate_grid_spacing(self, dimension: float) -> float:
        """Calculate much larger grid spacing for clean, readable squares."""
        # Create much larger grid squares like the reference image
        # Base square size should be much bigger - around 24 inches for clean appearance
        base_square_size = 24.0  # Large squares for clean grid
        
        # Adjust by density (keep density effect minimal for consistency)
        square_size = base_square_size / max(0.5, self.config.density)
        
        return square_size
    
    def _clip_line_to_viewport(self, start: Point2D, end: Point2D, 
                              screen_width: int, screen_height: int) -> tuple[Point2D, Point2D] | None:
        """
        Clip a line to the viewport bounds using Cohen-Sutherland algorithm.
        
        Args:
            start: Start point of the line
            end: End point of the line
            screen_width: Width of the viewport
            screen_height: Height of the viewport
            
        Returns:
            Tuple of clipped start and end points, or None if line is completely outside
        """
        # Define viewport with margin for better visual results
        margin = max(screen_width, screen_height) * 0.5  # 50% margin
        x_min = -margin
        y_min = -margin
        x_max = screen_width + margin
        y_max = screen_height + margin
        
        # Cohen-Sutherland region codes
        def compute_code(x: float, y: float) -> int:
            code = 0
            if x < x_min:
                code |= 1  # Left
            elif x > x_max:
                code |= 2  # Right
            if y < y_min:
                code |= 4  # Bottom
            elif y > y_max:
                code |= 8  # Top
            return code
        
        x1, y1 = start.x, start.y
        x2, y2 = end.x, end.y
        
        code1 = compute_code(x1, y1)
        code2 = compute_code(x2, y2)
        
        while True:
            # Both points inside
            if code1 == 0 and code2 == 0:
                return Point2D(x1, y1), Point2D(x2, y2)
            
            # Both points in same outside region
            if code1 & code2 != 0:
                return None
            
            # At least one point outside, pick one
            code = code1 if code1 != 0 else code2
            
            # Find intersection with boundary
            if code & 8:  # Top
                x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                y = y_max
            elif code & 4:  # Bottom
                x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                y = y_min
            elif code & 2:  # Right
                y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                x = x_max
            elif code & 1:  # Left
                y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                x = x_min
            
            # Update point and code
            if code == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2)
    
    def _project_and_clip_line(self, start_3d: Point3D, end_3d: Point3D,
                              view_matrix, projection_matrix, 
                              screen_width: int, screen_height: int,
                              panel_label: str, line_type: str) -> GridLine | None:
        """
        Project a 3D line to 2D and clip to viewport, returning a GridLine or None.
        
        Args:
            start_3d: 3D start point
            end_3d: 3D end point
            view_matrix: Camera view matrix
            projection_matrix: Camera projection matrix
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            panel_label: Label for the panel this line belongs to
            line_type: Type of line ("boundary", "horizontal", "vertical")
            
        Returns:
            GridLine if line is visible after clipping, None otherwise
        """
        # Project to screen coordinates
        start_2d = project_to_screen(
            start_3d, view_matrix, projection_matrix, screen_width, screen_height
        )
        end_2d = project_to_screen(
            end_3d, view_matrix, projection_matrix, screen_width, screen_height
        )
        
        # Clip to viewport
        clipped = self._clip_line_to_viewport(start_2d, end_2d, screen_width, screen_height)
        
        if clipped:
            return GridLine(clipped[0], clipped[1], panel_label, line_type)
        return None
    
    def _calculate_line_length(self, line: GridLine) -> float:
        """Calculate the length of a line in pixels."""
        dx = line.end.x - line.start.x
        dy = line.end.y - line.start.y
        return np.sqrt(dx*dx + dy*dy)
    
    def get_grid_stats(self, lines: List[GridLine]) -> Dict[str, Any]:
        """
        Get statistics about the generated grid.
        
        Args:
            lines: List of generated grid lines
            
        Returns:
            Dictionary with grid statistics
        """
        if not lines:
            return {"total_lines": 0, "panels": {}}
        
        stats = {
            "total_lines": len(lines),
            "panels": {},
            "line_types": {"horizontal": 0, "vertical": 0, "boundary": 0}
        }
        
        # Count lines by panel and type
        for line in lines:
            panel_label = line.panel_label
            line_type = line.line_type
            
            if panel_label not in stats["panels"]:
                stats["panels"][panel_label] = 0
            
            stats["panels"][panel_label] += 1
            stats["line_types"][line_type] += 1
        
        return stats
