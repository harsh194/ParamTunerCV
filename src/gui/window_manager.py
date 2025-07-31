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
        created until create_windows() is called.
        
        Args:
            config: ViewerConfig instance containing window configuration
                   including names, sizes, and debug mode settings.
        """
        self.config = config
        self.windows_created = False

    def create_windows(self, mouse_callback: Callable, text_mouse_callback: Callable, 
                      create_text_window: bool = True) -> None:
        """
        Create and configure all OpenCV windows with specified callbacks.
        
        Creates the main process window, optional text window, and trackbar window
        based on configuration settings. Sets up mouse callbacks for interaction
        and applies appropriate window flags and sizing.
        
        Windows are only created if debug mode is enabled in the configuration
        and they haven't been created previously.
        
        Args:
            mouse_callback: Callback function for mouse events in the process window.
                           Should have signature: callback(event, x, y, flags, param)
            text_mouse_callback: Callback function for mouse events in the text window.
                                Should have signature: callback(event, x, y, flags, param)
            create_text_window: Whether to create the text overlay window.
                               Defaults to True.
        
        Side Effects:
            - Creates OpenCV windows with specified properties
            - Registers mouse callbacks for user interaction
            - Sets windows_created flag to True on success
            - Prints error messages on failure
        
        Raises:
            Exception: Silently handled - prints error and sets windows_created to False
        """
        if self.windows_created: return
        if not self.config.enable_debug: # Don't create windows if debug is off
            # print("WindowManager: Debug mode is off, not creating windows.") # Optional log
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
            # print("WindowManager: Windows created successfully.") # Optional log
        except Exception as e:
            print(f"CRITICAL: Error creating OpenCV windows: {e}\n{traceback.format_exc()}")
            self.windows_created = False

    def destroy_all_windows(self) -> None:
        """
        Destroy all created OpenCV windows and clean up resources.
        
        Closes all OpenCV windows that were created by this manager and resets
        the internal state. Safe to call multiple times or when no windows exist.
        
        Side Effects:
            - Destroys all OpenCV windows
            - Sets windows_created flag to False
        """
        if self.windows_created:
            cv2.destroyAllWindows()
            self.windows_created = False
            # print("WindowManager: Windows destroyed.") # Optional log

    def resize_process_window(self, width: int, height: int) -> None:
        """
        Resize the main process window within configured constraints.
        
        Adjusts the size of the main process window while enforcing minimum
        and maximum size constraints from the configuration. Validates window
        existence and visibility before attempting resize.
        
        Args:
            width: Target width in pixels.
            height: Target height in pixels.
        
        Side Effects:
            - Resizes the process window if valid and visible
            - Applies size constraints from configuration
            - Silently handles resize errors
        
        Performance:
            Time Complexity: O(1) - Single window resize operation.
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
        original window titles for all visible OpenCV windows.
        
        Side Effects:
            - Restores titles for process, text, and trackbar windows
            - Only affects visible windows
            - Silently handles any errors during title restoration
        
        Performance:
            Time Complexity: O(1) - Fixed number of window title operations.
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
