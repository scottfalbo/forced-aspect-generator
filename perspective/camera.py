"""
Camera controls for perspective projection.

This module handles camera positioning, field of view, and view matrix generation.
"""

import numpy as np
from typing import Optional
from dataclasses import dataclass
from .transforms import Point3D, Vector3D, Matrix4x4, degrees_to_radians


@dataclass
class CameraConfig:
    """Configuration for camera parameters."""
    position: Point3D
    target: Point3D
    fov_degrees: float
    near_plane: float = 0.1
    far_plane: float = 100.0
    up_vector: Vector3D = None
    
    def __post_init__(self):
        """Set default up vector if not provided."""
        if self.up_vector is None:
            self.up_vector = Vector3D(0.0, 1.0, 0.0)


class Camera:
    """Camera for 3D to 2D perspective projection."""
    
    def __init__(self, config: CameraConfig):
        """
        Initialize camera with given configuration.
        
        Args:
            config: Camera configuration parameters
        """
        self.config = config
        self._view_matrix = None
        self._projection_matrix = None
        self._needs_update = True
    
    @property
    def position(self) -> Point3D:
        """Get camera position."""
        return self.config.position
    
    @position.setter
    def position(self, value: Point3D):
        """Set camera position."""
        self.config.position = value
        self._needs_update = True
    
    @property
    def target(self) -> Point3D:
        """Get camera target."""
        return self.config.target
    
    @target.setter
    def target(self, value: Point3D):
        """Set camera target."""
        self.config.target = value
        self._needs_update = True
    
    @property
    def fov_degrees(self) -> float:
        """Get field of view in degrees."""
        return self.config.fov_degrees
    
    @fov_degrees.setter
    def fov_degrees(self, value: float):
        """Set field of view in degrees."""
        if not 1 <= value <= 179:
            raise ValueError("FOV must be between 1 and 179 degrees")
        self.config.fov_degrees = value
        self._needs_update = True
    
    def get_view_matrix(self) -> Matrix4x4:
        """Get the view transformation matrix."""
        if self._needs_update or self._view_matrix is None:
            self._update_matrices()
        return self._view_matrix
    
    def get_projection_matrix(self, aspect_ratio: float) -> Matrix4x4:
        """
        Get the projection transformation matrix.
        
        Args:
            aspect_ratio: Screen width / height ratio
            
        Returns:
            Perspective projection matrix
        """
        if self._needs_update or self._projection_matrix is None:
            self._update_matrices(aspect_ratio)
        return self._projection_matrix
    
    def _update_matrices(self, aspect_ratio: float = 1.0):
        """Update view and projection matrices."""
        # Create view matrix using look-at
        self._view_matrix = Matrix4x4.look_at(
            self.config.position,
            self.config.target,
            self.config.up_vector
        )
        
        # Create projection matrix
        fov_radians = degrees_to_radians(self.config.fov_degrees)
        self._projection_matrix = Matrix4x4.perspective(
            fov_radians,
            aspect_ratio,
            self.config.near_plane,
            self.config.far_plane
        )
        
        self._needs_update = False
    
    def get_distance_to_target(self) -> float:
        """Get distance from camera to target."""
        dx = self.config.target.x - self.config.position.x
        dy = self.config.target.y - self.config.position.y
        dz = self.config.target.z - self.config.position.z
        return np.sqrt(dx*dx + dy*dy + dz*dz)
    
    def set_distance_to_target(self, distance: float):
        """
        Set camera distance to target while maintaining direction.
        
        Args:
            distance: New distance to target
        """
        if distance <= 0:
            raise ValueError("Distance must be positive")
        
        # Calculate current direction vector
        current_distance = self.get_distance_to_target()
        if current_distance == 0:
            raise ValueError("Camera and target cannot be at the same position")
        
        # Calculate unit direction vector from target to camera
        direction = Vector3D(
            (self.config.position.x - self.config.target.x) / current_distance,
            (self.config.position.y - self.config.target.y) / current_distance,
            (self.config.position.z - self.config.target.z) / current_distance
        )
        
        # Set new position
        self.position = Point3D(
            self.config.target.x + direction.x * distance,
            self.config.target.y + direction.y * distance,
            self.config.target.z + direction.z * distance
        )
    
    def orbit_around_target(self, azimuth_degrees: float, elevation_degrees: float, distance: float):
        """
        Position camera in spherical coordinates around target.
        
        Args:
            azimuth_degrees: Horizontal rotation (0° = +X axis)
            elevation_degrees: Vertical rotation (0° = XZ plane, 90° = +Y axis)
            distance: Distance from target
        """
        if distance <= 0:
            raise ValueError("Distance must be positive")
        
        azimuth_rad = degrees_to_radians(azimuth_degrees)
        elevation_rad = degrees_to_radians(elevation_degrees)
        
        # Convert spherical to cartesian coordinates
        x = distance * np.cos(elevation_rad) * np.cos(azimuth_rad)
        y = distance * np.sin(elevation_rad)
        z = distance * np.cos(elevation_rad) * np.sin(azimuth_rad)
        
        # Position relative to target
        self.position = Point3D(
            self.config.target.x + x,
            self.config.target.y + y,
            self.config.target.z + z
        )


def create_standard_camera(distance: float = 8.0, fov_degrees: float = 50.0) -> Camera:
    """
    Create a standard camera setup for forced perspective grids.
    
    Args:
        distance: Distance from target (in same units as scene)
        fov_degrees: Field of view in degrees
        
    Returns:
        Configured camera instance
    """
    config = CameraConfig(
        position=Point3D(0.0, 4.0, distance),  # Slightly above and behind
        target=Point3D(0.0, 0.0, 0.0),         # Looking at origin
        fov_degrees=fov_degrees
    )
    return Camera(config)


def create_orthographic_camera(distance: float = 8.0) -> Camera:
    """
    Create a camera for orthographic (parallel) projection.
    
    Args:
        distance: Distance from target
        
    Returns:
        Camera configured for orthographic projection
    """
    config = CameraConfig(
        position=Point3D(0.0, 4.0, distance),
        target=Point3D(0.0, 0.0, 0.0),
        fov_degrees=1.0,  # Very narrow FOV approximates orthographic
        near_plane=0.1,
        far_plane=distance * 2
    )
    return Camera(config)
