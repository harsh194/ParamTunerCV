"""
Thresholding window module for the Parameter image viewer application.

This module provides comprehensive image thresholding functionality with support
for multiple color spaces, thresholding methods, and both unified and legacy
interfaces. It integrates OpenCV thresholding operations with tkinter GUI controls
for interactive parameter adjustment and real-time preview.

Main Classes:
    - ThresholdingWindow: Complete thresholding interface supporting multiple
      color spaces, threshold methods, and parameter controls
    - ThresholdWindowManager: Custom window manager for thresholding operations

Features:
    - Multi-color space support (BGR, HSV, HLS, Lab, Luv, YCrCb, XYZ, Grayscale)
    - Multiple thresholding methods (Binary, Otsu, Triangle, Adaptive, Range)
    - Unified interface with integrated color space selection
    - Legacy simple OpenCV window interface
    - Real-time parameter adjustment with trackbars
    - Theme-aware GUI styling
    - Configuration saving and loading
    - Preset management system

Thresholding Methods:
    - Binary: Simple binary thresholding with single threshold value
    - Otsu: Automatic threshold selection using Otsu's method
    - Triangle: Automatic threshold using triangle algorithm
    - Adaptive: Adaptive thresholding for varying illumination
    - Range: Multi-channel range-based thresholding

Color Space Support:
    - BGR: Blue-Green-Red (OpenCV default)
    - HSV: Hue-Saturation-Value (good for color-based segmentation)
    - HLS: Hue-Lightness-Saturation (alternative color representation)
    - Lab: L*a*b* (perceptually uniform color space)
    - Luv: L*u*v* (CIE color space)
    - YCrCb: Luma-Chroma (used in video compression)
    - XYZ: CIE XYZ (device-independent color space)
    - Grayscale: Single channel intensity

Dependencies:
    - tkinter: GUI framework
    - cv2: OpenCV for image processing
    - numpy: Array operations
    - ThresholdProcessor: Core thresholding operations
    - TrackbarManager: Real-time parameter controls
    - ViewerConfig: Configuration management
    - ThemeManager: UI styling

Usage:
    # Unified interface
    threshold_window = ThresholdingWindow(viewer, "HSV")
    threshold_window.create_unified_window()
    
    # Simple OpenCV interface
    threshold_window.create_simple_threshold_viewer()
"""

import tkinter as tk
from tkinter import ttk, filedialog
import cv2
import numpy as np
import json
from ..analysis.threshold.image_processor import ThresholdProcessor
from ..controls.trackbar_manager import TrackbarManager, make_trackbar
from ..config.viewer_config import ViewerConfig
from .theme_manager import ThemeManager

