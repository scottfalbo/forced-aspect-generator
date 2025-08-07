"""Tests for grid generation and SVG rendering."""

import pytest
import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from perspective.grid_generator import GridGenerator, GridConfig, GridLine
from perspective.camera import create_standard_camera
from perspective.transforms import Point2D
from layouts.three_panel import ThreePanelLayout, create_standard_3panel_config
from rendering.svg_renderer import SVGRenderer, SVGConfig, create_standard_svg_config


class TestGridGenerator:
    """Test GridGenerator class."""
    
    def test_creation(self):
        """Test GridGenerator creation."""
        config = GridConfig(density=0.5)
        generator = GridGenerator(config)
        
        assert generator.config.density == 0.5
        assert generator.config.show_panel_boundaries == True
        assert generator.config.show_panel_labels == True
    
    def test_default_config(self):
        """Test GridGenerator with default config."""
        generator = GridGenerator()
        
        assert generator.config.density == 0.5
        assert generator.config.min_line_length == 5.0
    
    def test_grid_generation(self):
        """Test basic grid generation."""
        # Create test layout and camera
        layout_config = create_standard_3panel_config()
        layout = ThreePanelLayout(layout_config)
        panels = layout.get_panels()
        
        camera = create_standard_camera(distance=10.0, fov_degrees=50.0)
        
        # Generate grid
        generator = GridGenerator()
        grid_lines = generator.generate_grid(panels, camera, 800, 600)
        
        # Should have generated some lines
        assert len(grid_lines) > 0
        
        # All lines should be GridLine objects
        assert all(isinstance(line, GridLine) for line in grid_lines)
        
        # Should have lines for all panels
        panel_labels = set(line.panel_label for line in grid_lines)
        expected_labels = {"Floor", "Left Wall", "Right Wall"}
        assert expected_labels.issubset(panel_labels)
    
    def test_grid_line_types(self):
        """Test that different line types are generated."""
        layout_config = create_standard_3panel_config()
        layout = ThreePanelLayout(layout_config)
        panels = layout.get_panels()
        
        camera = create_standard_camera(distance=10.0, fov_degrees=50.0)
        
        generator = GridGenerator()
        grid_lines = generator.generate_grid(panels, camera, 800, 600)
        
        # Should have boundary lines
        boundary_lines = [line for line in grid_lines if line.line_type == "boundary"]
        assert len(boundary_lines) > 0
        
        # Should have interior lines
        interior_lines = [line for line in grid_lines if line.line_type in ["horizontal", "vertical"]]
        assert len(interior_lines) > 0
    
    def test_density_affects_grid(self):
        """Test that density setting affects number of lines."""
        layout_config = create_standard_3panel_config()
        layout = ThreePanelLayout(layout_config)
        panels = layout.get_panels()
        
        camera = create_standard_camera(distance=10.0, fov_degrees=50.0)
        
        # Generate with fine density
        fine_generator = GridGenerator(GridConfig(density=1.0))
        fine_lines = fine_generator.generate_grid(panels, camera, 800, 600)
        
        # Generate with coarse density
        coarse_generator = GridGenerator(GridConfig(density=0.2))
        coarse_lines = coarse_generator.generate_grid(panels, camera, 800, 600)
        
        # Fine density should generate more lines
        assert len(fine_lines) > len(coarse_lines)
    
    def test_line_length_filtering(self):
        """Test that very short lines are filtered out."""
        layout_config = create_standard_3panel_config()
        layout = ThreePanelLayout(layout_config)
        panels = layout.get_panels()
        
        camera = create_standard_camera(distance=10.0, fov_degrees=50.0)
        
        # Use a high minimum line length
        config = GridConfig(min_line_length=50.0)
        generator = GridGenerator(config)
        grid_lines = generator.generate_grid(panels, camera, 800, 600)
        
        # All lines should meet minimum length requirement
        for line in grid_lines:
            dx = line.end.x - line.start.x
            dy = line.end.y - line.start.y
            length = (dx*dx + dy*dy)**0.5
            assert length >= config.min_line_length
    
    def test_grid_stats(self):
        """Test grid statistics generation."""
        layout_config = create_standard_3panel_config()
        layout = ThreePanelLayout(layout_config)
        panels = layout.get_panels()
        
        camera = create_standard_camera(distance=10.0, fov_degrees=50.0)
        
        generator = GridGenerator()
        grid_lines = generator.generate_grid(panels, camera, 800, 600)
        stats = generator.get_grid_stats(grid_lines)
        
        # Should have basic statistics
        assert "total_lines" in stats
        assert "panels" in stats
        assert "line_types" in stats
        
        assert stats["total_lines"] == len(grid_lines)
        assert len(stats["panels"]) > 0
        assert stats["line_types"]["boundary"] >= 0
        assert stats["line_types"]["horizontal"] >= 0
        assert stats["line_types"]["vertical"] >= 0


