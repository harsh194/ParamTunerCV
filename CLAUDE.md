# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a comprehensive Python-based computer vision parameter tuning framework built around OpenCV with advanced analysis capabilities. The enhanced architecture includes:

### Core Components
- **ImageViewer**: Main class providing interactive image viewing with real-time parameter adjustment
- **ViewerConfig**: Configuration management for UI windows, trackbars, and display settings  
- **TrackbarManager**: Handles OpenCV trackbar creation and parameter callbacks
- **WindowManager**: Manages OpenCV window lifecycle and resizing
- **MouseHandler**: Enhanced mouse interactions for zoom, pan, ROI selection, and line drawing
- **AnalysisControlWindow**: Professional tkinter-based control panel for analysis features
- **ImageAnalyzer**: Advanced image analysis with pixel profiles and histogram generation

### Analysis Capabilities
- **Professional Analysis Interface**: Tkinter-based control window with buttons and dropdowns
- **Pixel Profile Analysis**: Interactive line drawing with intensity profile plotting
- **Histogram Analysis**: Full image and ROI-specific histogram generation
- **ROI Management**: Rectangle selection with targeted analysis capabilities
- **Multi-Channel Analysis**: RGB and grayscale image support

The system supports both interactive UI mode and headless processing mode, controlled by the `enable_debug` flag in ViewerConfig.

## Key Components

### parameter.py
Contains the complete enhanced ImageViewer framework with:

#### Interactive Features
- **Zoom/Pan**: Mouse wheel zoom and middle-click drag pan
- **Dual Drawing Modes**: 
  - ROI Mode: Left-click drag for rectangle selection
  - Line Mode: Left-click drag for line drawing (pixel profiles)
- **Mouse Controls**:
  - Left-click + drag: Draw ROI or line (mode-dependent)
  - Right-click: Remove last drawn element
  - Right double-click: Clear all elements
  - Middle-click + drag: Pan image
  - Mouse wheel: Zoom in/out

#### Analysis Features
- **Pixel Profile Plotting**: Draw lines across image features to see intensity transitions
- **Histogram Analysis**: View pixel distributions for entire images or specific ROIs
- **Professional Interface**: Tkinter control window with:
  - ROI Selection dropdown (Full Image, ROI 1, ROI 2, etc.)
  - Line Selection dropdown (All Lines, Line 1, Line 2, etc.)
  - Professional buttons with emoji icons
  - Real-time updates as elements are added/removed

#### Technical Features
- **Thread-safe parameter management** with locks
- **Automatic headless iteration handling**
- **Professional matplotlib plot generation**
- **Multi-window management** (OpenCV + tkinter)
- **Event-driven architecture** with responsive GUI

### Application Files
- **check.py**: Main example demonstrating the complete framework
- **check_simple.py**: Simplified version showing clean API usage
- **enhanced_analysis_demo.py**: Comprehensive demo of analysis features

## Enhanced Parameter System

### Trackbar Configuration Structure
Parameters are defined in `trackbar_definitions` arrays with enhanced structure:
```python
{
    "name": "Display Name",           # UI trackbar label
    "param_name": "internal_name",    # Parameter key for processing
    "max_value": 255,                 # Max trackbar value (or "num_images-1")
    "initial_value": 128,             # Default value
    "callback": "odd"                 # Optional: "odd", "roi_x", "roi_y", etc.
}
```

### Convenience Functions
The library provides helper functions for common trackbar types:
```python
# Helper functions available
make_trackbar(name, param_name, max_value, initial_value, callback)
make_int_trackbar(name, param_name, max_value, initial_value)
make_odd_trackbar(name, param_name, max_value, initial_value)  # For kernel sizes
make_image_selector(name, param_name)  # For image selection
make_roi_trackbars()  # Set of ROI control trackbars
```

### Parameter Access
Parameters are accessed via `viewer.trackbar.parameters` dictionary and persist between UI interactions.

