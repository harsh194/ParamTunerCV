# Parameter

A professional-grade interactive image viewer and processing application designed for computer vision research, image analysis, and parameter tuning. Built with OpenCV and Python, Parameter provides real-time interactive controls, advanced analysis tools, and comprehensive export capabilities.

## ✨ Key Features

### 🖼️ Interactive Image Viewing
- **Multi-image Display**: Display multiple processed images simultaneously with automatic navigation
- **Real-time Processing**: Live parameter tuning with immediate visual feedback
- **Zoom & Pan**: Mouse wheel zoom with panning support and viewport management
- **Multiple Display Modes**: Support for both color and grayscale images with automatic scaling

### 🎛️ Advanced Control Systems
- **Dynamic Trackbars**: Real-time parameter control with specialized trackbar types
- **Smart Constraints**: Automatic value validation and range enforcement
- **Custom Callbacks**: Specialized callbacks for odd numbers, ROI constraints, and image selection
- **Parameter Persistence**: Settings automatically saved across sessions

### 🔍 Analysis & Measurement Tools
- **ROI Selection**: Rectangular and polygon-based region selection with visual feedback
- **Pixel Profiles**: Line-based intensity profile analysis using Bresenham's algorithm
- **Histogram Analysis**: Multi-channel histogram generation for full images or selected regions
- **Export Capabilities**: JSON and CSV export for all analysis data

### 🎨 Professional GUI
- **Theme Support**: Light and dark mode with consistent styling
- **Analysis Control Panel**: Professional tkinter-based control interface
- **Plot Customization**: Real-time plot appearance customization with preset management
- **Enhanced Dialogs**: Improved file selection and export dialogs with memory

### 🔧 Advanced Image Processing
- **Multi-color Space Support**: BGR, HSV, HLS, Lab, Luv, YCrCb, XYZ, and Grayscale
- **Threshold Processing**: Range, binary, Otsu, triangle, and adaptive thresholding methods
- **Filtering Tools**: Gaussian, median, bilateral filtering with real-time preview
- **Morphological Operations**: Complete set of morphological operations with kernel control

### ⚡ Dual Operation Modes
- **GUI Mode**: Full interactive interface with trackbars and analysis tools
- **Headless Mode**: Automated processing for batch operations and testing

## 🚀 Installation

### Prerequisites
- Python 3.7+
- OpenCV 4.0+
- NumPy
- Matplotlib (optional, for plotting features)
- tkinter (optional, for enhanced GUI features)

### Quick Install
```bash
git clone https://github.com/your-username/parameter.git
cd parameter
pip install -r requirements.txt
```

### Dependencies
```bash
pip install opencv-python numpy matplotlib
```

## 📚 Usage Guide

### Quick Start Example
```python
import cv2
import numpy as np
from src import ImageViewer, ViewerConfig

# Create configuration
config = ViewerConfig()

# Define trackbars for real-time control
trackbar_definitions = [
    {"name": "Show Image", "param_name": "show", "max_value": "num_images-1", "initial_value": 0},
    {"name": "Threshold", "param_name": "threshold", "max_value": 255, "initial_value": 128},
    {"name": "Kernel Size", "param_name": "kernel_size", "max_value": 31, "callback": "odd", "initial_value": 5}
]

# Initialize viewer
viewer = ImageViewer(config, trackbar_definitions, True)

# Load test image
image = cv2.imread("path/to/image.jpg")

# Main processing loop
while viewer.should_loop_continue():
    params = viewer.trackbar.parameters
    
    # Get current parameters
    threshold_val = params.get("threshold", 128)
    kernel_size = params.get("kernel_size", 5)
    
    # Process image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, threshold_val, 255, cv2.THRESH_BINARY)
    
    # Apply morphological operations
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # Display results
    viewer.display_images = [
        (image, "Original"),
        (gray, "Grayscale"),
        (thresh, f"Threshold: {threshold_val}"),
        (morphed, f"Morphed (kernel: {kernel_size})")
    ]

# Cleanup
viewer.cleanup_viewer()
```

