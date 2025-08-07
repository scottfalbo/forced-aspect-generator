"""
3D transformations and coordinate system utilities.

This module handles the mathematical foundations for 3D to 2D perspective projection.
"""

import numpy as np
from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class Point3D:
    """Represents a point in 3D space."""
    x: float
    y: float
    z: float
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for calculations."""
        return np.array([self.x, self.y, self.z, 1.0])
    
    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'Point3D':
        """Create Point3D from numpy array."""
        return cls(arr[0], arr[1], arr[2])


@dataclass
class Point2D:
    """Represents a point in 2D screen space."""
    x: float
    y: float


@dataclass
class Vector3D:
    """Represents a 3D vector."""
    x: float
    y: float
    z: float
    
    def normalize(self) -> 'Vector3D':
        """Return normalized vector."""
        length = np.sqrt(self.x**2 + self.y**2 + self.z**2)
        if length == 0:
            return Vector3D(0, 0, 0)
        return Vector3D(self.x/length, self.y/length, self.z/length)
    
    def cross(self, other: 'Vector3D') -> 'Vector3D':
        """Cross product with another vector."""
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def dot(self, other: 'Vector3D') -> float:
        """Dot product with another vector."""
        return self.x * other.x + self.y * other.y + self.z * other.z


class Matrix4x4:
    """4x4 transformation matrix for 3D operations."""
    
    def __init__(self, matrix: np.ndarray = None):
        """Initialize with identity matrix if none provided."""
        if matrix is None:
            self.matrix = np.eye(4)
        else:
            self.matrix = matrix.copy()
    
    @classmethod
    def identity(cls) -> 'Matrix4x4':
        """Create identity matrix."""
        return cls()
    
    @classmethod
    def translation(cls, x: float, y: float, z: float) -> 'Matrix4x4':
        """Create translation matrix."""
        matrix = np.eye(4)
        matrix[0, 3] = x
        matrix[1, 3] = y
        matrix[2, 3] = z
        return cls(matrix)
    
    @classmethod
    def rotation_y(cls, angle_radians: float) -> 'Matrix4x4':
        """Create rotation matrix around Y axis."""
        cos_a = np.cos(angle_radians)
        sin_a = np.sin(angle_radians)
        matrix = np.array([
            [cos_a, 0, sin_a, 0],
            [0, 1, 0, 0],
            [-sin_a, 0, cos_a, 0],
            [0, 0, 0, 1]
        ])
        return cls(matrix)
    
    @classmethod
    def perspective(cls, fov_radians: float, aspect_ratio: float, near: float, far: float) -> 'Matrix4x4':
        """Create perspective projection matrix."""
        f = 1.0 / np.tan(fov_radians / 2.0)
        matrix = np.array([
            [f / aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
            [0, 0, -1, 0]
        ])
        return cls(matrix)
    
    @classmethod
    def look_at(cls, eye: Point3D, target: Point3D, up: Vector3D) -> 'Matrix4x4':
        """Create view matrix using look-at parameters."""
        # Calculate camera coordinate system
        forward = Vector3D(
            target.x - eye.x,
            target.y - eye.y,
            target.z - eye.z
        ).normalize()
        
        right = forward.cross(up).normalize()
        camera_up = right.cross(forward)
        
        # Create view matrix
        matrix = np.array([
            [right.x, camera_up.x, -forward.x, 0],
            [right.y, camera_up.y, -forward.y, 0],
            [right.z, camera_up.z, -forward.z, 0],
            [0, 0, 0, 1]
        ])
        
        # Apply translation
        translation = cls.translation(-eye.x, -eye.y, -eye.z)
        return cls(matrix @ translation.matrix)
    
    def multiply(self, other: 'Matrix4x4') -> 'Matrix4x4':
        """Multiply with another matrix."""
        return Matrix4x4(self.matrix @ other.matrix)
    
    def transform_point(self, point: Point3D) -> Point3D:
        """Transform a 3D point."""
        point_array = point.to_array()
        transformed = self.matrix @ point_array
        
        # Handle perspective division
        if transformed[3] != 0:
            transformed = transformed / transformed[3]
        
        return Point3D.from_array(transformed)


def project_to_screen(point_3d: Point3D, view_matrix: Matrix4x4, 
                     projection_matrix: Matrix4x4, screen_width: int, 
                     screen_height: int) -> Point2D:
    """
    Project a 3D point to 2D screen coordinates.
    
    Args:
        point_3d: 3D point to project
        view_matrix: Camera view transformation matrix
        projection_matrix: Perspective projection matrix
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels
    
    Returns:
        2D screen coordinates
    """
    # Transform to view space
    view_point = view_matrix.transform_point(point_3d)
    
    # Transform to clip space
    clip_point = projection_matrix.transform_point(view_point)
    
    # Convert normalized device coordinates to screen coordinates
    screen_x = (clip_point.x + 1.0) * 0.5 * screen_width
    screen_y = (1.0 - clip_point.y) * 0.5 * screen_height  # Flip Y axis
    
    return Point2D(screen_x, screen_y)


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * np.pi / 180.0


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180.0 / np.pi