## ImageViewer API

### Enhanced Constructor
```python
ImageViewer(
    config: ViewerConfig = None,
    trackbar_definitions: List[Dict[str, Any]] = None,
    app_debug_mode: bool = True,
    max_headless_iterations: int = 1
)
```

### Simplified Configuration
```python
# Method 1: Automatic configuration
viewer = ImageViewer(config, trackbar_definitions, APP_DEBUG_MODE)

# Method 2: Fluent interface
config = (ViewerConfig.create_simple(True)
          .set_window_size(800, 600)
          .add_trackbars(*trackbar_definitions))

# Method 3: Factory methods
viewer = ImageViewer.create_simple(enable_ui=True)
viewer = ImageViewer.create_with_trackbars(trackbars, enable_ui=True)
```

### Core Methods
- **`setup_viewer()`**: Initialize viewer (called automatically)
- **`should_loop_continue()`**: Check if main loop should continue
- **`display_images = [...]`**: Update displayed images
- **`cleanup_viewer()`**: Clean shutdown of all windows
- **`get_param(name, default)`**: Get single parameter value
- **`get_all_params()`**: Get all parameter values
- **`get_drawn_rois()`**: Get all drawn ROI rectangles
- **`get_drawn_lines()`**: Get all drawn lines

## Analysis Control Window

### Professional Interface Layout
```
┌─── Analysis Controls ─────────────┐
│ ROI Selection:    [Full Image  ▼] │
│ Line Selection:   [All Lines   ▼] │
│ ─────────────────────────────────  │
│    📊 Show Histogram              │
│    📈 Show Profiles               │
│ ─────────────────────────────────  │
│    🖊️ Toggle Line Mode            │
│    🗑️ Clear All                   │
│    ❌ Close Plots                 │
└───────────────────────────────────┘
```

### Button Functions
- **📊 Show Histogram**: Display histogram for selected ROI or full image
- **📈 Show Profiles**: Display pixel intensity profiles for selected line(s)
- **🖊️ Toggle Line Mode**: Switch between ROI and line drawing modes
- **🗑️ Clear All**: Remove all drawn ROIs and lines
- **❌ Close Plots**: Close all matplotlib analysis windows

### Dynamic Selection
- **ROI Dropdown**: Automatically updates with "Full Image", "ROI 1", "ROI 2", etc.
- **Line Dropdown**: Automatically updates with "All Lines", "Line 1", "Line 2", etc.
- **Smart Bounds Checking**: Selections automatically adjust when elements are removed

## Usage Patterns

### Basic Usage (Simplified API)
```python
from parameter import ImageViewer, ViewerConfig

# Configuration
config = ViewerConfig()
trackbar_definitions = [
    {"name": "Show Image", "param_name": "show", "max_value": "num_images-1", "initial_value": 0},
    {"name": "Threshold", "param_name": "threshold", "max_value": 255, "initial_value": 128}
]

# Create viewer - Analysis Control Window created automatically
viewer = ImageViewer(config, trackbar_definitions, True)

# Main processing loop
while viewer.should_loop_continue():
    params = viewer.trackbar.parameters
    # Process images using parameters
    processed_images = your_processing_function(params)
    viewer.display_images = processed_images

viewer.cleanup_viewer()
```

### Advanced Usage with Analysis
```python
# Enhanced setup with helper functions
from parameter import make_int_trackbar, make_odd_trackbar, make_image_selector

trackbars = [
    make_image_selector(),
    make_int_trackbar("Threshold", "threshold", 255, 128),
    make_odd_trackbar("Kernel Size", "kernel_size", 31, 5)
]

viewer = ImageViewer.create_with_trackbars(trackbars, True)

while viewer.should_loop_continue():
    params = viewer.get_all_params()
    
    # Your image processing
    processed_images = process_images(params)
    viewer.display_images = processed_images
    
    # Analysis features are available automatically:
    # - Draw ROIs and use Analysis Control Window
    # - Select specific ROIs for histogram analysis
    # - Draw lines for pixel profile analysis

viewer.cleanup_viewer()
```

