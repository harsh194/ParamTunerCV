"""
Thresholding manager module for the Parameter image viewer application.

This module provides centralized management of image thresholding operations
and windows. It handles the creation, lifecycle, and coordination of thresholding
windows across different color spaces and manages both unified and legacy
thresholding interfaces.

Main Classes:
    - ThresholdingManager: Central manager for thresholding operations that
      coordinates multiple thresholding windows and color space selections

Features:
    - Multi-color space thresholding support
    - Unified thresholding interface with integrated color space selection
    - Legacy simple thresholding windows for specific color spaces
    - Window lifecycle management and cleanup
    - Automatic window state validation and recovery
    - Coordinated threshold updates across all active windows

Supported Color Spaces:
    - BGR: Blue-Green-Red color space
    - HSV: Hue-Saturation-Value color space
    - HLS: Hue-Lightness-Saturation color space
    - Lab: L*a*b* color space
    - Luv: L*u*v* color space
    - YCrCb: Y-Chroma color space
    - XYZ: CIE XYZ color space
    - Grayscale: Single channel intensity

Dependencies:
    - ThresholdingWindow: Individual thresholding window implementation
    - tkinter: GUI framework for error handling

Usage:
    threshold_manager = ThresholdingManager(viewer)
    threshold_manager.open_colorspace_selection_window()
    threshold_manager.update_all_thresholds()
"""

from .thresholding_window import ThresholdingWindow
import tkinter as tk
from tkinter import ttk