### Factory Functions for Quick Setup

#### Basic Viewer
```python
from src.utils.viewer_factory import create_basic_viewer

# Minimal setup with no trackbars
viewer = create_basic_viewer(enable_ui=True)
```

#### Common Controls Viewer
```python
from src.utils.viewer_factory import create_viewer_with_common_controls

# Standard trackbars for general image processing
viewer = create_viewer_with_common_controls(enable_ui=True)
# Includes: Image Selector, Threshold, Kernel Size, Iterations
```

#### Filtering Specialized Viewer
```python
from src.utils.viewer_factory import create_viewer_for_filtering

# Optimized for image filtering tasks
viewer = create_viewer_for_filtering(enable_ui=True)
# Includes: Image Selector, Gaussian Size, Median Size, Bilateral parameters
```

#### Fully Customizable Viewer
```python
from src.utils.viewer_factory import create_auto_viewer
from src.config.viewer_config import ViewerConfig

config = ViewerConfig().set_window_size(1200, 800).set_debug_mode(True)
trackbars = [
    {"name": "Custom Param", "param_name": "custom", "max_value": 100, "initial_value": 50}
]
viewer = create_auto_viewer(config, trackbars, True, max_headless_iterations=1)
```

## 🎛️ Advanced Configuration

### ViewerConfig Options
```python
config = ViewerConfig()
config.set_window_size(1200, 800)          # Main window dimensions
config.set_debug_mode(True)                 # Enable/disable GUI
config.screen_width = 1200                  # Display width
config.screen_height = 800                  # Display height
config.text_window_width = 400              # Log window width
config.text_window_height = 400             # Log window height
config.min_size_ratio = 0.1                 # Minimum zoom ratio
config.max_size_ratio = 10.0                # Maximum zoom ratio
config.trackbar_window_name = "Controls"    # Trackbar window title
config.process_window_name = "Images"       # Main window title
```

### Trackbar Configuration Types

#### Standard Integer Trackbar
```python
{
    "name": "Display Name",
    "param_name": "variable_name",
    "max_value": 255,
    "initial_value": 128
}
```

#### Odd Number Trackbar (for kernel sizes)
```python
{
    "name": "Kernel Size",
    "param_name": "kernel_size",
    "max_value": 31,
    "initial_value": 5,
    "callback": "odd"  # Enforces odd numbers
}
```

#### Image Selector Trackbar
```python
{
    "name": "Show Image",
    "param_name": "show",
    "max_value": "num_images-1",  # Automatically adjusts to image count
    "initial_value": 0
}
```

#### ROI Control Trackbars
```python
from src.controls.trackbar_manager import make_roi_trackbars

roi_trackbars = make_roi_trackbars()
# Creates: RectX, RectY, RectWidth, RectHeight with smart constraints
```

#### Custom Callback Trackbar
```python
def custom_callback(value):
    print(f"Custom callback triggered with value: {value}")

{
    "name": "Custom Control",
    "param_name": "custom",
    "max_value": 100,
    "initial_value": 0,
    "custom_callback": custom_callback
}
```

## 🔍 Analysis Tools

### ROI Selection and Analysis

#### Rectangle Selection
```python
# Interactive rectangle selection (mouse drag)
# Access selected ROIs:
roi_rectangles = viewer.mouse_handler.selected_rectangles
for rect in roi_rectangles:
    x, y, w, h = rect
    roi_image = image[y:y+h, x:x+w]
    # Process ROI...
```

#### Polygon Selection
```python
# Multi-point polygon selection (click to add points)
# Access selected polygons:
polygons = viewer.mouse_handler.selected_polygons
for polygon in polygons:
    # Create mask from polygon
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [polygon], 255)
    # Apply mask to image...
```

