from .thresholding_window import ThresholdingWindow
import tkinter as tk
from tkinter import ttk

class ThresholdingManager:
    def __init__(self, viewer):
        self.viewer = viewer
        self.thresholding_windows = {}
        self.color_spaces = ["BGR", "HSV", "HLS", "Lab", "Luv", "YCrCb", "XYZ", "Grayscale"]

    def open_colorspace_selection_window(self):
        """Open unified thresholding window with colorspace selection and parameters."""
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

    def open_thresholding_window(self, color_space):
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

    def _on_window_closed(self, color_space):
        """Called when a thresholding window is closed."""
        if color_space in self.thresholding_windows:
            del self.thresholding_windows[color_space]

    def _on_unified_window_closed(self):
        """Called when the unified thresholding window is closed."""
        if hasattr(self, 'unified_window'):
            self.unified_window = None

    def cleanup_windows(self):
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

    def update_all_thresholds(self):
        # Update the unified window if it exists
        if hasattr(self, 'unified_window') and self.unified_window and self.unified_window.window_created:
            self.unified_window.update_threshold()
        
        # Update all active legacy thresholding windows
        for window in list(self.thresholding_windows.values()):
            if window and window.window_created:
                window.update_threshold()
