import tkinter as tk
from tkinter import ttk, filedialog
import cv2
import numpy as np
import json
from ..analysis.threshold.image_processor import ThresholdProcessor
from ..controls.trackbar_manager import TrackbarManager, make_trackbar

class ThresholdingWindow:
    def __init__(self, viewer, color_space):
        self.viewer = viewer
        self.color_space = color_space
        self.root = None
        self.window_created = False
        self.trackbar_manager = None
        
        # Initialize UI variables to prevent AttributeError
        self.threshold_method_var = None
        self.threshold_type_var = None
        self.adaptive_method_var = None
        
        # Track which trackbars are created for each method
        self.method_trackbars = {
            "Range": [],
            "Simple": [],
            "Otsu": [],
            "Triangle": [],
            "Adaptive": []
        }
        self.all_trackbar_configs = []
        self.current_method = None
        self.current_trackbars = []  # Keep track of currently displayed trackbars
        self.close_callback = None  # Callback to call when window is closed

        self.ranges = {
            "BGR": {"B": (0, 255), "G": (0, 255), "R": (0, 255)},
            "HSV": {"H": (0, 180), "S": (0, 255), "V": (0, 255)},
            "HLS": {"H": (0, 180), "L": (0, 255), "S": (0, 255)},
            "Lab": {"L": (0, 255), "a": (0, 255), "b": (0, 255)},
            "Luv": {"L": (0, 255), "u": (0, 255), "v": (0, 255)},
            "YCrCb": {"Y": (0, 255), "Cr": (0, 255), "Cb": (0, 255)},
            "XYZ": {"X": (0, 255), "Y": (0, 255), "Z": (0, 255)},
            "Grayscale": {"Gray": (0, 255)}
        }

    def create_window(self):
        if self.window_created:
            return

        self.image_window_name = f"Thresholded - {self.color_space}"
        cv2.namedWindow(self.image_window_name, cv2.WINDOW_NORMAL)

        self.trackbar_manager = TrackbarManager(self.image_window_name)
        
        self.root = tk.Toplevel()
        self.root.title(f"Thresholding Controls - {self.color_space}")

        if self.color_space == "Grayscale":
            # Thresholding method selection
            method_frame = ttk.LabelFrame(self.root, text="Thresholding Method")
            method_frame.pack(padx=10, pady=5, fill="x")
            
            self.threshold_method_var = tk.StringVar(value="Simple")
            methods = ["Simple", "Adaptive", "Otsu", "Triangle"]
            for method in methods:
                ttk.Radiobutton(method_frame, text=method, variable=self.threshold_method_var, 
                               value=method, command=self.on_method_change).pack(anchor="w")
            
            # Threshold type selection
            type_frame = ttk.LabelFrame(self.root, text="Threshold Type")
            type_frame.pack(padx=10, pady=5, fill="x")
            
            self.threshold_type_var = tk.StringVar(value="BINARY")
            types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
            self.threshold_type_combo = ttk.Combobox(type_frame, textvariable=self.threshold_type_var, 
                                                    values=types, state="readonly", width=15)
            self.threshold_type_combo.pack(padx=5, pady=5)
            self.threshold_type_combo.bind("<<ComboboxSelected>>", self._on_dropdown_threshold_type_change)
            
            # Adaptive method selection (initially hidden)
            self.adaptive_frame = ttk.LabelFrame(self.root, text="Adaptive Method")
            self.adaptive_method_var = tk.StringVar(value="MEAN_C")
            adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
            self.adaptive_method_combo = ttk.Combobox(self.adaptive_frame, textvariable=self.adaptive_method_var,
                                                     values=adaptive_methods, state="readonly", width=15)
            self.adaptive_method_combo.pack(padx=5, pady=5)
            self.adaptive_method_combo.bind("<<ComboboxSelected>>", self._on_dropdown_adaptive_method_change)
        else:
            # Color space thresholding method selection
            method_frame = ttk.LabelFrame(self.root, text="Thresholding Method")
            method_frame.pack(padx=10, pady=5, fill="x")
            
            self.threshold_method_var = tk.StringVar(value="Range")
            methods = ["Range", "Simple", "Otsu", "Triangle", "Adaptive"]
            for method in methods:
                ttk.Radiobutton(method_frame, text=method, variable=self.threshold_method_var, 
                               value=method, command=self.on_color_method_change).pack(anchor="w")
            
            # Threshold type selection for color spaces
            type_frame = ttk.LabelFrame(self.root, text="Threshold Type")
            type_frame.pack(padx=10, pady=5, fill="x")
            
            self.threshold_type_var = tk.StringVar(value="BINARY")
            types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
            self.threshold_type_combo = ttk.Combobox(type_frame, textvariable=self.threshold_type_var, 
                                                    values=types, state="readonly", width=15)
            self.threshold_type_combo.pack(padx=5, pady=5)
            self.threshold_type_combo.bind("<<ComboboxSelected>>", self._on_dropdown_threshold_type_change)
            
            # Advanced controls frame (initially hidden)
            self.advanced_controls_frame = ttk.LabelFrame(self.root, text="Advanced Controls")
            
            # Adaptive method selection for color spaces
            self.adaptive_method_var = tk.StringVar(value="MEAN_C")
            adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
            ttk.Label(self.advanced_controls_frame, text="Adaptive Method:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
            self.adaptive_method_combo = ttk.Combobox(self.advanced_controls_frame, textvariable=self.adaptive_method_var,
                                                     values=adaptive_methods, state="readonly", width=12)
            self.adaptive_method_combo.grid(row=0, column=1, padx=5, pady=2)
            self.adaptive_method_combo.bind("<<ComboboxSelected>>", self._on_dropdown_adaptive_method_change)

        # Status display frame
        status_frame = ttk.LabelFrame(self.root, text="Current Parameters")
        status_frame.pack(padx=10, pady=5, fill="x")
        
        self.status_text = tk.Text(status_frame, height=4, width=40, font=("Consolas", 8))
        self.status_text.pack(padx=5, pady=5, fill="x")
        self.status_text.config(state=tk.DISABLED)  # Read-only
        
        button_frame = ttk.Frame(self.root)
        button_frame.pack(padx=10, pady=10)
        
        # Add preset and save/load buttons
        ttk.Button(button_frame, text="Presets ▼", command=self._show_presets).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Config", command=self._save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Config", command=self._load_config).pack(side=tk.LEFT, padx=5)

        self.window_created = True
        self.viewer.log(f"Thresholding window for {self.color_space} created.")
        self.root.protocol("WM_DELETE_WINDOW", self.destroy_window)
        
        # Create trackbars after UI is set up
        self.create_trackbars()

    def create_trackbars(self):
        """Initialize trackbar definitions and create initial set."""
        if self.color_space == "Grayscale":
            self._define_grayscale_trackbars()
        else:
            self._define_color_trackbars()
        
        # Set initial method and create trackbars for it
        initial_method = "Simple" if self.color_space == "Grayscale" else "Range"
        self.current_method = initial_method
        self._create_trackbars_for_method(initial_method)
        self.update_threshold()
    
    def _define_grayscale_trackbars(self):
        """Define trackbar configurations for grayscale thresholding methods."""
        # Threshold Type trackbar (always shown)
        type_config = make_trackbar("Thresh Type [0=BIN,1=INV,2=TRU,3=TZ,4=TZI]", "threshold_type_idx", 4, 0, custom_callback=self._on_threshold_type_change)
        
        # Common trackbars for Simple/Otsu/Triangle methods
        common_configs = [
            type_config,
            make_trackbar("Threshold", "threshold", 255, 127, custom_callback=self.update_threshold),
            make_trackbar("Max Value", "max_value", 255, 255, custom_callback=self.update_threshold)
        ]
        
        # Adaptive method trackbars
        adaptive_configs = [
            make_trackbar("Thresh Type [0=BIN,1=INV]", "threshold_type_idx", 1, 0, custom_callback=self._on_threshold_type_change),
            make_trackbar("Block Size (must be odd)", "block_size", 99, 11, callback="odd", custom_callback=self.update_threshold),
            make_trackbar("C Constant (subtract from mean)", "c_constant", 50, 2, custom_callback=self.update_threshold),
            make_trackbar("Max Value", "max_value", 255, 255, custom_callback=self.update_threshold),
            make_trackbar("Adaptive [0=MEAN,1=GAUSSIAN]", "adaptive_method_idx", 1, 0, custom_callback=self._on_adaptive_method_change)
        ]
        
        # Organize trackbars by method
        self.method_trackbars["Simple"] = common_configs
        self.method_trackbars["Otsu"] = common_configs
        self.method_trackbars["Triangle"] = common_configs
        self.method_trackbars["Adaptive"] = adaptive_configs
    
    def _define_color_trackbars(self):
        """Define trackbar configurations for color space thresholding methods."""
        ranges = self.ranges.get(self.color_space, {})
        
        # Range thresholding trackbars (only min/max for each channel)
        range_configs = []
        for channel, (min_val, max_val) in ranges.items():
            range_configs.extend([
                make_trackbar(f"{channel} Min", f"{channel.lower()}_min", max_val, min_val, custom_callback=self.update_threshold),
                make_trackbar(f"{channel} Max", f"{channel.lower()}_max", max_val, max_val, custom_callback=self.update_threshold)
            ])
        
        # Advanced thresholding trackbars (threshold type + per channel parameters)
        type_config = make_trackbar("Thresh Type [0=BIN,1=INV,2=TRU,3=TZ,4=TZI]", "threshold_type_idx", 4, 0, custom_callback=self._on_threshold_type_change)
        
        advanced_configs = [type_config]
        for channel in ranges.keys():
            channel_lower = channel.lower()
            advanced_configs.extend([
                make_trackbar(f"{channel} Threshold", f"{channel_lower}_threshold", 255, 127, custom_callback=self.update_threshold),
                make_trackbar(f"{channel} Max Value", f"{channel_lower}_max_value", 255, 255, custom_callback=self.update_threshold)
            ])
        
        # Adaptive thresholding trackbars (limited threshold type + adaptive parameters)
        adaptive_type_config = make_trackbar("Thresh Type [0=BIN,1=INV]", "threshold_type_idx", 1, 0, custom_callback=self._on_threshold_type_change)
        adaptive_configs = [
            adaptive_type_config,
            make_trackbar("Adaptive [0=MEAN,1=GAUSSIAN]", "adaptive_method_idx", 1, 0, custom_callback=self._on_adaptive_method_change)
        ]
        
        for channel in ranges.keys():
            channel_lower = channel.lower()
            adaptive_configs.extend([
                make_trackbar(f"{channel} Max Value", f"{channel_lower}_max_value", 255, 255, custom_callback=self.update_threshold),
                make_trackbar(f"{channel} Block Size (odd)", f"{channel_lower}_block_size", 99, 11, callback="odd", custom_callback=self.update_threshold),
                make_trackbar(f"{channel} C Constant", f"{channel_lower}_c_constant", 50, 2, custom_callback=self.update_threshold)
            ])
        
        # Organize trackbars by method
        self.method_trackbars["Range"] = range_configs
        self.method_trackbars["Simple"] = advanced_configs
        self.method_trackbars["Otsu"] = advanced_configs
        self.method_trackbars["Triangle"] = advanced_configs
        self.method_trackbars["Adaptive"] = adaptive_configs
    
    def _create_trackbars_for_method(self, method):
        """Create trackbars for the specified method only."""
        if method not in self.method_trackbars:
            return
            
        # Get trackbar configs for this method
        trackbar_configs = self.method_trackbars[method]
        
        # Store current trackbars for cleanup
        self.current_trackbars = trackbar_configs
        
        # Create trackbars for this method
        for config in trackbar_configs:
            self.trackbar_manager.create_trackbar(config, self.viewer)
    
    def _clear_current_trackbars(self):
        """Clear current trackbars by recreating the window."""
        # Since OpenCV doesn't support deleting individual trackbars,
        # we need to destroy and recreate the window
        if hasattr(self, 'image_window_name'):
            cv2.destroyWindow(self.image_window_name)
            cv2.namedWindow(self.image_window_name, cv2.WINDOW_NORMAL)
            
        # Recreate trackbar manager
        self.trackbar_manager = TrackbarManager(self.image_window_name)
    
    def _switch_to_method(self, new_method):
        """Switch trackbars to show only those relevant for the new method."""
        if new_method == self.current_method:
            return  # No change needed
            
        # Ensure the UI variable reflects the new method
        if self.threshold_method_var:
            self.threshold_method_var.set(new_method)
            
        # Clear current trackbars
        self._clear_current_trackbars()
        
        # Create trackbars for new method
        self._create_trackbars_for_method(new_method)
        
        # Update current method
        self.current_method = new_method
        
        # Update the UI to reflect the method change
        self._update_ui_for_method(new_method)
        
        # Force UI refresh to ensure radio button state is correct
        if self.root:
            self.root.update_idletasks()
        
        # Log the switch
        self.viewer.log(f"Switched to {new_method} thresholding - trackbars updated")
    
    def _update_ui_for_method(self, method):
        """Update UI elements to reflect the selected method."""
        # Show/hide adaptive frame for grayscale
        if self.color_space == "Grayscale" and hasattr(self, 'adaptive_frame'):
            if method == "Adaptive":
                self.adaptive_frame.pack(padx=10, pady=5, fill="x")
                # Limit threshold types for adaptive
                if hasattr(self, 'threshold_type_combo'):
                    self.threshold_type_combo['values'] = ["BINARY", "BINARY_INV"]
            else:
                self.adaptive_frame.pack_forget()
                # All types available for other methods
                if hasattr(self, 'threshold_type_combo'):
                    self.threshold_type_combo['values'] = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
        
        # Show/hide adaptive frame for color spaces
        elif self.color_space != "Grayscale" and hasattr(self, 'advanced_controls_frame'):
            if method == "Adaptive":
                self.advanced_controls_frame.pack(padx=10, pady=5, fill="x")
                if hasattr(self, 'threshold_type_combo'):
                    self.threshold_type_combo['values'] = ["BINARY", "BINARY_INV"]
            else:
                self.advanced_controls_frame.pack_forget()
                if hasattr(self, 'threshold_type_combo'):
                    self.threshold_type_combo['values'] = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
    
    def _on_threshold_type_change(self, value):
        """Handle threshold type trackbar changes."""
        threshold_types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
        if self.threshold_type_var:
            self.threshold_type_var.set(threshold_types[value])
        self.update_threshold()
    
    def _on_adaptive_method_change(self, value):
        """Handle adaptive method trackbar changes."""
        adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
        if self.adaptive_method_var:
            self.adaptive_method_var.set(adaptive_methods[value])
        self.update_threshold()
    
    def _on_dropdown_threshold_type_change(self, event=None):
        """Handle threshold type dropdown changes - update trackbar."""
        if not self.threshold_type_var or not self.trackbar_manager:
            return
            
        # Get selected threshold type from dropdown
        selected_type = self.threshold_type_var.get()
        threshold_types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
        
        # Find index of selected type
        try:
            type_index = threshold_types.index(selected_type)
        except ValueError:
            type_index = 0  # Default to BINARY if not found
        
        # Update trackbar to match dropdown selection
        # Try both possible trackbar names (full and adaptive limited)
        trackbar_names = [
            "Thresh Type [0=BIN,1=INV,2=TRU,3=TZ,4=TZI]",
            "Thresh Type [0=BIN,1=INV]"
        ]
        
        for trackbar_name in trackbar_names:
            try:
                cv2.setTrackbarPos(trackbar_name, self.image_window_name, type_index)
                break  # Success, no need to try other names
            except:
                continue  # Try next trackbar name
            
        # Update internal parameter
        self.trackbar_manager.parameters["threshold_type_idx"] = type_index
        
        # Update thresholding
        self.update_threshold()
    
    def _on_dropdown_adaptive_method_change(self, event=None):
        """Handle adaptive method dropdown changes - update trackbar."""
        if not self.adaptive_method_var or not self.trackbar_manager:
            return
            
        # Get selected adaptive method from dropdown
        selected_method = self.adaptive_method_var.get()
        adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
        
        # Find index of selected method
        try:
            method_index = adaptive_methods.index(selected_method)
        except ValueError:
            method_index = 0  # Default to MEAN_C if not found
        
        # Update trackbar to match dropdown selection
        try:
            cv2.setTrackbarPos("Adaptive [0=MEAN,1=GAUSSIAN]", self.image_window_name, method_index)
        except:
            # Trackbar might not exist yet
            pass
            
        # Update internal parameter
        self.trackbar_manager.parameters["adaptive_method_idx"] = method_index
        
        # Update thresholding
        self.update_threshold()
    
    def on_color_method_change(self):
        """Handle threshold method selection changes for color spaces."""
        if not self.threshold_method_var:
            return
            
        method = self.threshold_method_var.get()
        
        # Switch trackbars for the selected method
        self._switch_to_method(method)
        self.update_threshold()
    
    def on_method_change(self):
        """Handle threshold method selection changes."""
        if not self.threshold_method_var:
            return
            
        method = self.threshold_method_var.get()
        
        # Switch trackbars for the selected method
        self._switch_to_method(method)
        self.update_threshold()

    def update_threshold(self, _=None):
        if not self.viewer._internal_images: return
        current_idx = self.viewer.trackbar.parameters.get('show', 0)
        image, _ = self.viewer._internal_images[current_idx]

        processor = ThresholdProcessor(image)
        converted_image = processor.convert_color_space(self.color_space)

        if self.color_space == "Grayscale":
            # Get parameters from trackbars and UI
            threshold_value = self.trackbar_manager.parameters.get("threshold", 127)
            max_value = self.trackbar_manager.parameters.get("max_value", 255)
            
            # Get threshold type from trackbar
            threshold_types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
            type_idx = self.trackbar_manager.parameters.get("threshold_type_idx", 0)
            threshold_type = threshold_types[min(type_idx, len(threshold_types)-1)]
            
            # Update UI combo box if it exists
            if self.threshold_type_var:
                self.threshold_type_var.set(threshold_type)
            
            method = self.threshold_method_var.get() if self.threshold_method_var else "Simple"
            
            if method == "Simple":
                thresholded_image = processor.apply_advanced_threshold(
                    converted_image, threshold_value, max_value, threshold_type)
            elif method == "Otsu":
                thresholded_image = processor.apply_advanced_threshold(
                    converted_image, threshold_value, max_value, threshold_type, use_otsu=True)
            elif method == "Triangle":
                thresholded_image = processor.apply_advanced_threshold(
                    converted_image, threshold_value, max_value, threshold_type, use_triangle=True)
            elif method == "Adaptive":
                block_size = self.trackbar_manager.parameters.get("block_size", 11)
                c_constant = self.trackbar_manager.parameters.get("c_constant", 2)
                
                # Get adaptive method from trackbar
                adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
                method_idx = self.trackbar_manager.parameters.get("adaptive_method_idx", 0)
                adaptive_method = adaptive_methods[min(method_idx, len(adaptive_methods)-1)]
                
                # Update UI combo box if it exists
                if self.adaptive_method_var:
                    self.adaptive_method_var.set(adaptive_method)
                
                thresholded_image = processor.apply_adaptive_threshold(
                    converted_image, max_value, adaptive_method, threshold_type, block_size, c_constant)
            else:
                # Fallback to simple binary threshold
                thresholded_image = processor.apply_binary_threshold(converted_image, threshold_value, False)
        else:
            # Color space thresholding with advanced methods
            method = self.threshold_method_var.get() if self.threshold_method_var else "Range"
            
            # Get threshold type from trackbar for color spaces too
            threshold_types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
            type_idx = self.trackbar_manager.parameters.get("threshold_type_idx", 0)
            threshold_type = threshold_types[min(type_idx, len(threshold_types)-1)]
            
            # Update UI combo box if it exists
            if self.threshold_type_var:
                self.threshold_type_var.set(threshold_type)
            
            if method == "Range":
                # Traditional range thresholding
                lower_bounds = []
                upper_bounds = []
                
                ranges = self.ranges.get(self.color_space, {})
                for channel in ranges.keys():
                    lower_bounds.append(self.trackbar_manager.parameters.get(f"{channel.lower()}_min", 0))
                    upper_bounds.append(self.trackbar_manager.parameters.get(f"{channel.lower()}_max", 255))

                thresholded_image = processor.apply_range_threshold(converted_image, lower_bounds, upper_bounds)
            else:
                # Advanced per-channel thresholding
                ranges = self.ranges.get(self.color_space, {})
                channel_params = []
                
                for channel in ranges.keys():
                    channel_lower = channel.lower()
                    params = {
                        'threshold': self.trackbar_manager.parameters.get(f"{channel_lower}_threshold", 127),
                        'max_value': self.trackbar_manager.parameters.get(f"{channel_lower}_max_value", 255),
                        'threshold_type': threshold_type
                    }
                    
                    if method == "Adaptive":
                        # Get adaptive method from trackbar
                        adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
                        method_idx = self.trackbar_manager.parameters.get("adaptive_method_idx", 0)
                        adaptive_method = adaptive_methods[min(method_idx, len(adaptive_methods)-1)]
                        
                        # Update UI combo box if it exists
                        if self.adaptive_method_var:
                            self.adaptive_method_var.set(adaptive_method)
                        
                        params.update({
                            'adaptive_method': adaptive_method,
                            'block_size': self.trackbar_manager.parameters.get(f"{channel_lower}_block_size", 11),
                            'c_constant': self.trackbar_manager.parameters.get(f"{channel_lower}_c_constant", 2)
                        })
                    
                    channel_params.append(params)
                
                thresholding_params = {
                    'method': method,
                    'threshold_type': threshold_type,
                    'channels': channel_params
                }
                
                thresholded_image = processor.apply_multi_channel_threshold(converted_image, thresholding_params)

        cv2.imshow(self.image_window_name, thresholded_image)
        
        # Update status display
        self._update_status_display()

    def _update_status_display(self):
        """Update the status display with current parameters."""
        if not hasattr(self, 'status_text') or not self.status_text:
            return
            
        # Get current parameters
        params = []
        method = self.threshold_method_var.get() if self.threshold_method_var else "Unknown"
        
        # Threshold type
        threshold_types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
        type_idx = self.trackbar_manager.parameters.get("threshold_type_idx", 0) if self.trackbar_manager else 0
        threshold_type = threshold_types[min(type_idx, len(threshold_types)-1)]
        
        params.append(f"Method: {method}")
        params.append(f"Type: {threshold_type}")
        
        if self.color_space == "Grayscale":
            if method == "Adaptive":
                adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
                method_idx = self.trackbar_manager.parameters.get("adaptive_method_idx", 0) if self.trackbar_manager else 0
                adaptive_method = adaptive_methods[min(method_idx, len(adaptive_methods)-1)]
                block_size = self.trackbar_manager.parameters.get("block_size", 11) if self.trackbar_manager else 11
                c_constant = self.trackbar_manager.parameters.get("c_constant", 2) if self.trackbar_manager else 2
                params.append(f"Adaptive: {adaptive_method}")
                params.append(f"Block: {block_size}, C: {c_constant}")
            else:
                threshold = self.trackbar_manager.parameters.get("threshold", 127) if self.trackbar_manager else 127
                max_val = self.trackbar_manager.parameters.get("max_value", 255) if self.trackbar_manager else 255
                params.append(f"Thresh: {threshold}, Max: {max_val}")
        else:
            params.append(f"Color Space: {self.color_space}")
            if method != "Range" and self.trackbar_manager:
                # Show first channel's parameters as example
                ranges = self.ranges.get(self.color_space, {})
                if ranges:
                    first_channel = list(ranges.keys())[0].lower()
                    thresh = self.trackbar_manager.parameters.get(f"{first_channel}_threshold", 127)
                    max_val = self.trackbar_manager.parameters.get(f"{first_channel}_max_value", 255)
                    params.append(f"{first_channel.upper()}: T={thresh}, M={max_val}")
        
        # Update status text
        status_str = "\n".join(params)
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, status_str)
        self.status_text.config(state=tk.DISABLED)

    def _save_config(self):
        """Save current thresholding configuration to file."""
        if not self.trackbar_manager:
            return
            
        try:
            config_data = {
                "color_space": self.color_space,
                "method": self.threshold_method_var.get() if self.threshold_method_var else "Unknown",
                "parameters": dict(self.trackbar_manager.parameters)
            }
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title=f"Save {self.color_space} Thresholding Config"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(config_data, f, indent=2)
                self.viewer.log(f"Thresholding config saved to {filename}")
                
        except Exception as e:
            self.viewer.log(f"Error saving config: {e}")

    def _load_config(self):
        """Load thresholding configuration from file."""
        if not self.trackbar_manager:
            return
            
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Load Thresholding Config"
            )
            
            if filename:
                with open(filename, 'r') as f:
                    config_data = json.load(f)
                
                # Load parameters
                if "parameters" in config_data:
                    for param_name, value in config_data["parameters"].items():
                        if param_name in self.trackbar_manager.parameters:
                            # Update trackbar value
                            try:
                                cv2.setTrackbarPos(param_name, self.image_window_name, value)
                            except:
                                pass  # Trackbar might not exist
                            self.trackbar_manager.parameters[param_name] = value
                
                # Update method if available
                if "method" in config_data and self.threshold_method_var:
                    self.threshold_method_var.set(config_data["method"])
                
                self.update_threshold()
                self.viewer.log(f"Thresholding config loaded from {filename}")
                
        except Exception as e:
            self.viewer.log(f"Error loading config: {e}")

    def _show_presets(self):
        """Show preset configurations popup."""
        preset_window = tk.Toplevel(self.root)
        preset_window.title("Thresholding Presets")
        preset_window.geometry("300x400")
        
        ttk.Label(preset_window, text="Common Thresholding Presets:").pack(pady=10)
        
        # Define presets
        presets = self._get_presets()
        
        # Create preset buttons
        for preset_name, preset_data in presets.items():
            btn_frame = ttk.Frame(preset_window)
            btn_frame.pack(fill="x", padx=10, pady=2)
            
            ttk.Button(btn_frame, text=preset_name, 
                      command=lambda p=preset_data: self._apply_preset(p, preset_window)).pack(side=tk.LEFT)
            ttk.Label(btn_frame, text=preset_data.get("description", ""), 
                     font=("Arial", 8), foreground="gray").pack(side=tk.LEFT, padx=(10, 0))

    def _get_presets(self):
        """Get predefined presets for current color space."""
        if self.color_space == "Grayscale":
            return {
                "Document Scan": {
                    "description": "High contrast binary",
                    "method": "Otsu",
                    "parameters": {"threshold_type_idx": 0, "threshold": 127, "max_value": 255}
                },
                "Adaptive Text": {
                    "description": "Variable lighting text",
                    "method": "Adaptive", 
                    "parameters": {"threshold_type_idx": 0, "adaptive_method_idx": 1, "block_size": 11, "c_constant": 2, "max_value": 255}
                },
                "Edge Detection": {
                    "description": "Truncated thresholding",
                    "method": "Simple",
                    "parameters": {"threshold_type_idx": 2, "threshold": 100, "max_value": 255}
                },
                "Bright Objects": {
                    "description": "Keep bright regions only",
                    "method": "Simple",
                    "parameters": {"threshold_type_idx": 3, "threshold": 150, "max_value": 255}
                }
            }
        elif self.color_space == "HSV":
            return {
                "Blue Objects": {
                    "description": "Isolate blue colored objects",
                    "method": "Range",
                    "parameters": {"h_min": 100, "h_max": 130, "s_min": 50, "s_max": 255, "v_min": 50, "v_max": 255}
                },
                "Red Objects": {
                    "description": "Isolate red colored objects", 
                    "method": "Range",
                    "parameters": {"h_min": 0, "h_max": 10, "s_min": 100, "s_max": 255, "v_min": 100, "v_max": 255}
                },
                "Green Objects": {
                    "description": "Isolate green colored objects",
                    "method": "Range", 
                    "parameters": {"h_min": 40, "h_max": 80, "s_min": 100, "s_max": 255, "v_min": 100, "v_max": 255}
                }
            }
        else:
            return {
                "Default Range": {
                    "description": "Full range thresholding",
                    "method": "Range",
                    "parameters": {}
                },
                "Simple Binary": {
                    "description": "Binary thresholding all channels",
                    "method": "Simple",
                    "parameters": {"threshold_type_idx": 0}
                }
            }

    def _apply_preset(self, preset_data, preset_window):
        """Apply a preset configuration."""
        try:
            # Set method
            if "method" in preset_data and self.threshold_method_var:
                self.threshold_method_var.set(preset_data["method"])
            
            # Set parameters
            if "parameters" in preset_data and self.trackbar_manager:
                for param_name, value in preset_data["parameters"].items():
                    if param_name in self.trackbar_manager.parameters:
                        # Update trackbar value
                        try:
                            cv2.setTrackbarPos(param_name, self.image_window_name, value)
                        except:
                            pass
                        self.trackbar_manager.parameters[param_name] = value
            
            # Update thresholding
            self.update_threshold()
            preset_window.destroy()
            self.viewer.log(f"Applied preset: {preset_data.get('description', 'Unknown')}")
            
        except Exception as e:
            self.viewer.log(f"Error applying preset: {e}")
    
    def set_close_callback(self, callback):
        """Set a callback to be called when the window is closed."""
        self.close_callback = callback
    
    def destroy_window(self):
        # Call close callback before destroying
        if self.close_callback:
            try:
                self.close_callback()
            except Exception as e:
                if hasattr(self, 'viewer'):
                    self.viewer.log(f"Error in close callback: {e}")
        
        if self.window_created and self.root:
            self.root.destroy()
            self.root = None
        
        # Check if the image window exists before destroying it
        if hasattr(self, 'image_window_name'):
            try:
                if cv2.getWindowProperty(self.image_window_name, cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.destroyWindow(self.image_window_name)
            except cv2.error:
                pass  # Window already destroyed
            
        self.window_created = False
