from .thresholding_window import ThresholdingWindow
import tkinter as tk
from tkinter import ttk

class ThresholdingManager:
    def __init__(self, viewer):
        self.viewer = viewer
        self.thresholding_windows = {}
        self.color_spaces = ["BGR", "HSV", "HLS", "Lab", "Luv", "YCrCb", "XYZ", "Grayscale"]

    def open_colorspace_selection_window(self):
        if not self.viewer._internal_images: return
        current_idx = self.viewer.trackbar.parameters.get('show', 0)
        image, _ = self.viewer._internal_images[current_idx]
        is_grayscale = len(image.shape) == 2

        selection_window = tk.Toplevel()
        selection_window.title("Select Color Space for Thresholding")
        selection_window.geometry("450x250")

        ttk.Label(selection_window, text="Select a color space for advanced thresholding:").pack(pady=10)
        
        # Info label with color conversion note
        info_text = "Available methods: Range, Simple, Otsu, Triangle, Adaptive\nAll color spaces supported with automatic conversion"
        info_label = ttk.Label(selection_window, text=info_text, font=("Arial", 8), foreground="gray")
        info_label.pack(pady=5)
        
        # Additional note for grayscale images
        if is_grayscale:
            note_text = "Note: Grayscale image detected - color spaces will show converted results"
            note_label = ttk.Label(selection_window, text=note_text, font=("Arial", 7), foreground="blue")
            note_label.pack(pady=2)

        color_space_var = tk.StringVar()
        
        # Enhanced color space descriptions
        color_space_descriptions = {
            "BGR": "BGR - Standard OpenCV color format",
            "HSV": "HSV - Best for color-based detection",
            "HLS": "HLS - Alternative color representation", 
            "Lab": "Lab - Perceptually uniform color space",
            "Luv": "Luv - Another perceptually uniform space",
            "YCrCb": "YCrCb - Luma-chroma (JPEG standard)",
            "XYZ": "XYZ - Device-independent color space",
            "Grayscale": "Grayscale - Single intensity channel"
        }
        
        color_space_combo = ttk.Combobox(selection_window, textvariable=color_space_var, 
                                        values=self.color_spaces, state="readonly", width=30)
        color_space_combo.pack(pady=5)
        
        # Add description label that updates with selection
        desc_var = tk.StringVar()
        desc_label = ttk.Label(selection_window, textvariable=desc_var, font=("Arial", 8), foreground="darkgreen")
        desc_label.pack(pady=5)
        
        def update_description(event=None):
            selected = color_space_var.get()
            desc_var.set(color_space_descriptions.get(selected, ""))
        
        color_space_combo.bind('<<ComboboxSelected>>', update_description)
        
        # Always show all color spaces, but set default based on image type
        if is_grayscale:
            color_space_combo.set("Grayscale")  # Default to Grayscale for grayscale images
        else:
            color_space_combo.set("BGR")  # Default to BGR for color images
        
        # Always allow all color spaces for maximum flexibility
        color_space_combo['values'] = self.color_spaces
        
        # Set initial description
        update_description()

        def on_select():
            selected_color_space = color_space_var.get()
            selection_window.destroy()
            self.open_thresholding_window(selected_color_space)

        ttk.Button(selection_window, text="Select", command=on_select).pack(pady=10)

    def open_thresholding_window(self, color_space):
        # Check if window exists and is still valid
        if color_space in self.thresholding_windows:
            window = self.thresholding_windows[color_space]
            if window and window.root and window.window_created:
                try:
                    window.root.lift()
                    return  # Successfully lifted existing window
                except tk.TclError:
                    # Window was destroyed, remove from dictionary
                    del self.thresholding_windows[color_space]
            else:
                # Window is invalid, remove from dictionary
                del self.thresholding_windows[color_space]
        
        # Create new window
        window = ThresholdingWindow(self.viewer, color_space)
        window.create_window()
        # Set up cleanup callback
        window.set_close_callback(lambda: self._on_window_closed(color_space))
        self.thresholding_windows[color_space] = window

    def _on_window_closed(self, color_space):
        """Called when a thresholding window is closed."""
        if color_space in self.thresholding_windows:
            del self.thresholding_windows[color_space]

    def cleanup_windows(self):
        for window in list(self.thresholding_windows.values()):  # Use list() to avoid dict change during iteration
            if window:
                window.destroy_window()
        self.thresholding_windows.clear()

    def update_all_thresholds(self):
        for window in list(self.thresholding_windows.values()):  # Use list() to avoid dict change during iteration
            if window and window.window_created:
                window.update_threshold()
