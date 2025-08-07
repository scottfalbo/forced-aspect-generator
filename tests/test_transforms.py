"""Tests for perspective transforms module."""

import pytest
import numpy as np
from perspective.transforms import (
    Point3D, Point2D, Vector3D, Matrix4x4, 
    project_to_screen, degrees_to_radians, radians_to_degrees
)


class TestPoint3D:
    """Test Point3D class."""
    
    def test_creation(self):
        """Test Point3D creation."""
        point = Point3D(1.0, 2.0, 3.0)
        assert point.x == 1.0
        assert point.y == 2.0
        assert point.z == 3.0
    
    def test_to_array(self):
        """Test conversion to numpy array."""
        point = Point3D(1.0, 2.0, 3.0)
        array = point.to_array()
        expected = np.array([1.0, 2.0, 3.0, 1.0])
        np.testing.assert_array_equal(array, expected)
    
    def test_from_array(self):
        """Test creation from numpy array."""
        array = np.array([1.0, 2.0, 3.0, 1.0])
        point = Point3D.from_array(array)
        assert point.x == 1.0
        assert point.y == 2.0
        assert point.z == 3.0


class TestPoint2D:
    """Test Point2D class."""
    
    def test_creation(self):
        """Test Point2D creation."""
        point = Point2D(10.0, 20.0)
        assert point.x == 10.0
        assert point.y == 20.0


class TestVector3D:
    """Test Vector3D class."""
    
    def test_creation(self):
        """Test Vector3D creation."""
        vector = Vector3D(1.0, 0.0, 0.0)
        assert vector.x == 1.0
        assert vector.y == 0.0
        assert vector.z == 0.0
    
    def test_normalize(self):
        """Test vector normalization."""
        vector = Vector3D(3.0, 4.0, 0.0)
        normalized = vector.normalize()
        assert abs(normalized.x - 0.6) < 1e-10
        assert abs(normalized.y - 0.8) < 1e-10
        assert abs(normalized.z - 0.0) < 1e-10
    
    def test_normalize_zero_vector(self):
        """Test normalization of zero vector."""
        vector = Vector3D(0.0, 0.0, 0.0)
        normalized = vector.normalize()
        assert normalized.x == 0.0
        assert normalized.y == 0.0
        assert normalized.z == 0.0
    
    def test_cross_product(self):
        """Test cross product."""
        v1 = Vector3D(1.0, 0.0, 0.0)
        v2 = Vector3D(0.0, 1.0, 0.0)
        cross = v1.cross(v2)
        assert cross.x == 0.0
        assert cross.y == 0.0
        assert cross.z == 1.0
    
    def test_dot_product(self):
        """Test dot product."""
        v1 = Vector3D(1.0, 2.0, 3.0)
        v2 = Vector3D(4.0, 5.0, 6.0)
        dot = v1.dot(v2)
        assert dot == 32.0  # 1*4 + 2*5 + 3*6


