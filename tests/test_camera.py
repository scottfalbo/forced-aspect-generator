"""Tests for camera module."""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from perspective.camera import Camera, CameraConfig, create_standard_camera, create_orthographic_camera
from perspective.transforms import Point3D, Vector3D


class TestCameraConfig:
    """Test CameraConfig dataclass."""
    
    def test_creation(self):
        """Test CameraConfig creation with defaults."""
        config = CameraConfig(
            position=Point3D(0.0, 0.0, 5.0),
            target=Point3D(0.0, 0.0, 0.0),
            fov_degrees=50.0
        )
        
        assert config.position.z == 5.0
        assert config.target.x == 0.0
        assert config.fov_degrees == 50.0
        assert config.near_plane == 0.1
        assert config.far_plane == 100.0
        assert config.up_vector.y == 1.0  # Default up vector
    
    def test_custom_up_vector(self):
        """Test CameraConfig with custom up vector."""
        custom_up = Vector3D(1.0, 0.0, 0.0)
        config = CameraConfig(
            position=Point3D(0.0, 0.0, 5.0),
            target=Point3D(0.0, 0.0, 0.0),
            fov_degrees=50.0,
            up_vector=custom_up
        )
        
        assert config.up_vector.x == 1.0
        assert config.up_vector.y == 0.0


class TestCamera:
    """Test Camera class."""
    
    def test_creation(self):
        """Test Camera creation."""
        config = CameraConfig(
            position=Point3D(0.0, 0.0, 5.0),
            target=Point3D(0.0, 0.0, 0.0),
            fov_degrees=50.0
        )
        camera = Camera(config)
        
        assert camera.position.z == 5.0
        assert camera.target.x == 0.0
        assert camera.fov_degrees == 50.0
    
    def test_property_setters(self):
        """Test camera property setters."""
        config = CameraConfig(
            position=Point3D(0.0, 0.0, 5.0),
            target=Point3D(0.0, 0.0, 0.0),
            fov_degrees=50.0
        )
        camera = Camera(config)
        
        # Test position setter
        new_position = Point3D(1.0, 2.0, 3.0)
        camera.position = new_position
        assert camera.position.x == 1.0
        assert camera.position.y == 2.0
        assert camera.position.z == 3.0
        
        # Test target setter
        new_target = Point3D(4.0, 5.0, 6.0)
        camera.target = new_target
        assert camera.target.x == 4.0
        assert camera.target.y == 5.0
        assert camera.target.z == 6.0
        
        # Test FOV setter
        camera.fov_degrees = 60.0
        assert camera.fov_degrees == 60.0
    
    def test_fov_validation(self):
        """Test FOV validation."""
        config = CameraConfig(
            position=Point3D(0.0, 0.0, 5.0),
            target=Point3D(0.0, 0.0, 0.0),
            fov_degrees=50.0
        )
        camera = Camera(config)
        
        # Valid FOV
        camera.fov_degrees = 45.0
        assert camera.fov_degrees == 45.0
        
        # Invalid FOV - too small
        with pytest.raises(ValueError):
            camera.fov_degrees = 0.5
        
        # Invalid FOV - too large
        with pytest.raises(ValueError):
            camera.fov_degrees = 180.0
    
    def test_view_matrix_generation(self):
        """Test view matrix generation."""
        config = CameraConfig(
            position=Point3D(0.0, 0.0, 5.0),
            target=Point3D(0.0, 0.0, 0.0),
            fov_degrees=50.0
        )
        camera = Camera(config)
        
        view_matrix = camera.get_view_matrix()
        
        # Basic checks - should be a valid 4x4 matrix
        assert view_matrix.matrix.shape == (4, 4)
        
        # Transform target point - should be in front of camera in view space
        transformed_target = view_matrix.transform_point(camera.target)
        assert transformed_target.z < 0  # Negative Z in view space means in front
    
    def test_projection_matrix_generation(self):
        """Test projection matrix generation."""
        config = CameraConfig(
            position=Point3D(0.0, 0.0, 5.0),
            target=Point3D(0.0, 0.0, 0.0),
            fov_degrees=50.0
        )
        camera = Camera(config)
        
        aspect_ratio = 16.0 / 9.0
        projection_matrix = camera.get_projection_matrix(aspect_ratio)
        
        # Basic checks
        assert projection_matrix.matrix.shape == (4, 4)
        assert projection_matrix.matrix[3, 2] == -1.0  # Perspective division
    
    def test_distance_calculation(self):
        """Test distance to target calculation."""
        config = CameraConfig(
            position=Point3D(0.0, 0.0, 5.0),
            target=Point3D(0.0, 0.0, 0.0),
            fov_degrees=50.0
        )
        camera = Camera(config)
        
        distance = camera.get_distance_to_target()
        assert abs(distance - 5.0) < 1e-10
    
    def test_set_distance_to_target(self):
        """Test setting distance to target."""
        config = CameraConfig(
            position=Point3D(0.0, 0.0, 5.0),
            target=Point3D(0.0, 0.0, 0.0),
            fov_degrees=50.0
        )
        camera = Camera(config)
        
        # Set new distance
        camera.set_distance_to_target(10.0)
        
        # Check new distance
        new_distance = camera.get_distance_to_target()
        assert abs(new_distance - 10.0) < 1e-10
        
        # Check that direction is maintained (still on Z axis)
        assert abs(camera.position.x) < 1e-10
        assert abs(camera.position.y) < 1e-10
        assert camera.position.z == 10.0
    
    def test_set_distance_validation(self):
        """Test distance setting validation."""
        config = CameraConfig(
            position=Point3D(0.0, 0.0, 5.0),
            target=Point3D(0.0, 0.0, 0.0),
            fov_degrees=50.0
        )
        camera = Camera(config)
        
        # Invalid distance
        with pytest.raises(ValueError):
            camera.set_distance_to_target(-1.0)
        
        with pytest.raises(ValueError):
            camera.set_distance_to_target(0.0)
    
    def test_orbit_around_target(self):
        """Test orbital positioning around target."""
        config = CameraConfig(
            position=Point3D(0.0, 0.0, 5.0),
            target=Point3D(0.0, 0.0, 0.0),
            fov_degrees=50.0
        )
        camera = Camera(config)
        
        # Orbit to 90 degrees azimuth (should be on X axis)
        camera.orbit_around_target(90.0, 0.0, 5.0)
        
        assert abs(camera.position.x - 5.0) < 1e-10
        assert abs(camera.position.y) < 1e-10
        assert abs(camera.position.z) < 1e-10
        
        # Check distance is maintained
        distance = camera.get_distance_to_target()
        assert abs(distance - 5.0) < 1e-10
    
    def test_orbit_validation(self):
        """Test orbit parameter validation."""
        config = CameraConfig(
            position=Point3D(0.0, 0.0, 5.0),
            target=Point3D(0.0, 0.0, 0.0),
            fov_degrees=50.0
        )
        camera = Camera(config)
        
        # Invalid distance
        with pytest.raises(ValueError):
            camera.orbit_around_target(0.0, 0.0, -1.0)