### Pixel Profile Analysis
```python
# Line-based intensity profiles
lines = viewer.mouse_handler.selected_lines
for line in lines:
    x1, y1, x2, y2 = line
    # Use built-in plot analyzer
    viewer.plot_analyzer.create_pixel_profile_plot(image, line, "Profile Analysis")
```

### Histogram Analysis
```python
# Generate histograms for ROIs or full image
roi_rectangles = viewer.mouse_handler.selected_rectangles
if roi_rectangles:
    rect = roi_rectangles[0]  # Use first ROI
    x, y, w, h = rect
    roi = image[y:y+h, x:x+w]
    viewer.plot_analyzer.create_histogram_plot(roi, "ROI Histogram")
else:
    viewer.plot_analyzer.create_histogram_plot(image, "Full Image Histogram")
```

## 📊 Data Export

### Export Analysis Data
```python
# Export histogram data
histogram_data = {"red": [255, 128, 64], "green": [200, 150, 100], "blue": [180, 120, 80]}
viewer.export_manager.export_histogram_data(histogram_data, format='json', filename='histogram_export')
viewer.export_manager.export_histogram_data(histogram_data, format='csv', filename='histogram_export')

# Export pixel profile data
profile_data = {"distance": [0, 1, 2, 3], "intensity": [255, 200, 150, 100]}
viewer.export_manager.export_profile_data(profile_data, format='json', filename='profile_export')

# Export polygon coordinates
polygon_data = {"vertices": [[100, 100], [200, 100], [200, 200], [100, 200]]}
viewer.export_manager.export_polygon_data(polygon_data, format='json', filename='polygon_export')
```

## 🎨 Advanced Thresholding

### Multi-Color Space Thresholding
```python
from src.analysis.threshold.image_processor import ThresholdProcessor

processor = ThresholdProcessor()

# Range thresholding in HSV color space
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
result = processor.apply_range_threshold(
    hsv_image, 
    color_space='HSV',
    channel_ranges=[
        (0, 30),    # Hue range
        (50, 255),  # Saturation range  
        (50, 255)   # Value range
    ]
)

# Adaptive thresholding
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
adaptive_result = processor.apply_adaptive_threshold(
    gray,
    max_value=255,
    adaptive_method='GAUSSIAN_C',
    threshold_type='BINARY',
    block_size=11,
    constant=2
)
```

### Automatic Threshold Methods
```python
# Otsu's method
otsu_thresh, otsu_result = processor.apply_otsu_threshold(gray)

# Triangle method
triangle_thresh, triangle_result = processor.apply_triangle_threshold(gray)

print(f"Otsu threshold: {otsu_thresh}")
print(f"Triangle threshold: {triangle_thresh}")
```

## 🖱️ Mouse Interactions

### Interaction Modes
- **Rectangle Mode**: Click and drag for rectangle ROI selection (default mode, 'R' key)
- **Line Mode**: Click to start line, click again to end (for pixel profiles, 'L' key)
- **Polygon Mode**: Click to add vertices, right-click or click near first point to close ('P' key)

### Mouse Controls
- **Left Click & Drag**: Create rectangle ROI
- **Left Click (Line Mode)**: Add line points
- **Left Click (Polygon Mode)**: Add polygon vertices
- **Right Click**: Remove last drawn item
- **Double Right Click**: Clear all selections
- **Mouse Wheel**: Zoom in/out
- **Mouse Wheel + Ctrl**: Fine zoom control
- **Middle Click & Drag**: Pan image

### Keyboard Shortcuts
- **'q' or ESC**: Quit application
- **'r'**: Toggle rectangle drawing mode (default mode)
- **'l'**: Toggle line drawing mode
- **'p'**: Toggle polygon drawing mode
- **'h'**: Show histogram for selected region
- **Shift+P**: Show pixel profiles for selected lines
- **Escape**: Clear current drawing mode (return to rectangle mode)

## 🎯 Advanced Usage Patterns

