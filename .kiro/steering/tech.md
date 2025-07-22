# Technical Stack & Development Guidelines

## Tech Stack
- **Language**: Python 3.x
- **Core Libraries**:
  - OpenCV (opencv-python) - Image processing and visualization
  - NumPy - Numerical operations and array handling
  - Matplotlib - Plotting and visualization

## Project Structure
The Parameter project follows a modular architecture with clear separation of concerns:

- `src/` - Main package directory
  - `analysis/` - Image analysis functionality
  - `config/` - Configuration management
  - `controls/` - UI controls and trackbars
  - `core/` - Core functionality including the main ImageViewer
  - `events/` - Event handling (mouse, keyboard)
  - `gui/` - GUI components and window management
  - `utils/` - Utility functions and factory methods

## Development Guidelines

### Imports
- Use relative imports within the package
- Maintain backward compatibility with existing import paths
- Follow the import structure defined in `src/__init__.py`

### Code Style
- Follow PEP 8 conventions
- Use type hints for function parameters and return values
- Document classes and functions with docstrings

### API Design
- Maintain backward compatibility with existing API
- Use fluent interfaces for configuration where appropriate
- Prefer composition over inheritance

## Common Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running the Sample
```bash
python check.py
```

### Development Workflow
1. Make changes to the modular code structure
2. Ensure backward compatibility with existing code
3. Test with `check.py` to verify functionality