# Forced Aspect Perspective Grid Tool

A specialized tool for creating perspective grids used in forced aspect, multi-panel compositions for 3D-looking illustrations. Perfect for artists creating pop-out panel artwork that creates a visual illusion of 3D space when photographed from a specific viewing angle.

## 🎨 What This Tool Does

This tool generates mathematically accurate perspective grids that help you create consistent artwork across multiple physical panels. When these panels are arranged and photographed from the correct angle, they create a convincing 3D illusion.

**Example Use Cases:**

- 6"×6" pop-out panel compositions
- Forced perspective room installations  
- Multi-panel 3D artwork for photography
- Perspective drawing practice guides
- Architectural visualization aids

## 🏗️ Panel Layout Types

### 3-Panel Corner Room

The classic setup with floor and two walls meeting at a corner.

- **Panels**: Floor + Left Wall + Right Wall
- **Best for**: Simple corner scenes, furniture arrangements
- **Viewing angle**: 45° from corner

### 4-Panel Corner Room + Ceiling  

Adds overhead space for more complex scenes.

- **Panels**: Floor + Left Wall + Right Wall + Ceiling
- **Best for**: Room interiors, overhead lighting effects
- **Viewing angle**: Slightly below eye level

### 5-Panel Full Room

Complete room environment with back wall.

- **Panels**: Floor + Ceiling + Left Wall + Right Wall + Back Wall
- **Best for**: Complete room scenes, complex environments
- **Viewing angle**: Centered room view

## 📐 Key Features

### Camera Controls

- **Field of View**: Adjust perspective distortion (wide to telephoto)
- **Viewing Distance**: Control how close/far the camera appears
- **Camera Position**: Customize the exact viewpoint
- **Orthographic Mode**: Parallel projection for technical drawing

### Grid Options

- **Density Control**: Fine to coarse grid spacing
- **Panel Labels**: Optional panel identification
- **Custom Colors**: Adjust line colors and weights
- **Smart Clipping**: Grid lines stop at panel boundaries

### Output Formats

- **SVG**: Vector format for infinite scalability and editing
- **PNG**: High-quality raster output with custom DPI
- **Custom Sizing**: Pixels, inches, or custom dimensions
- **Print Ready**: 300-600 DPI support for physical templates

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone [repository-url]
cd forced_aspect_grid

# Install dependencies
pip install -r requirements.txt
```

### Easy Mode: Interactive Interface

For artists and non-developers, use the guided Terminal User Interface:

```bash
# Launch the interactive interface
python tui_app.py

# Follow the step-by-step prompts:
# 1. Select panel layout (3, 4, or 5 panels)
# 2. Choose panel size (standard presets or custom)  
# 3. Set viewing angle and camera position
# 4. Configure grid density and visual options
# 5. Choose output format and size
# 6. Generate your grid!
```

### Advanced: Command Line

For power users and automation:

For power users and automation:

```bash
# Generate a simple 3-panel corner room grid
python main.py --layout 3panel --output my_grid.svg

# Create a high-resolution print template
python main.py --layout 4panel --format png --dpi 300 --size 11x8.5in --output print_template.png

# Use a preset configuration
python main.py --config presets/standard_6x6_panels.json --output room_grid.svg
```

### Configuration File

Create custom configurations for repeated use:

```json
{
  "preset_name": "my_setup",
  "layout": {
    "type": "3panel",
    "panel_size": {"width": 6, "height": 6, "units": "inches"}
  },
  "camera": {
    "fov": 50,
    "position": [0, 4, 8],
    "target": [0, 0, 0]
  },
  "output": {
    "format": "svg",
    "size": {"width": 1920, "height": 1080}
  }
}
```

## 📋 Command Reference

### Layout Options

- `--layout 3panel` - Corner room (floor + 2 walls)
- `--layout 4panel` - Corner room + ceiling  
- `--layout 5panel` - Full room (all surfaces)

### Camera Settings

- `--fov 50` - Field of view in degrees (20-120)
- `--distance 10` - Camera distance from target
- `--position X Y Z` - Custom camera position
- `--orthographic` - Use parallel projection

### Grid Controls

- `--grid-density 0.5` - Grid line spacing (0.1-2.0)
- `--line-weight 1` - Line thickness in pixels/points
- `--color "#333333"` - Grid line color (hex)

### Output Options

- `--format svg|png` - Output file format
- `--size WIDTHxHEIGHT` - Canvas size (pixels or with units)
- `--dpi 300` - Dots per inch for PNG output
- `--output filename` - Output file path

### Configuration

- `--config file.json` - Load configuration file
- `--save-config file.json` - Save current settings
- `--presets` - List available preset configurations

## 🎯 Workflow Examples

### For Digital Artists

1. Generate SVG grid with your panel dimensions
2. Import to Illustrator/Inkscape as a guide layer
3. Draw artwork using grid for perspective accuracy
4. Export panels separately for printing/cutting

### For Physical Installation Artists  

1. Measure your physical panel dimensions
2. Generate high-DPI PNG template at print scale
3. Print template on paper or directly on panels
4. Create artwork following the perspective guides
5. Arrange panels at calculated viewing angle

### For Photographers

1. Use tool to plan complex forced perspective shots
2. Generate multiple viewing angle options
3. Print templates for on-location reference
4. Position subjects/objects along grid lines

## 📖 Documentation

Detailed documentation is available in the `docs/` directory:

- **[Project Plan](docs/design/project-plan.md)** - Complete project overview and architecture
- **[Technical Design](docs/design/technical-design.md)** - System architecture and algorithms  
- **[User Interface](docs/design/user-interface.md)** - CLI reference and usage patterns

## 🔧 Technical Details

### Mathematical Foundation

- Pinhole camera model for perspective projection
- Configurable vanishing points (1-point, 2-point, 3-point perspective)
- Real-world scale calculations for print accuracy
- Adaptive grid density based on perspective distortion

### Performance

- Grid generation: <100ms for typical configurations
- SVG rendering: <500ms for high-density grids  
- PNG rendering: <2s for 300 DPI output
- Memory efficient for large grid configurations

### Coordinate System

- **3D World**: Right-handed coordinates (X=right, Y=up, Z=forward)
- **Room Origin**: Floor corner where walls meet
- **Panel Definition**: 3D corner coordinates for each surface
- **Camera Model**: Position, target, and field-of-view based

## 🎨 Example Gallery

(Coming soon: Example outputs showing different panel configurations, viewing angles, and grid densities)

*Created for artists who push the boundaries of perspective and spatial illusion.*
