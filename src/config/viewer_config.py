
from typing import List, Tuple, Dict, Any, Optional

class ViewerConfig:
    """Configuration settings for the ImageViewer."""
    def __init__(self):
        self.screen_width: int = 800
        self.screen_height: int = 800
        self.text_window_width: int = 400
        self.text_window_height: int = 400
        self.text_line_height: int = 20
        self.min_size_ratio: float = 0.1
        self.max_size_ratio: float = 10.0
        self.trackbar_window_name: str = "Trackbars"
        self.process_window_name: str = "Process Window"
        self.text_window_name: str = "Text Window"
        self.trackbar_window_width: int = 800
        self.trackbar_window_height: int = 800
        self.trackbar: List[Dict[str, Any]] = []
        self.enable_debug: bool = True
        self.min_window_size: Tuple[int, int] = (100, 100)
        self.desktop_resolution: Optional[Tuple[int, int]] = None

    def validate(self):
        """Validate configuration settings"""
        if self.screen_width <= 0 or self.screen_height <= 0:
            raise ValueError("Screen dimensions must be positive")
        if self.min_size_ratio <= 0 or self.max_size_ratio <= 0:
            raise ValueError("Size ratios must be positive")
        if self.min_size_ratio > self.max_size_ratio:
            raise ValueError("min_size_ratio cannot be greater than max_size_ratio")

    # Fluent interface for easier configuration
    def set_window_size(self, width: int, height: int) -> 'ViewerConfig':
        """Set the main window size."""
        self.screen_width = width
        self.screen_height = height
        return self

    def set_debug_mode(self, enabled: bool) -> 'ViewerConfig':
        """Enable or disable debug/UI mode."""
        self.enable_debug = enabled
        return self

    def add_trackbar(self, trackbar_config: Dict[str, Any]) -> 'ViewerConfig':
        """Add a trackbar configuration."""
        self.trackbar.append(trackbar_config)
        return self

    def add_trackbars(self, *trackbar_configs: Dict[str, Any]) -> 'ViewerConfig':
        """Add multiple trackbar configurations."""
        self.trackbar.extend(trackbar_configs)
        return self

    def set_trackbars(self, trackbar_list: List[Dict[str, Any]]) -> 'ViewerConfig':
        """Set the complete trackbar list."""
        self.trackbar = trackbar_list
        return self

    @classmethod
    def create_simple(cls, enable_ui: bool = True, window_size: Tuple[int, int] = (800, 600)) -> 'ViewerConfig':
        """Create a simple configuration with minimal setup."""
        config = cls()
        config.enable_debug = enable_ui
        config.screen_width, config.screen_height = window_size
        return config

    @classmethod
    def create_with_trackbars(cls, trackbars: List[Dict[str, Any]], enable_ui: bool = True) -> 'ViewerConfig':
        """Create configuration with trackbars in one call."""
        config = cls.create_simple(enable_ui)
        config.trackbar = trackbars
        return config
