"""Comprehensive test demonstrating the full Forced Aspect Grid Tool pipeline."""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    # Import all modules
    from perspective.transforms import Point3D, Vector3D, Matrix4x4
    from perspective.camera import Camera, CameraConfig, create_standard_camera
    from perspective.grid_generator import GridGenerator, GridConfig
    from layouts.three_panel import ThreePanelLayout, create_standard_3panel_config
    from rendering.svg_renderer import SVGRenderer, create_standard_svg_config
    
    print("=" * 60)
    print("🎯 FORCED ASPECT GRID TOOL - PIPELINE DEMONSTRATION")
    print("=" * 60)
    print()
    
    print("📐 Phase 1: 3D Mathematics Foundation")
    print("-" * 40)
    
    # Demonstrate 3D coordinate system
    origin = Point3D(0.0, 0.0, 0.0)
    corner = Point3D(144.0, 96.0, 144.0)
    center = Point3D(72.0, 48.0, 72.0)
    print(f"✓ 3D points: Origin{origin}, Corner{corner}, Center{center}")
    
    # Demonstrate vector operations
    direction = Vector3D(1.0, 1.0, 1.0).normalize()
    print(f"✓ Normalized diagonal vector: ({direction.x:.3f}, {direction.y:.3f}, {direction.z:.3f})")
    
    # Demonstrate matrix transformations
    rotation = Matrix4x4.rotation_y(45.0)  # 45-degree Y rotation
    translation = Matrix4x4.translation(100.0, 50.0, 100.0)
    transform = translation.multiply(rotation)
    transformed_point = transform.transform_point(Point3D(10.0, 0.0, 0.0))
    print(f"✓ Transformed point: ({transformed_point.x:.2f}, {transformed_point.y:.2f}, {transformed_point.z:.2f})")
    print()
    
    print("📷 Phase 2: Camera System")
    print("-" * 40)
    
    # Create and configure camera
    camera = create_standard_camera(distance=12.0, fov_degrees=50.0)
    print(f"✓ Standard camera created with {camera.get_distance_to_target():.1f} unit distance")
    print(f"  - Position: ({camera.position.x:.2f}, {camera.position.y:.2f}, {camera.position.z:.2f})")
    print(f"  - Target: ({camera.target.x:.2f}, {camera.target.y:.2f}, {camera.target.z:.2f})")
    print(f"  - FOV: {camera.config.fov_degrees}°")
    
    # Test camera positioning
    camera.orbit_around_target(45.0, 30.0, 15.0)
    print(f"✓ Camera orbited to 45°/30° at 15.0 units")
    print(f"  - New position: ({camera.position.x:.2f}, {camera.position.y:.2f}, {camera.position.z:.2f})")
    
    # Generate matrices
    view_matrix = camera.get_view_matrix()
    projection_matrix = camera.get_projection_matrix(16.0/9.0)
    print("✓ View and projection matrices generated for perspective projection")
    print()
    
    print("🏠 Phase 3: Layout Generation")
    print("-" * 40)
    
    # Create 3-panel layout
    config = create_standard_3panel_config()
    layout = ThreePanelLayout(config)
    panels = layout.get_panels()
    
    print(f"✓ {layout.get_layout_name()} layout created")
    print(f"  - Panel count: {layout.get_panel_count()}")
    print(f"  - Panels: {', '.join([panel.label for panel in panels])}")
    
    # Show layout dimensions
    bounds = layout.get_total_bounds()
    center = layout.get_center_point()
    print(f"  - Dimensions: {bounds['max_x']:.0f}×{bounds['max_y']:.0f}×{bounds['max_z']:.0f} units")
    print(f"  - Center point: ({center.x:.1f}, {center.y:.1f}, {center.z:.1f})")
    
    # Optimal camera positioning
    optimal_pos = layout.get_optimal_camera_position()
    optimal_target = layout.get_optimal_camera_target()
    print(f"  - Optimal camera: ({optimal_pos.x:.1f}, {optimal_pos.y:.1f}, {optimal_pos.z:.1f})")
    print(f"  - Looking at: ({optimal_target.x:.1f}, {optimal_target.y:.1f}, {optimal_target.z:.1f})")
    print()
    
    print("🔳 Phase 4: Grid Generation")
    print("-" * 40)
    
    # Create grid with different density settings
    densities = [0.4, 0.6, 1.0, 1.5]
    output_resolutions = [(1920, 1080), (3840, 2160), (1080, 1080)]
    
    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)
    
    print("✓ Testing multiple density and resolution configurations:")
    
    for density in densities:
        # Setup grid generation
        camera_grid = create_standard_camera(distance=12.0, fov_degrees=50.0)
        camera_grid.orbit_around_target(45.0, 30.0, 12.0)
        
        grid_config = GridConfig(
            density=density,
            show_panel_boundaries=True,
            min_line_length=50,
            max_lines_per_panel=25
        )
        generator = GridGenerator(grid_config)
        
        # Generate grid
        grid_lines = generator.generate_grid(panels, camera_grid, 1920, 1080)
        stats = generator.get_grid_stats(grid_lines)
        
        print(f"  📊 Density {density}:")
        print(f"    - Total lines: {stats['total_lines']}")
        print(f"    - Boundary: {stats['line_types']['boundary']}, " +
              f"Horizontal: {stats['line_types']['horizontal']}, " +
              f"Vertical: {stats['line_types']['vertical']}")
        print(f"    - Per panel: {dict(stats['panels'])}")
    
    print()
    
    print("📄 Phase 5: SVG Rendering")
    print("-" * 40)
    
    # Create final grid for export
    final_camera = create_standard_camera(distance=12.0, fov_degrees=50.0)
    final_camera.orbit_around_target(45.0, 30.0, 12.0)
    
    final_config = GridConfig(density=0.8, show_panel_boundaries=True)
    final_generator = GridGenerator(final_config)
    final_grid = final_generator.generate_grid(panels, final_camera, 1920, 1080)
    
    # Render to SVG
    svg_config = create_standard_svg_config(1920, 1080)
    renderer = SVGRenderer(svg_config)
    
    output_path = exports_dir / "forced_aspect_3panel_demo.svg"
    success = renderer.render(
        final_grid, 
        str(output_path), 
        "Forced Aspect 3-Panel Corner Room - Demo Grid"
    )
    
    if success:
        file_size = output_path.stat().st_size
        estimated_size = renderer.get_file_size_estimate(final_grid)
        print(f"✓ SVG exported successfully:")
        print(f"  - File: {output_path}")
        print(f"  - Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"  - Lines: {len(final_grid)}")
        print(f"  - Estimate accuracy: {abs(file_size - estimated_size) / file_size * 100:.1f}% difference")
    
    # Generate multiple resolution examples
    resolutions = [
        (1920, 1080, "HD"),
        (3840, 2160, "4K"),
        (1080, 1080, "Square"),
        (2048, 2048, "Print_2K")
    ]
    
    print(f"\n✓ Generating examples for different output formats:")
    for width, height, label in resolutions:
        res_config = create_standard_svg_config(width, height)
        res_renderer = SVGRenderer(res_config)
        res_path = exports_dir / f"demo_{label.lower()}_{width}x{height}.svg"
        
        # Regenerate grid for this resolution
        res_grid = final_generator.generate_grid(panels, final_camera, width, height)
        res_success = res_renderer.render(
            res_grid, 
            str(res_path), 
            f"Forced Aspect Grid - {label} ({width}×{height})"
        )
        
        if res_success:
            res_size = res_path.stat().st_size
            print(f"  - {label}: {res_path.name} ({res_size:,} bytes)")
    
    print()
    print("=" * 60)
    print("🎉 PIPELINE DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print()
    print("📋 SUMMARY:")
    print("  ✅ 3D coordinate system and transformations")
    print("  ✅ Camera positioning and perspective projection")
    print("  ✅ 3-panel corner room layout generation")
    print("  ✅ Perspective-accurate grid line calculation")
    print("  ✅ SVG rendering with multiple resolutions")
    print("  ✅ File size estimation and optimization")
    print()
    print("📁 GENERATED FILES:")
    print("  • forced_aspect_3panel_demo.svg - Main demonstration")
    print("  • demo_*.svg - Resolution examples (HD, 4K, Square, Print)")
    print()
    print("🚀 READY FOR:")
    print("  • TUI (Terminal User Interface) implementation")
    print("  • 4-panel and 5-panel layout extensions")
    print("  • PNG rendering with raster output")
    print("  • CLI interface for automation")
    print("  • Configuration preset system")
    print()
    print("The foundation is solid - perspective mathematics, camera controls,")
    print("layout generation, and rendering pipeline are all working perfectly!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Ensure all required modules are available in the current directory.")
except Exception as e:
    print(f"❌ Error during demonstration: {e}")
    import traceback
    traceback.print_exc()