class TestSVGRenderer:
    """Test SVGRenderer class."""
    
    def test_creation(self):
        """Test SVGRenderer creation."""
        config = SVGConfig(width=800, height=600)
        renderer = SVGRenderer(config)
        
        assert renderer.config.width == 800
        assert renderer.config.height == 600
    
    def test_default_config(self):
        """Test SVGRenderer with default config."""
        renderer = SVGRenderer()
        
        assert renderer.config.width == 1920
        assert renderer.config.height == 1080
        assert renderer.config.show_labels == True
    
    def test_svg_rendering(self):
        """Test basic SVG file generation."""
        # Generate some test grid lines
        layout_config = create_standard_3panel_config()
        layout = ThreePanelLayout(layout_config)
        panels = layout.get_panels()
        
        camera = create_standard_camera(distance=10.0, fov_degrees=50.0)
        
        generator = GridGenerator()
        grid_lines = generator.generate_grid(panels, camera, 800, 600)
        
        # Render to SVG
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_grid.svg"
            
            renderer = SVGRenderer()
            success = renderer.render(grid_lines, str(output_path), "Test Grid")
            
            assert success == True
            assert output_path.exists()
            
            # Check file content
            svg_content = output_path.read_text()
            assert '<?xml version="1.0" encoding="UTF-8"?>' in svg_content
            assert '<svg xmlns="http://www.w3.org/2000/svg"' in svg_content
            assert '<title>Test Grid</title>' in svg_content
            assert '<line' in svg_content  # Should have line elements
    
    def test_svg_structure(self):
        """Test SVG file structure and organization."""
        # Create minimal test data
        test_lines = [
            GridLine(Point2D(0, 0), Point2D(100, 0), "Floor", "boundary"),
            GridLine(Point2D(0, 0), Point2D(0, 100), "Floor", "boundary"),
            GridLine(Point2D(50, 0), Point2D(50, 100), "Floor", "vertical"),
            GridLine(Point2D(0, 50), Point2D(100, 50), "Floor", "horizontal")
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "structure_test.svg"
            
            renderer = SVGRenderer()
            success = renderer.render(test_lines, str(output_path), "Structure Test")
            
            assert success == True
            
            svg_content = output_path.read_text()
            
            # Should have organized groups
            assert 'id="panel-boundaries"' in svg_content
            assert 'id="grid-lines"' in svg_content
            assert 'class="horizontal-lines"' in svg_content
            assert 'class="vertical-lines"' in svg_content
    
    def test_label_generation(self):
        """Test panel label generation."""
        test_lines = [
            GridLine(Point2D(0, 0), Point2D(100, 0), "Test Panel", "boundary"),
            GridLine(Point2D(100, 0), Point2D(100, 100), "Test Panel", "boundary"),
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "labels_test.svg"
            
            config = SVGConfig(show_labels=True)
            renderer = SVGRenderer(config)
            success = renderer.render(test_lines, str(output_path), "Labels Test")
            
            assert success == True
            
            svg_content = output_path.read_text()
            
            # Should have labels group and text element
            assert 'id="panel-labels"' in svg_content
            assert '<text' in svg_content
            assert 'Test Panel' in svg_content
    
    def test_no_labels(self):
        """Test SVG generation without labels."""
        test_lines = [
            GridLine(Point2D(0, 0), Point2D(100, 0), "Test Panel", "boundary")
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "no_labels_test.svg"
            
            config = SVGConfig(show_labels=False)
            renderer = SVGRenderer(config)
            success = renderer.render(test_lines, str(output_path), "No Labels Test")
            
            assert success == True
            
            svg_content = output_path.read_text()
            
            # Should not have labels
            assert 'id="panel-labels"' not in svg_content
            assert '<text' not in svg_content
    
    def test_file_size_estimation(self):
        """Test SVG file size estimation."""
        test_lines = [
            GridLine(Point2D(0, 0), Point2D(100, 0), "Panel1", "boundary"),
            GridLine(Point2D(0, 0), Point2D(100, 0), "Panel2", "horizontal"),
        ]
        
        renderer = SVGRenderer()
        estimated_size = renderer.get_file_size_estimate(test_lines)
        
        # Should be a reasonable estimate
        assert estimated_size > 1000  # At least 1KB
        assert estimated_size < 100000  # Less than 100KB for small grid


class TestSVGConfigFactory:
    """Test SVG configuration factory."""
    
    def test_standard_config(self):
        """Test standard SVG config creation."""
        config = create_standard_svg_config()
        
        assert config.width == 1920
        assert config.height == 1080
        assert config.background_color == "#ffffff"
        assert config.show_labels == True
        assert config.grid_style.stroke_color == "#666666"
        assert config.boundary_style.stroke_color == "#000000"
    
    def test_custom_dimensions(self):
        """Test standard config with custom dimensions."""
        config = create_standard_svg_config(800, 600)
        
        assert config.width == 800
        assert config.height == 600


class TestIntegration:
    """Integration tests for grid generation and SVG rendering."""
    
    def test_full_pipeline(self):
        """Test complete pipeline from layout to SVG file."""
        # Create layout
        layout_config = create_standard_3panel_config("standard", "standard")
        layout = ThreePanelLayout(layout_config)
        
        # Create camera
        camera = create_standard_camera(distance=12.0, fov_degrees=45.0)
        
        # Generate grid
        grid_config = GridConfig(density=0.8, show_panel_boundaries=True)
        generator = GridGenerator(grid_config)
        grid_lines = generator.generate_grid(layout.get_panels(), camera, 1920, 1080)
        
        # Render SVG
        svg_config = create_standard_svg_config(1920, 1080)
        renderer = SVGRenderer(svg_config)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "integration_test.svg"
            
            success = renderer.render(
                grid_lines, 
                str(output_path), 
                "Integration Test - 3-Panel Corner Room"
            )
            
            assert success == True
            assert output_path.exists()
            
            # Verify file has content
            file_size = output_path.stat().st_size
            assert file_size > 2000  # Should be substantial file
            
            # Get grid statistics
            stats = generator.get_grid_stats(grid_lines)
            assert stats["total_lines"] > 20  # Should have many lines
            assert len(stats["panels"]) == 3  # Three panels
            
            # Verify SVG content structure
            svg_content = output_path.read_text()
            assert "3-Panel Corner Room" in svg_content
            assert "Floor" in svg_content
            assert "Wall" in svg_content


if __name__ == "__main__":
    # Run tests if executed directly
    import subprocess
    subprocess.run(["python", "-m", "pytest", __file__, "-v"])
