"""
OpenCV window management module for the Parameter image viewer application.

This module provides centralized management of OpenCV windows used for image
display, text overlays, and trackbar controls. It handles window creation,
lifecycle management, resizing, and title management with proper error handling
and configuration-based control.

Main Classes:
    - WindowManager: Central manager for OpenCV window operations including
      creation, resizing, destruction, and title management

Features:
    - Configuration-driven window creation
    - Multiple window type support (process, text, trackbar)
    - Automatic window sizing and constraints
    - Mouse callback registration
    - Window state validation and recovery
    - Debug mode integration
    - Error handling and graceful degradation
    - Window title refresh for matplotlib compatibility

Window Types:
    - Process Window: Main image display window with mouse interaction
    - Text Window: Overlay information and status display
    - Trackbar Window: Parameter control interface

Dependencies:
    - cv2: OpenCV for window management and display
    - typing: Type hints for callback functions
    - ViewerConfig: Configuration management for window properties

Usage:
    window_manager = WindowManager(config)
    window_manager.create_windows(mouse_callback, text_callback)
    window_manager.resize_process_window(800, 600)
    window_manager.refresh_window_titles()
    window_manager.destroy_all_windows()
"""

import cv2
import traceback
from typing import Callable
from ..config.viewer_config import ViewerConfig