class TestCameraFactories:
    """Test camera factory functions."""
    
    def test_create_standard_camera(self):
        """Test standard camera creation."""
        camera = create_standard_camera(distance=10.0, fov_degrees=60.0)
        
        assert camera.get_distance_to_target() == 10.0
        assert camera.fov_degrees == 60.0
        assert camera.position.y == 4.0  # Slightly elevated
        assert camera.target.x == 0.0
        assert camera.target.y == 0.0
        assert camera.target.z == 0.0
    
    def test_create_orthographic_camera(self):
        """Test orthographic camera creation."""
        camera = create_orthographic_camera(distance=12.0)
        
        assert camera.get_distance_to_target() == 12.0
        assert camera.fov_degrees == 1.0  # Very narrow for orthographic approximation
        assert camera.position.y == 4.0
        assert camera.config.far_plane == 24.0  # 2 * distance


class TestCameraMatrixUpdates:
    """Test camera matrix update behavior."""
    
    def test_matrix_caching(self):
        """Test that matrices are cached until camera changes."""
        config = CameraConfig(
            position=Point3D(0.0, 0.0, 5.0),
            target=Point3D(0.0, 0.0, 0.0),
            fov_degrees=50.0
        )
        camera = Camera(config)
        
        # Get matrices twice - should be the same object (cached)
        view1 = camera.get_view_matrix()
        view2 = camera.get_view_matrix()
        
        # Should be the same cached matrix
        assert view1 is view2
        
        # Change camera position - should trigger update
        camera.position = Point3D(1.0, 0.0, 5.0)
        view3 = camera.get_view_matrix()
        
        # Should be a new matrix
        assert view1 is not view3


if __name__ == "__main__":
    # Run tests if executed directly
    import subprocess
    subprocess.run(["python", "-m", "pytest", __file__, "-v"])
