# Forced Aspect Perspective Grid Tool - Technical Design

## System Architecture Diagrams

### High-Level Component Architecture

```mermaid
graph TB
    TUI[TUI Application] --> Config[Configuration Manager]
    CLI[CLI Interface] --> Config
    
    TUI --> Screens[TUI Screens]
    TUI --> Widgets[TUI Widgets]
    TUI --> Navigation[Screen Flow]
    
    Config --> Settings[settings.py]
    Config --> Examples[example configs]
    
    TUI --> Layout[Layout System]
    CLI --> Layout
    Layout --> Base[BaseLayout]
    Layout --> Three[ThreePanel]
    Layout --> Four[FourPanel]
    Layout --> Five[FivePanel]
    
    Base --> Three
    Base --> Four
    Base --> Five
    
    TUI --> Render[Rendering Engine]
    CLI --> Render
    Render --> SVG[SVG Renderer]
    Render --> PNG[PNG Renderer]
    
    Layout --> Perspective[Perspective Engine]
    Perspective --> Camera[Camera Controls]
    Perspective --> Grid[Grid Generator]
    Perspective --> Transform[3D Transforms]
    
    SVG --> Export[Export Files]
    PNG --> Export
```

### Data Flow Sequence

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Config
    participant Layout
    participant Perspective
    participant Renderer
    participant File
    
    User->>CLI: Run command with parameters
    CLI->>Config: Load configuration
    Config-->>CLI: Settings & defaults
    
    CLI->>Layout: Create layout instance
    Layout->>Layout: Define panel geometry
    Layout-->>CLI: 3D panel definitions
    
    CLI->>Perspective: Initialize camera
    Perspective->>Perspective: Calculate view matrix
    Perspective-->>CLI: Camera ready
    
    CLI->>Perspective: Generate grid
    Perspective->>Perspective: Create 3D grid points
    Perspective->>Perspective: Project to 2D
    Perspective-->>CLI: 2D grid coordinates
    
    CLI->>Renderer: Render output
    Renderer->>Renderer: Create drawing commands
    Renderer->>File: Write SVG/PNG
    File-->>Renderer: Success
    Renderer-->>CLI: File created
    CLI-->>User: Output file path
```

### Class Relationship Diagram

```mermaid
classDiagram
    class BaseLayout {
        <<abstract>>
        +get_panels() List~Panel~
        +get_bounds() BoundingBox
        +validate_config() bool
    }
    
    class ThreePanel {
        +get_panels() List~Panel~
        +_create_floor_panel() Panel
        +_create_wall_panels() List~Panel~
    }
    
    class FourPanel {
        +get_panels() List~Panel~
        +_create_ceiling_panel() Panel
    }
    
    class FivePanel {
        +get_panels() List~Panel~
        +_create_back_wall() Panel
    }
    
    class Panel {
        +corners: List~Point3D~
        +normal: Vector3D
        +label: str
        +grid_density: float
    }
    
    class Camera {
        +position: Point3D
        +target: Point3D
        +fov: float
        +near_plane: float
        +far_plane: float
        +get_view_matrix() Matrix4x4
        +get_projection_matrix() Matrix4x4
    }
    
    class GridGenerator {
        +generate_panel_grid(panel, density) List~Point3D~
        +project_to_2d(points, camera) List~Point2D~
        +clip_to_bounds(points, bounds) List~Point2D~
    }
    
    class Renderer {
        <<abstract>>
        +render(grid_data, config) bool
        +_setup_canvas() void
        +_draw_grid_lines() void
        +_draw_panel_labels() void
    }
    
    class SVGRenderer {
        +render(grid_data, config) bool
        +_write_svg_header() void
        +_create_path_element() Element
    }
    
    class PNGRenderer {
        +render(grid_data, config) bool
        +_create_image() Image
        +_draw_antialiased_line() void
    }
    
    BaseLayout <|-- ThreePanel
    BaseLayout <|-- FourPanel
    BaseLayout <|-- FivePanel
    ThreePanel <|-- FourPanel
    FourPanel <|-- FivePanel
    BaseLayout --> Panel
    Renderer <|-- SVGRenderer
    Renderer <|-- PNGRenderer
    GridGenerator --> Camera
    GridGenerator --> Panel