class ThresholdingWindow:
    """
    Comprehensive image thresholding interface with multi-color space support.
    
    This class provides a complete thresholding solution with both unified GUI
    interfaces and simple OpenCV window modes. It supports multiple color spaces,
    various thresholding methods, real-time parameter adjustment, and configuration
    persistence.
    
    The class can operate in two main modes:
    1. Unified Window: Complete tkinter interface with color space selection,
       method controls, and integrated parameter adjustment
    2. Simple Viewer: OpenCV-only interface for lightweight thresholding
    
    Attributes:
        viewer: Reference to the main ImageViewer instance.
        color_space (str): Currently selected color space for thresholding.
        root: Main tkinter window for the interface.
        window_created (bool): Flag indicating if the window has been created.
        theme_manager: ThemeManager instance for consistent styling.
        threshold_method_var: tkinter variable for threshold method selection.
        threshold_type_var: tkinter variable for binary threshold type.
        adaptive_method_var: tkinter variable for adaptive method selection.
        color_space_var: tkinter variable for color space selection.
        method_trackbars (dict): Trackbar configurations for each method.
        current_method (str): Currently active thresholding method.
        threshold_viewer: Dedicated ImageViewer instance for threshold preview.
        ranges (dict): Valid parameter ranges for each color space.
        close_callback: Optional callback function for window closing.
    
    Examples:
        >>> threshold_window = ThresholdingWindow(viewer, "HSV")
        >>> threshold_window.create_unified_window()
        # Creates unified interface with HSV color space
        
        >>> threshold_window.create_simple_threshold_viewer()
        # Creates simple OpenCV window interface
        
        >>> threshold_window.update_threshold()
        # Updates threshold processing with current parameters
    """
    def __init__(self, viewer, color_space: str = None) -> None:
        """
        Initialize the thresholding window with viewer and color space.
        
        Sets up the thresholding interface with the specified color space,
        initializes UI variables, creates parameter ranges for all supported
        color spaces, and prepares for threshold processing with theme support.
        
        Args:
            viewer: The ImageViewer instance that provides the source images
                   for thresholding operations. Must have loaded images and trackbar.
            color_space (str, optional): The initial color space to use. Must be one of:
                                       "BGR", "HSV", "HLS", "Lab", "Luv", "YCrCb", "XYZ", "Grayscale".
                                       Defaults to "BGR" if not specified.
        
        Returns:
            None: Constructor initializes instance, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> # HSV thresholding window initialized
            >>> threshold_window = ThresholdingWindow(viewer)
            >>> # BGR thresholding window initialized (default)
            >>> print(threshold_window.color_space)  # "BGR"
            
        Performance:
            Time Complexity: O(1) - Fixed initialization with color space ranges.
            Space Complexity: O(1) - Fixed memory for UI variables and ranges.
        """
        self.viewer = viewer
        self.color_space = color_space or "BGR"  # Default to BGR if not specified
        self.root = None
        self.window_created = False
        
        # Initialize theme manager with dark mode to match analysis control window
        self.theme_manager = ThemeManager(use_dark_mode=True)
        
        # Initialize UI variables to prevent AttributeError
        self.threshold_method_var = None
        self.threshold_type_var = None
        self.adaptive_method_var = None
        self.color_space_var = None  # For colorspace selection
        
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
        
        # Create dedicated ImageViewer for thresholding with full functionality
        self.threshold_viewer = None
        self.is_processing = False  # Prevent recursive updates

        self.ranges = {
            "BGR": {"B": (0, 255), "G": (0, 255), "R": (0, 255)},
            "HSV": {"H": (0, 180), "S": (0, 255), "V": (0, 255)},
            "HLS": {"H": (0, 180), "L": (0, 255), "S": (0, 255)},
            "Lab": {"L": (0, 255), "a": (42, 226), "b": (20, 223)},
            "Luv": {"L": (0, 255), "u": (0, 255), "v": (0, 255)},
            "YCrCb": {"Y": (0, 255), "Cr": (0, 255), "Cb": (0, 255)},
            "XYZ": {"X": (0, 255), "Y": (0, 255), "Z": (0, 255)},
            "Grayscale": {"Gray": (0, 255)}
        }

    def create_window(self) -> None:
        """
        Create the legacy thresholding window with color space-specific controls.
        
        Creates a tkinter window with controls appropriate for the current color
        space. For grayscale images, shows grayscale-specific thresholding methods.
        For color images, shows color-based thresholding options. Legacy interface.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates window as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window.create_window()
            >>> # Legacy thresholding window created with HSV-specific controls
            >>> print(threshold_window.window_created)  # True
            
        Performance:
            Time Complexity: O(1) - Fixed UI widget creation and setup.
            Space Complexity: O(1) - Fixed memory for window components.
        """
        if self.window_created:
            return

        # Create a dedicated ImageViewer for thresholding
        self._create_threshold_viewer()

        self.trackbar_manager = self.threshold_viewer.trackbar
        
        self.root = tk.Toplevel()
        self.root.title("Thresholding Controls")
        self.root.geometry("500x700")
        
        # Apply theme to match analysis control window
        self.theme_manager.configure_theme(self.root)
        
        # Create colorspace selection section at the top
        self._create_colorspace_selection()
        
        # Create separator
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=5)

        # Create method controls based on colorspace
        if self.color_space == "Grayscale":
            self._create_grayscale_method_controls()
        else:
            self._create_color_method_controls()
        
        # Create status and buttons sections
        self._create_status_section()
        self._create_buttons_section()

        self.window_created = True
        self.root.protocol("WM_DELETE_WINDOW", self.destroy_window)
        
        # Create trackbars after UI is set up
        self.create_trackbars()
    
    def create_unified_window(self) -> None:
        """
        Create unified thresholding window with integrated color space selection.
        
        Creates a comprehensive thresholding interface that combines color space
        selection with parameter controls in a single, dynamically-sized window.
        The interface adapts its size based on the selected color space and method.
        Modern interface with enhanced UX.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates window as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window.create_unified_window()
            >>> # Unified thresholding window created with dynamic sizing
            >>> # User can select color space from dropdown
            >>> print(threshold_window.window_created)  # True
            
        Performance:
            Time Complexity: O(1) - Fixed UI creation with dynamic content placeholder.
            Space Complexity: O(1) - Fixed memory for unified window components.
        """
        if self.window_created:
            return

        # Create tkinter window
        self.root = tk.Toplevel()
        self.root.title("Thresholding Controls")
        # Start with reasonable initial size, will be adjusted later
        self.root.geometry("480x300")
        
        # Apply theme to match analysis control window
        self.theme_manager.configure_theme(self.root)
        
        # Create main content frame (simpler, no scrolling initially)
        self.main_container = ttk.Frame(self.root, style=self.theme_manager.get_frame_style())
        self.main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create colorspace selection section at the top
        self._create_colorspace_selection_unified()
        
        # Create separator
        separator = ttk.Separator(self.main_container, orient='horizontal')
        separator.pack(fill='x', padx=5, pady=10)
        
        # Create thresholding controls section (initially empty, will be populated when colorspace is selected)
        self.controls_frame = ttk.Frame(self.main_container, style=self.theme_manager.get_frame_style())
        self.controls_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Show initial message
        self.status_label = ttk.Label(self.controls_frame, 
                                     text="👆 Please select a color space above to see thresholding parameters",
                                     style=self.theme_manager.get_label_style())
        self.status_label.pack(pady=20)
        
        # Set minimum size and allow window to resize
        self.root.minsize(400, 200)
        
        # Set max size constraints to prevent oversized windows
        screen_height = self.root.winfo_screenheight()
        max_height = int(screen_height * 0.8)  # Max 80% of screen height
        self.root.maxsize(600, max_height)
        
        # Initial size adjustment to fit initial content
        self.root.update_idletasks()
        self._adjust_window_size()

        self.window_created = True
        self.root.protocol("WM_DELETE_WINDOW", self.destroy_window)
    
    def _adjust_window_size(self) -> None:
        """
        Dynamically adjust window size to fit current content.
        
        Calculates the required window size based on the current content and
        adjusts the window geometry within reasonable bounds. Ensures the window
        doesn't exceed screen dimensions or become too small for usability.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates window geometry as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window.create_unified_window()
            >>> threshold_window._adjust_window_size()
            >>> # Window resized to fit current content optimally
            >>> # Size constrained between 400x200 and 600x(80% screen height)
            
        Performance:
            Time Complexity: O(1) - Simple geometry calculation and update.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if not self.root:
            return
            
        try:
            # Update all pending geometry changes
            self.root.update_idletasks()
            
            # Get the required size for the content
            req_width = self.main_container.winfo_reqwidth() + 40  # Add padding
            req_height = self.main_container.winfo_reqheight() + 40  # Add padding
            
            # Set reasonable bounds
            min_width = 400
            max_width = 600
            min_height = 200
            
            # Apply bounds
            final_width = max(min_width, min(req_width, max_width))
            final_height = max(min_height, req_height)
            
            # Get screen dimensions for max height
            screen_height = self.root.winfo_screenheight()
            max_height = int(screen_height * 0.8)
            final_height = min(final_height, max_height)
            
            # Set the new geometry
            self.root.geometry(f"{final_width}x{final_height}")
            
        except Exception as e:
            print(f"Error adjusting window size: {e}")

    
    def _create_colorspace_selection_unified(self) -> None:
        """
        Create the color space selection section for the unified window.
        
        Creates a dropdown interface for selecting color spaces in the unified
        thresholding window. The selection triggers dynamic updates to the
        parameter controls and threshold viewer with detailed descriptions.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates UI components as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "BGR")
            >>> threshold_window.create_unified_window()
            >>> threshold_window._create_colorspace_selection_unified()
            >>> # Color space selection UI created with descriptions
            >>> # Dropdown shows: BGR, HSV, HLS, Lab, Luv, YCrCb, XYZ, Grayscale
            
        Performance:
            Time Complexity: O(1) - Fixed UI component creation.
            Space Complexity: O(1) - Fixed memory for UI elements.
        """
        colorspace_frame = ttk.Frame(self.main_container, style=self.theme_manager.get_frame_style())
        colorspace_frame.pack(fill='x', padx=5, pady=5)
        
        # Available color spaces
        color_spaces = ["BGR", "HSV", "HLS", "Lab", "Luv", "YCrCb", "XYZ", "Grayscale"]
        
        # Colorspace selection (removed info text)
        selection_frame = ttk.Frame(colorspace_frame, style=self.theme_manager.get_frame_style())
        selection_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(selection_frame, text="Color Space:", 
                 style=self.theme_manager.get_label_style()).pack(side=tk.LEFT, padx=(0, 10))
        
        self.color_space_var = tk.StringVar()
        color_space_combo = ttk.Combobox(selection_frame, textvariable=self.color_space_var, 
                                       values=color_spaces, state="readonly", width=15,
                                       style=self.theme_manager.get_combobox_style())
        color_space_combo.pack(side=tk.LEFT, padx=(0, 10))
        color_space_combo.bind('<<ComboboxSelected>>', self._on_colorspace_change_unified)
        
        # Description label that updates with selection
        self.desc_var = tk.StringVar()
        desc_label = ttk.Label(selection_frame, textvariable=self.desc_var, font=("Arial", 8), 
                             style=self.theme_manager.get_label_style())
        desc_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Enhanced color space descriptions
        self.color_space_descriptions = {
            "BGR": "BGR - Standard OpenCV color format",
            "HSV": "HSV - Best for color-based detection",
            "HLS": "HLS - Alternative color representation", 
            "Lab": "Lab - Perceptually uniform color space",
            "Luv": "Luv - Another perceptually uniform space",
            "YCrCb": "YCrCb - Luma-chroma (JPEG standard)",
            "XYZ": "XYZ - Device-independent color space",
            "Grayscale": "Grayscale - Single intensity channel"
        }
        
        # Don't set initial selection - user must choose
        self.color_space_var.set("")
        self.desc_var.set("Please select a color space above")
        
        # Bind description update
        def update_description(event=None):
            selected = self.color_space_var.get()
            if selected:
                self.desc_var.set(self.color_space_descriptions.get(selected, ""))
            else:
                self.desc_var.set("Please select a color space above")
        
        color_space_combo.bind('<<ComboboxSelected>>', lambda e: [update_description(e), self._on_colorspace_change_unified(e)])
        
        # Determine if grayscale image
        if self.viewer._internal_images:
            current_idx = self.viewer.trackbar.parameters.get('show', 0)
            image, _ = self.viewer._internal_images[current_idx]
            is_grayscale = len(image.shape) == 2
            
            if is_grayscale:
                note_text = "Note: Grayscale image detected - color spaces will show converted results"
                note_label = ttk.Label(colorspace_frame, text=note_text, font=("Arial", 7), 
                                     style=self.theme_manager.get_label_style())
                note_label.pack(pady=2)

    def _on_colorspace_change_unified(self, event=None) -> None:
        """
        Handle color space selection changes in the unified window interface.
        
        Updates the unified thresholding interface when the user selects a different
        color space, including updating descriptions, recreating the threshold viewer,
        and rebuilding the parameter controls for the new color space.
        
        Args:
            event: The tkinter event that triggered the change (optional).
        
        Side Effects:
            - Updates color space description text
            - Updates internal color_space attribute
            - Clears existing control widgets
            - Recreates threshold viewer for new color space
            - Rebuilds thresholding controls
            - Updates method selection styling
        """
        new_colorspace = self.color_space_var.get()
        
        if not new_colorspace:
            return
        
        # Update description
        self.desc_var.set(self.color_space_descriptions.get(new_colorspace, ""))
        
        # Update colorspace
        self.color_space = new_colorspace
        pass
        
        # Clear the controls frame
        for widget in self.controls_frame.winfo_children():
            widget.destroy()
        
        # Create/recreate the threshold viewer for new colorspace
        self._create_or_update_threshold_viewer()
        
        # Create thresholding controls for the new colorspace
        self._create_thresholding_controls_unified()
        
        # Ensure the initial method selection is visually highlighted
        self._update_method_selection_style()
        
        # Adjust window size to fit content (with small delay)
        self.root.after(100, self._adjust_window_size)
        
    def _create_or_update_threshold_viewer(self) -> None:
        """
        Create or update the threshold viewer for the current color space.
        
        Creates a new threshold viewer if none exists, or updates the existing
        viewer to work with the current color space. Ensures the viewer is
        properly configured for the selected color space's characteristics.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates/updates threshold viewer as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "BGR")
            >>> threshold_window.color_space = "HSV"  # Change color space
            >>> threshold_window._create_or_update_threshold_viewer()
            >>> # Threshold viewer updated for HSV processing
            
        Performance:
            Time Complexity: O(1) - Viewer creation and trackbar setup.
            Space Complexity: O(1) - Single viewer instance allocation.
        """
        # Clean up existing threshold viewer if it exists
        if hasattr(self, 'threshold_viewer') and self.threshold_viewer:
            try:
                self.threshold_viewer.cleanup_viewer()
            except:
                pass
            self.threshold_viewer = None
        
        # Create new threshold viewer with appropriate trackbars
        self._create_threshold_viewer()
        
        # Create trackbars for the current colorspace
        self.create_trackbars()
    
    def _create_thresholding_controls_unified(self) -> None:
        """
        Create comprehensive thresholding controls in the unified window.
        
        Builds the complete set of thresholding controls appropriate for the
        current color space, including method selection buttons, parameter
        controls, and method-specific options.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates method control UI as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "Grayscale")
            >>> threshold_window._create_thresholding_controls_unified()
            >>> # Grayscale method controls created (Binary, Adaptive, etc.)
            >>> threshold_window.color_space = "HSV"
            >>> threshold_window._create_thresholding_controls_unified()
            >>> # Color method controls created (Inrange, Custom, etc.)
            
        Performance:
            Time Complexity: O(n) where n is number of available methods.
            Space Complexity: O(n) - UI elements for each method.
        """
        # Method selection frame
        method_frame = ttk.LabelFrame(self.controls_frame, text="Thresholding Method", 
                                    style=self.theme_manager.get_frame_style())
        method_frame.pack(fill='x', pady=5)
        
        # Store method buttons for styling
        self.method_buttons = {}
        
        if self.color_space == "Grayscale":
            # Grayscale methods
            self.threshold_method_var = tk.StringVar(value="Simple")
            methods = ["Simple", "Adaptive", "Otsu", "Triangle"]
        else:
            # Color space methods
            self.threshold_method_var = tk.StringVar(value="Range")
            methods = ["Range", "Simple", "Otsu", "Triangle", "Adaptive"]
        
        # Create custom square method buttons
        for method in methods:
            method_container = ttk.Frame(method_frame, style=self.theme_manager.get_frame_style())
            method_container.pack(fill='x', padx=5, pady=2)
            
            # Create square checkbox using Unicode character
            checkbox_label = ttk.Label(method_container, text="☐", font=("Arial", 12))
            checkbox_label.pack(side=tk.LEFT, padx=(5, 8))
            
            # Create method text label
            method_label = ttk.Label(method_container, text=method, font=("Arial", 10))
            method_label.pack(side=tk.LEFT)
            
            # Store references for styling updates
            self.method_buttons[method] = {
                'checkbox': checkbox_label,
                'text': method_label,
                'container': method_container
            }
            
            # Bind click events to both checkbox and text
            def make_click_handler(method_name):
                def on_click(event):
                    self.threshold_method_var.set(method_name)
                    self._update_method_selection_style()
                    self._on_method_change_unified()
                return on_click
            
            click_handler = make_click_handler(method)
            checkbox_label.bind("<Button-1>", click_handler)
            method_label.bind("<Button-1>", click_handler)
            method_container.bind("<Button-1>", click_handler)
        
        # Set initial selection style
        self._update_method_selection_style()
        
        # Threshold type selection
        type_frame = ttk.LabelFrame(self.controls_frame, text="Threshold Type", 
                                  style=self.theme_manager.get_frame_style())
        type_frame.pack(fill='x', pady=5)
        
        self.threshold_type_var = tk.StringVar(value="BINARY")
        types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
        self.threshold_type_combo = ttk.Combobox(type_frame, textvariable=self.threshold_type_var, 
                                                values=types, state="readonly", width=15,
                                                style=self.theme_manager.get_combobox_style())
        self.threshold_type_combo.pack(padx=5, pady=5)
        self.threshold_type_combo.bind("<<ComboboxSelected>>", self._on_threshold_type_change_unified)
        
        # Adaptive method frame (initially hidden)
        self.adaptive_frame = ttk.LabelFrame(self.controls_frame, text="Adaptive Method", 
                                           style=self.theme_manager.get_frame_style())
        self.adaptive_method_var = tk.StringVar(value="MEAN_C")
        adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
        self.adaptive_method_combo = ttk.Combobox(self.adaptive_frame, textvariable=self.adaptive_method_var,
                                                 values=adaptive_methods, state="readonly", width=15,
                                                 style=self.theme_manager.get_combobox_style())
        self.adaptive_method_combo.pack(padx=5, pady=5)
        self.adaptive_method_combo.bind("<<ComboboxSelected>>", self._on_adaptive_method_change_unified)
        
        # Status display
        status_frame = ttk.LabelFrame(self.controls_frame, text="Current Parameters", 
                                    style=self.theme_manager.get_frame_style())
        status_frame.pack(fill='x', pady=5)
        
        self.status_text = tk.Text(status_frame, height=3, width=40, font=("Consolas", 8))
        self.status_text.pack(padx=5, pady=5, fill="x")
        self.status_text.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(self.controls_frame, style=self.theme_manager.get_frame_style())
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Presets ▼", command=self._show_presets,
                  style=self.theme_manager.get_button_style()).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Config", command=self._save_config,
                  style=self.theme_manager.get_button_style()).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Config", command=self._load_config,
                  style=self.theme_manager.get_button_style()).pack(side=tk.LEFT, padx=5)
        
        # Update UI for current method
        self._update_ui_for_method_unified(self.threshold_method_var.get())
        
        # Update status display
        self._update_status_display()
    
    def _update_method_selection_style(self) -> None:
        """
        Update the visual styling of method selection buttons.
        
        Applies appropriate styling to method selection buttons to indicate
        the currently selected method using theme-aware active and inactive
        button styles.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates button styling as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window.threshold_method_var.set("Adaptive")
            >>> threshold_window._update_method_selection_style()
            >>> # Adaptive method button highlighted, others reset to normal
            
        Performance:
            Time Complexity: O(n) where n is number of method buttons.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if not hasattr(self, 'method_buttons'):
            return
            
        selected_method = self.threshold_method_var.get()
        
        # Get theme colors
        default_fg = self.theme_manager.theme.get('fg', '#ffffff')
        green_color = "#00bb00"  # Bright green that works on both dark and light backgrounds
        
        for method, components in self.method_buttons.items():
            checkbox = components['checkbox']
            text_label = components['text']
            
            if method == selected_method:
                # Selected: filled square checkbox and green text
                checkbox.config(text="☑", foreground=green_color)  # Green checkbox
                text_label.config(foreground=green_color)  # Green text
            else:
                # Unselected: empty square checkbox and default text color
                checkbox.config(text="☐", foreground=default_fg)
                text_label.config(foreground=default_fg)
    
    def _on_method_change_unified(self) -> None:
        """
        Handle threshold method changes in the unified window interface.
        
        Updates the unified interface when the user selects a different
        thresholding method, including updating UI elements and switching
        trackbar configurations.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates interface state as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window.threshold_method_var.set("Adaptive")
            >>> threshold_window._on_method_change_unified()
            >>> # Interface updated for Adaptive method, trackbars switched
            
        Performance:
            Time Complexity: O(1) - UI update and method switching operations.
            Space Complexity: O(1) - Fixed memory for UI updates.
        """
        if not self.threshold_method_var:
            return
        
        method = self.threshold_method_var.get()
        self._update_method_selection_style()  # Update visual selection
        self._switch_to_method(method)
        self._update_ui_for_method_unified(method)
        self.update_threshold()
        
        # Adjust window size for method-specific controls (with small delay)
        self.root.after(50, self._adjust_window_size)
    
    def _on_threshold_type_change_unified(self, event=None) -> None:
        """
        Handle threshold type changes in the unified window interface.
        
        Updates the threshold type selection when changed via dropdown in
        the unified interface.
        
        Args:
            event: The tkinter event that triggered the change (optional).
        
        Returns:
            None: Updates threshold type as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "Grayscale")
            >>> # User selects BINARY_INV from dropdown
            >>> threshold_window._on_threshold_type_change_unified()
            >>> # Threshold type updated, processing refreshed
            
        Performance:
            Time Complexity: O(1) - Simple type update and callback.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self._on_dropdown_threshold_type_change(event)
    
    def _on_adaptive_method_change_unified(self, event=None) -> None:
        """
        Handle adaptive method changes in the unified window interface.
        
        Updates the adaptive thresholding method selection when changed
        via dropdown in the unified interface.
        
        Args:
            event: The tkinter event that triggered the change (optional).
        
        Returns:
            None: Updates adaptive method as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "Grayscale")
            >>> threshold_window.threshold_method_var.set("Adaptive")
            >>> # User selects GAUSSIAN_C from dropdown
            >>> threshold_window._on_adaptive_method_change_unified()
            >>> # Adaptive method updated to GAUSSIAN_C
            
        Performance:
            Time Complexity: O(1) - Simple method update and callback.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self._on_dropdown_adaptive_method_change(event)
    
    def _update_ui_for_method_unified(self, method: str) -> None:
        """
        Update UI elements for the selected method in the unified window.
        
        Adjusts the user interface to show or hide controls appropriate
        for the selected thresholding method in the unified window interface.
        
        Args:
            method (str): The selected thresholding method name. Must be one of:
                        "Simple", "Adaptive", "Otsu", "Triangle", "Range".
        
        Returns:
            None: Updates UI elements as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "Grayscale")
            >>> threshold_window._update_ui_for_method_unified("Adaptive")
            >>> # Adaptive controls shown, threshold types limited to BINARY/BINARY_INV
            >>> threshold_window._update_ui_for_method_unified("Simple")
            >>> # Adaptive controls hidden, all threshold types available
            
        Performance:
            Time Complexity: O(1) - Fixed UI element show/hide operations.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if not hasattr(self, 'adaptive_frame'):
            return
            
        if method == "Adaptive":
            self.adaptive_frame.pack(fill='x', pady=5, after=self.threshold_type_combo.master)
            # Limit threshold types for adaptive
            if hasattr(self, 'threshold_type_combo'):
                self.threshold_type_combo['values'] = ["BINARY", "BINARY_INV"]
        else:
            self.adaptive_frame.pack_forget()
            # All types available for other methods
            if hasattr(self, 'threshold_type_combo'):
                self.threshold_type_combo['values'] = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]

    def create_simple_threshold_viewer(self) -> None:
        """
        Create a lightweight OpenCV-only thresholding interface without tkinter GUI.
        
        Creates a minimal thresholding interface using only OpenCV windows for
        parameter adjustment and preview. This mode is useful for lightweight
        thresholding operations without the full GUI overhead. Legacy compatibility mode.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates OpenCV windows as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window.create_simple_threshold_viewer()
            >>> # OpenCV-only interface created with trackbars
            >>> # No tkinter GUI components
            >>> print(threshold_window.window_created)  # True
            
        Performance:
            Time Complexity: O(1) - Lightweight OpenCV window and trackbar creation.
            Space Complexity: O(1) - Minimal memory for OpenCV interface only.
        """
        if self.window_created:
            return

        # Create a dedicated ImageViewer for thresholding
        self._create_threshold_viewer()
        self.trackbar_manager = self.threshold_viewer.trackbar
        
        # Mark as created but without tkinter window
        self.window_created = True
        pass
        
        # Create trackbars for the selected colorspace
        self.create_trackbars()
        
    def _create_colorspace_selection(self) -> None:
        """
        Create the color space selection section for the legacy thresholding window.
        
        Builds a labeled frame containing color space selection controls including
        a dropdown for color space selection and informational text about the
        current selection. This is used in the legacy window interface.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates UI components as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window.create_window()
            >>> threshold_window._create_colorspace_selection()
            >>> # Color space selection frame created with HSV pre-selected
            
        Performance:
            Time Complexity: O(1) - Fixed UI component creation.
            Space Complexity: O(1) - Fixed memory for selection controls.
        """
        colorspace_frame = ttk.LabelFrame(self.root, text="Color Space Selection", style=self.theme_manager.get_frame_style())
        colorspace_frame.pack(padx=10, pady=5, fill="x")
        
        # Available color spaces
        color_spaces = ["BGR", "HSV", "HLS", "Lab", "Luv", "YCrCb", "XYZ", "Grayscale"]
        
        # Info label
        info_text = "Available methods: Range, Simple, Otsu, Triangle, Adaptive\nAll color spaces supported with automatic conversion"
        info_label = ttk.Label(colorspace_frame, text=info_text, font=("Arial", 8), style=self.theme_manager.get_label_style())
        info_label.pack(pady=5)
        
        # Colorspace selection
        selection_frame = ttk.Frame(colorspace_frame, style=self.theme_manager.get_frame_style())
        selection_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(selection_frame, text="Color Space:", style=self.theme_manager.get_label_style()).pack(side=tk.LEFT, padx=(0, 10))
        
        self.color_space_var = tk.StringVar(value=self.color_space)
        color_space_combo = ttk.Combobox(selection_frame, textvariable=self.color_space_var, 
                                       values=color_spaces, state="readonly", width=15,
                                       style=self.theme_manager.get_combobox_style())
        color_space_combo.pack(side=tk.LEFT, padx=(0, 10))
        color_space_combo.bind('<<ComboboxSelected>>', self._on_colorspace_change)
        
        # Description label that updates with selection
        self.desc_var = tk.StringVar()
        desc_label = ttk.Label(selection_frame, textvariable=self.desc_var, font=("Arial", 8), 
                             style=self.theme_manager.get_label_style())
        desc_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Enhanced color space descriptions
        self.color_space_descriptions = {
            "BGR": "BGR - Standard OpenCV color format",
            "HSV": "HSV - Best for color-based detection",
            "HLS": "HLS - Alternative color representation", 
            "Lab": "Lab - Perceptually uniform color space",
            "Luv": "Luv - Another perceptually uniform space",
            "YCrCb": "YCrCb - Luma-chroma (JPEG standard)",
            "XYZ": "XYZ - Device-independent color space",
            "Grayscale": "Grayscale - Single intensity channel"
        }
        
        # Set initial description
        self.desc_var.set(self.color_space_descriptions.get(self.color_space, ""))
        
        # Determine if grayscale image
        if self.viewer._internal_images:
            current_idx = self.viewer.trackbar.parameters.get('show', 0)
            image, _ = self.viewer._internal_images[current_idx]
            is_grayscale = len(image.shape) == 2
            
            if is_grayscale:
                note_text = "Note: Grayscale image detected - color spaces will show converted results"
                note_label = ttk.Label(colorspace_frame, text=note_text, font=("Arial", 7), 
                                     style=self.theme_manager.get_label_style())
                note_label.pack(pady=2)

    def _on_colorspace_change(self, event=None) -> None:
        """
        Handle color space selection changes in the legacy window interface.
        
        Updates the thresholding interface when the user selects a different
        color space, including recreating the threshold viewer and method controls
        to match the new color space requirements.
        
        Args:
            event: The tkinter event that triggered the change (optional).
        
        Side Effects:
            - Updates internal color_space attribute
            - Recreates threshold viewer for new color space
            - Recreates method controls appropriate for new color space
            - Updates trackbar definitions
        """
        new_colorspace = self.color_space_var.get()
        
        # Update description
        self.desc_var.set(self.color_space_descriptions.get(new_colorspace, ""))
        
        # If colorspace actually changed, recreate the window content
        if new_colorspace != self.color_space:
            self.color_space = new_colorspace
            pass
            
            # Update window title
            self.root.title(f"Thresholding Controls - {self.color_space}")
            
            # Recreate the threshold viewer with new colorspace
            self._recreate_threshold_viewer()
            
            # Update trackbars for new colorspace
            self._recreate_method_controls()
            
            # Update the threshold processing
            self.update_threshold()
    
    def _recreate_threshold_viewer(self) -> None:
        """
        Recreate the threshold viewer for the newly selected color space.
        
        Destroys the existing threshold viewer and creates a new one configured
        for the current color space. This ensures the viewer uses appropriate
        processing and display settings for the selected color space.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Recreates threshold viewer as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "BGR")
            >>> threshold_window.color_space = "HSV"
            >>> threshold_window._recreate_threshold_viewer()
            >>> # Old BGR viewer destroyed, new HSV viewer created
            
        Performance:
            Time Complexity: O(1) - Viewer cleanup and recreation.
            Space Complexity: O(1) - Single viewer instance replacement.
        """
        if self.threshold_viewer:
            self.threshold_viewer.cleanup_viewer()
        
        # Get initial method for the new colorspace
        initial_method = "Simple" if self.color_space == "Grayscale" else "Range"
        initial_trackbars = self._get_trackbar_configs_for_method(initial_method)
        
        # Update viewer config
        self.threshold_viewer.config.trackbar = initial_trackbars
        self.threshold_viewer.config.process_window_name = f"Thresholded Process - {self.color_space}"
        self.threshold_viewer.config.trackbar_window_name = f"Thresholding Trackbars - {self.color_space}"
        
        # Recreate the viewer
        self.threshold_viewer.setup_viewer(image_processor_func=self._threshold_processor)
        self.trackbar_manager = self.threshold_viewer.trackbar
    
    def _recreate_method_controls(self) -> None:
        """
        Recreate method control sections for the newly selected color space.
        
        Rebuilds the method selection controls to match the capabilities of the
        current color space. Grayscale images get grayscale-specific controls,
        while color images get color-appropriate method options.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Recreates method controls as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "BGR")
            >>> threshold_window.color_space = "Grayscale"
            >>> threshold_window._recreate_method_controls()
            >>> # Color controls removed, grayscale controls created
            
        Performance:
            Time Complexity: O(n) where n is number of UI widgets to destroy/create.
            Space Complexity: O(1) - Fixed memory for new control widgets.
        """
        # Remove existing method controls (find all LabelFrames except colorspace)
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget.cget('text') not in ['Color Space Selection']:
                widget.destroy()
        
        # Also remove any separators after the colorspace section
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Separator):
                widget.destroy()
        
        # Recreate separator
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=5)
        
        # Recreate method controls based on new colorspace
        if self.color_space == "Grayscale":
            self._create_grayscale_method_controls()
        else:
            self._create_color_method_controls()
        
        # Recreate other sections
        self._create_status_section()
        self._create_buttons_section()
        
        # Update current method
        self.current_method = "Simple" if self.color_space == "Grayscale" else "Range"
        
    def _create_grayscale_method_controls(self) -> None:
        """
        Create thresholding method controls specific to grayscale images.
        
        Builds method selection controls optimized for grayscale image processing,
        including binary thresholding, Otsu's method, triangle method, and
        adaptive thresholding options.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates grayscale controls as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "Grayscale")
            >>> threshold_window._create_grayscale_method_controls()
            >>> # Creates: Simple, Adaptive, Otsu, Triangle method controls
            >>> # Plus threshold type and adaptive method dropdowns
            
        Performance:
            Time Complexity: O(1) - Fixed number of UI control creation.
            Space Complexity: O(1) - Fixed memory for grayscale controls.
        """
        """Create method controls for grayscale."""
        # Reset UI variables
        self.threshold_method_var = None
        self.threshold_type_var = None
        self.adaptive_method_var = None
        
        # Thresholding method selection
        method_frame = ttk.LabelFrame(self.root, text="Thresholding Method", style=self.theme_manager.get_frame_style())
        method_frame.pack(padx=10, pady=5, fill="x")
        
        self.threshold_method_var = tk.StringVar(value="Simple")
        methods = ["Simple", "Adaptive", "Otsu", "Triangle"]
        for method in methods:
            ttk.Radiobutton(method_frame, text=method, variable=self.threshold_method_var, 
                           value=method, command=self.on_method_change).pack(anchor="w")
        
        # Threshold type selection
        type_frame = ttk.LabelFrame(self.root, text="Threshold Type", style=self.theme_manager.get_frame_style())
        type_frame.pack(padx=10, pady=5, fill="x")
        
        self.threshold_type_var = tk.StringVar(value="BINARY")
        types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
        self.threshold_type_combo = ttk.Combobox(type_frame, textvariable=self.threshold_type_var, 
                                                values=types, state="readonly", width=15,
                                                style=self.theme_manager.get_combobox_style())
        self.threshold_type_combo.pack(padx=5, pady=5)
        self.threshold_type_combo.bind("<<ComboboxSelected>>", self._on_dropdown_threshold_type_change)
        
        # Adaptive method selection (initially hidden)
        self.adaptive_frame = ttk.LabelFrame(self.root, text="Adaptive Method", style=self.theme_manager.get_frame_style())
        self.adaptive_method_var = tk.StringVar(value="MEAN_C")
        adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
        self.adaptive_method_combo = ttk.Combobox(self.adaptive_frame, textvariable=self.adaptive_method_var,
                                                 values=adaptive_methods, state="readonly", width=15,
                                                 style=self.theme_manager.get_combobox_style())
        self.adaptive_method_combo.pack(padx=5, pady=5)
        self.adaptive_method_combo.bind("<<ComboboxSelected>>", self._on_dropdown_adaptive_method_change)
    
    def _create_color_method_controls(self) -> None:
        """
        Create thresholding method controls specific to color images.
        
        Builds method selection controls optimized for color image processing,
        including range-based thresholding and other color-appropriate methods.
        Currently focuses on range-based thresholding for multi-channel color spaces.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates color controls as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window._create_color_method_controls()
            >>> # Creates: Range, Simple, Otsu, Triangle, Adaptive method controls
            >>> # Plus threshold type dropdown and advanced controls
            
        Performance:
            Time Complexity: O(1) - Fixed number of UI control creation.
            Space Complexity: O(1) - Fixed memory for color method controls.
        """
        """Create method controls for color spaces."""
        # Reset UI variables
        self.threshold_method_var = None
        self.threshold_type_var = None
        self.adaptive_method_var = None
        
        # Color space thresholding method selection
        method_frame = ttk.LabelFrame(self.root, text="Thresholding Method", style=self.theme_manager.get_frame_style())
        method_frame.pack(padx=10, pady=5, fill="x")
        
        self.threshold_method_var = tk.StringVar(value="Range")
        methods = ["Range", "Simple", "Otsu", "Triangle", "Adaptive"]
        for method in methods:
            ttk.Radiobutton(method_frame, text=method, variable=self.threshold_method_var, 
                           value=method, command=self.on_color_method_change).pack(anchor="w")
        
        # Threshold type selection for color spaces
        type_frame = ttk.LabelFrame(self.root, text="Threshold Type", style=self.theme_manager.get_frame_style())
        type_frame.pack(padx=10, pady=5, fill="x")
        
        self.threshold_type_var = tk.StringVar(value="BINARY")
        types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
        self.threshold_type_combo = ttk.Combobox(type_frame, textvariable=self.threshold_type_var, 
                                                values=types, state="readonly", width=15,
                                                style=self.theme_manager.get_combobox_style())
        self.threshold_type_combo.pack(padx=5, pady=5)
        self.threshold_type_combo.bind("<<ComboboxSelected>>", self._on_dropdown_threshold_type_change)
        
        # Advanced controls frame (initially hidden)
        self.advanced_controls_frame = ttk.LabelFrame(self.root, text="Advanced Controls", style=self.theme_manager.get_frame_style())
        
        # Adaptive method selection for color spaces
        self.adaptive_method_var = tk.StringVar(value="MEAN_C")
        adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
        ttk.Label(self.advanced_controls_frame, text="Adaptive Method:", style=self.theme_manager.get_label_style()).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.adaptive_method_combo = ttk.Combobox(self.advanced_controls_frame, textvariable=self.adaptive_method_var,
                                                 values=adaptive_methods, state="readonly", width=12,
                                                 style=self.theme_manager.get_combobox_style())
        self.adaptive_method_combo.grid(row=0, column=1, padx=5, pady=2)
        self.adaptive_method_combo.bind("<<ComboboxSelected>>", self._on_dropdown_adaptive_method_change)
    
    def _create_status_section(self) -> None:
        """
        Create the status display section for parameter information.
        
        Creates a labeled frame that displays current thresholding parameters
        and settings. This provides users with feedback about the current
        configuration state.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates status display as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window._create_status_section()
            >>> # Status display created showing current parameters
            >>> # Text area shows method, type, and parameter values
            
        Performance:
            Time Complexity: O(1) - Fixed status display widget creation.
            Space Complexity: O(1) - Fixed memory for status text widget.
        """
        # Status display frame
        status_frame = ttk.LabelFrame(self.root, text="Current Parameters", style=self.theme_manager.get_frame_style())
        status_frame.pack(padx=10, pady=5, fill="x")
        
        self.status_text = tk.Text(status_frame, height=4, width=40, font=("Consolas", 8))
        self.status_text.pack(padx=5, pady=5, fill="x")
        self.status_text.config(state=tk.DISABLED)  # Read-only
    
    def _create_buttons_section(self) -> None:
        """
        Create the action buttons section for configuration management.
        
        Creates buttons for saving, loading, and managing thresholding
        configurations, including preset management functionality.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates button section as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window._create_buttons_section()
            >>> # Button frame created with Presets, Save Config, Load Config buttons
            
        Performance:
            Time Complexity: O(1) - Fixed number of button creation.
            Space Complexity: O(1) - Fixed memory for button widgets.
        """
        button_frame = ttk.Frame(self.root, style=self.theme_manager.get_frame_style())
        button_frame.pack(padx=10, pady=10)
        
        # Add preset and save/load buttons
        ttk.Button(button_frame, text="Presets ▼", command=self._show_presets,
                  style=self.theme_manager.get_button_style()).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Config", command=self._save_config,
                  style=self.theme_manager.get_button_style()).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Config", command=self._load_config,
                  style=self.theme_manager.get_button_style()).pack(side=tk.LEFT, padx=5)
        
    def _create_threshold_viewer(self) -> None:
        """
        Create a dedicated ImageViewer instance for thresholding operations.
        
        Creates a specialized ImageViewer configured specifically for threshold
        preview with full zoom, pan, and interaction capabilities. The viewer
        is optimized for real-time threshold visualization.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates threshold viewer as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window._create_threshold_viewer()
            >>> # Dedicated ImageViewer created for threshold preview
            >>> # Configured with zoom/pan and HSV processing
            
        Performance:
            Time Complexity: O(1) - Viewer creation and configuration.
            Space Complexity: O(1) - Single specialized viewer instance.
        """
        # Import ImageViewer dynamically to avoid circular imports
        from ..core.image_viewer import ImageViewer
        
        # Create configuration for the threshold viewer
        threshold_config = ViewerConfig()
        threshold_config.process_window_name = f"Thresholded Process - {self.color_space}"
        threshold_config.trackbar_window_name = f"Thresholding Trackbars - {self.color_space}" 
        threshold_config.text_window_name = f"Thresholding Text - {self.color_space}"  # Won't be created
        threshold_config.screen_width = 800
        threshold_config.screen_height = 600
        threshold_config.enable_debug = True
        # # Set trackbar window size for better parameter name visibility
        # threshold_config.trackbar_window_width = 600
        # threshold_config.trackbar_window_height = 400
        
        # Get initial trackbar definitions using the same method as switching
        initial_method = "Simple" if self.color_space == "Grayscale" else "Range"
        initial_trackbars = self._get_trackbar_configs_for_method(initial_method)
            
        # Create a completely custom ImageViewer that doesn't create unwanted windows
        self.threshold_viewer = self._create_minimal_image_viewer(threshold_config, initial_trackbars)
        
        # Set up the viewer with the threshold processor function
        self.threshold_viewer.setup_viewer(image_processor_func=self._threshold_processor)
        
    def _create_minimal_image_viewer(self, config, trackbar_definitions):
        """
        Create a minimal ImageViewer optimized for thresholding operations.
        
        Builds a lightweight ImageViewer that only creates the windows and
        functionality needed for thresholding, avoiding unnecessary overhead
        while maintaining full zoom, pan, and interaction capabilities.
        
        Args:
            config: ViewerConfig instance with window configuration.
            trackbar_definitions: List of trackbar configuration dictionaries.
        
        Returns:
            Configured ImageViewer instance optimized for thresholding.
        
        Side Effects:
            - Creates minimal ImageViewer with custom methods
            - Sets up threshold-specific processing pipeline
            - Configures zoom and pan functionality
            - Establishes parameter change callbacks
        """
        """Create a minimal ImageViewer that only creates the windows we want."""
        # Import ImageViewer dynamically
        from ..core.image_viewer import ImageViewer
        from ..events.mouse_handler import MouseHandler
        from ..controls.trackbar_manager import TrackbarManager
        from ..analysis import ImageAnalyzer
        from types import SimpleNamespace
        import numpy as np
        
        # Create the ImageViewer but bypass its normal initialization
        viewer = object.__new__(ImageViewer)  # Create without calling __init__
        
        # Set configuration
        viewer.config = config
        viewer.config.trackbar = trackbar_definitions
        viewer.config.enable_debug = True
        
        # Prevent any analysis window creation by setting a flag
        viewer.config.create_analysis_window = False
        viewer.config.create_text_window = False
        
        # Basic initialization
        viewer.max_headless_iterations = 1
        viewer._headless_iteration_count = 0
        viewer._app_debug_mode = True
        viewer._should_continue_loop = True
        viewer._auto_initialized = False
        viewer._params_changed = False
        viewer._event_handlers = {}
        
        # Initialize essential attributes to prevent AttributeError
        viewer._internal_images = []
        viewer.current_image_dims = None
        viewer.size_ratio = 1.0
        viewer.show_area = [0, 0, config.screen_width, config.screen_height]
        viewer.address = "(0,0)"
        viewer.initial_window_size = (config.screen_width, config.screen_height)
        viewer.user_image_processor = None
        viewer.image_processing_func_internal = None
        viewer._cached_scaled_image = None
        viewer._cached_size_ratio = None
        viewer._cached_show_area = None
        
        # Add zoom/pan limits similar to main window
        viewer.config.min_size_ratio = 0.1
        viewer.config.max_size_ratio = 20.0
        
        # Mock text window attributes without creating actual window
        viewer.text_image = np.full((getattr(config, 'text_window_height', 200), getattr(config, 'text_window_width', 400), 3), 255, dtype=np.uint8)
        
        # Initialize components 
        viewer.mouse = MouseHandler()
        viewer.mouse.mouse_point = [0, 0]  # Initialize mouse position
        viewer.trackbar = TrackbarManager(config.trackbar_window_name)
        viewer.windows = self._create_custom_window_manager(config)
        viewer.analyzer = ImageAnalyzer()
        
        # Create completely inert analysis window mock
        viewer.analysis_window = SimpleNamespace()
        viewer.analysis_window.create_window = lambda: None
        viewer.analysis_window.cleanup_windows = lambda: None 
        viewer.analysis_window.update_selections = lambda: None
        viewer.analysis_window._process_tk_events = lambda: None
        viewer.analysis_window.window_created = False
        
        # Override ALL methods that could create unwanted windows
        viewer._show_text_window = lambda: None
        viewer._text_mouse_callback = lambda event, x, y, flags, param: None
        viewer._process_tk_events = lambda: None
        viewer._create_text_window = lambda: None
        viewer._create_analysis_control_window = lambda: None
        
        # Add essential methods from ImageViewer
        viewer.log = self._create_log_method(viewer)
        viewer.setup_viewer = self._create_setup_viewer_method(viewer)
        viewer.cleanup_viewer = self._create_cleanup_viewer_method(viewer)
        viewer.should_loop_continue = lambda: viewer._should_continue_loop
        viewer._process_frame_and_check_quit = self._create_process_frame_method(viewer)
        
        # Add zoom/pan transformation methods
        viewer._apply_zoom_pan_transform = self._create_zoom_pan_method(viewer)
        
        # Add display_images property that triggers processing
        def get_display_images():
            return viewer._internal_images
            
        def set_display_images(image_list):
            if not isinstance(image_list, list) or not image_list:
                viewer._internal_images = [(np.zeros((100, 100, 1), dtype=np.uint8), "Empty")]
                return
                
            # Validate images
            valid_images = []
            for item in image_list:
                if isinstance(item, tuple) and len(item) == 2:
                    img, title = item
                    if isinstance(img, np.ndarray) and img.size > 0:
                        valid_images.append((img, title))
                        
            if not valid_images:
                viewer._internal_images = [(np.zeros((100, 100, 1), dtype=np.uint8), "Invalid Images")]
            else:
                viewer._internal_images = valid_images
            
            # Process the image if viewer is active
            if viewer.config.enable_debug and viewer._should_continue_loop and hasattr(viewer, 'windows') and viewer.windows.windows_created:
                try:
                    viewer._process_frame_and_check_quit()
                except Exception as e:
                    print(f"Error in display update: {e}")
        
        # Create display_images as simple methods instead of property
        def get_display_images():
            return viewer._internal_images
            
        def set_display_images(image_list):
            if not isinstance(image_list, list) or not image_list:
                viewer._internal_images = [(np.zeros((100, 100, 1), dtype=np.uint8), "Empty")]
                return
                
            # Validate images
            valid_images = []
            for item in image_list:
                if isinstance(item, tuple) and len(item) == 2:
                    img, title = item
                    if isinstance(img, np.ndarray) and img.size > 0:
                        valid_images.append((img, title))
                        
            if not valid_images:
                viewer._internal_images = [(np.zeros((100, 100, 1), dtype=np.uint8), "Invalid Images")]
            else:
                viewer._internal_images = valid_images
            
            # Process the image if viewer is active
            if viewer.config.enable_debug and viewer._should_continue_loop and hasattr(viewer, 'windows') and viewer.windows.windows_created:
                try:
                    viewer._process_frame_and_check_quit()
                except Exception as e:
                    print(f"Error in display update: {e}")
        
        # Add methods to viewer
        viewer.get_display_images = get_display_images
        viewer.set_display_images = set_display_images
        
        # Note: ImageViewer already has display_images property, no need to override
        # Initialize with empty images if not already initialized
        if not hasattr(viewer, '_internal_images'):
            viewer._internal_images = []
        
        return viewer
        
    def _create_log_method(self, viewer) -> callable:
        """
        Create a no-operation log method for the minimal viewer.
        
        Provides a lightweight logging function that does nothing, reducing
        overhead in the minimal viewer while maintaining interface compatibility.
        
        Args:
            viewer: The ImageViewer instance to create the log method for.
        
        Returns:
            callable: No-op log function.
        """
        def log_method(message):
            pass  # No logging for thresholding viewer
        return log_method
        
    def _create_setup_viewer_method(self, viewer) -> callable:
        """
        Create a setup_viewer method optimized for thresholding operations.
        
        Creates a specialized setup method that initializes the viewer for
        thresholding with optimized window management, trackbar setup, and
        processing pipeline configuration.
        
        Args:
            viewer: The ImageViewer instance to create the setup method for.
        
        Returns:
            callable: Optimized setup_viewer method.
        
        Side Effects:
            - Sets up viewer state and configuration
            - Creates custom window manager
            - Initializes trackbar system
            - Configures processing pipeline
        """
        def setup_viewer_method(initial_images_for_first_frame=None, image_processor_func=None):
            pass
            viewer._should_continue_loop = True
            viewer.user_image_processor = image_processor_func
            
            # Initialize parameters from trackbar definitions
            viewer.trackbar.parameters = {}
            for trackbar_config in viewer.config.trackbar:
                param_name = trackbar_config.get('param_name')
                initial_value = trackbar_config.get('initial_value', 0)
                if param_name:
                    viewer.trackbar.parameters[param_name] = initial_value
            
            # Only create windows if debug is enabled
            if viewer.config.enable_debug:
                # Create mouse callback for zoom/pan functionality similar to main window
                def mouse_callback(event, x, y, flags, param):
                    import cv2  # Import cv2 for event constants
                    try:
                        # Get image dimensions for coordinate transformations
                        if not viewer._internal_images or not viewer.current_image_dims:
                            return
                            
                        orig_img_h, orig_img_w = viewer.current_image_dims[:2]
                        view_w, view_h = viewer.config.screen_width, viewer.config.screen_height
                        
                        # Convert mouse coordinates to view coordinates (with bounds checking)
                        x_view = max(0, min(x, view_w - 1))
                        y_view = max(0, min(y, view_h - 1))
                        
                        # Convert view coordinates to scaled image coordinates
                        x_on_scaled_img = viewer.show_area[0] + x_view
                        y_on_scaled_img = viewer.show_area[1] + y_view
                        
                        # Convert scaled image coordinates to original image coordinates
                        current_size_ratio = viewer.size_ratio if abs(viewer.size_ratio) > 1e-6 else 1e-6
                        ptr_x_orig = int(x_on_scaled_img / current_size_ratio)
                        ptr_y_orig = int(y_on_scaled_img / current_size_ratio)
                        
                        # Clamp to original image bounds
                        ptr_x_orig = max(0, min(ptr_x_orig, orig_img_w - 1))
                        ptr_y_orig = max(0, min(ptr_y_orig, orig_img_h - 1))
                        
                        # Update mouse position
                        viewer.mouse.mouse_point = [x_view, y_view]
                        viewer.mouse.scale_ptr = [ptr_x_orig, ptr_y_orig]
                        viewer.address = f"({ptr_x_orig},{ptr_y_orig})"
                        
                        # Handle zoom functionality (mouse wheel)
                        if event == cv2.EVENT_MOUSEWHEEL:
                            delta = flags
                            ctrl_key = (flags & cv2.EVENT_FLAG_CTRLKEY) != 0
                            zoom_factor = 1.15 if not ctrl_key else 1.40
                            
                            if delta > 0:
                                viewer.size_ratio *= zoom_factor
                            else:
                                viewer.size_ratio /= zoom_factor
                                
                            # Apply zoom limits
                            viewer.size_ratio = max(viewer.config.min_size_ratio, 
                                                  min(viewer.size_ratio, viewer.config.max_size_ratio))
                            
                            # Adjust show_area to zoom at mouse cursor
                            viewer.show_area[0] = int(ptr_x_orig * viewer.size_ratio - x_view)
                            viewer.show_area[1] = int(ptr_y_orig * viewer.size_ratio - y_view)
                            
                            # Silent zoom - no need to log zoom changes
                            
                            # Force display refresh after zoom
                            if hasattr(viewer, '_process_frame_and_check_quit'):
                                viewer._process_frame_and_check_quit()
                        
                        # Handle pan functionality (middle button drag)
                        elif event == cv2.EVENT_MBUTTONDOWN:
                            viewer.mouse.is_middle_button_down = True
                            viewer.mouse.middle_button_start = (x_view, y_view)
                            viewer.mouse.middle_button_area_start = (viewer.show_area[0], viewer.show_area[1])
                            
                        elif event == cv2.EVENT_MBUTTONUP:
                            viewer.mouse.is_middle_button_down = False
                            
                        elif (event == cv2.EVENT_MOUSEMOVE and 
                              hasattr(viewer.mouse, 'is_middle_button_down') and viewer.mouse.is_middle_button_down and
                              hasattr(viewer.mouse, 'middle_button_start') and hasattr(viewer.mouse, 'middle_button_area_start')):
                            # Calculate pan delta
                            dx = x_view - viewer.mouse.middle_button_start[0]
                            dy = y_view - viewer.mouse.middle_button_start[1]
                            
                            # Apply pan to show_area
                            viewer.show_area[0] = viewer.mouse.middle_button_area_start[0] - dx
                            viewer.show_area[1] = viewer.mouse.middle_button_area_start[1] - dy
                            
                            # Force display refresh during pan
                            if hasattr(viewer, '_process_frame_and_check_quit'):
                                viewer._process_frame_and_check_quit()
                        
                                
                    except Exception as e:
                        print(f"Mouse callback error: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Create only the windows we need (process + trackbar)
                viewer.windows.create_windows(mouse_callback, None)
                
                # Create trackbars only if windows were created successfully
                if viewer.windows.windows_created:
                    pass
                    for trackbar_config in viewer.config.trackbar:
                        try:
                            viewer.trackbar.create_trackbar(trackbar_config, viewer)
                        except Exception as e:
                            print(f"Error creating trackbar {trackbar_config.get('name', 'Unknown')}: {e}")
                else:
                    pass
                    viewer._should_continue_loop = False
                    return
            
            # Set initial images
            if image_processor_func and viewer._should_continue_loop:
                try:
                    temp_images = image_processor_func(dict(viewer.trackbar.parameters), lambda x: None)
                    if temp_images:
                        viewer._internal_images = temp_images
                    else:
                        viewer._internal_images = [(np.zeros((100, 100, 1), dtype=np.uint8), "No Images")]
                except Exception as e:
                    print(f"Error in initial image processing: {e}")
                    viewer._internal_images = [(np.zeros((100, 100, 1), dtype=np.uint8), "Process Error")]
            elif initial_images_for_first_frame:
                viewer._internal_images = initial_images_for_first_frame
            else:
                viewer._internal_images = [(np.zeros((100, 100, 1), dtype=np.uint8), "Empty Start")]
            
            pass
            
        return setup_viewer_method
        
    def _create_cleanup_viewer_method(self, viewer) -> callable:
        """
        Create a cleanup method for proper resource management.
        
        Creates a cleanup method that properly destroys windows and releases
        resources when the thresholding viewer is no longer needed.
        
        Args:
            viewer: The ImageViewer instance to create the cleanup method for.
        
        Returns:
            callable: Cleanup method for resource deallocation.
        
        Side Effects:
            - Destroys OpenCV windows
            - Releases viewer resources
        """
        def cleanup_viewer_method():
            pass
            viewer._should_continue_loop = False
            if hasattr(viewer.windows, 'destroy_all_windows'):
                viewer.windows.destroy_all_windows()
        return cleanup_viewer_method
        
    def _create_process_frame_method(self, viewer) -> callable:
        """
        Create an optimized frame processing method for threshold visualization.
        
        Creates a specialized processing method that handles image display
        with zoom, pan, and threshold overlay capabilities optimized for
        real-time threshold preview.
        
        Args:
            viewer: The ImageViewer instance to create the process method for.
        
        Returns:
            callable: Optimized frame processing method.
        
        Side Effects:
            - Processes and displays images with transformations
            - Applies zoom and pan transformations
            - Updates display windows
        """
        def process_frame_method():
            if not viewer.config.enable_debug or not viewer._should_continue_loop:
                return
            if not viewer.windows.windows_created:
                return
                
            if not viewer._internal_images:
                viewer._internal_images = [(np.zeros((100, 100, 1), dtype=np.uint8), "No Images")]
            
            try:
                # Process the current image and display it with proper scaling and mouse interaction
                if viewer._internal_images:
                    current_image, title = viewer._internal_images[0]
                    if current_image is not None and current_image.size > 0:
                        
                        # Update image dimensions for mouse calculations
                        viewer.current_image_dims = current_image.shape
                        
                        # Apply zoom and pan transformations similar to main viewer
                        display_image = viewer._apply_zoom_pan_transform(current_image)
                        
                        # Display the processed image
                        cv2.imshow(viewer.config.process_window_name, display_image)
                
                # Handle key events
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    pass
                    viewer._should_continue_loop = False
                elif key == ord('r'):
                    # Reset zoom and pan
                    viewer.size_ratio = 1.0
                    viewer.show_area[0], viewer.show_area[1] = 0, 0
                    # Reset window size to match original image dimensions (same as main ImageViewer)
                    if viewer.current_image_dims:
                        viewer.windows.resize_process_window(viewer.current_image_dims[1], viewer.current_image_dims[0])
                    else:
                        viewer.windows.resize_process_window(viewer.config.screen_width, viewer.config.screen_height)
                    # Silent view reset
                    
            except Exception as e:
                print(f"Error in process_frame: {e}")
                import traceback
                traceback.print_exc()
                
        return process_frame_method
        
    def _create_zoom_pan_method(self, viewer) -> callable:
        """
        Create zoom and pan transformation method for threshold viewer.
        
        Creates a method that handles zoom and pan transformations identical
        to the main ImageViewer, providing consistent navigation experience
        in the threshold preview.
        
        Args:
            viewer: The ImageViewer instance to create the method for.
        
        Returns:
            callable: Zoom and pan transformation method.
        
        Performance:
            Time Complexity: O(1) - Direct coordinate transformations.
            Space Complexity: O(1) - No additional memory allocation.
        """
        def zoom_pan_transform(image):
            import cv2
            import numpy as np
            
            if image is None or image.size == 0:
                return image
                
            # Get original image dimensions
            orig_h, orig_w = image.shape[:2]
            viewer.current_image_dims = image.shape
            
            # Calculate scaled dimensions (same as main ImageViewer)
            scaled_w, scaled_h = int(orig_w * viewer.size_ratio), int(orig_h * viewer.size_ratio)
            
            if scaled_w <= 0 or scaled_h <= 0: 
                min_dim_on_screen = 10 
                viewer.size_ratio = max(viewer.config.min_size_ratio, float(min_dim_on_screen) / max(orig_w, orig_h, 1))
                scaled_w = max(min_dim_on_screen, int(orig_w * viewer.size_ratio))
                scaled_h = max(min_dim_on_screen, int(orig_h * viewer.size_ratio))
            
            # Start with default viewport dimensions
            view_w, view_h = viewer.config.screen_width, viewer.config.screen_height
            
            # Handle window resizing (same as main ImageViewer)
            try: 
                _wx, _wy, current_win_w, current_win_h = cv2.getWindowImageRect(viewer.config.process_window_name)
                max_win_w = viewer.config.desktop_resolution[0] if viewer.config.desktop_resolution else viewer.config.screen_width * 2
                max_win_h = viewer.config.desktop_resolution[1] if viewer.config.desktop_resolution else viewer.config.screen_height * 2
                target_win_w = max(viewer.config.min_window_size[0], min(scaled_w, max_win_w))
                target_win_h = max(viewer.config.min_window_size[1], min(scaled_h, max_win_h))

                if abs(current_win_w - target_win_w) > 1 or abs(current_win_h - target_win_h) > 1 :
                    viewer.windows.resize_process_window(target_win_w, target_win_h)
                # Get ACTUAL window size after resizing (key difference!)
                _wx, _wy, view_w, view_h = cv2.getWindowImageRect(viewer.config.process_window_name)
            except cv2.error: 
                pass 
            view_w, view_h = max(1, view_w), max(1, view_h)

            # Scale the image (same as main ImageViewer)
            scaled_image_for_roi = cv2.resize(image, (scaled_w, scaled_h), interpolation=cv2.INTER_NEAREST)
            
            # Handle viewport clipping with ACTUAL window dimensions
            max_show_x = max(0, scaled_w - view_w)
            max_show_y = max(0, scaled_h - view_h)
            viewer.show_area[0] = max(0, min(viewer.show_area[0], max_show_x))
            viewer.show_area[1] = max(0, min(viewer.show_area[1], max_show_y))
            
            # Extract the viewable region (same as main ImageViewer)
            roi_x_start = viewer.show_area[0]
            roi_y_start = viewer.show_area[1]
            roi_w_actual = min(view_w, scaled_w - roi_x_start)
            roi_h_actual = min(view_h, scaled_h - roi_y_start)
            
            if roi_w_actual > 0 and roi_h_actual > 0:
                try:
                    viewport_image = scaled_image_for_roi[roi_y_start:roi_y_start + roi_h_actual, 
                                                        roi_x_start:roi_x_start + roi_w_actual]
                except Exception as e:
                    print(f"Viewport extraction error: {e}")
                    return image
                    
                # Create display canvas with exact viewport dimensions
                if len(image.shape) == 3:
                    display_canvas = np.zeros((view_h, view_w, image.shape[2]), dtype=image.dtype)
                else:
                    display_canvas = np.zeros((view_h, view_w), dtype=image.dtype)
                
                # Place the viewport image in the canvas
                display_canvas[:viewport_image.shape[0], :viewport_image.shape[1]] = viewport_image
                return display_canvas
            else:
                # Return black canvas if no valid viewport
                if len(image.shape) == 3:
                    return np.zeros((view_h, view_w, image.shape[2]), dtype=image.dtype)
                else:
                    return np.zeros((view_h, view_w), dtype=image.dtype)
                    
        return zoom_pan_transform
        
        
    def _create_custom_window_manager(self, config):
        """
        Create a custom window manager optimized for thresholding operations.
        
        Creates a specialized window manager that only creates the process
        and trackbar windows needed for thresholding, avoiding unnecessary
        text windows and reducing resource usage.
        
        Args:
            config: ViewerConfig instance with window configuration.
        
        Returns:
            ThresholdWindowManager: Custom window manager instance.
        
        Side Effects:
            - Creates nested ThresholdWindowManager class
            - Configures window creation for thresholding needs
        """
        from types import SimpleNamespace
        
        class ThresholdWindowManager:
            """
            Custom window manager optimized for thresholding operations.
            
            Specialized window manager that creates only the essential windows
            needed for thresholding (process and trackbar windows), avoiding
            unnecessary text windows to reduce resource usage and complexity.
            
            Attributes:
                config: ViewerConfig instance with window configuration.
                windows_created (bool): Flag indicating if windows have been created.
            """
            
            def __init__(self, config) -> None:
                """
                Initialize the threshold window manager.
                
                Args:
                    config: ViewerConfig instance containing window settings.
                """
                self.config = config
                self.windows_created = False
                
            def create_windows(self, mouse_callback, text_mouse_callback) -> None:
                """
                Create only the process and trackbar windows needed for thresholding.
                
                Creates a minimal set of OpenCV windows optimized for thresholding
                operations, including the main process window for image display
                and trackbar window for parameter controls.
                
                Args:
                    mouse_callback: Callback function for mouse events in process window.
                    text_mouse_callback: Text mouse callback (unused in threshold mode).
                
                Side Effects:
                    - Creates process window with zoom/pan capabilities
                    - Creates trackbar window if trackbars are defined
                    - Sets up mouse callbacks for interaction
                    - Sets windows_created flag on success
                """
                if self.windows_created: return
                if not self.config.enable_debug: return
                
                try:
                    # Only create process window and trackbar window
                    cv2.namedWindow(self.config.process_window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
                    cv2.resizeWindow(self.config.process_window_name, self.config.screen_width, self.config.screen_height)
                    
                    # Set mouse callback for zoom/pan functionality
                    if mouse_callback:
                        cv2.setMouseCallback(self.config.process_window_name, mouse_callback)
                    
                    # Create trackbar window if trackbar definitions exist
                    if self.config.trackbar:
                        cv2.namedWindow(self.config.trackbar_window_name, cv2.WINDOW_AUTOSIZE)
                        if hasattr(self.config, 'trackbar_window_width') and hasattr(self.config, 'trackbar_window_height'):
                            cv2.resizeWindow(self.config.trackbar_window_name, self.config.trackbar_window_width, self.config.trackbar_window_height)
                        else:
                            cv2.resizeWindow(self.config.trackbar_window_name, 600, 400)  # Wider for long parameter names
                    
                    self.windows_created = True
                    
                except Exception as e:
                    print(f"Error creating threshold windows: {e}")
                    self.windows_created = False
                    
            def destroy_all_windows(self) -> None:
                """
                Destroy created OpenCV windows and clean up resources.
                
                Selectively destroys only the windows created by this manager
                (process and trackbar windows) and resets the internal state.
                
                Side Effects:
                    - Destroys process and trackbar windows if they exist
                    - Resets windows_created flag
                    - Handles window destruction errors gracefully
                """
                if self.windows_created:
                    try:
                        # Only destroy our specific windows
                        if cv2.getWindowProperty(self.config.process_window_name, cv2.WND_PROP_VISIBLE) >= 1:
                            cv2.destroyWindow(self.config.process_window_name)
                    except: pass
                    try:
                        if self.config.trackbar and cv2.getWindowProperty(self.config.trackbar_window_name, cv2.WND_PROP_VISIBLE) >= 1:
                            cv2.destroyWindow(self.config.trackbar_window_name)
                    except: pass
                    self.windows_created = False
                    
            def resize_process_window(self, width: int, height: int) -> None:
                """
                Resize the process window to the specified dimensions.
                
                Adjusts the size of the main process window while applying
                configured size constraints and validating window visibility.
                
                Args:
                    width: Target width in pixels.
                    height: Target height in pixels.
                
                Side Effects:
                    - Resizes process window if valid and visible
                    - Applies size constraints from configuration
                    - Silently handles resize errors
                """
                if not self.windows_created: return
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
                except: pass
        
        return ThresholdWindowManager(config)
        
    def _get_initial_grayscale_trackbars(self) -> list:
        """
        Get initial trackbar definitions for grayscale thresholding.
        
        Returns the default set of trackbars appropriate for grayscale
        image thresholding operations.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            list: List of trackbar configuration dictionaries for grayscale.
                 Contains threshold and max_value trackbars.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "Grayscale")
            >>> trackbars = threshold_window._get_initial_grayscale_trackbars()
            >>> print(len(trackbars))  # 2
            >>> print(trackbars[0]['name'])  # "Thresh"
            
        Performance:
            Time Complexity: O(1) - Fixed trackbar creation.
            Space Complexity: O(1) - Fixed trackbar configuration list.
        """
        # Create lambdas to avoid method reference issues
        return [
            make_trackbar("Thresh", "threshold", 255, 127, custom_callback=lambda v: self._on_param_change(v)),
            make_trackbar("Max", "max_value", 255, 255, custom_callback=lambda v: self._on_param_change(v))
        ]
        
    def _get_initial_color_trackbars(self) -> list:
        """
        Get initial trackbar definitions for color space thresholding.
        
        Returns the default set of trackbars appropriate for color image
        thresholding in the current color space.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            list: List of trackbar configuration dictionaries for color spaces.
                 Contains min/max trackbars for each color channel.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> trackbars = threshold_window._get_initial_color_trackbars()
            >>> print(len(trackbars))  # 6 (H Min/Max, S Min/Max, V Min/Max)
            >>> print(trackbars[0]['name'])  # "H Min"
            
        Performance:
            Time Complexity: O(n) where n is number of color channels.
            Space Complexity: O(n) - Trackbar configuration for each channel.
        """
        ranges = self.ranges.get(self.color_space, {})
        trackbars = []
        
        # Add range trackbars by default
        for channel, (min_val, max_val) in ranges.items():
            trackbars.extend([
                make_trackbar(f"{channel} Min", f"{channel.lower()}_min", max_val, min_val, custom_callback=lambda v: self._on_param_change(v)),
                make_trackbar(f"{channel} Max", f"{channel.lower()}_max", max_val, max_val, custom_callback=lambda v: self._on_param_change(v))
            ])
            
        return trackbars
        
    def _on_param_change(self, value=None) -> None:
        """
        Handle parameter changes from trackbars and update threshold display.
        
        Called when any trackbar value changes, triggering an update of the
        threshold visualization and status display.
        
        Args:
            value: The new parameter value (optional).
        
        Side Effects:
            - Triggers threshold viewer update
            - Updates status display
            - Prevents recursive parameter updates
        """
        try:
            if self.threshold_viewer and not self.is_processing:
                # Force immediate threshold update
                self.update_threshold()
                pass
        except Exception as e:
            print(f"Error in _on_param_change: {e}")
            import traceback
            traceback.print_exc()
            
    def _threshold_processor(self, params: dict, log_func: callable) -> list:
        """
        Process images for the threshold viewer with current parameters.
        
        Main processing function that applies thresholding to the current
        image using the specified parameters and returns the processed
        result for display.
        
        Args:
            params: Dictionary of current parameter values from trackbars.
            log_func: Logging function for status messages.
        
        Returns:
            list: List of (image, title) tuples for display.
        
        Side Effects:
            - Processes current image with thresholding
            - Updates status display
        """
        """Process images for the threshold viewer."""
        if not self.viewer._internal_images or self.is_processing:
            return [(np.zeros((100, 100, 1), dtype=np.uint8), "No Image")]
            
        self.is_processing = True
        try:
            # Get current image from main viewer
            current_idx = self.viewer.trackbar.parameters.get('show', 0)
            image, title = self.viewer._internal_images[current_idx]
            
            # Apply thresholding
            thresholded_image = self._apply_thresholding(image, params)
            
            return [(thresholded_image, f"Thresholded - {self.color_space}")]
        finally:
            self.is_processing = False
            
    def _apply_thresholding(self, image, params: dict):
        """
        Apply thresholding to the image using current parameters.
        
        Core thresholding function that processes the input image according
        to the current method and parameter settings, supporting multiple
        color spaces and thresholding techniques. Main processing algorithm.
        
        Args:
            image: Input image array to threshold. Must be valid numpy array.
            params (dict): Dictionary of current parameter values from trackbars.
                          Contains method-specific parameters like threshold values,
                          color channel ranges, and processing options.
        
        Returns:
            numpy.ndarray: Thresholded image array with same dimensions as input.
                          Binary or processed image based on selected method.
        
        Examples:
            >>> params = {'threshold': 127, 'max_value': 255, 'threshold_type_idx': 0}
            >>> result = threshold_window._apply_thresholding(image, params)
            >>> # Returns thresholded binary image
            >>> print(result.shape)  # Same as input image shape
            
        Performance:
            Time Complexity: O(n) where n is the number of pixels in the image.
            Space Complexity: O(n) for color space conversion and image copies.
        """
        processor = ThresholdProcessor(image)
        converted_image = processor.convert_color_space(self.color_space)

        if self.color_space == "Grayscale":
            # Get parameters
            threshold_value = params.get("threshold", 127)
            max_value = params.get("max_value", 255)
            
            # Get threshold type
            threshold_types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
            type_idx = params.get("threshold_type_idx", 0)
            threshold_type = threshold_types[min(type_idx, len(threshold_types)-1)]
            
            # Log the threshold type being applied
            pass
            
            # Update UI combo box if it exists
            if self.threshold_type_var:
                self.threshold_type_var.set(threshold_type)
            
            method = self.threshold_method_var.get() if self.threshold_method_var else "Simple"
            
            if method == "Simple":
                return processor.apply_advanced_threshold(
                    converted_image, threshold_value, max_value, threshold_type)
            elif method == "Otsu":
                return processor.apply_advanced_threshold(
                    converted_image, threshold_value, max_value, threshold_type, use_otsu=True)
            elif method == "Triangle":
                return processor.apply_advanced_threshold(
                    converted_image, threshold_value, max_value, threshold_type, use_triangle=True)
            elif method == "Adaptive":
                block_size = params.get("block_size", 11)
                c_constant = params.get("c_constant", 2)
                
                # Get adaptive method
                adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
                method_idx = params.get("adaptive_method_idx", 0)
                adaptive_method = adaptive_methods[min(method_idx, len(adaptive_methods)-1)]
                
                if self.adaptive_method_var:
                    self.adaptive_method_var.set(adaptive_method)
                
                return processor.apply_adaptive_threshold(
                    converted_image, max_value, adaptive_method, threshold_type, block_size, c_constant)
            else:
                return processor.apply_binary_threshold(converted_image, threshold_value, False)
        else:
            # Color space thresholding
            method = self.threshold_method_var.get() if self.threshold_method_var else "Range"
            
            # Get threshold type
            threshold_types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
            type_idx = params.get("threshold_type_idx", 0)
            threshold_type = threshold_types[min(type_idx, len(threshold_types)-1)]
            
            if self.threshold_type_var:
                self.threshold_type_var.set(threshold_type)
            
            if method == "Range":
                # Traditional range thresholding
                lower_bounds = []
                upper_bounds = []
                
                ranges = self.ranges.get(self.color_space, {})
                for channel in ranges.keys():
                    lower_bounds.append(params.get(f"{channel.lower()}_min", 0))
                    upper_bounds.append(params.get(f"{channel.lower()}_max", 255))

                return processor.apply_range_threshold(converted_image, lower_bounds, upper_bounds)
            else:
                # Advanced per-channel thresholding
                ranges = self.ranges.get(self.color_space, {})
                channel_params = []
                
                for channel in ranges.keys():
                    channel_lower = channel.lower()
                    channel_param = {
                        'threshold': params.get(f"{channel_lower}_threshold", 127),
                        'max_value': params.get(f"{channel_lower}_max_value", 255),
                        'threshold_type': threshold_type
                    }
                    
                    if method == "Adaptive":
                        adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
                        method_idx = params.get("adaptive_method_idx", 0)
                        adaptive_method = adaptive_methods[min(method_idx, len(adaptive_methods)-1)]
                        
                        if self.adaptive_method_var:
                            self.adaptive_method_var.set(adaptive_method)
                        
                        channel_param.update({
                            'adaptive_method': adaptive_method,
                            'block_size': params.get(f"{channel_lower}_block_size", 11),
                            'c_constant': params.get(f"{channel_lower}_c_constant", 2)
                        })
                    
                    channel_params.append(channel_param)
                
                thresholding_params = {
                    'method': method,
                    'threshold_type': threshold_type,
                    'channels': channel_params
                }
                
                return processor.apply_multi_channel_threshold(converted_image, thresholding_params)

    def create_trackbars(self) -> None:
        """
        Initialize trackbar definitions and create the initial trackbar set.
        
        Sets up trackbar configurations for both grayscale and color space
        thresholding, then creates the initial set of trackbars appropriate
        for the current color space and method.
        
        Side Effects:
            - Defines trackbar configurations for all methods
            - Creates initial trackbars for current color space
            - Sets up parameter change callbacks
        """
        if not self.threshold_viewer:
            return
            
        # Get the appropriate trackbars for the colorspace and initial method
        initial_method = "Simple" if self.color_space == "Grayscale" else "Range"
        trackbar_configs = self._get_trackbar_configs_for_method(initial_method)
        
        # Update the threshold viewer config with the new trackbars
        self.threshold_viewer.config.trackbar = trackbar_configs
        
        # Recreate the threshold viewer with proper trackbars
        self.threshold_viewer.cleanup_viewer()
        self.threshold_viewer.setup_viewer(image_processor_func=self._threshold_processor)
        
        # Update trackbar manager reference
        self.trackbar_manager = self.threshold_viewer.trackbar
        
        # Set current method
        self.current_method = initial_method
        
        # Trigger initial threshold update
        self.update_threshold()
    
    def _define_grayscale_trackbars(self) -> None:
        """
        Define trackbar configurations for all grayscale thresholding methods.
        
        Creates comprehensive trackbar definitions for grayscale image processing
        including simple binary thresholding, Otsu's method, triangle method,
        and adaptive thresholding with all their respective parameters.
        
        Side Effects:
            - Populates method_trackbars dictionary with grayscale configurations
            - Sets up parameter ranges and initial values
            - Configures callback functions for parameter updates
        """
        """Define trackbar configurations for grayscale thresholding methods."""
        # Common trackbars for Simple/Otsu/Triangle methods
        common_configs = [
            make_trackbar("Thresh", "threshold", 255, 127, custom_callback=lambda v: self.update_threshold(v)),
            make_trackbar("Max", "max_value", 255, 255, custom_callback=lambda v: self.update_threshold(v))
        ]
        
        # Adaptive method trackbars (no threshold type or adaptive method - controlled by UI)
        adaptive_configs = [
            make_trackbar("Size", "block_size", 99, 11, callback="odd", custom_callback=lambda v: self.update_threshold(v)),
            make_trackbar("C", "c_constant", 50, 2, custom_callback=lambda v: self.update_threshold(v)),
            make_trackbar("Max", "max_value", 255, 255, custom_callback=lambda v: self.update_threshold(v))
        ]
        
        # Organize trackbars by method
        self.method_trackbars["Simple"] = common_configs
        self.method_trackbars["Otsu"] = common_configs
        self.method_trackbars["Triangle"] = common_configs
        self.method_trackbars["Adaptive"] = adaptive_configs
    
    def _define_color_trackbars(self) -> None:
        """
        Define trackbar configurations for all color space thresholding methods.
        
        Creates comprehensive trackbar definitions for color image processing
        including range-based thresholding with min/max values for each
        channel in the current color space.
        
        Side Effects:
            - Populates method_trackbars dictionary with color configurations
            - Sets up channel-specific parameter ranges
            - Configures callback functions for parameter updates
        """
        """Define trackbar configurations for color space thresholding methods."""
        ranges = self.ranges.get(self.color_space, {})
        
        # Range thresholding trackbars (only min/max for each channel)
        range_configs = []
        for channel, (min_val, max_val) in ranges.items():
            range_configs.extend([
                make_trackbar(f"{channel} Min", f"{channel.lower()}_min", max_val, min_val, custom_callback=lambda v: self.update_threshold(v)),
                make_trackbar(f"{channel} Max", f"{channel.lower()}_max", max_val, max_val, custom_callback=lambda v: self.update_threshold(v))
            ])
        
        # Advanced thresholding trackbars (per channel parameters only - no threshold type)
        advanced_configs = []
        for channel in ranges.keys():
            channel_lower = channel.lower()
            advanced_configs.extend([
                make_trackbar(f"{channel} Thresh", f"{channel_lower}_threshold", 255, 127, custom_callback=lambda v: self.update_threshold(v)),
                make_trackbar(f"{channel} Max", f"{channel_lower}_max_value", 255, 255, custom_callback=lambda v: self.update_threshold(v))
            ])
        
        # Adaptive thresholding trackbars (adaptive parameters only - no threshold type or adaptive method)
        adaptive_configs = []
        for channel in ranges.keys():
            channel_lower = channel.lower()
            adaptive_configs.extend([
                make_trackbar(f"{channel} Max", f"{channel_lower}_max_value", 255, 255, custom_callback=lambda v: self.update_threshold(v)),
                make_trackbar(f"{channel} Block Size", f"{channel_lower}_block_size", 99, 11, callback="odd", custom_callback=lambda v: self.update_threshold(v)),
                make_trackbar(f"{channel} C Constant", f"{channel_lower}_c_constant", 50, 2, custom_callback=lambda v: self.update_threshold(v))
            ])
        
        # Organize trackbars by method
        self.method_trackbars["Range"] = range_configs
        self.method_trackbars["Simple"] = advanced_configs
        self.method_trackbars["Otsu"] = advanced_configs
        self.method_trackbars["Triangle"] = advanced_configs
        self.method_trackbars["Adaptive"] = adaptive_configs
    
    
    def _switch_to_method(self, new_method: str) -> None:
        """
        Switch trackbars to display only those relevant for the specified method.
        
        Updates the trackbar display to show parameters appropriate for the
        newly selected thresholding method, hiding irrelevant controls and
        showing method-specific parameters.
        
        Args:
            new_method: The name of the thresholding method to switch to.
        
        Side Effects:
            - Updates trackbar manager with new configurations
            - Updates current_method attribute
            - Refreshes trackbar display
            - Updates current_trackbars list
        """
        if new_method == self.current_method:
            return  # No change needed
            
        # Ensure the UI variable reflects the new method
        if self.threshold_method_var:
            self.threshold_method_var.set(new_method)
            
        # Get trackbar configs for the new method - recreate them to ensure fresh callbacks
        trackbar_configs = self._get_trackbar_configs_for_method(new_method)
        
        # Update the threshold viewer with new trackbars
        if self.threshold_viewer:
            # Clear existing trackbars by destroying and recreating viewer
            self.threshold_viewer.cleanup_viewer()
            
            # Update config with new trackbars
            self.threshold_viewer.config.trackbar = trackbar_configs
            
            # Recreate the viewer with new trackbars
            self.threshold_viewer.setup_viewer(image_processor_func=self._threshold_processor)
            self.trackbar_manager = self.threshold_viewer.trackbar
        
        # Update current method
        self.current_method = new_method
        
        # Update the UI to reflect the method change
        self._update_ui_for_method(new_method)
        
        # Force UI refresh to ensure radio button state is correct
        if self.root:
            self.root.update_idletasks()
        
        # Log the switch
        pass
        
    def _get_trackbar_configs_for_method(self, method: str) -> list:
        """
        Get fresh trackbar configurations for the specified method.
        
        Retrieves appropriate trackbar configurations for the given method,
        ensuring proper callback functions and parameter ranges are set.
        
        Args:
            method: The thresholding method name to get configurations for.
        
        Returns:
            list: List of trackbar configuration dictionaries.
        """
        """Get fresh trackbar configurations for the specified method with proper callbacks."""
        if self.color_space == "Grayscale":
            return self._get_grayscale_trackbars_for_method(method)
        else:
            return self._get_color_trackbars_for_method(method)
            
    def _get_grayscale_trackbars_for_method(self, method: str) -> list:
        """
        Get grayscale trackbar configurations for the specified method.
        
        Returns trackbar configurations appropriate for the specified grayscale
        thresholding method, including method-specific parameters and ranges.
        
        Args:
            method: The grayscale thresholding method name.
        
        Returns:
            list: List of trackbar configurations for the method.
        """
        """Get grayscale trackbar configurations for the specified method."""
        
        # Create safer callback functions that handle errors
        def safe_threshold_type_callback(v):
            try:
                return self._on_threshold_type_change(v)
            except Exception as e:
                print(f"Threshold type callback error: {e}")
                
        def safe_param_callback(v):
            try:
                return self._on_param_change(v)
            except Exception as e:
                print(f"Param callback error: {e}")
                
        def safe_adaptive_callback(v):
            try:
                return self._on_adaptive_method_change(v)
            except Exception as e:
                print(f"Adaptive callback error: {e}")
        
        if method == "Simple" or method == "Otsu" or method == "Triangle":
            return [
                make_trackbar("Thresh", "threshold", 255, 127, custom_callback=safe_param_callback),
                make_trackbar("Max", "max_value", 255, 255, custom_callback=safe_param_callback)
            ]
        elif method == "Adaptive":
            return [
                make_trackbar("Size", "block_size", 99, 11, callback="odd", custom_callback=safe_param_callback),
                make_trackbar("C", "c_constant", 50, 2, custom_callback=safe_param_callback),
                make_trackbar("Max", "max_value", 255, 255, custom_callback=safe_param_callback)
            ]
        else:
            return []
            
    def _get_color_trackbars_for_method(self, method: str) -> list:
        """
        Get color space trackbar configurations for the specified method.
        
        Returns trackbar configurations appropriate for the specified color
        thresholding method, including channel-specific parameters and ranges
        for the current color space.
        
        Args:
            method: The color thresholding method name.
        
        Returns:
            list: List of trackbar configurations for the method.
        """
        """Get color space trackbar configurations for the specified method."""
        ranges = self.ranges.get(self.color_space, {})
        
        # Create safer callback functions that handle errors
        def safe_threshold_type_callback(v):
            try:
                return self._on_threshold_type_change(v)
            except Exception as e:
                print(f"Color threshold type callback error: {e}")
                
        def safe_param_callback(v):
            try:
                return self._on_param_change(v)
            except Exception as e:
                print(f"Color param callback error: {e}")
                
        def safe_adaptive_callback(v):
            try:
                return self._on_adaptive_method_change(v)
            except Exception as e:
                print(f"Color adaptive callback error: {e}")
        
        if method == "Range":
            trackbars = []
            for channel, (min_val, max_val) in ranges.items():
                trackbars.extend([
                    make_trackbar(f"{channel} Min", f"{channel.lower()}_min", max_val, min_val, custom_callback=safe_param_callback),
                    make_trackbar(f"{channel} Max", f"{channel.lower()}_max", max_val, max_val, custom_callback=safe_param_callback)
                ])
            return trackbars
            
        elif method == "Simple" or method == "Otsu" or method == "Triangle":
            trackbars = []
            for channel in ranges.keys():
                channel_lower = channel.lower()
                trackbars.extend([
                    make_trackbar(f"{channel} Thresh", f"{channel_lower}_threshold", 255, 127, custom_callback=safe_param_callback),
                    make_trackbar(f"{channel} Max", f"{channel_lower}_max_value", 255, 255, custom_callback=safe_param_callback)
                ])
            return trackbars
            
        elif method == "Adaptive":
            trackbars = []
            for channel in ranges.keys():
                channel_lower = channel.lower()
                trackbars.extend([
                    make_trackbar(f"{channel} Max", f"{channel_lower}_max_value", 255, 255, custom_callback=safe_param_callback),
                    make_trackbar(f"{channel} Size", f"{channel_lower}_block_size", 99, 11, callback="odd", custom_callback=safe_param_callback),
                    make_trackbar(f"{channel} C", f"{channel_lower}_c_constant", 50, 2, custom_callback=safe_param_callback)
                ])
            return trackbars
            
        else:
            return []
    
    def _update_ui_for_method(self, method: str) -> None:
        """
        Update UI elements to reflect the selected thresholding method.
        
        Adjusts the user interface to show or hide controls appropriate for
        the selected method, including threshold type options and adaptive
        method selections.
        
        Args:
            method: The selected thresholding method name.
        
        Side Effects:
            - Shows/hides method-specific UI elements
            - Updates dropdown options
            - Adjusts control visibility
        """
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
    
    def _on_threshold_type_change(self, value: int) -> None:
        """
        Handle threshold type trackbar changes and update dropdown.
        
        Updates the threshold type dropdown to reflect changes made via
        the trackbar control, maintaining synchronization between different
        input methods.
        
        Args:
            value: The new threshold type value from trackbar.
        
        Side Effects:
            - Updates threshold type dropdown selection
            - Maintains UI consistency
        """
        """Handle threshold type trackbar changes."""
        try:
            threshold_types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
            if self.threshold_type_var and value < len(threshold_types):
                self.threshold_type_var.set(threshold_types[value])
            
            # Ensure the parameter is updated in the trackbar manager
            if self.threshold_viewer and self.threshold_viewer.trackbar:
                self.threshold_viewer.trackbar.parameters["threshold_type_idx"] = value
            
            # Force threshold update
            self.update_threshold()
            
            pass
            
        except Exception as e:
            print(f"Error in _on_threshold_type_change: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_adaptive_method_change(self, value: int) -> None:
        """
        Handle adaptive method trackbar changes and update dropdown.
        
        Updates the adaptive method dropdown to reflect changes made via
        the trackbar control for adaptive thresholding.
        
        Args:
            value: The new adaptive method value from trackbar.
        
        Side Effects:
            - Updates adaptive method dropdown selection
            - Maintains UI consistency
        """
        """Handle adaptive method trackbar changes."""
        try:
            adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
            if self.adaptive_method_var:
                self.adaptive_method_var.set(adaptive_methods[value])
            self._on_param_change(value)
        except Exception as e:
            print(f"Error in _on_adaptive_method_change: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_dropdown_threshold_type_change(self, event=None) -> None:
        """
        Handle threshold type dropdown changes and update trackbar.
        
        Updates the threshold type trackbar to reflect changes made via
        the dropdown selection, maintaining synchronization between
        different input methods.
        
        Args:
            event: The tkinter event that triggered the change (optional).
        
        Side Effects:
            - Updates threshold type trackbar value
            - Maintains UI consistency
            - Triggers threshold update
        """
        """Handle threshold type dropdown changes - update trackbar."""
        if not self.threshold_type_var or not self.threshold_viewer or not self.threshold_viewer.trackbar:
            return
            
        # Get selected threshold type from dropdown
        selected_type = self.threshold_type_var.get()
        threshold_types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
        
        # Find index of selected type
        try:
            type_index = threshold_types.index(selected_type)
        except ValueError:
            type_index = 0  # Default to BINARY if not found
        
        # No need to update trackbar since Thresh Type is now only in UI
        # Threshold type is controlled by UI combobox only
            
        # Update internal parameter
        self.threshold_viewer.trackbar.parameters["threshold_type_idx"] = type_index
        
        # Update thresholding
        self.update_threshold()
    
    def _on_dropdown_adaptive_method_change(self, event=None) -> None:
        """
        Handle adaptive method dropdown changes and update trackbar.
        
        Updates the adaptive method trackbar to reflect changes made via
        the dropdown selection for adaptive thresholding parameters.
        
        Args:
            event: The tkinter event that triggered the change (optional).
        
        Side Effects:
            - Updates adaptive method trackbar value
            - Maintains UI consistency
            - Triggers threshold update
        """
        """Handle adaptive method dropdown changes - update trackbar."""
        if not self.adaptive_method_var or not self.threshold_viewer or not self.threshold_viewer.trackbar:
            return
            
        # Get selected adaptive method from dropdown
        selected_method = self.adaptive_method_var.get()
        adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
        
        # Find index of selected method
        try:
            method_index = adaptive_methods.index(selected_method)
        except ValueError:
            method_index = 0  # Default to MEAN_C if not found
        
        # No need to update trackbar since Adaptive Method is now only in UI
        # Adaptive method is controlled by UI combobox only
            
        # Update internal parameter
        self.threshold_viewer.trackbar.parameters["adaptive_method_idx"] = method_index
        
        # Update thresholding
        self.update_threshold()
    
    def on_color_method_change(self) -> None:
        """
        Handle threshold method selection changes for color spaces.
        
        Updates the thresholding interface when the user selects a different
        method for color image processing. Currently handles range-based
        thresholding method changes.
        
        Side Effects:
            - Updates current method selection
            - Switches trackbars to match selected method
            - Updates UI to reflect method capabilities
        """
        """Handle threshold method selection changes for color spaces."""
        if not self.threshold_method_var:
            return
            
        method = self.threshold_method_var.get()
        
        # Switch trackbars for the selected method
        self._switch_to_method(method)
        self.update_threshold()
    
    def on_method_change(self) -> None:
        """
        Handle threshold method selection changes for the current interface.
        
        Updates the thresholding interface when the user selects a different
        thresholding method, ensuring appropriate controls and parameters
        are displayed for the selected method.
        
        Side Effects:
            - Updates method-specific UI elements
            - Switches trackbar configurations
            - Updates parameter controls
        """
        if not self.threshold_method_var:
            return
            
        method = self.threshold_method_var.get()
        
        # Switch trackbars for the selected method
        self._switch_to_method(method)
        self.update_threshold()

    def update_threshold(self, _=None) -> None:
        """
        Update the thresholding display by triggering the threshold viewer.
        
        Forces an update of the threshold preview by calling the viewer's
        update display method. This ensures the threshold visualization
        reflects current parameter settings. Core method for real-time updates.
        
        Args:
            _ (optional): Unused parameter for callback compatibility. Allows this
                         method to be used as trackbar callback.
        
        Returns:
            None: Updates display as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window.create_unified_window()
            >>> threshold_window.update_threshold()
            >>> # Threshold preview updated with current parameters
            >>> # Status display shows current settings
            
        Performance:
            Time Complexity: O(n) where n is number of image pixels for processing.
            Space Complexity: O(n) - Copy of image for threshold processing.
        """
        if not self.threshold_viewer or self.is_processing:
            return
            
        try:
            self.is_processing = True
            
            # Get current image from main viewer
            if self.viewer._internal_images:
                current_idx = self.viewer.trackbar.parameters.get('show', 0)
                if current_idx < len(self.viewer._internal_images):
                    source_image, title = self.viewer._internal_images[current_idx]
                    
                    # Apply thresholding using current parameters
                    params = dict(self.threshold_viewer.trackbar.parameters)
                    
                    # Log all parameters for debugging
                    pass
                    
                    thresholded_image = self._apply_thresholding(source_image, params)
                    
                    # Update the threshold viewer's internal images directly
                    self.threshold_viewer._internal_images = [(thresholded_image, f"Thresholded - {self.color_space}")]
                    
                    # Force multiple display refresh attempts
                    if (hasattr(self.threshold_viewer, 'windows') and 
                        self.threshold_viewer.windows.windows_created and 
                        self.threshold_viewer._should_continue_loop):
                        
                        # Force immediate display update
                        self.threshold_viewer._process_frame_and_check_quit()
                        
                        # Also try direct imshow
                        try:
                            import cv2
                            cv2.imshow(self.threshold_viewer.config.process_window_name, thresholded_image)
                            pass
                        except Exception as e:
                            print(f"Direct imshow failed: {e}")
            
            # Update status display
            self._update_status_display()
            
        except Exception as e:
            print(f"Error in update_threshold: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_processing = False

    def _update_status_display(self) -> None:
        """
        Update the status display with current thresholding parameters.
        
        Refreshes the status text area to show the current method, color space,
        and parameter values, providing users with feedback about the current
        configuration state and parameter settings.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates status display as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window.create_window()
            >>> threshold_window._update_status_display()
            >>> # Status shows: Method: Range, Type: BINARY, Color Space: HSV
            >>> # Adaptive method shows block size and C constant
            
        Performance:
            Time Complexity: O(1) - Fixed number of parameter retrievals and display updates.
            Space Complexity: O(1) - Fixed memory for status string construction.
        """
        if not hasattr(self, 'status_text') or not self.status_text or not self.threshold_viewer:
            return
        
        # Check if widget is still valid (not destroyed)
        try:
            if not self.status_text.winfo_exists():
                return
        except tk.TclError:
            # Widget has been destroyed
            return
            
        # Get current parameters from threshold viewer
        params = []
        method = self.threshold_method_var.get() if self.threshold_method_var else "Unknown"
        
        # Get parameters from threshold viewer's trackbar manager
        viewer_params = self.threshold_viewer.trackbar.parameters if self.threshold_viewer.trackbar else {}
        
        # Threshold type
        threshold_types = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
        type_idx = viewer_params.get("threshold_type_idx", 0)
        threshold_type = threshold_types[min(type_idx, len(threshold_types)-1)]
        
        params.append(f"Method: {method}")
        params.append(f"Type: {threshold_type}")
        
        if self.color_space == "Grayscale":
            if method == "Adaptive":
                adaptive_methods = ["MEAN_C", "GAUSSIAN_C"]
                method_idx = viewer_params.get("adaptive_method_idx", 0)
                adaptive_method = adaptive_methods[min(method_idx, len(adaptive_methods)-1)]
                block_size = viewer_params.get("block_size", 11)
                c_constant = viewer_params.get("c_constant", 2)
                params.append(f"Adaptive: {adaptive_method}")
                params.append(f"Block: {block_size}, C: {c_constant}")
            else:
                threshold = viewer_params.get("threshold", 127)
                max_val = viewer_params.get("max_value", 255)
                params.append(f"Thresh: {threshold}, Max: {max_val}")
        else:
            params.append(f"Color Space: {self.color_space}")
            if method != "Range":
                # Show first channel's parameters as example
                ranges = self.ranges.get(self.color_space, {})
                if ranges:
                    first_channel = list(ranges.keys())[0].lower()
                    thresh = viewer_params.get(f"{first_channel}_threshold", 127)
                    max_val = viewer_params.get(f"{first_channel}_max_value", 255)
                    params.append(f"{first_channel.upper()}: T={thresh}, M={max_val}")
        
        # Update status text with error handling
        try:
            status_str = "\n".join(params)
            self.status_text.config(state=tk.NORMAL)
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(1.0, status_str)
            self.status_text.config(state=tk.DISABLED)
        except tk.TclError:
            # Widget was destroyed while we were updating it
            pass

    def _save_config(self) -> None:
        """
        Save current thresholding configuration to a JSON file.
        
        Opens a file save dialog and saves the current thresholding parameters,
        method selection, and color space settings to a JSON configuration file
        for later restoration.
        
        Side Effects:
            - Opens file save dialog
            - Writes configuration to selected file
            - Shows success/error messages
        
        Raises:
            Exception: If file save operation fails.
        """
        """Save current thresholding configuration to file."""
        if not self.threshold_viewer or not self.threshold_viewer.trackbar:
            return
            
        try:
            config_data = {
                "color_space": self.color_space,
                "method": self.threshold_method_var.get() if self.threshold_method_var else "Unknown",
                "parameters": dict(self.threshold_viewer.trackbar.parameters)
            }
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title=f"Save {self.color_space} Thresholding Config"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(config_data, f, indent=2)
                pass
                
        except Exception as e:
            print(f"Error saving config: {e}")

    def _load_config(self) -> None:
        """
        Load thresholding configuration from a JSON file.
        
        Opens a file open dialog and loads previously saved thresholding
        parameters, restoring the method selection, color space, and
        parameter values from the selected JSON configuration file.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Loads configuration as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window.create_window()
            >>> threshold_window._load_config()
            >>> # File dialog opens, user selects config.json
            >>> # Parameters restored from file, UI updated
            
        Performance:
            Time Complexity: O(n) where n is number of parameters in config file.
            Space Complexity: O(n) - Configuration data loaded into memory.
        """
        if not self.threshold_viewer or not self.threshold_viewer.trackbar:
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
                        if param_name in self.threshold_viewer.trackbar.parameters:
                            # Update trackbar value in threshold viewer
                            try:
                                cv2.setTrackbarPos(param_name, self.threshold_viewer.config.trackbar_window_name, value)
                            except:
                                pass  # Trackbar might not exist
                            self.threshold_viewer.trackbar.parameters[param_name] = value
                
                # Update method if available
                if "method" in config_data and self.threshold_method_var:
                    self.threshold_method_var.set(config_data["method"])
                
                self.update_threshold()
                pass
                
        except Exception as e:
            print(f"Error loading config: {e}")

    def _show_presets(self) -> None:
        """
        Display preset configuration options in a popup window.
        
        Creates a popup window showing predefined thresholding presets
        appropriate for the current color space, allowing users to quickly
        apply common thresholding configurations for typical use cases.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates preset popup window as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window.create_window()
            >>> threshold_window._show_presets()
            >>> # Preset popup window opens with HSV-specific presets
            >>> # User can click on presets to apply them
            
        Performance:
            Time Complexity: O(n) where n is number of available presets.
            Space Complexity: O(1) - Fixed popup window with preset buttons.
        """
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

    def _get_presets(self) -> dict:
        """
        Get predefined preset configurations for the current color space.
        
        Returns a dictionary of predefined thresholding configurations
        optimized for common use cases in the current color space.
        
        Returns:
            dict: Dictionary of preset configurations with descriptive names
                 as keys and parameter dictionaries as values.
        """
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

    def _apply_preset(self, preset_data: dict, preset_window) -> None:
        """
        Apply a preset configuration to the current thresholding setup.
        
        Applies the specified preset parameters to the current thresholding
        interface, updating trackbars, method selection, and UI state to
        match the preset configuration.
        
        Args:
            preset_data: Dictionary containing preset parameter values.
            preset_window: The preset selection window to close after application.
        
        Side Effects:
            - Updates method selection and UI
            - Sets trackbar values to preset parameters
            - Closes preset selection window
            - Triggers threshold update
        """
        """Apply a preset configuration."""
        try:
            # Set method
            if "method" in preset_data and self.threshold_method_var:
                self.threshold_method_var.set(preset_data["method"])
                # Switch to the new method
                self._switch_to_method(preset_data["method"])
            
            # Set parameters
            if "parameters" in preset_data and self.threshold_viewer and self.threshold_viewer.trackbar:
                for param_name, value in preset_data["parameters"].items():
                    if param_name in self.threshold_viewer.trackbar.parameters:
                        # Update trackbar value in threshold viewer
                        try:
                            cv2.setTrackbarPos(param_name, self.threshold_viewer.config.trackbar_window_name, value)
                        except:
                            pass
                        self.threshold_viewer.trackbar.parameters[param_name] = value
            
            # Update thresholding
            self.update_threshold()
            preset_window.destroy()
            pass
            
        except Exception as e:
            print(f"Error applying preset: {e}")
    
    def set_close_callback(self, callback: callable) -> None:
        """
        Set a callback function to be called when the window is closed.
        
        Registers a callback function that will be invoked during window
        cleanup, allowing parent components to perform necessary cleanup
        operations and resource management.
        
        Args:
            callback (callable): Function to invoke on window close. Should take
                               no arguments and handle cleanup operations.
        
        Returns:
            None: Stores callback reference as side effect, no return value.
        
        Examples:
            >>> def cleanup_handler():
            ...     print("Thresholding window closed")
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window.set_close_callback(cleanup_handler)
            >>> # Callback will be called when window is destroyed
            
        Performance:
            Time Complexity: O(1) - Simple callback storage.
            Space Complexity: O(1) - Single callback reference stored.
        """
        self.close_callback = callback
    
    def destroy_window(self) -> None:
        """
        Clean up and destroy the thresholding window and associated resources.
        
        Performs comprehensive cleanup of the thresholding window including
        destroying the tkinter window, cleaning up the threshold viewer,
        and invoking any registered close callbacks for proper resource management.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Performs cleanup as side effect, no return value.
        
        Examples:
            >>> threshold_window = ThresholdingWindow(viewer, "HSV")
            >>> threshold_window.create_window()
            >>> threshold_window.destroy_window()
            >>> # Window destroyed, resources cleaned up, callbacks invoked
            >>> print(threshold_window.window_created)  # False
            
        Performance:
            Time Complexity: O(1) - Fixed cleanup operations.
            Space Complexity: O(1) - No additional memory allocation during cleanup.
        """
        # Call close callback before destroying
        if self.close_callback:
            try:
                self.close_callback()
            except Exception as e:
                if hasattr(self, 'viewer'):
                    print(f"Error in close callback: {e}")
        
        # Clean up the dedicated threshold viewer
        if self.threshold_viewer:
            try:
                self.threshold_viewer.cleanup_viewer()
                self.threshold_viewer = None
            except Exception as e:
                if hasattr(self, 'viewer'):
                    print(f"Error cleaning up threshold viewer: {e}")
        
        # Only destroy tkinter root if it exists (for full UI mode)
        if self.window_created and hasattr(self, 'root') and self.root:
            try:
                self.root.destroy()
            except:
                pass
            self.root = None
            
        self.window_created = False