### Custom Image Processor
```python
from typing import List, Tuple
import numpy as np
import cv2

def custom_image_processor(params: dict, log_func) -> List[Tuple[np.ndarray, str]]:
    """
    Custom processing function that takes parameters and returns processed images.
    
    Args:
        params: Dictionary of current trackbar values
        log_func: Function to log messages to the viewer
        
    Returns:
        List of (image, title) tuples for display
    """
    # Get parameters
    blur_size = params.get("blur_size", 5)
    threshold = params.get("threshold", 128)
    
    # Log current parameters
    log_func(f"Processing with blur_size={blur_size}, threshold={threshold}")
    
    # Your processing logic here
    processed_images = []
    
    # Return list of (image, title) tuples
    return processed_images

# Set up viewer with custom processor
viewer.setup_viewer(image_processor_func=custom_image_processor)
```

### Headless Mode for Automation
```python
# Disable UI for automated processing
config = ViewerConfig().set_debug_mode(False)
viewer = ImageViewer(config, trackbar_definitions, False, max_headless_iterations=100)

# Process images without GUI
while viewer.should_loop_continue():
    # Your processing logic
    params = viewer.trackbar.parameters
    # ... process images ...
    viewer.display_images = processed_results
```

### Batch Processing Example
```python
import glob
import os

def batch_process_images(input_folder, output_folder):
    """Process all images in a folder with consistent parameters."""
    
    # Setup headless viewer
    config = ViewerConfig().set_debug_mode(False)
    trackbars = [
        {"name": "Threshold", "param_name": "threshold", "max_value": 255, "initial_value": 128},
        {"name": "Kernel Size", "param_name": "kernel_size", "max_value": 31, "callback": "odd", "initial_value": 5}
    ]
    viewer = ImageViewer(config, trackbars, False, max_headless_iterations=1)
    
    # Process all images
    for image_path in glob.glob(os.path.join(input_folder, "*.jpg")):
        image = cv2.imread(image_path)
        
        # Single iteration processing
        while viewer.should_loop_continue():
            params = viewer.trackbar.parameters
            
            # Your processing logic
            processed_image = process_single_image(image, params)
            
            # Save result
            filename = os.path.basename(image_path)
            output_path = os.path.join(output_folder, f"processed_{filename}")
            cv2.imwrite(output_path, processed_image)
            
            viewer.display_images = [(processed_image, "Processed")]
    
    viewer.cleanup_viewer()
```

## 🎨 GUI Customization

### Theme Management
```python
from src.gui.theme_manager import ThemeManager

theme_manager = ThemeManager()

# Switch to dark theme
theme_manager.set_dark_theme()

# Switch to light theme  
theme_manager.set_light_theme()
```

### Analysis Control Window
```python
from src.gui.analysis_control_window import AnalysisControlWindow

# Create enhanced control panel
control_window = AnalysisControlWindow(viewer)
control_window.show()

# Available controls:
# - Drawing tool mode selection (rectangle, line, polygon) with keyboard shortcuts (R, L, P)
# - Analysis function quick access (histogram, pixel profiles)
# - Selection management for ROIs, lines, and polygons
# - Export controls for data and coordinates
# - Plot customization access
# - Keyboard shortcuts: R (Rectangle), L (Line), P (Polygon), H (Histogram), Shift+P (Profiles)
```

### Plot Customization
```python
# Customize plot appearance
plot_settings = {
    "figure_size": (12, 8),
    "dpi": 150,
    "grid": True,
    "grid_alpha": 0.3,
    "title_fontsize": 16,
    "axis_fontsize": 14,
    "line_width": 3,
    "colors": {
        "red": "#FF0000",
        "green": "#00FF00", 
        "blue": "#0000FF"
    }
}

viewer.plot_analyzer.update_plot_settings("histogram", plot_settings)
```

## 🔧 Performance Optimization

