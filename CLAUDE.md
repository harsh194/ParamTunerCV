# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Dependencies
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
# Run the example/test script
python check.py

# For headless mode, set APP_DEBUG_MODE = False in check.py
```

### Testing
```bash
# The main test/example is check.py
python check.py
```

## Architecture Overview

**Parameter** is a Python-based interactive image viewer and processing application built around OpenCV. The core architecture follows a modular design with clear separation of concerns:

### Core Components

1. **ImageViewer** (`src/core/image_viewer.py`) - Central orchestrator that manages the entire application lifecycle, supports both GUI and headless modes
2. **ViewerConfig** (`src/config/viewer_config.py`) - Configuration management with fluent interface for window sizing, debug modes, and trackbar definitions  
3. **TrackbarManager** (`src/controls/trackbar_manager.py`) - Real-time parameter control via OpenCV trackbars with factory functions for common types
4. **MouseHandler** (`src/events/mouse_handler.py`) - Mouse interaction management for ROI selection, zoom, and pan
5. **WindowManager** (`src/gui/window_manager.py`) - OpenCV window lifecycle management

### Key Design Patterns

- **Factory Pattern**: `src/utils/viewer_factory.py` provides factory functions like `create_basic_viewer()`, `create_viewer_with_common_controls()`
- **Observer Pattern**: Trackbar callbacks and event handling system
- **Fluent Interface**: Configuration building with ViewerConfig
- **Strategy Pattern**: Pluggable image processing functions

### Module Structure
```
src/
├── core/           # ImageViewer main class
├── config/         # ViewerConfig management  
├── controls/       # TrackbarManager for real-time controls
├── events/         # MouseHandler for interactions
├── gui/            # WindowManager and UI components
├── analysis/       # Analysis modules (plotting, export, threshold)
└── utils/          # Factory methods and utilities
```

## Usage Patterns

### Creating a Viewer
```python
# Via factory (recommended)
from src.utils.viewer_factory import create_viewer_with_common_controls
viewer = create_viewer_with_common_controls()

# Direct instantiation
from src import ImageViewer, ViewerConfig
config = ViewerConfig()
trackbar_definitions = [...]
viewer = ImageViewer(config, trackbar_definitions, debug_mode)
```

### Trackbar Definitions Format
```python
trackbar_definitions = [
    {"name": "Display Name", "param_name": "code_name", "max_value": 255, "initial_value": 128},
    {"name": "Odd Size", "param_name": "kernel", "max_value": 31, "callback": "odd", "initial_value": 5},
    {"name": "Image Selector", "param_name": "show", "max_value": "num_images-1", "initial_value": 0}
]
```

### Main Loop Pattern
```python
while viewer.should_loop_continue():
    params = viewer.trackbar.parameters
    # Process images using params
    viewer.display_images = [(image, "title"), ...]
viewer.cleanup_viewer()
```

## Dependencies

- **opencv-python**: Core image processing and GUI
- **numpy**: Array operations and image data handling
- **matplotlib**: Optional plotting functionality

## Headless vs GUI Mode

The application supports both interactive GUI mode and headless automation mode controlled by the `APP_DEBUG_MODE` flag. In headless mode, set `max_headless_iterations` parameter to limit processing cycles.