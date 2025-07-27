# Parameter Library Examples

This folder contains 4 essential examples that cover all the core functionality you need to know to use the Parameter library effectively.

## 🚀 Quick Start

```bash
# Run examples from the main project directory
python examples/01_basic_usage.py
python examples/02_window_control.py
python examples/03_trackbar_definitions.py
python examples/04_app_debug_mode.py
```

## 📋 Prerequisites

```bash
pip install -r requirements.txt
```

## 📖 Examples Overview

### 1. `01_basic_usage.py` - Essential Basics
**What it shows**: The fundamental workflow of the Parameter library
- How to create a viewer with basic configuration
- How to define trackbars for parameter control
- The standard main processing loop pattern
- How to access parameter values and display images

**Key concepts**:
```python
# Basic viewer setup
config = ViewerConfig()
trackbar_definitions = [...]
viewer = ImageViewer(config, trackbar_definitions)

# Main loop pattern
while viewer.should_loop_continue():
    params = viewer.trackbar.parameters
    value = params.get("param_name", default)
    # Process images...
    viewer.display_images = [(image, "title"), ...]
viewer.cleanup_viewer()
```

### 2. `02_window_control.py` - UI Window Management
**What it shows**: How to control which windows are displayed
- Enable/disable text window: `text_window=True/False`
- Enable/disable analysis control window: `analysis_control_window=True/False`
- Different UI configurations for different needs

**Key concepts**:
```python
# Control which windows appear
viewer = ImageViewer(config, trackbars, 
                    text_window=False,              # Hide text window
                    analysis_control_window=False)  # Hide analysis panel

# Default is both windows enabled
viewer = ImageViewer(config, trackbars)  # Both windows ON
```

### 3. `03_trackbar_definitions.py` - Parameter Control
**What it shows**: Complete guide to defining trackbars and accessing parameters
- Manual trackbar definition format
- Helper functions (`make_int_trackbar`, `make_odd_trackbar`, etc.)
- Special callbacks (`"odd"`, ROI controls)
- How to access and use parameter values

**Key concepts**:
```python
# Manual definition
{"name": "Display Name", "param_name": "code_name", "max_value": 100, "initial_value": 50}

# Helper functions (recommended)
make_int_trackbar("Threshold", "threshold", 255, 128)
make_odd_trackbar("Kernel Size", "kernel_size", 31, 5)  # Forces odd values
make_roi_trackbars()  # Returns 4 ROI trackbars

# Parameter access
params = viewer.trackbar.parameters
value = params.get("param_name")  # Gets initial_value from trackbar definition
```

### 4. `04_app_debug_mode.py` - Development vs Production
**What it shows**: When to use APP_DEBUG_MODE True vs False
- `APP_DEBUG_MODE = True`: Development, parameter tuning, analysis
- `APP_DEBUG_MODE = False`: Production deployment without GUI
- Visual comparison of both modes
- Typical development-to-production workflow

**Key concepts**:
```python
# Development mode - shows GUI, allows parameter tuning
viewer = ImageViewer(config, trackbars, enable_ui=True)  # APP_DEBUG_MODE = True

# Production mode - no GUI, fixed parameters  
viewer = ImageViewer(config, trackbars, 
                    enable_ui=False) # Automatic processing

# Workflow: Develop with True → Deploy with False
```

## 🎯 Essential Patterns

### Basic Viewer Setup
```python
from src import ImageViewer, ViewerConfig

config = ViewerConfig()
trackbars = [
    {"name": "Show Image", "param_name": "show", "max_value": "num_images-1", "initial_value": 0},
    {"name": "Threshold", "param_name": "threshold", "max_value": 255, "initial_value": 128}
]
viewer = ImageViewer(config, trackbars)
```

### Trackbar Definition Format
```python
{
    "name": "Display Name",        # What user sees
    "param_name": "code_name",     # What you use in code
    "max_value": 255,              # Maximum value (or "num_images-1")
    "initial_value": 128,          # Starting value
    "callback": "odd"              # Optional: "odd" for odd-only values
}
```

### Parameter Access
```python
while viewer.should_loop_continue():
    params = viewer.trackbar.parameters
    
    # Get parameter values (uses initial_value from trackbar definition)
    threshold = params.get("threshold")
    kernel_size = params.get("kernel_size")
    
    # Your processing code here...
    
    # Set images to display
    viewer.display_images = [
        (original_image, "Original"),
        (processed_image, f"Processed (T:{threshold})")
    ]
```

### Window Control Options
```python
# Full UI (default)
viewer = ImageViewer(config, trackbars)

# No text window
viewer = ImageViewer(config, trackbars, text_window=False)

# No analysis window  
viewer = ImageViewer(config, trackbars, analysis_control_window=False)

# Minimal UI (trackbars only)
viewer = ImageViewer(config, trackbars, text_window=False, analysis_control_window=False)

# Production mode (no GUI at all)
viewer = ImageViewer(config, trackbars, enable_ui=False, max_headless_iterations=1)
```

## 🔧 Common Use Cases

**Interactive parameter tuning**: Use examples 1 and 3
**Clean UI for presentations**: Use example 2 with windows disabled
**Production processing**: Use example 4 with APP_DEBUG_MODE=False 
**Server deployment**: Use example 4 with APP_DEBUG_MODE=False (no GUI needed)
**Real-time processing**: Use examples 1 and 3 with live camera feed

## 💡 Tips

1. **Start with example 1** to understand the basic workflow
2. **Use helper functions** (`make_int_trackbar`, etc.) instead of manual definitions
3. **Use `params.get()`** to access parameters (no need for defaults since initial_value is set)
4. **Use APP_DEBUG_MODE=False** for production with fixed parameters (not for parameter tuning)
5. **Disable unnecessary windows** to keep UI clean

## 🔍 Troubleshooting

**"No module named 'src'"** - Run from the main project directory, not the examples folder

**Empty/black windows** - Make sure you're setting `viewer.display_images` in the loop

**Trackbars don't work** - Check that `param_name` in trackbar definition matches what you use in `params.get()`

**Performance issues** - Use APP_DEBUG_MODE=False for batch processing, or reduce image sizes

---

These 4 examples contain everything you need to use the Parameter library effectively. Start with `01_basic_usage.py` and work through them in order!