### Memory Management
```python
# For large images, consider limiting display size
config = ViewerConfig()
config.max_size_ratio = 2.0  # Limit maximum zoom
config.min_size_ratio = 0.2  # Limit minimum zoom

# Use ROI processing for large images
def process_large_image_roi(image, roi_coords):
    x, y, w, h = roi_coords
    roi = image[y:y+h, x:x+w]
    # Process only the ROI
    return process_roi(roi)
```

### Efficient Processing Loops
```python
# Minimize processing overhead
while viewer.should_loop_continue():
    params = viewer.trackbar.parameters
    
    # Only process if parameters changed
    if viewer.parameters_changed():
        processed_images = expensive_processing(image, params)
        viewer.display_images = processed_images
    
    # Or use built-in parameter change detection
    if viewer.should_reprocess():
        # Your processing logic
        pass
```

## 🐛 Troubleshooting

### Common Issues

#### OpenCV Window Issues
```python
# If windows don't appear or respond
try:
    viewer = ImageViewer(config, trackbars, True)
except Exception as e:
    print(f"Error initializing viewer: {e}")
    # Try reducing window size or disabling features
```

#### Memory Issues with Large Images
```python
# Reduce image size before processing
def resize_if_large(image, max_dimension=1920):
    h, w = image.shape[:2]
    if max(h, w) > max_dimension:
        scale = max_dimension / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(image, (new_w, new_h))
    return image
```

#### Matplotlib Backend Issues
```python
# If plots don't appear, try different backends
import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg', 'Agg'
```

### Debug Mode
```python
# Enable verbose logging
config = ViewerConfig()
config.enable_debug = True

# Check viewer state
print(f"Current parameters: {viewer.trackbar.parameters}")
print(f"Image dimensions: {viewer.current_image_dims}")
print(f"Selected ROIs: {len(viewer.mouse_handler.selected_rectangles)}")
```

## 🏗️ Architecture Overview

### Core Components
- **ImageViewer**: Central orchestrator managing the application lifecycle
- **ViewerConfig**: Configuration management with fluent interface
- **TrackbarManager**: Real-time parameter control via OpenCV trackbars
- **MouseHandler**: Mouse interaction management for ROI selection and drawing
- **WindowManager**: OpenCV window lifecycle management
- **PlotAnalyzer**: Histogram and pixel profile generation
- **ExportManager**: Data export functionality
- **ThresholdProcessor**: Advanced thresholding capabilities

### Design Patterns
- **Factory Pattern**: Viewer creation and configuration
- **Observer Pattern**: Trackbar callbacks and event handling
- **Strategy Pattern**: Pluggable image processing functions
- **Fluent Interface**: Configuration building
- **Protocol-based Design**: Type hints for extensibility

## 🤝 Contributing

### Development Setup
```bash
git clone https://github.com/your-username/parameter.git
cd parameter
pip install -r requirements.txt
python check.py  # Run test script
```

### Code Structure
```
src/
├── core/           # ImageViewer main class
├── config/         # ViewerConfig management
├── controls/       # TrackbarManager for real-time controls
├── events/         # MouseHandler for interactions
├── gui/            # UI components (theme, dialogs, windows)
├── analysis/       # Analysis modules (plotting, export, threshold)
└── utils/          # Factory methods and utilities
```

### Testing
```bash
# Run the main test example
python check.py

# Test different viewer configurations
python -c "from src.utils.viewer_factory import create_viewer_with_common_controls; viewer = create_viewer_with_common_controls()"
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with OpenCV for computer vision functionality
- Uses NumPy for efficient array operations
- Matplotlib integration for advanced plotting
- tkinter for enhanced GUI components

## 📞 Support

For issues, feature requests, or questions:
1. Check the troubleshooting section above
2. Review the example code in `check.py`
3. Create an issue on GitHub with detailed information about your problem

---

**Parameter** - Professional image analysis made simple. Whether you're doing research, developing computer vision applications, or need interactive parameter tuning, Parameter provides the tools you need with the flexibility to adapt to your workflow.