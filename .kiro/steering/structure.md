# Project Structure & Architecture

## Overview
The Parameter project follows a modular architecture that separates concerns into logical packages. The codebase has been refactored from a monolithic design to a well-organized, modular structure while maintaining backward compatibility.

## Directory Structure

```
parameter/
├── src/                      # Main package directory
│   ├── analysis/             # Image analysis functionality
│   │   ├── export/           # Data export capabilities
│   │   ├── plotting/         # Visualization and plotting
│   │   └── threshold/        # Thresholding algorithms
│   ├── config/               # Configuration management
│   ├── controls/             # UI controls and trackbars
│   ├── core/                 # Core functionality
│   ├── events/               # Event handling
│   ├── gui/                  # GUI components
│   └── utils/                # Utility functions
├── check.py                  # Sample usage script
└── requirements.txt          # Project dependencies
```

## Key Components

### Core Components
- **ImageViewer** (`src/core/image_viewer.py`): The main class that handles image display, interaction, and processing.
- **ViewerConfig** (`src/config/viewer_config.py`): Configuration settings for the viewer.

### UI Components
- **TrackbarManager** (`src/controls/trackbar_manager.py`): Manages trackbar controls for parameter tuning.
- **WindowManager** (`src/gui/window_manager.py`): Handles window creation and management.
- **MouseHandler** (`src/events/mouse_handler.py`): Processes mouse events for interaction.

### Analysis Components
- **ImageAnalyzer** (`src/analysis/__init__.py`): Provides image analysis capabilities.
- **PlotAnalyzer** (`src/analysis/plotting/plot_analyzer.py`): Handles plotting and visualization.
- **ExportManager** (`src/analysis/export/export_manager.py`): Manages data export to various formats.

### Factory Methods
- **Viewer Factory** (`src/utils/viewer_factory.py`): Provides factory methods for creating pre-configured viewers.

## Architecture Patterns

1. **Composition over Inheritance**: Components are composed rather than extended.
2. **Dependency Injection**: Components receive their dependencies through constructors.
3. **Fluent Interface**: Configuration objects use method chaining for a cleaner API.
4. **Factory Pattern**: Factory methods create pre-configured instances.
5. **Observer Pattern**: Event handling for mouse and UI interactions.

## Module Dependencies

- Core modules have minimal dependencies on other modules
- Analysis modules depend on core functionality
- GUI modules depend on events and controls
- Utils provide factory methods that depend on all other modules

## Backward Compatibility

The project maintains backward compatibility through:
- Re-exporting all public classes and functions in `src/__init__.py`
- Preserving the original API signatures
- Ensuring that existing code like `check.py` continues to work without modification