```

## Core Algorithm Flow

### Perspective Projection Pipeline

```mermaid
flowchart TD
    Start([Start: User Input]) --> LoadConfig[Load Configuration]
    LoadConfig --> CreateLayout[Create Layout Instance]
    CreateLayout --> DefinePanel[Define Panel Geometry in 3D]
    
    DefinePanel --> SetupCamera[Setup Camera Parameters]
    SetupCamera --> CalcViewMatrix[Calculate View Matrix]
    CalcViewMatrix --> CalcProjMatrix[Calculate Projection Matrix]
    
    CalcProjMatrix --> GenGrid[Generate 3D Grid Points]
    GenGrid --> Transform3D[Apply World Transform]
    Transform3D --> ViewTransform[Apply View Transform]
    ViewTransform --> ProjTransform[Apply Projection Transform]
    ProjTransform --> NDCToScreen[Convert NDC to Screen Coordinates]
    
    NDCToScreen --> ClipBounds[Clip to Canvas Bounds]
    ClipBounds --> GroupByPanel[Group Lines by Panel]
    GroupByPanel --> AddLabels[Add Panel Labels]
    
    AddLabels --> ChooseRenderer{Output Format?}
    ChooseRenderer -->|SVG| SVGRender[Render SVG]
    ChooseRenderer -->|PNG| PNGRender[Render PNG]
    
    SVGRender --> WriteFile[Write Output File]
    PNGRender --> WriteFile
    WriteFile --> End([End: File Created])
```

### Grid Generation Detail

```mermaid
flowchart LR
    Panel[Panel Definition] --> Corners[Extract Corner Points]
    Corners --> Bounds[Calculate 2D Bounds]
    Bounds --> GridSpacing[Determine Grid Spacing]
    
    GridSpacing --> HorizontalLines[Generate Horizontal Lines]
    GridSpacing --> VerticalLines[Generate Vertical Lines]
    
    HorizontalLines --> ClipH[Clip to Panel Bounds]
    VerticalLines --> ClipV[Clip to Panel Bounds]
    
    ClipH --> Combine[Combine Line Segments]
    ClipV --> Combine
    Combine --> PanelGrid[Panel Grid Points]
```

## Key Technical Specifications

### Coordinate Systems

**3D World Space:**
- Origin at room corner (floor level)
- X-axis: Left wall to right wall
- Y-axis: Floor to ceiling  
- Z-axis: Front to back
- Units: Abstract (scaled during rendering)

**2D Screen Space:**
- Origin at top-left of canvas
- X-axis: Left to right
- Y-axis: Top to bottom
- Units: Pixels or SVG units

### Camera Model

**Perspective Projection:**
```
x_screen = (x_3d * focal_length) / z_3d
y_screen = (y_3d * focal_length) / z_3d
```

**Field of View Calculation:**
```
focal_length = canvas_width / (2 * tan(fov / 2))
```

### Grid Density Algorithm

**Adaptive Spacing:**
- Base grid spacing in 3D world units
- Perspective scaling factor based on distance from camera
- Minimum screen-space line separation to avoid overcrowding
- Maximum subdivision depth for performance

### Performance Considerations

**Optimization Strategies:**
- Frustum culling for off-screen grid lines
- Level-of-detail grid generation
- Spatial partitioning for large grids
- Efficient 2D clipping algorithms
- Memory-conscious point generation

**Target Performance:**
- Grid generation: < 100ms for typical configurations
- SVG rendering: < 500ms for high-density grids
- PNG rendering: < 2s for 300 DPI output
- Memory usage: < 100MB for largest configurations
