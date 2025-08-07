# Forced Aspect Perspective Grid Tool - Project Plan

## 📋 Project Overview

A specialized tool for creating perspective grids used in forced aspect, multi-panel compositions for 3D-looking illustrations. These grids help artists create consistent perspective across multiple panels that, when photographed from a specific angle, create a visual illusion of 3D space.

## 🎯 Core Requirements

### Output Formats
- **SVG**: Vector format for scalable, editable grids
- **PNG**: Raster format with custom resolution and DPI
- **Custom sizing**: Support for both pixel and inch-based dimensions

### Panel Layout Types
1. **3-Panel Corner Room**: Floor + Left wall + Right wall
2. **4-Panel Corner Room + Ceiling**: Adds ceiling panel to 3-panel
3. **5-Panel Full Room**: Floor + Ceiling + Left wall + Right wall + Back wall

### Camera Controls
- Adjustable vanishing point distance
- Field of View (FOV) control / simulated lens angle
- Optional orthographic mode (infinite focal length)
- Support for 1-point, 2-point, and 3-point perspective

### Grid Features
- Perspective-accurate grid lines
- Optional panel boundary labels
- Adjustable grid density
- Customizable line styles and colors

## 🏗️ Project Structure

```
forced_aspect_grid/
├── main.py                 # CLI interface & main orchestrator
├── tui_app.py              # Terminal User Interface (primary interface)
├── config/
│   └── settings.py         # Default configurations, output formats
├── layouts/
│   ├── __init__.py
│   ├── base_layout.py      # Abstract base class for all layouts
│   ├── three_panel.py      # Corner room (floor + 2 walls)
│   ├── four_panel.py       # Corner room + ceiling
│   └── five_panel.py       # Full room (floor, ceiling, 3 walls)
├── perspective/
│   ├── __init__.py
│   ├── camera.py           # Camera controls (FOV, vanishing points)
│   ├── grid_generator.py   # Core perspective grid calculations
│   └── transforms.py       # 3D to 2D projection math
├── rendering/
│   ├── __init__.py
│   ├── svg_renderer.py     # SVG export functionality
│   └── png_renderer.py     # PNG rasterization
├── tui/
│   ├── __init__.py
│   ├── screens.py          # TUI screen definitions
│   ├── widgets.py          # Custom TUI widgets
│   └── navigation.py       # Screen flow management
├── exports/
│   └── (generated files)
├── examples/
│   └── sample_configs.json # Preset configurations
└── requirements.txt
```

## 🚀 Implementation Phases

### Phase 1: Core Foundation
- **Goal**: Working 3-panel perspective grid with basic TUI and SVG output
- **Deliverables**:
  - Basic perspective projection math
  - 3D coordinate system setup
  - Simple 3-panel corner room layout
  - SVG rendering pipeline
  - Terminal User Interface (TUI) for guided configuration
  - CLI interface for power users

### Phase 2: Extended Layouts & Features
- **Goal**: All panel configurations with PNG support and TUI polish
- **Deliverables**:
  - 4-panel and 5-panel layouts
  - PNG rendering with DPI control
  - Enhanced TUI with visual feedback
  - Grid density controls
  - Panel labeling system
  - Preset configurations

### Phase 3: Polish & Advanced Features
- **Goal**: Production-ready tool with full feature set
- **Deliverables**:
  - Advanced TUI features (custom dimensions, batch mode)
  - Comprehensive CLI with argument parsing
  - Configuration file system
  - Example presets and documentation
  - Error handling and validation
  - Performance optimization

## 🔧 Technical Architecture

### Coordinate System
- **3D Space**: Right-handed coordinate system
  - X-axis: Left (-) to Right (+)
  - Y-axis: Down (-) to Up (+)
  - Z-axis: Back (-) to Front (+)
- **2D Canvas**: Standard screen coordinates (origin top-left)

### Core Data Flow
1. **Layout Definition**: Define panel geometry in 3D space
2. **Grid Generation**: Create 3D grid points for each panel
3. **Perspective Projection**: Transform 3D points to 2D screen coordinates
4. **Rendering**: Export to SVG/PNG with proper scaling

### Key Design Patterns
- **Strategy Pattern**: Interchangeable layout types
- **Template Method**: Common rendering pipeline with format-specific implementations
- **Builder Pattern**: Complex configuration assembly
- **Command Pattern**: CLI operation encapsulation

## 📐 Mathematical Foundations

### Perspective Projection
- **Pinhole Camera Model**: Standard perspective transformation
- **Vanishing Points**: Calculated from camera position and panel orientations
- **Field of View**: Controls perspective distortion amount

### Grid Generation
- **Regular Spacing**: Evenly distributed grid lines in 3D space
- **Adaptive Density**: Optional grid refinement based on perspective distortion
- **Panel Boundaries**: Intersection calculations for clean panel edges

## 🎨 Output Specifications

### SVG Features
- Vector paths for infinite scalability
- Grouped elements for easy editing
- Metadata for panel identification
- Layer organization for selective visibility

### PNG Features
- Configurable DPI for print quality
- Anti-aliasing for smooth lines
- Transparent backgrounds optional
- Multiple resolution presets

## 🔄 Future Extensibility

### Potential Enhancements
- **Custom Panel Shapes**: Non-rectangular panels
- **Curved Surfaces**: Cylindrical or spherical panels
- **Animation Export**: Perspective transitions
- **Interactive Preview**: Real-time parameter adjustment
- **Template Library**: Common room configurations
- **Measurement Tools**: Scale references and rulers

### Integration Possibilities
- **CAD Software**: Import/export to design tools
- **3D Modeling**: Blender/Maya integration
- **Web Interface**: Browser-based tool
- **Mobile App**: Tablet-optimized interface