class ThresholdingManager:
    """
    Central manager for image thresholding operations and window coordination.
    
    This class provides comprehensive management of thresholding functionality
    across multiple color spaces and window types. It handles the creation and
    lifecycle of both unified thresholding interfaces and legacy color space-specific
    windows, ensuring proper resource management and coordinated updates.
    
    The manager supports automatic color space detection based on image properties,
    window state validation and recovery, and coordinated threshold updates across
    all active thresholding windows.
    
    Attributes:
        viewer: Reference to the main ImageViewer instance.
        thresholding_windows (dict): Dictionary of active legacy thresholding windows
                                   keyed by color space name.
        unified_window: Reference to the unified thresholding window interface.
        color_spaces (list): List of supported color space names for thresholding.
    
    Examples:
        >>> manager = ThresholdingManager(image_viewer)
        >>> manager.open_colorspace_selection_window()
        # Opens unified thresholding interface
        
        >>> manager.open_thresholding_window("HSV")
        # Opens HSV-specific thresholding window
        
        >>> manager.update_all_thresholds()
        # Updates all active thresholding windows
    """
    def __init__(self, viewer) -> None:
        """
        Initialize the thresholding manager with viewer reference.
        
        Sets up the manager with references to the image viewer and initializes
        storage for thresholding windows and supported color spaces. Prepares
        the system for managing multiple thresholding interfaces.
        
        Args:
            viewer: The ImageViewer instance that this manager will provide
                   thresholding functionality for. Must be a valid ImageViewer
                   with loaded images and trackbar interface.
        
        Returns:
            None: Constructor initializes instance, no return value.
        
        Examples:
            >>> from src.core.image_viewer import ImageViewer
            >>> viewer = ImageViewer(config, trackbar_defs)
            >>> threshold_mgr = ThresholdingManager(viewer)
            >>> print(len(threshold_mgr.color_spaces))  # 8
            >>> print(threshold_mgr.thresholding_windows)  # {}
            
        Performance:
            Time Complexity: O(1) - Simple initialization with fixed list creation.
            Space Complexity: O(1) - Fixed memory for color space list and dictionaries.
        """
        self.viewer = viewer
        self.thresholding_windows = {}
        self.color_spaces = ["BGR", "HSV", "HLS", "Lab", "Luv", "YCrCb", "XYZ", "Grayscale"]

    def open_colorspace_selection_window(self) -> None:
        """
        Open the unified thresholding window with integrated color space selection.
        
        Creates or brings to front a comprehensive thresholding interface that
        combines color space selection with parameter controls in a single window.
        Automatically detects whether the current image is grayscale or color
        and sets appropriate default color space.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates/shows window as side effect, returns early if no images loaded.
        
        Examples:
            >>> threshold_mgr = ThresholdingManager(viewer)
            >>> threshold_mgr.open_colorspace_selection_window()
            >>> # Unified thresholding window opens with appropriate default colorspace
            >>> # For grayscale images: default is "Grayscale"
            >>> # For color images: default is "BGR"
            >>> 
            >>> # If window already open, brings to front instead of creating new
            >>> threshold_mgr.open_colorspace_selection_window()
            >>> # Existing window lifted to front
            
        Performance:
            Time Complexity: O(1) - Window creation or front-bringing operation.
            Space Complexity: O(1) - Single unified window instance.
        """
        if not self.viewer._internal_images: 
            return
            
        # Check if unified window already exists
        if hasattr(self, 'unified_window') and self.unified_window:
            try:
                if hasattr(self.unified_window, 'root') and self.unified_window.root:
                    self.unified_window.root.lift()
                    return
            except tk.TclError:
                self.unified_window = None
        
        # Determine default colorspace based on image type
        current_idx = self.viewer.trackbar.parameters.get('show', 0)
        image, _ = self.viewer._internal_images[current_idx]
        is_grayscale = len(image.shape) == 2
        
        # Set default colorspace but don't pre-select it
        default_colorspace = "Grayscale" if is_grayscale else "BGR"
        
        # Create unified thresholding window
        self.unified_window = ThresholdingWindow(self.viewer, default_colorspace)
        self.unified_window.create_unified_window()  # Create unified window with both colorspace and parameters
        # Set up cleanup callback
        self.unified_window.set_close_callback(lambda: self._on_unified_window_closed())

    def open_thresholding_window(self, color_space: str) -> None:
        """
        Open a legacy thresholding window for a specific color space.
        
        Creates or brings to front a simple thresholding window that operates
        in the specified color space using OpenCV windows only. This is the
        legacy interface maintained for backward compatibility and direct OpenCV control.
        
        Args:
            color_space (str): The color space name to use for thresholding.
                              Must be one of the supported color spaces:
                              "BGR", "HSV", "HLS", "Lab", "Luv", "YCrCb", "XYZ", "Grayscale".
        
        Returns:
            None: Creates/shows window as side effect, no return value.
        
        Examples:
            >>> threshold_mgr = ThresholdingManager(viewer)
            >>> threshold_mgr.open_thresholding_window("HSV")
            >>> # HSV thresholding window opens with OpenCV trackbars
            >>> 
            >>> # Opening same colorspace again brings existing window to front
            >>> threshold_mgr.open_thresholding_window("HSV")
            >>> # Existing HSV window brought to foreground
            >>> 
            >>> # Multiple colorspaces can be open simultaneously
            >>> threshold_mgr.open_thresholding_window("Lab")
            >>> # Lab window opens alongside existing HSV window
            
        Performance:
            Time Complexity: O(1) - Window creation or front-bringing with validation.
            Space Complexity: O(1) - Single window instance per color space.
        """
        # Check if window for this colorspace already exists and is valid
        if color_space in self.thresholding_windows:
            window = self.thresholding_windows[color_space]
            if window and window.window_created:
                try:
                    # Bring existing OpenCV windows to front
                    import cv2
                    cv2.setWindowProperty(window.threshold_viewer.config.process_window_name, cv2.WND_PROP_TOPMOST, 1)
                    cv2.setWindowProperty(window.threshold_viewer.config.process_window_name, cv2.WND_PROP_TOPMOST, 0)
                    return  # Successfully brought existing window to front
                except:
                    # Window was destroyed, remove from dictionary
                    del self.thresholding_windows[color_space]
            else:
                # Window is invalid, remove from dictionary
                del self.thresholding_windows[color_space]
        
        # Create new simple thresholding window (only OpenCV windows)
        window = ThresholdingWindow(self.viewer, color_space)
        window.create_simple_threshold_viewer()  # Only create OpenCV windows
        # Set up cleanup callback
        window.set_close_callback(lambda: self._on_window_closed(color_space))
        self.thresholding_windows[color_space] = window

    def _on_window_closed(self, color_space: str) -> None:
        """
        Handle cleanup when a legacy thresholding window is closed.
        
        Removes the window reference from the active windows dictionary
        to prevent memory leaks and invalid references. Called automatically
        when a legacy thresholding window is closed by the user.
        
        Args:
            color_space (str): The color space name of the window being closed.
                              Must match a key in thresholding_windows dictionary.
        
        Returns:
            None: Performs cleanup as side effect, no return value.
        
        Examples:
            >>> threshold_mgr = ThresholdingManager(viewer)
            >>> threshold_mgr.open_thresholding_window("HSV")
            >>> print("HSV" in threshold_mgr.thresholding_windows)  # True
            >>> # User closes HSV window, callback automatically called
            >>> threshold_mgr._on_window_closed("HSV")
            >>> print("HSV" in threshold_mgr.thresholding_windows)  # False
            
        Performance:
            Time Complexity: O(1) - Dictionary key deletion operation.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if color_space in self.thresholding_windows:
            del self.thresholding_windows[color_space]

    def _on_unified_window_closed(self) -> None:
        """
        Handle cleanup when the unified thresholding window is closed.
        
        Clears the unified window reference to prevent memory leaks
        and invalid references. Called automatically when the unified
        thresholding window is closed by the user.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Performs cleanup as side effect, no return value.
        
        Examples:
            >>> threshold_mgr = ThresholdingManager(viewer)
            >>> threshold_mgr.open_colorspace_selection_window()
            >>> print(hasattr(threshold_mgr, 'unified_window'))  # True
            >>> # User closes unified window, callback automatically called
            >>> threshold_mgr._on_unified_window_closed()
            >>> print(threshold_mgr.unified_window)  # None
            
        Performance:
            Time Complexity: O(1) - Simple attribute clearing operation.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if hasattr(self, 'unified_window'):
            self.unified_window = None

    def cleanup_windows(self) -> None:
        """
        Clean up and destroy all active thresholding windows.
        
        Performs comprehensive cleanup of both unified and legacy thresholding
        windows, ensuring proper resource deallocation and preventing memory leaks.
        This method is typically called when the main application is closing
        or when resetting the thresholding system.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Performs cleanup as side effect, no return value.
        
        Examples:
            >>> threshold_mgr = ThresholdingManager(viewer)
            >>> threshold_mgr.open_colorspace_selection_window()
            >>> threshold_mgr.open_thresholding_window("HSV")
            >>> threshold_mgr.open_thresholding_window("Lab")
            >>> print(len(threshold_mgr.thresholding_windows))  # 2
            >>> threshold_mgr.cleanup_windows()
            >>> print(len(threshold_mgr.thresholding_windows))  # 0
            >>> print(threshold_mgr.unified_window)  # None
            
        Performance:
            Time Complexity: O(n) where n is number of active thresholding windows.
            Space Complexity: O(1) - No additional memory allocation during cleanup.
        """
        # Clean up unified window if it exists
        if hasattr(self, 'unified_window') and self.unified_window:
            try:
                self.unified_window.destroy_window()
            except:
                pass
            self.unified_window = None
        
        # Clean up all legacy thresholding windows
        for window in list(self.thresholding_windows.values()):
            if window:
                window.destroy_window()
        self.thresholding_windows.clear()

    def update_all_thresholds(self) -> None:
        """
        Update threshold processing in all active thresholding windows.
        
        Triggers threshold recalculation and display updates in both the
        unified thresholding window and all active legacy thresholding windows.
        This ensures all thresholding interfaces stay synchronized with
        changes in the main image or parameters.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates all active windows as side effect, no return value.
        
        Examples:
            >>> threshold_mgr = ThresholdingManager(viewer)
            >>> threshold_mgr.open_colorspace_selection_window()
            >>> threshold_mgr.open_thresholding_window("HSV")
            >>> threshold_mgr.open_thresholding_window("Lab")
            >>> # Image changed in main viewer
            >>> threshold_mgr.update_all_thresholds()
            >>> # All 3 windows (unified + HSV + Lab) updated with new thresholds
            >>> 
            >>> # Safe to call even with no active windows
            >>> empty_mgr = ThresholdingManager(viewer)
            >>> empty_mgr.update_all_thresholds()  # No effect, no error
            
        Performance:
            Time Complexity: O(n) where n is number of active thresholding windows.
                           Each window update involves image processing operations.
            Space Complexity: O(1) - No additional memory allocation during updates.
        """
        # Update the unified window if it exists
        if hasattr(self, 'unified_window') and self.unified_window and self.unified_window.window_created:
            self.unified_window.update_threshold()
        
        # Update all active legacy thresholding windows
        for window in list(self.thresholding_windows.values()):
            if window and window.window_created:
                window.update_threshold()