class TestMatrix4x4:
    """Test Matrix4x4 class."""
    
    def test_identity(self):
        """Test identity matrix creation."""
        matrix = Matrix4x4.identity()
        expected = np.eye(4)
        np.testing.assert_array_equal(matrix.matrix, expected)
    
    def test_translation(self):
        """Test translation matrix."""
        matrix = Matrix4x4.translation(1.0, 2.0, 3.0)
        point = Point3D(0.0, 0.0, 0.0)
        transformed = matrix.transform_point(point)
        assert transformed.x == 1.0
        assert transformed.y == 2.0
        assert transformed.z == 3.0
    
    def test_rotation_y(self):
        """Test rotation around Y axis."""
        # 90 degree rotation
        matrix = Matrix4x4.rotation_y(np.pi / 2)
        point = Point3D(1.0, 0.0, 0.0)
        transformed = matrix.transform_point(point)
        
        # After 90° Y rotation, X becomes Z
        assert abs(transformed.x) < 1e-10  # Should be ~0
        assert abs(transformed.y) < 1e-10  # Should be ~0
        assert abs(transformed.z - 1.0) < 1e-10  # Should be ~1
    
    def test_perspective_matrix(self):
        """Test perspective projection matrix creation."""
        fov = np.pi / 4  # 45 degrees
        aspect = 16.0 / 9.0
        near = 0.1
        far = 100.0
        
        matrix = Matrix4x4.perspective(fov, aspect, near, far)
        
        # Basic checks - perspective matrix should have specific structure
        assert matrix.matrix[3, 2] == -1.0  # Perspective division component
        assert matrix.matrix[2, 3] != 0.0   # Z translation component
    
    def test_look_at(self):
        """Test look-at matrix creation."""
        eye = Point3D(0.0, 0.0, 5.0)
        target = Point3D(0.0, 0.0, 0.0)
        up = Vector3D(0.0, 1.0, 0.0)
        
        matrix = Matrix4x4.look_at(eye, target, up)
        
        # Transform the target point - should be at origin in view space
        view_target = matrix.transform_point(target)
        assert abs(view_target.x) < 1e-10
        assert abs(view_target.y) < 1e-10
        assert abs(view_target.z - (-5.0)) < 1e-10  # Should be -5 in view space
    
    def test_matrix_multiplication(self):
        """Test matrix multiplication."""
        # Translation then rotation
        translation = Matrix4x4.translation(1.0, 0.0, 0.0)
        rotation = Matrix4x4.rotation_y(np.pi / 2)
        
        combined = rotation.multiply(translation)
        
        point = Point3D(0.0, 0.0, 0.0)
        result = combined.transform_point(point)
        
        # Point at origin, translated by (1,0,0), then rotated 90° around Y
        # Should end up at (0,0,1)
        assert abs(result.x) < 1e-10
        assert abs(result.y) < 1e-10
        assert abs(result.z - 1.0) < 1e-10


class TestProjection:
    """Test projection functions."""
    
    def test_project_to_screen(self):
        """Test 3D to 2D projection."""
        # Simple case: point at origin, camera looking down negative Z
        point_3d = Point3D(0.0, 0.0, -1.0)
        
        # Identity view matrix (camera at origin)
        view_matrix = Matrix4x4.identity()
        
        # Simple perspective matrix
        projection_matrix = Matrix4x4.perspective(np.pi/4, 1.0, 0.1, 100.0)
        
        screen_width = 800
        screen_height = 600
        
        point_2d = project_to_screen(
            point_3d, view_matrix, projection_matrix, screen_width, screen_height
        )
        
        # Point should project to center of screen
        assert abs(point_2d.x - screen_width/2) < 1.0
        assert abs(point_2d.y - screen_height/2) < 1.0
    
    def test_degrees_to_radians(self):
        """Test degree to radian conversion."""
        assert abs(degrees_to_radians(180.0) - np.pi) < 1e-10
        assert abs(degrees_to_radians(90.0) - np.pi/2) < 1e-10
        assert abs(degrees_to_radians(0.0)) < 1e-10
    
    def test_radians_to_degrees(self):
        """Test radian to degree conversion."""
        assert abs(radians_to_degrees(np.pi) - 180.0) < 1e-10
        assert abs(radians_to_degrees(np.pi/2) - 90.0) < 1e-10
        assert abs(radians_to_degrees(0.0)) < 1e-10


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_transform_point_with_perspective_division(self):
        """Test point transformation with perspective division."""
        # Create a matrix that will result in w != 1
        matrix = Matrix4x4.perspective(np.pi/4, 1.0, 0.1, 100.0)
        point = Point3D(1.0, 1.0, -2.0)
        
        # Should not raise exception and should handle perspective division
        transformed = matrix.transform_point(point)
        
        # Result should be valid numbers
        assert not np.isnan(transformed.x)
        assert not np.isnan(transformed.y)
        assert not np.isnan(transformed.z)


if __name__ == "__main__":
    pytest.main([__file__])