class WindowManager:
    """
    Comprehensive manager for OpenCV window operations and lifecycle.
    
    This class provides centralized management of all OpenCV windows used by the
    Parameter image viewer, including the main process window, text overlay window,
    and trackbar control window. It handles creation, configuration, resizing,
    and destruction of windows with proper error handling and state management.
    
    The manager integrates with the configuration system to respect debug mode
    settings and window sizing preferences. It ensures consistent window behavior
    across different platforms and handles edge cases like window visibility
    validation and title restoration after matplotlib operations.
    
    Attributes:
        config: ViewerConfig instance containing window configuration settings.
        windows_created (bool): Flag indicating whether windows have been created.
    
    Examples:
        >>> config = ViewerConfig()
        >>> window_manager = WindowManager(config)
        >>> window_manager.create_windows(
        ...     mouse_callback=handle_mouse,
        ...     text_mouse_callback=handle_text_mouse
        ... )
        >>> window_manager.resize_process_window(1024, 768)
        >>> window_manager.destroy_all_windows()
    """
    def __init__(self, config: ViewerConfig) -> None:
        """
        Initialize the window manager with the provided configuration.
        
        Sets up the window manager with configuration settings that control
        window properties, sizes, and behavior. The actual windows are not
        created until create_windows() is called to allow for lazy initialization.
        
        Args:
            config (ViewerConfig): ViewerConfig instance containing window configuration
                                  including window names, sizes, debug mode settings,
                                  and trackbar definitions.
        
        Returns:
            None: Constructor initializes instance, no return value.
        
        Examples:
            >>> from src.config.viewer_config import ViewerConfig
            >>> config = ViewerConfig()
            >>> config.screen_width = 800
            >>> config.screen_height = 600
            >>> window_manager = WindowManager(config)
            >>> print(window_manager.windows_created)  # False
            
        Performance:
            Time Complexity: O(1) - Simple configuration storage and flag initialization.
            Space Complexity: O(1) - Fixed memory for configuration reference and state.
        """
        self.config = config
        self.windows_created = False

    def create_windows(self, mouse_callback: Callable, text_mouse_callback: Callable, 
                      create_text_window: bool = True) -> None:
        """
        Create and configure all OpenCV windows with specified callbacks.
        
        Creates the main process window, optional text window, and trackbar window
        based on configuration settings. Sets up mouse callbacks for interaction
        and applies appropriate window flags and sizing. Only creates windows
        if debug mode is enabled and windows haven't been created previously.
        
        Args:
            mouse_callback (Callable): Callback function for mouse events in the process window.
                                      Should have signature: callback(event, x, y, flags, param)
                                      where event is cv2 mouse event type.
            text_mouse_callback (Callable): Callback function for mouse events in the text window.
                                           Should have signature: callback(event, x, y, flags, param)
            create_text_window (bool): Whether to create the text overlay window.
                                     Defaults to True. False skips text window creation.
        
        Returns:
            None: Creates windows as side effect, no return value.
        
        Examples:
            >>> def handle_mouse(event, x, y, flags, param):
            ...     if event == cv2.EVENT_LBUTTONDOWN:
            ...         print(f"Clicked at ({x}, {y})")
            >>> def handle_text_mouse(event, x, y, flags, param):
            ...     pass  # Handle text window mouse events
            >>> window_manager = WindowManager(config)
            >>> window_manager.create_windows(handle_mouse, handle_text_mouse)
            >>> # Three OpenCV windows created with mouse callbacks
            >>> print(window_manager.windows_created)  # True
            
        Performance:
            Time Complexity: O(1) - Fixed number of window creation operations.
            Space Complexity: O(1) - Fixed memory for OpenCV windows and callbacks.
        """
        if self.windows_created: return
        if not self.config.enable_debug: # Don't create windows if debug is off
            return

        try:
            cv2.namedWindow(self.config.process_window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
            cv2.resizeWindow(self.config.process_window_name, self.config.screen_width, self.config.screen_height)
            cv2.setMouseCallback(self.config.process_window_name, mouse_callback)

            if create_text_window:
                cv2.namedWindow(self.config.text_window_name, cv2.WINDOW_AUTOSIZE)
                cv2.resizeWindow(self.config.text_window_name, self.config.text_window_width, self.config.text_window_height)
                cv2.setMouseCallback(self.config.text_window_name, text_mouse_callback)

            if self.config.trackbar: # Only create trackbar window if trackbar defs exist
                cv2.namedWindow(self.config.trackbar_window_name, cv2.WINDOW_AUTOSIZE)
                cv2.resizeWindow(self.config.trackbar_window_name, self.config.trackbar_window_width, self.config.trackbar_window_height)
            
            self.windows_created = True
        except Exception as e:
            print(f"CRITICAL: Error creating OpenCV windows: {e}\n{traceback.format_exc()}")
            self.windows_created = False

    def destroy_all_windows(self) -> None:
        """
        Destroy all created OpenCV windows and clean up resources.
        
        Closes all OpenCV windows that were created by this manager and resets
        the internal state. Safe to call multiple times or when no windows exist.
        Ensures proper cleanup of OpenCV resources and window handles.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Destroys windows as side effect, no return value.
        
        Examples:
            >>> window_manager = WindowManager(config)
            >>> window_manager.create_windows(mouse_cb, text_cb)
            >>> print(window_manager.windows_created)  # True
            >>> window_manager.destroy_all_windows()
            >>> print(window_manager.windows_created)  # False
            >>> # Safe to call multiple times
            >>> window_manager.destroy_all_windows()  # No error
            
        Performance:
            Time Complexity: O(1) - Single OpenCV destroy operation for all windows.
            Space Complexity: O(1) - Frees memory allocated for window resources.
        """
        if self.windows_created:
            cv2.destroyAllWindows()
            self.windows_created = False

    def resize_process_window(self, width: int, height: int) -> None:
        """
        Resize the main process window within configured constraints.
        
        Adjusts the size of the main process window while enforcing minimum
        and maximum size constraints from the configuration. Validates window
        existence and visibility before attempting resize to prevent errors.
        
        Args:
            width (int): Target width in pixels. Must be positive integer.
                        Will be clamped to configuration constraints.
            height (int): Target height in pixels. Must be positive integer.
                         Will be clamped to configuration constraints.
        
        Returns:
            None: Resizes window as side effect, no return value.
        
        Examples:
            >>> window_manager = WindowManager(config)
            >>> window_manager.create_windows(mouse_cb, text_cb)
            >>> window_manager.resize_process_window(1024, 768)
            >>> # Process window resized to 1024x768 (within constraints)
            >>> window_manager.resize_process_window(50, 50)
            >>> # Resized to minimum allowed size (constraints applied)
            >>> window_manager.resize_process_window(5000, 5000)
            >>> # Resized to maximum allowed size (constraints applied)
            
        Performance:
            Time Complexity: O(1) - Single window resize operation with bounds checking.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if not self.windows_created: return # No window to resize
        try:
            if cv2.getWindowProperty(self.config.process_window_name, cv2.WND_PROP_VISIBLE) < 1:
                return
            min_w, min_h = self.config.min_window_size
            max_w, max_h = self.config.screen_width * 2, self.config.screen_height * 2
            if self.config.desktop_resolution:
                max_w, max_h = self.config.desktop_resolution
            width = max(min_w, min(width, max_w))
            height = max(min_h, min(height, max_h))
            cv2.resizeWindow(self.config.process_window_name, width, height)
        except cv2.error: pass 
        except Exception: pass

    def refresh_window_titles(self) -> None:
        """
        Refresh OpenCV window titles to ensure visibility after matplotlib operations.
        
        Matplotlib operations can sometimes interfere with OpenCV window titles,
        making them disappear or become corrupted. This method restores the
        original window titles for all visible OpenCV windows created by this manager.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Refreshes window titles as side effect, no return value.
        
        Examples:
            >>> window_manager = WindowManager(config)
            >>> window_manager.create_windows(mouse_cb, text_cb)
            >>> # After matplotlib plotting operations that might corrupt titles
            >>> import matplotlib.pyplot as plt
            >>> plt.show()  # May interfere with OpenCV window titles
            >>> window_manager.refresh_window_titles()
            >>> # Window titles restored to original names
            
        Performance:
            Time Complexity: O(1) - Fixed number of window title restoration operations.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if not self.windows_created:
            return
        
        try:
            # Force refresh of OpenCV windows to restore titles
            if cv2.getWindowProperty(self.config.process_window_name, cv2.WND_PROP_VISIBLE) >= 1:
                cv2.setWindowTitle(self.config.process_window_name, self.config.process_window_name)
                
            if cv2.getWindowProperty(self.config.text_window_name, cv2.WND_PROP_VISIBLE) >= 1:
                cv2.setWindowTitle(self.config.text_window_name, self.config.text_window_name)
                
            if hasattr(self.config, 'trackbar_window_name') and cv2.getWindowProperty(self.config.trackbar_window_name, cv2.WND_PROP_VISIBLE) >= 1:
                cv2.setWindowTitle(self.config.trackbar_window_name, self.config.trackbar_window_name)
                
        except (cv2.error, Exception):
            # Silently handle any errors - window title refresh is not critical
            pass
