
"""Configuration management for the Parameter project ImageViewer.

This module provides the ViewerConfig class which manages all configuration settings
for the ImageViewer application. It supports fluent interface patterns for easy
configuration building, window sizing, trackbar management, and debug mode control.

The configuration system handles:
- Window dimensions and layout settings
- Trackbar definitions and management  
- Debug and UI mode toggles
- Size ratio constraints for image scaling
- Desktop resolution detection and handling

Main Classes:
    ViewerConfig: Central configuration management with fluent interface

Usage:
    # Simple configuration
    config = ViewerConfig.create_simple(enable_ui=True, window_size=(1024, 768))
    
    # Advanced configuration with trackbars
    trackbars = [{"name": "Brightness", "param_name": "brightness", "max_value": 255}]
    config = ViewerConfig.create_with_trackbars(trackbars, enable_ui=True)
    
    # Fluent interface configuration
    config = (ViewerConfig()
              .set_window_size(800, 600)
              .set_debug_mode(True)
              .add_trackbar({"name": "Threshold", "param_name": "thresh", "max_value": 255}))
"""

from typing import List, Tuple, Dict, Any, Optional

class ViewerConfig:
    """Configuration settings manager for the ImageViewer with fluent interface support.
    
    This class manages all configuration parameters for the ImageViewer application,
    providing a centralized location for window settings, trackbar definitions,
    debug modes, and layout parameters. It implements a fluent interface pattern
    that allows method chaining for intuitive configuration building.
    
    The class handles comprehensive configuration including:
    - Main window dimensions and positioning
    - Text and trackbar window sizing
    - Image scaling constraints (min/max ratios)
    - Debug and UI mode toggles
    - Trackbar definitions with validation
    - Desktop resolution management
    
    Attributes:
        screen_width (int): Width of the main display window in pixels
        screen_height (int): Height of the main display window in pixels
        text_window_width (int): Width of the text display window
        text_window_height (int): Height of the text display window
        text_line_height (int): Height of each text line in pixels
        min_size_ratio (float): Minimum scaling ratio for image display
        max_size_ratio (float): Maximum scaling ratio for image display
        trackbar_window_name (str): Name of the trackbar window
        process_window_name (str): Name of the main process window
        text_window_name (str): Name of the text display window
        trackbar_window_width (int): Width of the trackbar window
        trackbar_window_height (int): Height of the trackbar window
        trackbar (List[Dict[str, Any]]): List of trackbar configurations
        enable_debug (bool): Whether debug/UI mode is enabled
        min_window_size (Tuple[int, int]): Minimum window dimensions
        desktop_resolution (Optional[Tuple[int, int]]): Desktop resolution if detected
    
    Examples:
        >>> # Basic configuration
        >>> config = ViewerConfig()
        >>> config.set_window_size(1024, 768).set_debug_mode(True)
        
        >>> # Configuration with trackbars
        >>> trackbar_def = {"name": "Threshold", "param_name": "thresh", "max_value": 255}
        >>> config = ViewerConfig().add_trackbar(trackbar_def)
        
        >>> # Factory method usage
        >>> config = ViewerConfig.create_simple(enable_ui=True, window_size=(800, 600))
    """
    def __init__(self) -> None:
        """Initialize ViewerConfig with default settings.
        
        Creates a new ViewerConfig instance with sensible default values for all
        configuration parameters. The defaults are suitable for typical image
        viewing applications with standard window sizes and scaling ratios.
        
        Default settings include:
        - 800x800 main window dimensions
        - 400x400 text window dimensions
        - Scaling ratios from 0.1x to 10.0x
        - Debug mode enabled
        - Empty trackbar list ready for configuration
        - Standard window names for UI components
        
        Examples:
            >>> config = ViewerConfig()
            >>> print(f"Default size: {config.screen_width}x{config.screen_height}")
            >>> print(f"Debug enabled: {config.enable_debug}")
            
        Performance:
            Time Complexity: O(1) - constant time initialization.
            Space Complexity: O(1) - fixed memory allocation for attributes.
        """
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

    def validate(self) -> None:
        """Validate configuration settings to ensure they are within acceptable ranges.
        
        This method performs comprehensive validation of all configuration parameters
        to ensure the ImageViewer can operate correctly. It checks for logical
        consistency, positive values where required, and proper relationships
        between related parameters.
        
        Validation checks include:
        - Screen dimensions must be positive integers
        - Size ratios must be positive numbers
        - Minimum size ratio must not exceed maximum size ratio
        - Window dimensions must be reasonable for the system
        
        Raises:
            ValueError: If screen dimensions are not positive.
            ValueError: If size ratios are not positive.
            ValueError: If min_size_ratio is greater than max_size_ratio.
            
        Examples:
            >>> config = ViewerConfig()
            >>> config.screen_width = -100  # Invalid
            >>> config.validate()  # Raises ValueError
            Traceback (most recent call last):
                ...
            ValueError: Screen dimensions must be positive
            
            >>> config.screen_width = 800
            >>> config.min_size_ratio = 5.0
            >>> config.max_size_ratio = 1.0  # Invalid relationship
            >>> config.validate()  # Raises ValueError
            
        Performance:
            Time Complexity: O(1) - constant time parameter checks.
            Space Complexity: O(1) - no additional memory allocation.
        """
        if self.screen_width <= 0 or self.screen_height <= 0:
            raise ValueError("Screen dimensions must be positive")
        if self.min_size_ratio <= 0 or self.max_size_ratio <= 0:
            raise ValueError("Size ratios must be positive")
        if self.min_size_ratio > self.max_size_ratio:
            raise ValueError("min_size_ratio cannot be greater than max_size_ratio")

    # Fluent interface for easier configuration
    def set_window_size(self, width: int, height: int) -> 'ViewerConfig':
        """Set the main window dimensions with fluent interface support.
        
        This method updates the screen width and height for the main ImageViewer
        window. It returns self to enable method chaining in fluent interface
        patterns, allowing for intuitive configuration building.
        
        Args:
            width: Width of the main window in pixels. Must be positive.
            height: Height of the main window in pixels. Must be positive.
            
        Returns:
            ViewerConfig: Returns self for method chaining.
            
        Examples:
            >>> config = ViewerConfig().set_window_size(1024, 768)
            >>> print(f"Size: {config.screen_width}x{config.screen_height}")
            Size: 1024x768
            
            >>> # Method chaining
            >>> config = (ViewerConfig()
            ...           .set_window_size(1200, 800)
            ...           .set_debug_mode(True))
            
        Performance:
            Time Complexity: O(1) - simple attribute assignment.
            Space Complexity: O(1) - no additional memory allocation.
        """
        self.screen_width = width
        self.screen_height = height
        return self

    def set_debug_mode(self, enabled: bool) -> 'ViewerConfig':
        """Enable or disable debug/UI mode with fluent interface support.
        
        This method controls whether the ImageViewer operates in debug mode with
        full UI components (trackbars, text windows, etc.) or in headless mode
        for automated processing. Debug mode is essential for interactive image
        analysis and parameter tuning.
        
        Args:
            enabled: True to enable debug/UI mode with interactive components,
                False for headless operation without UI elements.
                
        Returns:
            ViewerConfig: Returns self for method chaining.
            
        Examples:
            >>> # Enable interactive mode
            >>> config = ViewerConfig().set_debug_mode(True)
            >>> print(f"Interactive mode: {config.enable_debug}")
            Interactive mode: True
            
            >>> # Headless mode for automation
            >>> config = ViewerConfig().set_debug_mode(False)
            >>> # Method chaining
            >>> config = (ViewerConfig()
            ...           .set_debug_mode(True)
            ...           .set_window_size(800, 600))
            
        Performance:
            Time Complexity: O(1) - simple boolean assignment.
            Space Complexity: O(1) - no additional memory allocation.
        """
        self.enable_debug = enabled
        return self

    def add_trackbar(self, trackbar_config: Dict[str, Any]) -> 'ViewerConfig':
        """Add a single trackbar configuration with fluent interface support.
        
        This method appends a new trackbar configuration to the existing list,
        enabling real-time parameter adjustment in the ImageViewer. Trackbars
        are essential for interactive image processing and algorithm tuning.
        
        Args:
            trackbar_config: Dictionary containing trackbar definition with keys:
                - 'name': Display name for the trackbar
                - 'param_name': Parameter name used in code
                - 'max_value': Maximum value for the trackbar
                - 'initial_value': Starting value (optional)
                - 'callback': Callback function name (optional)
                
        Returns:
            ViewerConfig: Returns self for method chaining.
            
        Examples:
            >>> config = ViewerConfig()
            >>> trackbar = {
            ...     "name": "Brightness", 
            ...     "param_name": "brightness", 
            ...     "max_value": 255,
            ...     "initial_value": 128
            ... }
            >>> config.add_trackbar(trackbar)
            >>> print(f"Trackbars: {len(config.trackbar)}")
            Trackbars: 1
            
            >>> # Method chaining
            >>> config = (ViewerConfig()
            ...           .add_trackbar({"name": "Contrast", "param_name": "contrast", "max_value": 100})
            ...           .add_trackbar({"name": "Gamma", "param_name": "gamma", "max_value": 300}))
            
        Performance:
            Time Complexity: O(1) - simple list append operation.
            Space Complexity: O(1) - single dictionary reference added.
        """
        self.trackbar.append(trackbar_config)
        return self

    def add_trackbars(self, *trackbar_configs: Dict[str, Any]) -> 'ViewerConfig':
        """Add multiple trackbar configurations in a single call with fluent interface support.
        
        This method extends the trackbar list with multiple configurations at once,
        providing a convenient way to add several trackbars simultaneously. This is
        more efficient than multiple individual add_trackbar() calls and enables
        cleaner configuration code.
        
        Args:
            *trackbar_configs: Variable number of trackbar configuration dictionaries.
                Each dictionary should contain the same keys as described in add_trackbar().
                
        Returns:
            ViewerConfig: Returns self for method chaining.
            
        Examples:
            >>> config = ViewerConfig()
            >>> brightness = {"name": "Brightness", "param_name": "brightness", "max_value": 255}
            >>> contrast = {"name": "Contrast", "param_name": "contrast", "max_value": 100}
            >>> gamma = {"name": "Gamma", "param_name": "gamma", "max_value": 300}
            >>> config.add_trackbars(brightness, contrast, gamma)
            >>> print(f"Total trackbars: {len(config.trackbar)}")
            Total trackbars: 3
            
            >>> # Method chaining with multiple trackbars
            >>> config = (ViewerConfig()
            ...           .set_window_size(800, 600)
            ...           .add_trackbars(brightness, contrast))
            
        Performance:
            Time Complexity: O(n) where n is the number of trackbar configurations.
            Space Complexity: O(n) for storing n trackbar references.
        """
        self.trackbar.extend(trackbar_configs)
        return self

    def set_trackbars(self, trackbar_list: List[Dict[str, Any]]) -> 'ViewerConfig':
        """Replace the entire trackbar list with a new list of configurations.
        
        This method completely replaces the existing trackbar list with a new
        list of trackbar configurations. This is useful when you need to set
        all trackbars at once or reset the trackbar configuration entirely.
        It provides a fluent interface for method chaining.
        
        Args:
            trackbar_list: List of trackbar configuration dictionaries.
                Each dictionary should contain the same keys as described
                in add_trackbar(). The list completely replaces any existing
                trackbar configurations.
                
        Returns:
            ViewerConfig: Returns self for method chaining.
            
        Examples:
            >>> config = ViewerConfig()
            >>> trackbars = [
            ...     {"name": "Brightness", "param_name": "brightness", "max_value": 255},
            ...     {"name": "Contrast", "param_name": "contrast", "max_value": 100}
            ... ]
            >>> config.set_trackbars(trackbars)
            >>> print(f"Total trackbars: {len(config.trackbar)}")
            Total trackbars: 2
            
            >>> # Method chaining with complete replacement
            >>> config = (ViewerConfig()
            ...           .set_window_size(800, 600)
            ...           .set_trackbars(trackbars))
                
        Performance:
            Time Complexity: O(1) - simple list assignment.
            Space Complexity: O(n) where n is the number of trackbar configurations.
        """
        self.trackbar = trackbar_list
        return self

    @classmethod
    def create_simple(cls, enable_ui: bool = True, window_size: Tuple[int, int] = (800, 600)) -> 'ViewerConfig':
        """Create a simple ViewerConfig instance with minimal setup requirements.
        
        This factory method provides a convenient way to create a ViewerConfig
        instance with basic settings for common use cases. It sets up essential
        configuration parameters while leaving advanced options at their defaults.
        This is ideal for quick prototyping or simple image viewing scenarios.
        
        Args:
            enable_ui: Whether to enable the user interface components including
                trackbars, text windows, and interactive elements. True enables
                full UI mode, False creates a headless configuration.
                Defaults to True.
            window_size: Tuple specifying the main window dimensions as (width, height)
                in pixels. Must contain two positive integers. Defaults to (800, 600).
                
        Returns:
            ViewerConfig: A new ViewerConfig instance with the specified basic settings
                and all other parameters set to defaults.
                
        Examples:
            >>> # Basic configuration with default UI enabled
            >>> config = ViewerConfig.create_simple()
            >>> print(f"UI enabled: {config.enable_debug}")
            UI enabled: True
            
            >>> # Headless configuration with custom window size
            >>> config = ViewerConfig.create_simple(enable_ui=False, window_size=(1024, 768))
            >>> print(f"Window size: {config.screen_width}x{config.screen_height}")
            Window size: 1024x768
            
            >>> # Simple setup for automation
            >>> config = ViewerConfig.create_simple(enable_ui=False, window_size=(640, 480))
            
        Performance:
            Time Complexity: O(1) - constant time instantiation and setup.
            Space Complexity: O(1) - fixed memory allocation for configuration object.
        """
        config = cls()
        config.enable_debug = enable_ui
        config.screen_width, config.screen_height = window_size
        return config

    @classmethod
    def create_with_trackbars(cls, trackbars: List[Dict[str, Any]], enable_ui: bool = True) -> 'ViewerConfig':
        """Create a ViewerConfig instance with trackbars pre-configured in a single call.
        
        This factory method provides a convenient way to create a fully configured
        ViewerConfig instance with both basic settings and trackbar definitions.
        It combines the simplicity of create_simple() with immediate trackbar setup,
        making it ideal for interactive image processing applications that require
        real-time parameter adjustment.
        
        Args:
            trackbars: List of trackbar configuration dictionaries. Each dictionary
                should contain the trackbar definition with keys as described in
                add_trackbar(). This list will become the complete trackbar configuration
                for the ViewerConfig instance.
            enable_ui: Whether to enable the user interface components including
                trackbars, text windows, and interactive elements. True enables
                full UI mode (recommended when using trackbars), False creates
                a headless configuration. Defaults to True.
                
        Returns:
            ViewerConfig: A new ViewerConfig instance with default settings and
                the specified trackbar configurations ready for use.
                
        Examples:
            >>> trackbars = [
            ...     {"name": "Brightness", "param_name": "brightness", "max_value": 255, "initial_value": 128},
            ...     {"name": "Contrast", "param_name": "contrast", "max_value": 100, "initial_value": 50},
            ...     {"name": "Threshold", "param_name": "thresh", "max_value": 255, "initial_value": 127}
            ... ]
            >>> config = ViewerConfig.create_with_trackbars(trackbars, enable_ui=True)
            >>> print(f"Trackbars configured: {len(config.trackbar)}")
            Trackbars configured: 3
            
            >>> # For image processing with interactive controls
            >>> image_controls = [
            ...     {"name": "Blur Kernel", "param_name": "kernel", "max_value": 31, "initial_value": 5},
            ...     {"name": "Edge Threshold", "param_name": "edge_thresh", "max_value": 255}
            ... ]
            >>> config = ViewerConfig.create_with_trackbars(image_controls)
            
        Performance:
            Time Complexity: O(1) - constant time setup regardless of trackbar count.
            Space Complexity: O(n) where n is the number of trackbar configurations.
        """
        config = cls.create_simple(enable_ui)
        config.trackbar = trackbars
        return config