### Headless Mode (No UI)
```python
# Set APP_DEBUG_MODE = False or enable_ui = False
viewer = ImageViewer(config, trackbar_definitions, False, max_headless_iterations=5)

while viewer.should_loop_continue():
    params = viewer.get_all_params()  # Uses initial_value defaults
    processed_images = process_images(params)
    viewer.display_images = processed_images  # No UI updates

# Automatically stops after max_headless_iterations
```

## Analysis Workflows

### Histogram Analysis Workflow
1. Run your image processing code
2. Draw ROI rectangles on areas of interest
3. Open Analysis Control Window
4. Select specific ROI from dropdown
5. Click "📊 Show Histogram"
6. Professional matplotlib histogram appears

### Pixel Profile Workflow
1. Click "🖊️ Toggle Line Mode" in Analysis Control Window
2. Draw lines across image features (edges, gradients, etc.)
3. Select specific line or "All Lines" from dropdown
4. Click "📈 Show Profiles"
5. Professional matplotlib intensity profile plots appear

### Comparative Analysis
1. Draw multiple ROIs and lines on different image regions
2. Use Analysis Control Window to analyze each individually
3. Compare histograms and profiles across different areas
4. Generate multiple plots for documentation

## Technical Implementation

### Window Management
- **OpenCV Windows**: Main image display, trackbar controls, text logging
- **Tkinter Window**: Professional Analysis Control Window
- **Matplotlib Windows**: Analysis plots (histograms, profiles)
- **Automatic Cleanup**: All windows properly destroyed on exit

### Threading and Events
- **Main Thread**: OpenCV event processing
- **GUI Events**: Tkinter event processing integrated with OpenCV loop
- **Thread Safety**: Parameter access protected with locks
- **Responsive Interface**: Non-blocking GUI updates

### Error Handling
- **Graceful Degradation**: Features disable if dependencies unavailable
- **Bounds Checking**: ROI and line coordinates validated
- **Exception Handling**: Robust error recovery throughout
- **User Feedback**: Clear logging of operations and errors

## Dependencies

### Required Dependencies
- **OpenCV (cv2)**: Core image processing and GUI
- **NumPy**: Array operations and image data
- **Python 3.x**: With threading support

### Optional Dependencies
- **tkinter**: Professional analysis control interface (usually built-in)
- **matplotlib**: Advanced plotting for histograms and profiles
- **ttk**: Enhanced tkinter widgets (usually built-in)

### Dependency Handling
The library gracefully handles missing optional dependencies:
- Without **tkinter**: Analysis Control Window disabled, core functionality remains
- Without **matplotlib**: Plotting features disabled, interactive features remain
- All features degrade gracefully with informative messages

## Common Commands

### Run Interactive Demo
```bash
python check.py                    # Full interactive mode



### Parameter Definition
- Use descriptive names for trackbars
- Set appropriate max_value ranges
- Use callback="odd" for kernel sizes
- Group related parameters logically

### Image Processing Integration
- Access parameters via `viewer.get_all_params()`
- Update images with `viewer.display_images = [...]`
- Handle parameter validation in your processing code
- Use meaningful image titles for clarity

### Analysis Workflow
- Draw ROIs around areas of interest before analysis
- Use line mode for edge and gradient analysis
- Select specific regions/lines for targeted analysis
- Save analysis plots for documentation

### Performance Optimization
- Minimize expensive operations in the main loop
- Cache processed images when parameters haven't changed
- Use appropriate image resolutions for analysis
- Close unused matplotlib windows to free memory

This enhanced framework provides a professional, feature-rich environment for computer vision parameter tuning with advanced analysis capabilities while maintaining simple, clean API usage.