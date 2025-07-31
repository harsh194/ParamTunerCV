"""
Analysis control window module for the Parameter image viewer application.

This module provides a comprehensive GUI interface for controlling image analysis
operations in the Parameter project. It includes functionality for ROI selection,
analysis tools (histograms, profiles, thresholding), drawing management, and
data export capabilities.

Main Classes:
    - Tooltip: Provides tooltip functionality for GUI widgets
    - AnalysisControlWindow: Main control window for analysis operations

The module integrates with various analysis components including thresholding
managers, theme managers, and export dialogs to provide a unified interface
for image analysis workflows.

Dependencies:
    - tkinter: GUI framework for the control window
    - ThresholdingManager: Handles image thresholding operations
    - ThemeManager: Manages visual themes and styling
    - EnhancedExportDialog: Advanced export functionality (optional)

Usage:
    control_window = AnalysisControlWindow(viewer)
    control_window.create_window()
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
from .thresholding_manager import ThresholdingManager
from .theme_manager import ThemeManager
from .enhanced_widgets import ComboboxWithIndicator
try:
    from .enhanced_export_dialog import EnhancedExportDialog
    ENHANCED_EXPORT_AVAILABLE = True
except ImportError as e:
    ENHANCED_EXPORT_AVAILABLE = False
    print(f"❌ Failed to import EnhancedExportDialog: {e}")
    
    # Create a fallback simple export dialog
    class SimpleExportDialog:
        def __init__(self, parent, theme_manager):
            self.parent = parent
            
        def show(self, filename_prefix="", on_export=None, on_cancel=None):
            # Simple fallback - just call the export with default values
            if on_export:
                on_export("histogram", "json", f"{filename_prefix}_export.json")
    
    EnhancedExportDialog = SimpleExportDialog

TKINTER_AVAILABLE = True
try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    TKINTER_AVAILABLE = False

class Tooltip:
    """
    Create a tooltip widget that displays helpful text when hovering over GUI elements.
    
    This class provides a simple tooltip mechanism for tkinter widgets, showing
    informative text when the user hovers their mouse over the associated widget.
    The tooltip appears as a small popup window with a light yellow background.
    
    Attributes:
        widget: The tkinter widget this tooltip is attached to.
        text (str): The text content displayed in the tooltip.
        tooltip_window: The popup window displaying the tooltip (None when hidden).
    
    Examples:
        >>> button = ttk.Button(root, text="Click me")
        >>> tooltip = Tooltip(button, "This button performs an action")
        # Tooltip will appear when hovering over the button
    """
    def __init__(self, widget, text: str) -> None:
        """
        Initialize a tooltip for the specified widget.
        
        Creates a tooltip instance that will display helpful text when the user
        hovers over the associated widget. Sets up event bindings for mouse
        enter and leave events to control tooltip visibility.
        
        Args:
            widget: The tkinter widget to attach the tooltip to. Must be a valid
                   tkinter widget with bind() and winfo_* methods.
            text: The text content to display in the tooltip. Should be concise
                 and informative about the widget's functionality.
        
        Returns:
            None: This is a constructor method.
            
        Examples:
            >>> import tkinter as tk
            >>> from tkinter import ttk
            >>> root = tk.Tk()
            >>> button = ttk.Button(root, text="Click me")
            >>> tooltip = Tooltip(button, "This button performs an action")
            >>> # Tooltip will appear when hovering over the button
            
        Performance:
            Time Complexity: O(1) - Simple attribute assignment and event binding.
            Space Complexity: O(1) - Fixed memory allocation for instance variables.
        """
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event) -> None:
        """
        Display the tooltip popup window at the cursor location.
        
        Creates and shows a popup window containing the tooltip text,
        positioned slightly offset from the widget's location. The tooltip
        appears as a small window with light yellow background and black text.
        
        Args:
            event: The tkinter event that triggered the tooltip display.
                  Contains information about the mouse enter event.
        
        Returns:
            None: This method displays the tooltip but returns nothing.
            
        Examples:
            >>> # This method is typically called automatically by tkinter
            >>> # when mouse enters the widget, but can be called manually:
            >>> tooltip = Tooltip(widget, "Help text")
            >>> event = type('Event', (), {})()  # Mock event
            >>> tooltip.show_tooltip(event)
            
        Performance:
            Time Complexity: O(1) - Widget creation and positioning operations.
            Space Complexity: O(1) - Single tooltip window creation.
        """
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event) -> None:
        """
        Hide and destroy the tooltip popup window.
        
        Removes the tooltip popup from the screen and cleans up resources.
        Safely handles cases where no tooltip is currently displayed.
        
        Args:
            event: The tkinter event that triggered the tooltip hiding.
                  Contains information about the mouse leave event.
        
        Returns:
            None: This method hides the tooltip but returns nothing.
            
        Examples:
            >>> # This method is typically called automatically by tkinter
            >>> # when mouse leaves the widget, but can be called manually:
            >>> tooltip = Tooltip(widget, "Help text")
            >>> event = type('Event', (), {})()  # Mock event
            >>> tooltip.hide_tooltip(event)
            
        Performance:
            Time Complexity: O(1) - Single window destruction operation.
            Space Complexity: O(1) - Memory cleanup for tooltip window.
        """
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

class AnalysisControlWindow:
    """
    Professional tkinter-based analysis control window for the Parameter image viewer.
    
    This class provides a comprehensive GUI interface for controlling image analysis
    operations including ROI selection, drawing tools, analysis functions, and data
    export capabilities. The window features a scrollable interface with organized
    sections for different types of operations.
    
    The control window integrates with the ImageViewer to provide real-time control
    over analysis parameters and visualization options. It supports various drawing
    modes (rectangle, line, polygon), analysis tools (histogram, profiles, thresholding),
    and export functionality for analysis results.
    
    Attributes:
        viewer: Reference to the main ImageViewer instance.
        window_created (bool): Flag indicating if the GUI window has been created.
        roi_selection (int): Index of the currently selected ROI (0 for full image).
        line_selection (int): Index of the currently selected line (0 for all lines).
        polygon_selection (int): Index of the currently selected polygon (0 for all polygons).
        root: The main tkinter window instance.
        theme_manager: Manages visual themes and styling for the interface.
        thresholding_manager: Handles image thresholding operations.
        active_buttons (dict): Tracks the state of mode toggle buttons.
        active_states (dict): Tracks which buttons are currently active in each section.
    
    Examples:
        >>> from src.core.image_viewer import ImageViewer
        >>> viewer = ImageViewer(config, trackbar_definitions)
        >>> control_window = AnalysisControlWindow(viewer)
        >>> control_window.create_window()
        # Creates and displays the analysis control interface
    """
    
    def __init__(self, viewer: 'ImageViewer') -> None:
        """
        Initialize the analysis control window with the specified image viewer.
        
        Sets up the control window's initial state, theme management, and button
        tracking dictionaries. The window is not created until create_window() is called.
        
        Args:
            viewer: The ImageViewer instance this control window will manage.
                   Must have mouse, config, and display update capabilities.
        
        Returns:
            None: This is a constructor method.
            
        Examples:
            >>> from src.core.image_viewer import ImageViewer
            >>> from src.config.viewer_config import ViewerConfig
            >>> config = ViewerConfig()
            >>> viewer = ImageViewer(config, [])
            >>> control_window = AnalysisControlWindow(viewer)
            >>> print(control_window.window_created)  # False
            
        Performance:
            Time Complexity: O(1) - Simple object initialization.
            Space Complexity: O(1) - Fixed memory allocation for state variables.
        """
        self.viewer = viewer
        self.window_created = False
        self.roi_selection = 0
        self.line_selection = 0
        self.polygon_selection = 0
        self.root = None
        self.theme_manager = ThemeManager(use_dark_mode=True)
        self.thresholding_manager = ThresholdingManager(viewer)
        
        self.active_buttons = {
            'line_mode': False,
            'polygon_mode': False,
            'thresholding': False
        }
        self.quick_access_buttons = {}
        self.action_buttons = {}  # Store references to action buttons for feedback
        
        # Track active states for persistent green highlighting
        self.active_states = {
            'analysis': None,  # Currently active analysis button
            'drawing_management': None,  # Currently active drawing management button
            'export_plots': None  # Currently active export/plots button
        }
        
    def create_window(self) -> None:
        """
        Create and display the analysis control window with enhanced UI.
        
        Builds the complete GUI interface including scrollable content, themed sections,
        and interactive controls. The window includes drawing tools, selection controls,
        analysis functions, and export capabilities. Only creates the window if debug
        mode is enabled and tkinter is available.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates window as side effect, no return value.
            
        Examples:
            >>> control_window = AnalysisControlWindow(viewer)
            >>> control_window.create_window()
            >>> print(control_window.window_created)  # True if successful
            >>> # Window with scrollable sections now displayed
            
        Performance:
            Time Complexity: O(n) where n is the number of UI elements created.
            Space Complexity: O(n) for storing references to all UI components.
            
        Raises:
            Exception: If window creation fails due to missing dependencies
                      or system limitations.
        """
        if self.window_created or not self.viewer.config.enable_debug or not TKINTER_AVAILABLE:
            return

        try:
            if not hasattr(tk, '_default_root') or tk._default_root is None:
                root = tk.Tk()
                root.withdraw()

            self.root = tk.Toplevel()
            self.root.title("Analysis Controls")
            self.root.geometry("420x650")
            self.root.minsize(380, 550)
            
            # Ensure window stays visible and maintains its title
            self.root.wm_attributes("-topmost", False)  # Don't force always on top
            self.root.resizable(True, True)  # Allow resizing but with constraints

            self.theme_manager.configure_theme(self.root)
            
            # Create a container frame
            container = ttk.Frame(self.root)
            container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
            
            # Create canvas with scrollbar - store as instance attributes
            self.canvas = tk.Canvas(container, highlightthickness=0, bd=0)
            self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
            
            # Create a main frame inside the canvas - store as instance attribute
            self.main_frame = ttk.Frame(self.canvas, style=self.theme_manager.get_frame_style())
            
            # Configure the canvas
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            # Position at origin to fill width
            self.canvas_frame = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
            
            # Pack the canvas and scrollbar
            self.canvas.pack(side="left", fill="both", expand=True)
            self.scrollbar.pack(side="right", fill="y")
            
            # Ensure scrollbar is visible
            self.scrollbar.lift()
            
            # Bind events for proper scrolling behavior
            self.main_frame.bind("<Configure>", self._on_frame_configure)
            self.canvas.bind("<Configure>", self._on_canvas_configure)
            
            # Add mouse wheel scrolling support
            self._bind_mousewheel()
            
            # No padding frame needed - content fills full width

            self._create_quick_access_section(self.main_frame)
            self._create_selection_section(self.main_frame)
            self._create_analysis_section(self.main_frame)
            self._create_drawing_section(self.main_frame)
            self._create_export_section(self.main_frame)
            
            # Add minimal bottom padding to prevent text cutoff
            bottom_padding = ttk.Frame(self.main_frame, style=self.theme_manager.get_frame_style())
            bottom_padding.pack(fill='x', pady=(5, 15), padx=0)

            self.update_selectors()
            self._update_quick_access_buttons()
            self.window_created = True
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            # Make window focus and bring to front
            self.root.lift()
            self.root.focus_force()

        except Exception as e:
            print(f"Failed to create analysis control window: {e}")
            self.window_created = False

    def _on_frame_configure(self, event) -> None:
        """
        Update scroll region when the main frame size changes.
        
        Recalculates the scrollable area based on the actual content size
        to ensure proper scrolling behavior when content is added or removed.
        
        Args:
            event: The tkinter configure event containing size information.
                  Includes width, height, and widget reference data.
        
        Returns:
            None: Updates scroll region as side effect, no return value.
            
        Examples:
            >>> # This method is called automatically by tkinter when frame resizes
            >>> # Manual call example:
            >>> event = type('Event', (), {'width': 400, 'height': 600})()
            >>> control_window._on_frame_configure(event)
            >>> # Scroll region updated to match content size
            
        Performance:
            Time Complexity: O(1) - Single bbox calculation and configure call.
            Space Complexity: O(1) - No additional memory allocation.
        """
        try:
            # Get the actual bounding box of all content
            bbox = self.canvas.bbox("all")
            if bbox:
                x1, y1, x2, y2 = bbox
                # Use actual content size for scroll region
                content_width = x2 - x1
                content_height = y2 - y1
                
                # Set scroll region to actual content size (this enables proper scrolling)
                self.canvas.configure(scrollregion=(0, 0, content_width, content_height))
            else:
                # If no content bounding box, use minimal scroll region
                self.canvas.configure(scrollregion=(0, 0, 1, 1))
        except Exception as e:
            if self.viewer:
                print(f"Error updating scroll region: {e}")
    
    def _on_canvas_configure(self, event) -> None:
        """
        Update the scrollable frame width when the canvas is resized.
        
        Ensures the scrollable content frame matches the canvas width to
        prevent horizontal scrollbars and maintain proper layout.
        
        Args:
            event: The tkinter configure event containing the new canvas dimensions.
                  Includes width, height, and other canvas properties.
        
        Returns:
            None: Updates canvas frame width as side effect, no return value.
            
        Examples:
            >>> # This method is called automatically by tkinter when canvas resizes
            >>> # Manual call example:
            >>> event = type('Event', (), {'width': 350})()
            >>> control_window._on_canvas_configure(event)
            >>> # Canvas frame width now matches canvas width
            
        Performance:
            Time Complexity: O(1) - Single itemconfig operation.
            Space Complexity: O(1) - No additional memory allocation.
        """
        try:
            # Update the width of the scrollable frame to match the canvas width
            canvas_width = event.width
            if canvas_width > 0 and hasattr(self, 'canvas_frame') and self.canvas_frame:
                self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
        except Exception as e:
            if self.viewer:
                print(f"Error configuring canvas: {e}")
    
    def _bind_mousewheel(self) -> None:
        """
        Bind mouse wheel scrolling to the canvas for intuitive navigation.
        
        Sets up mouse wheel event handlers that are active when the mouse
        is over the control window, providing smooth scrolling through the
        interface content.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Sets up event bindings as side effect, no return value.
            
        Examples:
            >>> control_window = AnalysisControlWindow(viewer)
            >>> control_window._bind_mousewheel()
            >>> # Mouse wheel scrolling now works when over the window
            
        Performance:
            Time Complexity: O(1) - Simple event binding operations.
            Space Complexity: O(1) - Function closure creation for event handlers.
        """
        def _on_mousewheel(event):
            try:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        # Bind mouse wheel events when entering/leaving the window
        self.root.bind('<Enter>', _bind_to_mousewheel)
        self.root.bind('<Leave>', _unbind_from_mousewheel)
        
        # Also bind to canvas for better UX
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)

    def _create_section_frame(self, parent, title: str):
        """
        Create a themed section frame with header and separator.
        
        Builds a standardized section container with consistent styling,
        including a header label and horizontal separator line.
        
        Args:
            parent: The parent tkinter widget to contain this section.
                   Must be a valid tkinter container widget.
            title: The display title for the section header.
                  Should be descriptive of the section's purpose.
            
        Returns:
            ttk.Frame: The inner frame ready for content widgets.
                      Configured with appropriate styling and layout.
            
        Examples:
            >>> frame = control_window._create_section_frame(main_frame, "Analysis")
            >>> button = ttk.Button(frame, text="Test Button")
            >>> button.pack()
            >>> # Section with header "Analysis" and separator created
            
        Performance:
            Time Complexity: O(1) - Fixed number of widget creation operations.
            Space Complexity: O(1) - Creates fixed number of frame and label widgets.
        """
        section_frame = ttk.Frame(parent, style=self.theme_manager.get_frame_style())
        section_frame.pack(fill='x', pady=(5, 10), padx=2)
        
        inner_frame = ttk.Frame(section_frame, style=self.theme_manager.get_frame_style())
        inner_frame.pack(fill='x', padx=5, pady=12)
        
        header = ttk.Label(inner_frame, text=title, style="Header.TLabel")
        header.pack(fill='x', pady=(0, 8), padx=2)
        
        separator = ttk.Separator(inner_frame, orient='horizontal')
        separator.pack(fill='x', pady=(0, 12), padx=2)
        
        return inner_frame

    def _create_selection_section(self, parent_frame) -> None:
        """
        Create the selection section with ROI, line, and polygon selectors.
        
        Builds dropdown selectors that allow users to choose specific regions
        of interest, lines, or polygons for analysis operations. Each selector
        includes tooltip help and updates the viewer's selection state.
        
        Args:
            parent_frame: The parent frame to contain the selection controls.
                         Must be a valid tkinter container widget.
        
        Returns:
            None: Creates selection UI as side effect, no return value.
            
        Examples:
            >>> control_window._create_selection_section(main_frame)
            >>> # Creates ROI, Line, and Polygon dropdown selectors
            >>> # Each with appropriate tooltips and event bindings
            
        Performance:
            Time Complexity: O(1) - Fixed number of widget creation operations.
            Space Complexity: O(1) - Creates fixed number of selector widgets.
        """
        selection_frame = self._create_section_frame(parent_frame, "Selection")

        # ROI Selection
        roi_frame = ttk.Frame(selection_frame, style=self.theme_manager.get_frame_style())
        roi_frame.pack(fill='x', pady=3, padx=8)
        roi_frame.columnconfigure(1, weight=1)
        
        roi_label = ttk.Label(roi_frame, text="ROI:", width=10, anchor='w')
        roi_label.grid(row=0, column=0, sticky='w', padx=(5, 12))
        Tooltip(roi_label, "Select a region of interest for analysis")
        
        self.roi_var = tk.StringVar(value="Full Image")
        self.roi_combo = ComboboxWithIndicator(
            roi_frame, 
            theme_manager=self.theme_manager,
            textvariable=self.roi_var, 
            state="readonly",
            max_dropdown_items=10
        )
        self.roi_combo.grid(row=0, column=1, sticky='ew')
        self.roi_combo.bind('<<ComboboxSelected>>', self._on_roi_select)
        Tooltip(self.roi_combo, "Choose a specific region of interest or use the full image")

        # Line Selection
        line_frame = ttk.Frame(selection_frame, style=self.theme_manager.get_frame_style())
        line_frame.pack(fill='x', pady=3, padx=8)
        line_frame.columnconfigure(1, weight=1)
        
        line_label = ttk.Label(line_frame, text="Line:", width=10, anchor='w')
        line_label.grid(row=0, column=0, sticky='w', padx=(5, 12))
        Tooltip(line_label, "Select a line for pixel profile analysis")
        
        self.line_var = tk.StringVar(value="All Lines")
        self.line_combo = ComboboxWithIndicator(
            line_frame, 
            theme_manager=self.theme_manager,
            textvariable=self.line_var, 
            state="readonly",
            max_dropdown_items=10
        )
        self.line_combo.grid(row=0, column=1, sticky='ew')
        self.line_combo.bind('<<ComboboxSelected>>', self._on_line_select)
        Tooltip(self.line_combo, "Choose a specific line or analyze all lines")

        # Polygon Selection
        poly_frame = ttk.Frame(selection_frame, style=self.theme_manager.get_frame_style())
        poly_frame.pack(fill='x', pady=3, padx=8)
        poly_frame.columnconfigure(1, weight=1)
        
        poly_label = ttk.Label(poly_frame, text="Polygon:", width=10, anchor='w')
        poly_label.grid(row=0, column=0, sticky='w', padx=(5, 12))
        Tooltip(poly_label, "Select a polygon for area analysis")
        
        self.polygon_var = tk.StringVar(value="All Polygons")
        self.polygon_combo = ComboboxWithIndicator(
            poly_frame, 
            theme_manager=self.theme_manager,
            textvariable=self.polygon_var, 
            state="readonly",
            max_dropdown_items=10
        )
        self.polygon_combo.grid(row=0, column=1, sticky='ew')
        self.polygon_combo.bind('<<ComboboxSelected>>', self._on_polygon_select)
        Tooltip(self.polygon_combo, "Choose a specific polygon or analyze all polygons")

    def _create_analysis_section(self, parent_frame) -> None:
        """
        Create the analysis section with histogram, profile, and thresholding tools.
        
        Builds buttons for core analysis operations including histogram display,
        pixel profile plotting, and thresholding window access. Buttons provide
        visual feedback and keyboard shortcut integration.
        
        Args:
            parent_frame: The parent frame to contain the analysis controls.
                         Must be a valid tkinter container widget.
        
        Returns:
            None: Creates analysis UI as side effect, no return value.
            
        Examples:
            >>> control_window._create_analysis_section(main_frame)
            >>> # Creates histogram, profiles, and thresholding buttons
            >>> # Each with tooltips showing keyboard shortcuts
            
        Performance:
            Time Complexity: O(1) - Fixed number of button creation operations.
            Space Complexity: O(1) - Creates fixed number of button widgets.
        """
        analysis_frame = self._create_section_frame(parent_frame, "Analysis")
        
        btn_style = self.theme_manager.get_button_style("primary")
        
        # Create a grid layout for better organization
        analysis_grid = ttk.Frame(analysis_frame, style=self.theme_manager.get_frame_style())
        analysis_grid.pack(fill='x', pady=5)
        analysis_grid.columnconfigure(0, weight=1, minsize=100)
        analysis_grid.columnconfigure(1, weight=1, minsize=100)
        
        hist_btn = ttk.Button(analysis_grid, text="📊 Show Histogram", command=self._show_histogram, style=btn_style)
        hist_btn.grid(row=0, column=0, padx=3, pady=3, sticky="ew")
        Tooltip(hist_btn, "Display histogram of the selected ROI or polygon (H key)")
        self.action_buttons['histogram'] = hist_btn

        prof_btn = ttk.Button(analysis_grid, text="📈 Show Profiles", command=self._show_profiles, style=btn_style)
        prof_btn.grid(row=0, column=1, padx=3, pady=3, sticky="ew")
        Tooltip(prof_btn, "Display pixel profiles of the selected lines (Shift+P)")
        self.action_buttons['profiles'] = prof_btn

        thresh_btn = ttk.Button(analysis_frame, text="🌡️ Thresholding", command=self._open_thresholding_window, style=btn_style)
        thresh_btn.pack(fill='x', pady=2)
        Tooltip(thresh_btn, "Open the thresholding window for image segmentation")
        self.action_buttons['thresholding'] = thresh_btn
        

    def _create_drawing_section(self, parent_frame) -> None:
        """
        Create the drawing management section with edit and clear tools.
        
        Builds controls for managing drawn objects including undo functionality
        and various clear operations. Clear tools use warning styling to indicate
        their destructive nature.
        
        Args:
            parent_frame: The parent frame to contain the drawing management controls.
                         Must be a valid tkinter container widget.
        
        Returns:
            None: Creates drawing management UI as side effect, no return value.
            
        Examples:
            >>> control_window._create_drawing_section(main_frame)
            >>> # Creates undo button and clear buttons (rect, line, polygon, all)
            >>> # Each with appropriate tooltips and warning styling
            
        Performance:
            Time Complexity: O(1) - Fixed number of button creation operations.
            Space Complexity: O(1) - Creates fixed number of button widgets.
        """
        drawing_frame = self._create_section_frame(parent_frame, "Drawing Management")

        btn_style = self.theme_manager.get_button_style()
        warning_style = self.theme_manager.get_button_style()  # Use default for destructive actions
        
        # Edit tools
        edit_label = ttk.Label(drawing_frame, text="Edit Tools:", font=('TkDefaultFont', 9, 'bold'))
        edit_label.pack(anchor='w', pady=(0, 5))
        
        undo_btn = ttk.Button(drawing_frame, text="↶ Undo Last Point", command=self._undo_last_point, style=btn_style)
        undo_btn.pack(fill='x', pady=2)
        Tooltip(undo_btn, "Undo the last point of the current polygon (Ctrl+Z)")
        self.action_buttons['undo'] = undo_btn
        
        # Clear tools with warning styling
        clear_label = ttk.Label(drawing_frame, text="Clear Tools:", font=('TkDefaultFont', 9, 'bold'))
        clear_label.pack(anchor='w', pady=(10, 5))

        # Create a grid for clear buttons
        clear_grid = ttk.Frame(drawing_frame, style=self.theme_manager.get_frame_style())
        clear_grid.pack(fill='x', pady=2)
        clear_grid.columnconfigure(0, weight=1, minsize=100)
        clear_grid.columnconfigure(1, weight=1, minsize=100)

        clear_rect_btn = ttk.Button(clear_grid, text="🗑️ Clear Last Rectangle", command=self._clear_last_rectangle, style=warning_style)
        clear_rect_btn.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        Tooltip(clear_rect_btn, "Clear the last drawn rectangle/ROI")
        self.action_buttons['clear_rect'] = clear_rect_btn

        clear_line_btn = ttk.Button(clear_grid, text="🗑️ Clear Last Line", command=self._clear_last_line, style=warning_style)
        clear_line_btn.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        Tooltip(clear_line_btn, "Clear the last drawn line")
        self.action_buttons['clear_line'] = clear_line_btn

        clear_last_btn = ttk.Button(clear_grid, text="🗑️ Clear Last Polygon", command=self._clear_last_polygon, style=warning_style)
        clear_last_btn.grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        Tooltip(clear_last_btn, "Clear the last drawn polygon (Delete key)")
        self.action_buttons['clear_polygon'] = clear_last_btn

        clear_all_btn = ttk.Button(clear_grid, text="🗑️ Clear All Objects", command=self._clear_all, style=warning_style)
        clear_all_btn.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        Tooltip(clear_all_btn, "Clear all ROIs, lines, and polygons (Ctrl+Delete)")
        self.action_buttons['clear_all'] = clear_all_btn

    def _create_export_section(self, parent_frame) -> None:
        """
        Create the export and plot management section.
        
        Builds controls for exporting analysis data to various formats and
        managing matplotlib plot windows. Includes both data export and
        plot cleanup functionality.
        
        Args:
            parent_frame: The parent frame to contain the export controls.
                         Must be a valid tkinter container widget.
        
        Returns:
            None: Creates export UI as side effect, no return value.
            
        Examples:
            >>> control_window._create_export_section(main_frame)
            >>> # Creates export data button and close plots button
            >>> # Export button opens enhanced export dialog
            
        Performance:
            Time Complexity: O(1) - Fixed number of button creation operations.
            Space Complexity: O(1) - Creates fixed number of export widgets.
        """
        export_frame = self._create_section_frame(parent_frame, "Export & Plots")
        
        btn_style = self.theme_manager.get_button_style()
        
        # Export tools
        export_label = ttk.Label(export_frame, text="Export Data:", font=('TkDefaultFont', 9, 'bold'))
        export_label.pack(anchor='w', pady=(0, 5))
        
        export_data_btn = tk.Button(
            export_frame,
            text="📊 Export Analysis Data", 
            command=self._export_analysis_data,
            width=20,
            height=1,
            relief="raised",
            bd=2,
            font=('TkDefaultFont', 10, 'bold'),
            bg='#007bff',
            fg='white',
            activebackground='#0056b3',
            activeforeground='white'
        )
        export_data_btn.pack(fill='x', pady=3)
        Tooltip(export_data_btn, "Export histogram, profile, or polygon data to CSV/JSON/PNG (Ctrl+E)")
        self.action_buttons['export_data'] = export_data_btn
        
        # Plot management
        plots_label = ttk.Label(export_frame, text="Plot Management:", font=('TkDefaultFont', 9, 'bold'))
        plots_label.pack(anchor='w', pady=(10, 5))

        close_plots_btn = ttk.Button(export_frame, text="❌ Close All Plots", command=self._close_plots, style=btn_style)
        close_plots_btn.pack(fill='x', pady=3)
        Tooltip(close_plots_btn, "Close all open matplotlib windows (Ctrl+W)")
        self.action_buttons['close_plots'] = close_plots_btn
    
    def update_selectors(self) -> None:
        """
        Update the dropdown selectors with current ROI, line, and polygon options.
        
        Refreshes all selection dropdowns to reflect the current state of drawn
        objects in the viewer. Handles boundary conditions and maintains selection
        consistency when objects are added or removed.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates GUI selectors as side effect, no return value.
            
        Examples:
            >>> # Add a new ROI to the viewer
            >>> viewer.mouse.draw_rects.append((10, 10, 50, 50))
            >>> control_window.update_selectors()
            >>> # ROI dropdown now shows "Full Image", "ROI 1"
            
        Performance:
            Time Complexity: O(n) where n is total number of drawn objects.
            Space Complexity: O(n) for creating option lists for dropdowns.
        """
        if not self.window_created: return
        try:
            # Update ROI selector
            try:
                roi_options = ["Full Image"] + [f"ROI {i+1}" for i in range(len(self.viewer.mouse.draw_rects))]
                self.roi_combo['values'] = roi_options  # Use direct assignment instead of set_values
                if self.roi_selection >= len(roi_options): self.roi_selection = 0
                self.roi_var.set(roi_options[self.roi_selection])
            except Exception as e:
                print(f"Error updating ROI selector: {e}")
            
            # Update Line selector
            try:
                line_options = ["All Lines"] + [f"Line {i+1}" for i in range(len(self.viewer.mouse.draw_lines))]
                self.line_combo['values'] = line_options  # Use direct assignment instead of set_values
                if self.line_selection >= len(line_options): self.line_selection = 0
                self.line_var.set(line_options[self.line_selection])
            except Exception as e:
                print(f"Error updating Line selector: {e}")

            # Update Polygon selector
            try:
                poly_options = ["All Polygons"] + [f"Polygon {i+1}" for i in range(len(self.viewer.mouse.draw_polygons))]
                self.polygon_combo['values'] = poly_options  # Use direct assignment instead of set_values
                if self.polygon_selection >= len(poly_options): self.polygon_selection = 0
                self.polygon_var.set(poly_options[self.polygon_selection])
            except Exception as e:
                print(f"Error updating Polygon selector: {e}")
                
        except Exception as e:
            print(f"Error updating selectors: {e}")
            pass
    
    def _on_roi_select(self, event) -> None:
        """
        Handle ROI selection changes from the dropdown.
        
        Updates the viewer's selected ROI based on user selection and triggers
        display updates to highlight the chosen region. Validates the selection
        and maintains consistency between the GUI and viewer state.
        
        Args:
            event: The tkinter selection event from the ROI dropdown.
                  Contains information about the ComboboxSelected event.
        
        Returns:
            None: Updates viewer state as side effect, no return value.
            
        Examples:
            >>> # User selects "ROI 2" from dropdown
            >>> event = type('Event', (), {})()  # Mock event
            >>> control_window._on_roi_select(event)
            >>> print(viewer.mouse.selected_roi)  # 1 (0-based index)
            
        Performance:
            Time Complexity: O(1) - Simple selection updates and validation.
            Space Complexity: O(1) - No additional memory allocation.
        """
        selection = self.roi_var.get()
        self.roi_selection = 0 if selection == "Full Image" else int(selection.split()[-1])
        
        prev_selection = self.viewer.mouse.selected_roi
        self.viewer.mouse.selected_roi = self.roi_selection - 1 if self.roi_selection > 0 else None
        
        changes = self.viewer.mouse.validate_selections()
        
        if changes['roi_changed']:
            if self.viewer.mouse.selected_roi is None:
                if prev_selection is not None:
                    pass
                elif self.roi_selection > 0:
                    pass
            else:
                pass
        
        self.viewer.update_display()

    def _on_line_select(self, event) -> None:
        """
        Handle line selection changes from the dropdown.
        
        Updates the viewer's selected line based on user selection and triggers
        display updates to highlight the chosen line. Validates the selection
        and maintains consistency between the GUI and viewer state.
        
        Args:
            event: The tkinter selection event from the line dropdown.
                  Contains information about the ComboboxSelected event.
        
        Returns:
            None: Updates viewer state as side effect, no return value.
            
        Examples:
            >>> # User selects "Line 3" from dropdown
            >>> event = type('Event', (), {})()  # Mock event
            >>> control_window._on_line_select(event)
            >>> print(viewer.mouse.selected_line)  # 2 (0-based index)
            
        Performance:
            Time Complexity: O(1) - Simple selection updates and validation.
            Space Complexity: O(1) - No additional memory allocation.
        """
        selection = self.line_var.get()
        self.line_selection = 0 if selection == "All Lines" else int(selection.split()[-1])
        
        prev_selection = self.viewer.mouse.selected_line
        self.viewer.mouse.selected_line = self.line_selection - 1 if self.line_selection > 0 else None
        
        changes = self.viewer.mouse.validate_selections()
        
        if changes['line_changed']:
            if self.viewer.mouse.selected_line is None:
                if prev_selection is not None:
                    pass
                elif self.line_selection > 0:
                    pass
            else:
                pass
        
        self.viewer.update_display()

    def _on_polygon_select(self, event) -> None:
        """
        Handle polygon selection changes from the dropdown.
        
        Updates the viewer's selected polygon based on user selection and triggers
        display updates to highlight the chosen polygon. Validates the selection
        and maintains consistency between the GUI and viewer state.
        
        Args:
            event: The tkinter selection event from the polygon dropdown.
                  Contains information about the ComboboxSelected event.
        
        Returns:
            None: Updates viewer state as side effect, no return value.
            
        Examples:
            >>> # User selects "Polygon 2" from dropdown
            >>> event = type('Event', (), {})()  # Mock event
            >>> control_window._on_polygon_select(event)
            >>> print(viewer.mouse.selected_polygon)  # 1 (0-based index)
            
        Performance:
            Time Complexity: O(1) - Simple selection updates and validation.
            Space Complexity: O(1) - No additional memory allocation.
        """
        selection = self.polygon_var.get()
        self.polygon_selection = 0 if selection == "All Polygons" else int(selection.split()[-1])
        
        prev_selection = self.viewer.mouse.selected_polygon
        self.viewer.mouse.selected_polygon = self.polygon_selection - 1 if self.polygon_selection > 0 else None
        
        changes = self.viewer.mouse.validate_selections()
        
        if changes['polygon_changed']:
            if self.viewer.mouse.selected_polygon is None:
                if prev_selection is not None:
                    pass
                elif self.polygon_selection > 0:
                    pass
            else:
                pass
        
        self.viewer.update_display()

    def _show_histogram(self) -> None:
        """
        Display histogram analysis for the selected region or full image.
        
        Creates and displays a histogram plot based on the current selection
        (ROI, polygon, or full image). Preserves window state during plot
        creation and provides visual feedback through button highlighting.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates histogram plot as side effect, no return value.
            
        Examples:
            >>> # Select a ROI first
            >>> viewer.mouse.draw_rects.append((10, 10, 100, 100))
            >>> control_window.roi_selection = 1
            >>> control_window._show_histogram()
            >>> # Histogram plot window appears showing ROI 1 analysis
            
        Performance:
            Time Complexity: O(n*m) where n*m is the pixel count in selected region.
            Space Complexity: O(k) where k is the number of histogram bins (typically 256).
        """
        # Set as active button in analysis section
        self._set_active_button('analysis', 'histogram')
        
        if not self.viewer._internal_images: return
        current_idx = self.viewer.trackbar.parameters.get('show', 0)
        image, title = self.viewer._internal_images[current_idx]
        
        # Store current window focus and geometry to restore later
        current_focus = self.root.focus_get()
        current_geometry = self.root.geometry()
        current_title = self.root.title()
        
        try:
            if self.polygon_selection > 0:
                poly_index = self.polygon_selection - 1
                if poly_index < len(self.viewer.mouse.draw_polygons):
                    polygon = self.viewer.mouse.draw_polygons[poly_index]
                    self.viewer.analyzer.create_histogram_plot(image, polygon=polygon, title=f"{title} - Polygon {self.polygon_selection}")
            elif self.roi_selection > 0:
                roi_index = self.roi_selection - 1
                if roi_index < len(self.viewer.mouse.draw_rects):
                    roi = self.viewer.mouse.draw_rects[roi_index]
                    self.viewer.analyzer.create_histogram_plot(image, roi=roi, title=f"{title} - ROI {self.roi_selection}")
            else:
                self.viewer.analyzer.create_histogram_plot(image, title=f"{title} - Full Image")
        finally:
            # Restore window focus, geometry and title after matplotlib plot creation
            # Reduced delay since we're now using proper threading
            self.root.after(50, lambda: self._restore_window_state(current_focus, current_geometry, current_title))

    def _restore_window_state(self, focus_widget, geometry: str, title: str) -> None:
        """
        Restore window state after matplotlib plot creation.
        
        Restores the control window's title, geometry, and focus after creating
        matplotlib plots, which can interfere with window management. Also refreshes
        OpenCV window titles to maintain visibility.
        
        Args:
            focus_widget: The widget that previously had focus, or None.
                         Should have focus_set() method if not None.
            geometry: The window geometry string to restore.
                     Format: "widthxheight+x+y" (e.g., "420x650+100+100").
            title: The window title to restore.
                  Falls back to "Analysis Controls" if empty.
        
        Returns:
            None: Restores window state as side effect, no return value.
            
        Examples:
            >>> focus_widget = some_button_widget
            >>> geometry = "420x650+100+100"
            >>> title = "Analysis Controls"
            >>> control_window._restore_window_state(focus_widget, geometry, title)
            >>> # Window state restored to pre-plot creation state
            
        Performance:
            Time Complexity: O(1) - Fixed window state restoration operations.
            Space Complexity: O(1) - No additional memory allocation.
        """
        try:
            # Restore window title (most important for user visibility)
            if self.root and self.root.winfo_exists():
                self.root.title(title or "Analysis Controls")
                
                # Restore window geometry without forcing minimum size
                if geometry:
                    self.root.geometry(geometry)
                
                # Restore focus if possible
                if focus_widget and hasattr(focus_widget, 'focus_set'):
                    try:
                        focus_widget.focus_set()
                    except:
                        self.root.focus_set()
                else:
                    self.root.focus_set()
                    
                # Ensure window is visible and properly drawn
                self.root.lift()
                self.root.update_idletasks()
                
                # Also refresh OpenCV window titles to ensure they remain visible
                if hasattr(self.viewer, 'windows') and self.viewer.windows:
                    self.viewer.windows.refresh_window_titles()
                    
        except Exception as e:
            print(f"Error restoring window state: {e}")

    def _show_profiles(self) -> None:
        """
        Display pixel profile plots for the selected lines.
        
        Creates and displays pixel intensity profile plots for either all drawn
        lines or a specific selected line. Each profile shows pixel values along
        the line path, useful for analyzing intensity variations.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates profile plots as side effect, no return value.
            
        Examples:
            >>> # Draw some lines first
            >>> viewer.mouse.draw_lines.append((0, 0, 100, 100))
            >>> viewer.mouse.draw_lines.append((50, 0, 50, 100))
            >>> control_window.line_selection = 0  # All lines
            >>> control_window._show_profiles()
            >>> # Profile plot windows appear for all lines
            
        Performance:
            Time Complexity: O(n*m) where n is number of lines, m is pixels per line.
            Space Complexity: O(m) for storing profile data per line.
        """
        # Set as active button in analysis section
        self._set_active_button('analysis', 'profiles')
        
        if not self.viewer._internal_images or not self.viewer.mouse.draw_lines: return
        current_idx = self.viewer.trackbar.parameters.get('show', 0)
        image, title = self.viewer._internal_images[current_idx]
        
        # Store current window state to restore later
        current_focus = self.root.focus_get()
        current_geometry = self.root.geometry()
        current_title = self.root.title()
        
        try:
            if self.line_selection == 0:
                for i, line in enumerate(self.viewer.mouse.draw_lines):
                    self.viewer.analyzer.create_pixel_profile_plot(image, line, f"{title} - Line {i+1}")
            else:
                line_index = self.line_selection - 1
                if line_index < len(self.viewer.mouse.draw_lines):
                    line = self.viewer.mouse.draw_lines[line_index]
                    self.viewer.analyzer.create_pixel_profile_plot(image, line, f"{title} - Line {self.line_selection}")
        finally:
            # Restore window state after matplotlib plot creation
            # Reduced delay since we're now using proper threading
            self.root.after(50, lambda: self._restore_window_state(current_focus, current_geometry, current_title))

    def _toggle_line_mode(self) -> None:
        """
        Toggle line drawing mode on/off.
        
        Switches the viewer between line drawing mode and normal mode.
        When enabled, clicking on the image creates line endpoints.
        Automatically disables polygon mode to prevent conflicts.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates drawing mode state as side effect, no return value.
            
        Examples:
            >>> control_window._toggle_line_mode()
            >>> print(viewer.mouse.is_line_mode)  # True (if was False)
            >>> print(viewer.mouse.is_polygon_mode)  # False (disabled)
            
        Performance:
            Time Complexity: O(1) - Simple boolean operations and button updates.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self.viewer.mouse.is_line_mode = not self.viewer.mouse.is_line_mode
        self.viewer.mouse.is_polygon_mode = False
        self._update_quick_access_buttons()

    def _toggle_polygon_mode(self) -> None:
        """
        Toggle polygon drawing mode on/off.
        
        Switches the viewer between polygon drawing mode and normal mode.
        When enabled, clicking on the image adds polygon vertices.
        Automatically disables line mode to prevent conflicts.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates drawing mode state as side effect, no return value.
            
        Examples:
            >>> control_window._toggle_polygon_mode()
            >>> print(viewer.mouse.is_polygon_mode)  # True (if was False)
            >>> print(viewer.mouse.is_line_mode)  # False (disabled)
            
        Performance:
            Time Complexity: O(1) - Simple boolean operations and button updates.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self.viewer.mouse.is_polygon_mode = not self.viewer.mouse.is_polygon_mode
        self.viewer.mouse.is_line_mode = False
        self._update_quick_access_buttons()

    def _toggle_rectangle_mode(self) -> None:
        """
        Enable rectangle (ROI) drawing mode.
        
        Switches the viewer to rectangle drawing mode by disabling other
        drawing modes. Rectangle mode is the default state when no other
        drawing modes are active.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates drawing mode state as side effect, no return value.
            
        Examples:
            >>> control_window._toggle_rectangle_mode()
            >>> print(viewer.mouse.is_line_mode)  # False
            >>> print(viewer.mouse.is_polygon_mode)  # False
            
        Performance:
            Time Complexity: O(1) - Simple boolean operations and button updates.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self.viewer.mouse.is_line_mode = False
        self.viewer.mouse.is_polygon_mode = False
        self._update_quick_access_buttons()

    def _undo_last_point(self) -> None:
        """
        Undo the last point added to the current polygon.
        
        Removes the most recently added vertex from the polygon being drawn.
        Only operates when in polygon drawing mode and a polygon is currently
        being constructed.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Modifies polygon state as side effect, no return value.
            
        Examples:
            >>> # Start drawing a polygon and add some points
            >>> viewer.mouse.is_polygon_mode = True
            >>> viewer.mouse.current_polygon = [(10, 10), (20, 20), (30, 10)]
            >>> control_window._undo_last_point()
            >>> print(viewer.mouse.current_polygon)  # [(10, 10), (20, 20)]
            
        Performance:
            Time Complexity: O(1) - Simple list pop operation.
            Space Complexity: O(1) - No additional memory allocation.
        """
        # Set as active button in drawing management section
        self._set_active_button('drawing_management', 'undo')
        
        if self.viewer.mouse.is_polygon_mode and self.viewer.mouse.current_polygon:
            self.viewer.mouse.undo_last_point()

    def _clear_last_rectangle(self) -> None:
        """
        Remove the most recently drawn rectangle/ROI.
        
        Deletes the last rectangle from the drawing list and updates the
        selection state if the removed rectangle was selected. Refreshes
        the selector dropdowns and display.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Modifies rectangle list as side effect, no return value.
            
        Examples:
            >>> # Draw some rectangles first
            >>> viewer.mouse.draw_rects = [(10, 10, 50, 50), (20, 20, 60, 60)]
            >>> viewer.mouse.selected_roi = 1  # Select last rectangle
            >>> control_window._clear_last_rectangle()
            >>> print(len(viewer.mouse.draw_rects))  # 1
            >>> print(viewer.mouse.selected_roi)  # None (was cleared)
            
        Performance:
            Time Complexity: O(n) where n is number of UI elements to update.
            Space Complexity: O(1) - No additional memory allocation.
        """
        # Set as active button in drawing management section
        self._set_active_button('drawing_management', 'clear_rect')
        
        if self.viewer.mouse.draw_rects:
            if self.viewer.mouse.selected_roi == len(self.viewer.mouse.draw_rects) - 1:
                self.viewer.mouse.selected_roi = None
            
            self.viewer.mouse.draw_rects.pop()
            self.update_selectors()
            self.viewer.update_display()

    def _clear_last_line(self) -> None:
        """
        Remove the most recently drawn line.
        
        Deletes the last line from the drawing list and updates the selection
        state if the removed line was selected. Clears any current line being
        drawn and refreshes the interface.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Modifies line list as side effect, no return value.
            
        Examples:
            >>> # Draw some lines first
            >>> viewer.mouse.draw_lines = [(0, 0, 100, 100), (50, 50, 150, 150)]
            >>> viewer.mouse.selected_line = 1  # Select last line
            >>> control_window._clear_last_line()
            >>> print(len(viewer.mouse.draw_lines))  # 1
            >>> print(viewer.mouse.selected_line)  # None (was cleared)
            >>> print(viewer.mouse.current_line)  # None (cleared)
            
        Performance:
            Time Complexity: O(n) where n is number of UI elements to update.
            Space Complexity: O(1) - No additional memory allocation.
        """
        # Set as active button in drawing management section
        self._set_active_button('drawing_management', 'clear_line')
        
        if self.viewer.mouse.draw_lines:
            if self.viewer.mouse.selected_line == len(self.viewer.mouse.draw_lines) - 1:
                self.viewer.mouse.selected_line = None
            
            self.viewer.mouse.draw_lines.pop()
            self.update_selectors()
            self.viewer.update_display()
        self.viewer.mouse.current_line = None

    def _clear_last_polygon(self) -> None:
        """
        Remove the most recently drawn polygon.
        
        Deletes the last polygon from the drawing list and updates the
        selection state if the removed polygon was selected. Refreshes
        the selector dropdowns and display.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Modifies polygon list as side effect, no return value.
            
        Examples:
            >>> # Draw some polygons first
            >>> viewer.mouse.draw_polygons = [[(10, 10), (20, 10), (15, 20)], [(30, 30), (40, 30), (35, 40)]]
            >>> viewer.mouse.selected_polygon = 1  # Select last polygon
            >>> control_window._clear_last_polygon()
            >>> print(len(viewer.mouse.draw_polygons))  # 1
            >>> print(viewer.mouse.selected_polygon)  # None (was cleared)
            
        Performance:
            Time Complexity: O(n) where n is number of UI elements to update.
            Space Complexity: O(1) - No additional memory allocation.
        """
        # Set as active button in drawing management section
        self._set_active_button('drawing_management', 'clear_polygon')
        
        if self.viewer.mouse.draw_polygons:
            if self.viewer.mouse.selected_polygon == len(self.viewer.mouse.draw_polygons) - 1:
                self.viewer.mouse.selected_polygon = None
            
            self.viewer.mouse.draw_polygons.pop()
            self.update_selectors()
            self.viewer.update_display()

    def _clear_all(self) -> None:
        """
        Clear all drawn objects (rectangles, lines, polygons).
        
        Removes all drawing objects from the viewer and resets all selection
        states. This is a comprehensive cleanup operation that returns the
        drawing state to initial conditions.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Clears all drawing data as side effect, no return value.
            
        Examples:
            >>> # Draw various objects first
            >>> viewer.mouse.draw_rects = [(10, 10, 50, 50)]
            >>> viewer.mouse.draw_lines = [(0, 0, 100, 100)]
            >>> viewer.mouse.draw_polygons = [[(10, 10), (20, 10), (15, 20)]]
            >>> control_window._clear_all()
            >>> print(len(viewer.mouse.draw_rects))  # 0
            >>> print(len(viewer.mouse.draw_lines))  # 0
            >>> print(len(viewer.mouse.draw_polygons))  # 0
            
        Performance:
            Time Complexity: O(n) where n is total number of UI elements to update.
            Space Complexity: O(1) - Memory deallocation for cleared objects.
        """
        # Set as active button in drawing management section
        self._set_active_button('drawing_management', 'clear_all')
        
        self.viewer.mouse.draw_rects.clear()
        self.viewer.mouse.draw_lines.clear()
        self.viewer.mouse.draw_polygons.clear()
        self.viewer.mouse.current_polygon.clear()
        self.viewer.mouse.current_line = None
        self.viewer.mouse.clear_selections()
        self.update_selectors()
        self.viewer.update_display()

    def _close_plots(self) -> None:
        """
        Close all open matplotlib plot windows.
        
        Closes all analysis plots (histograms, profiles) that have been
        created during the current session. Provides a clean way to manage
        plot window clutter.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Closes plot windows as side effect, no return value.
            
        Examples:
            >>> # After creating some plots
            >>> control_window._show_histogram()
            >>> control_window._show_profiles()
            >>> control_window._close_plots()
            >>> # All matplotlib windows now closed
            
        Performance:
            Time Complexity: O(n) where n is the number of open plot windows.
            Space Complexity: O(1) - No additional memory allocation.
        """
        # Set as active button in export_plots section
        self._set_active_button('export_plots', 'close_plots')
        
        if hasattr(self.viewer, 'analyzer') and self.viewer.analyzer:
            self.viewer.analyzer.close_all_plots()

        
    def _export_analysis_data(self) -> None:
        """
        Open the export dialog for analysis data.
        
        Launches the enhanced export dialog that allows users to export
        histogram, profile, or polygon data in various formats (JSON, CSV, PNG).
        Falls back to a simple export dialog if the enhanced version is unavailable.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Opens export dialog as side effect, no return value.
            
        Examples:
            >>> # Ensure image is loaded first
            >>> viewer._internal_images = [(image_array, "test_image")]
            >>> control_window._export_analysis_data()
            >>> # Export dialog window opens with format options
            
        Performance:
            Time Complexity: O(1) - Dialog creation and display operations.
            Space Complexity: O(1) - Export dialog widget creation.
            
        Raises:
            Exception: If export dialog creation fails or image data is unavailable.
        """
        # Set as active button in export_plots section
        self._set_active_button('export_plots', 'export_data')
        
        if not self.viewer._internal_images:
            messagebox.showinfo("Export Analysis", "No image available for analysis.")
            return
            
        current_idx = self.viewer.trackbar.parameters.get('show', 0)
        image, title = self.viewer._internal_images[current_idx]
        
        try:
            export_dialog = EnhancedExportDialog(self.root, self.theme_manager)
            export_dialog.show(
                filename_prefix=title.replace(' ', '_'),
                on_export=lambda export_type, export_format, full_path, data_source: self._handle_export(
                    export_type, export_format, full_path, image, title, data_source
                ),
                viewer=self.viewer
            )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to open export dialog: {str(e)}")
        
    def _handle_export(self, export_type: str, export_format: str, full_path: str, 
                      image, title: str, data_source: str) -> None:
        """
        Handle the actual export operation based on user selections.
        
        Processes export requests from the export dialog, handling different
        data types, formats, and sources. Supports both data file exports
        (JSON, CSV) and image exports (PNG) for plots.
        
        Args:
            export_type: Type of data to export ('histogram', 'profile', 'polygon').
            export_format: Output format ('json', 'csv', 'image').
            full_path: Complete file path for the export output.
            image: The image data to analyze for export. NumPy array format.
            title: Display title for the analysis. Used in plot titles.
            data_source: Source specification (e.g., 'full_image', 'roi_0', 'line_1').
        
        Returns:
            None: Performs export operations as side effect, no return value.
            
        Examples:
            >>> # Export histogram data as JSON
            >>> control_window._handle_export(
            ...     "histogram", "json", "/path/output.json", 
            ...     image_array, "Test Image", "full_image"
            ... )
            >>> # Creates JSON file with histogram data
            
        Performance:
            Time Complexity: O(n*m) where n*m is pixels in analysis region.
            Space Complexity: O(k) where k is size of exported data structure.
            
        Raises:
            Exception: If export operation fails due to invalid data or I/O errors.
        """
        # Handle image export
        if export_format == "image":
            if export_type == "histogram":
                try:
                    # Parse data source to determine what to plot
                    if data_source == "full_image":
                        self.viewer.analyzer.create_histogram_plot(image, title=f"{title} - Full Image")
                    elif data_source.startswith("roi_"):
                        roi_index = int(data_source.split("_")[1])
                        if roi_index < len(self.viewer.mouse.draw_rects):
                            roi = self.viewer.mouse.draw_rects[roi_index]
                            self.viewer.analyzer.create_histogram_plot(image, roi=roi, title=f"{title} - ROI {roi_index + 1}")
                        else:
                            messagebox.showerror("Export Error", "Selected ROI is no longer valid")
                            return
                    elif data_source.startswith("polygon_"):
                        poly_index = int(data_source.split("_")[1])
                        if poly_index < len(self.viewer.mouse.draw_polygons):
                            polygon = self.viewer.mouse.draw_polygons[poly_index]
                            self.viewer.analyzer.create_histogram_plot(image, polygon=polygon, title=f"{title} - Polygon {poly_index + 1}")
                        else:
                            messagebox.showerror("Export Error", "Selected polygon is no longer valid")
                            return
                    else:
                        messagebox.showerror("Export Error", f"Unknown data source: {data_source}")
                        return
                    
                    # Save the generated plot
                    success = self.viewer.analyzer.save_last_histogram_plot(full_path)
                    if success:
                        messagebox.showinfo("Export Complete", f"Histogram plot image saved to {full_path}")
                    else:
                        messagebox.showerror("Export Failed", "Failed to save histogram plot image")
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to create histogram plot: {str(e)}")
            elif export_type == "profile":
                try:
                    # Parse data source to determine what to plot
                    if data_source == "all_lines":
                        # For multiple lines, create individual plots and save the last one
                        for i, line in enumerate(self.viewer.mouse.draw_lines):
                            self.viewer.analyzer.create_pixel_profile_plot(image, line, f"{title} - Line {i+1}")
                    elif data_source.startswith("line_"):
                        line_index = int(data_source.split("_")[1])
                        if line_index < len(self.viewer.mouse.draw_lines):
                            line = self.viewer.mouse.draw_lines[line_index]
                            self.viewer.analyzer.create_pixel_profile_plot(image, line, f"{title} - Line {line_index + 1}")
                        else:
                            messagebox.showerror("Export Error", "Selected line is no longer valid")
                            return
                    else:
                        messagebox.showerror("Export Error", f"Unknown data source: {data_source}")
                        return
                    
                    # Save the generated plot
                    success = self.viewer.analyzer.save_last_profile_plot(full_path)
                    if success:
                        messagebox.showinfo("Export Complete", f"Profile plot image saved to {full_path}")
                    else:
                        messagebox.showerror("Export Failed", "Failed to save profile plot image")
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to create profile plot: {str(e)}")
            else:
                messagebox.showerror("Export Error", f"Image export not supported for {export_type}")
            return
        
        try:
            if export_type == "histogram":
                # Parse data source to determine what to export
                if data_source == "full_image":
                    histogram_data = self.viewer.analyzer.calculate_histogram(image)
                elif data_source.startswith("roi_"):
                    roi_index = int(data_source.split("_")[1])
                    if roi_index < len(self.viewer.mouse.draw_rects):
                        roi = self.viewer.mouse.draw_rects[roi_index]
                        histogram_data = self.viewer.analyzer.calculate_histogram(image, roi=roi)
                    else:
                        messagebox.showerror("Export Error", "Selected ROI is no longer valid")
                        return
                elif data_source.startswith("polygon_"):
                    poly_index = int(data_source.split("_")[1])
                    if poly_index < len(self.viewer.mouse.draw_polygons):
                        polygon = self.viewer.mouse.draw_polygons[poly_index]
                        histogram_data = self.viewer.analyzer.calculate_histogram(image, polygon=polygon)
                    else:
                        messagebox.showerror("Export Error", "Selected polygon is no longer valid")
                        return
                else:
                    messagebox.showerror("Export Error", f"Unknown data source: {data_source}")
                    return
                
                success = self.viewer.analyzer.export_analysis_data('histogram', histogram_data, export_format, full_path)
                if success:
                    messagebox.showinfo("Export Complete", f"Histogram data exported to {full_path}")
                else:
                    messagebox.showerror("Export Failed", "Failed to export histogram data")
            
            elif export_type == "profile":
                # Parse data source to determine what to export
                if data_source == "all_lines":
                    base_path = os.path.splitext(full_path)[0]
                    exported_count = 0
                    
                    for i, line in enumerate(self.viewer.mouse.draw_lines):
                        line_path = f"{base_path}_line{i+1}.{export_format}"
                        profile_data = self.viewer.analyzer.calculate_pixel_profile(image, line)
                        success = self.viewer.analyzer.export_analysis_data('profile', profile_data, export_format, line_path)
                        if success:
                            exported_count += 1
                            
                    if exported_count > 0:
                        messagebox.showinfo("Export Complete", f"Exported {exported_count} line profiles.")
                    else:
                        messagebox.showerror("Export Failed", "Failed to export any line profiles")
                elif data_source.startswith("line_"):
                    line_index = int(data_source.split("_")[1])
                    if line_index < len(self.viewer.mouse.draw_lines):
                        line = self.viewer.mouse.draw_lines[line_index]
                        profile_data = self.viewer.analyzer.calculate_pixel_profile(image, line)
                        success = self.viewer.analyzer.export_analysis_data('profile', profile_data, export_format, full_path)
                        if success:
                            messagebox.showinfo("Export Complete", f"Profile data exported to {full_path}")
                        else:
                            messagebox.showerror("Export Failed", "Failed to export profile data")
                    else:
                        messagebox.showerror("Export Error", "Selected line is no longer valid")
                        return
                else:
                    messagebox.showerror("Export Error", f"Unknown data source: {data_source}")
                    return
                            
            else:
                messagebox.showerror("Export Error", f"Unknown export type: {export_type}")
                return
                        
        except Exception as e:
            messagebox.showerror("Export Error", f"Error during export: {str(e)}")

    def _open_thresholding_window(self) -> None:
        """
        Open the thresholding color space selection window.
        
        Launches the thresholding manager's interface for image segmentation
        operations. The thresholding window provides controls for adjusting
        threshold parameters across different color spaces.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Opens thresholding window as side effect, no return value.
            
        Examples:
            >>> control_window._open_thresholding_window()
            >>> # Thresholding color space selection window appears
            >>> # User can adjust HSV, RGB, or other color space thresholds
            
        Performance:
            Time Complexity: O(1) - Simple window creation and display.
            Space Complexity: O(1) - Thresholding window widget creation.
        """
        # Set as active button in analysis section
        self._set_active_button('analysis', 'thresholding')
        
        self.thresholding_manager.open_colorspace_selection_window()
        

    def _on_closing(self) -> None:
        """
        Handle window closing event.
        
        Performs cleanup operations when the analysis control window is closed,
        including closing any thresholding windows and destroying the main window.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Performs cleanup as side effect, no return value.
            
        Examples:
            >>> # This method is called automatically when user closes window
            >>> # Manual call example:
            >>> control_window._on_closing()
            >>> # All child windows closed and main window destroyed
            
        Performance:
            Time Complexity: O(1) - Fixed cleanup operations.
            Space Complexity: O(1) - Memory deallocation during cleanup.
        """
        self.thresholding_manager.cleanup_windows()
        self.destroy_window()
    
    def destroy_window(self) -> None:
        """
        Destroy the analysis control window and clean up resources.
        
        Performs comprehensive cleanup of the window and its components,
        including unbinding event handlers and clearing object references
        to prevent memory leaks.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Destroys window and cleans up as side effect, no return value.
            
        Examples:
            >>> control_window = AnalysisControlWindow(viewer)
            >>> control_window.create_window()
            >>> print(control_window.window_created)  # True
            >>> control_window.destroy_window()
            >>> print(control_window.window_created)  # False
            
        Performance:
            Time Complexity: O(1) - Fixed cleanup operations.
            Space Complexity: O(1) - Memory deallocation for window components.
        """
        if self.window_created and self.root:
            try: 
                # Clean up mouse wheel bindings
                if hasattr(self, 'canvas'):
                    self.canvas.unbind_all("<MouseWheel>")
                self.root.destroy()
            except: 
                pass
            self.window_created = False
            self.root = None
            self.canvas = None
            self.main_frame = None
            self.scrollbar = None
            self.canvas_frame = None
    
    def _setup_keyboard_shortcuts(self) -> None:
        """
        Setup keyboard shortcuts for quick access to common operations.
        
        Binds keyboard events to the main window for rapid access to drawing
        modes and analysis functions. Provides professional workflow efficiency
        through standard keyboard shortcuts.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Sets up keyboard bindings as side effect, no return value.
            
        Examples:
            >>> control_window._setup_keyboard_shortcuts()
            >>> # Now pressing 'H' key will show histogram
            >>> # Pressing 'L' key will toggle line drawing mode
            
        Performance:
            Time Complexity: O(1) - Fixed number of event binding operations.
            Space Complexity: O(1) - Function closure creation for event handler.
        """
        def on_key_press(event):
            try:
                key = event.keysym.lower()
                if key == 'r':
                    self._toggle_rectangle_mode()
                elif key == 'l':
                    self._toggle_line_mode()
                elif key == 'p' and not (event.state & 0x1):  # P without shift
                    self._toggle_polygon_mode()
                elif key == 'h':
                    self._show_histogram()
                elif key == 'p' and (event.state & 0x1):  # Shift+P
                    self._show_profiles()
                elif key == 'escape':
                    # Clear current drawing mode
                    if self.viewer.mouse.is_line_mode or self.viewer.mouse.is_polygon_mode:
                        self.viewer.mouse.is_line_mode = False
                        self.viewer.mouse.is_polygon_mode = False
                        self._update_quick_access_buttons()
            except Exception as e:
                if self.viewer:
                    print(f"Keyboard shortcut error: {e}")
        
        # Bind to the root window
        self.root.bind('<KeyPress>', on_key_press)
        self.root.focus_set()  # Make sure the window can receive key events

    def _create_quick_access_section(self, parent_frame) -> None:
        """
        Create the quick access section with drawing mode toggle buttons.
        
        Builds the drawing tools section containing buttons for switching between
        rectangle, line, and polygon drawing modes. Includes visual state indicators
        and keyboard shortcut setup.
        
        Args:
            parent_frame: The parent frame to contain the quick access controls.
                         Must be a valid tkinter container widget.
        
        Returns:
            None: Creates quick access UI as side effect, no return value.
            
        Examples:
            >>> control_window._create_quick_access_section(main_frame)
            >>> # Creates rectangle, line, and polygon mode toggle buttons
            >>> # Sets up keyboard shortcuts (R, L, P keys)
            
        Performance:
            Time Complexity: O(1) - Fixed number of button creation operations.
            Space Complexity: O(1) - Creates fixed number of button widgets.
        """
        quick_frame = self._create_section_frame(parent_frame, "Drawing Tools")
        
        drawing_frame = ttk.Frame(quick_frame, style=self.theme_manager.get_frame_style())
        drawing_frame.pack(fill='x', pady=(0, 10))
        drawing_frame.columnconfigure(0, weight=1, minsize=100)
        drawing_frame.columnconfigure(1, weight=1, minsize=100)
        drawing_frame.columnconfigure(2, weight=1, minsize=100)
        
        rectangle_btn = ttk.Button(
            drawing_frame, 
            text="⬛ Rectangle Mode", 
            command=self._toggle_rectangle_mode,
            style=self.theme_manager.get_button_style()
        )
        rectangle_btn.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        Tooltip(rectangle_btn, "Toggle rectangle drawing mode (R key)")
        self.quick_access_buttons['rectangle_mode'] = rectangle_btn
        
        line_btn = ttk.Button(
            drawing_frame, 
            text="📏 Line Mode", 
            command=self._toggle_line_mode,
            style=self.theme_manager.get_button_style()
        )
        line_btn.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        Tooltip(line_btn, "Toggle line drawing mode (L key)")
        self.quick_access_buttons['line_mode'] = line_btn
        
        polygon_btn = ttk.Button(
            drawing_frame, 
            text="🔺 Polygon Mode", 
            command=self._toggle_polygon_mode,
            style=self.theme_manager.get_button_style()
        )
        polygon_btn.grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        Tooltip(polygon_btn, "Toggle polygon drawing mode (P key)")
        self.quick_access_buttons['polygon_mode'] = polygon_btn
        
        # Add keyboard bindings
        self._setup_keyboard_shortcuts()

    def _update_quick_access_buttons(self) -> None:
        """
        Update the visual state of quick access drawing mode buttons.
        
        Refreshes button styling to reflect the current drawing mode state.
        Active modes are highlighted with the theme's active button style,
        while inactive modes use the default styling.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates button styling as side effect, no return value.
            
        Examples:
            >>> viewer.mouse.is_line_mode = True
            >>> control_window._update_quick_access_buttons()
            >>> # Line mode button now highlighted, others normal
            
        Performance:
            Time Complexity: O(1) - Fixed button style update operations.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if not self.window_created or not self.quick_access_buttons:
            return
            
        try:
            # Rectangle mode is active when neither line nor polygon mode is active
            is_rectangle_mode = not self.viewer.mouse.is_line_mode and not self.viewer.mouse.is_polygon_mode
            
            # Update rectangle mode button
            if self.quick_access_buttons.get('rectangle_mode'):
                style = self.theme_manager.get_button_style("active") if is_rectangle_mode else self.theme_manager.get_button_style()
                self.quick_access_buttons['rectangle_mode'].config(style=style)
                
            # Update line mode button
            if self.quick_access_buttons.get('line_mode'):
                style = self.theme_manager.get_button_style("active") if self.viewer.mouse.is_line_mode else self.theme_manager.get_button_style()
                self.quick_access_buttons['line_mode'].config(style=style)
                
            # Update polygon mode button
            if self.quick_access_buttons.get('polygon_mode'):
                style = self.theme_manager.get_button_style("active") if self.viewer.mouse.is_polygon_mode else self.theme_manager.get_button_style()
                self.quick_access_buttons['polygon_mode'].config(style=style)
        except Exception as e:
            print(f"Error updating quick access buttons: {e}")

    def _set_active_button(self, section: str, button_key: str) -> None:
        """
        Set a button as active and update visual states for the section.
        
        Manages button state highlighting within organized sections to provide
        visual feedback about the most recent action. Only one button per
        section can be active at a time.
        
        Args:
            section: The section name ('analysis', 'drawing_management', 'export_plots').
            button_key: The specific button identifier within the section.
        
        Side Effects:
            - Clears previous active button styling in the section
            - Applies active styling to the new button
            - Updates internal active_states tracking
        
        Performance:
            Time Complexity: O(1) - Direct dictionary lookups and single button updates.
        """
        if not self.action_buttons or not self.window_created:
            return
            
        try:
            # Clear previous active button in this section
            if self.active_states.get(section):
                prev_button = self.action_buttons.get(self.active_states[section])
                if prev_button and prev_button.winfo_exists():
                    # Check if it's a tk.Button or ttk.Button
                    if isinstance(prev_button, tk.Button):
                        # Handle tk.Button styling - restore original colors
                        if self.active_states[section] == 'export_data':
                            prev_button.config(
                                bg='#007bff',
                                fg='white',
                                relief="raised",
                                bd=2,
                                activebackground='#0056b3'
                            )
                    else:
                        # Handle ttk.Button styling
                        prev_button.config(style=self.theme_manager.get_button_style())
            
            # Set new active button
            self.active_states[section] = button_key
            current_button = self.action_buttons.get(button_key)
            if current_button and current_button.winfo_exists():
                # Check if it's a tk.Button or ttk.Button
                if isinstance(current_button, tk.Button):
                    # Handle tk.Button styling - apply active green style
                    current_button.config(
                        bg='#28a745',
                        fg='white',
                        relief="solid",
                        bd=2,
                        activebackground='#1e7e34'
                    )
                else:
                    # Handle ttk.Button styling
                    current_button.config(style=self.theme_manager.get_button_style("active"))
                    
        except Exception as e:
            if self.viewer:
                print(f"Button state error: {e}")
                
    def _rebind_canvas_events(self) -> None:
        """
        Re-bind canvas events after button state changes.
        
        This method is no longer needed since canvas events are not unbound
        during button state changes. Maintained for backward compatibility.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: This method performs no operations and returns nothing.
            
        Examples:
            >>> # This method is deprecated but can be called safely
            >>> control_window._rebind_canvas_events()
            >>> # No effect - method does nothing
            
        Performance:
            Time Complexity: O(1) - No operations performed.
            Space Complexity: O(1) - No memory allocation.
            
        Deprecated:
            This method is deprecated and performs no operations.
        """
        # This method is no longer needed since we're not unbinding events
        pass

    def _provide_button_feedback(self, button) -> None:
        """
        Provide visual feedback when action buttons are clicked.
        
        Creates temporary visual feedback by briefly changing the button style
        to the active state, then returning to the original style. Provides
        user confirmation that the button press was registered.
        
        Args:
            button: The tkinter button widget to provide feedback for.
                   Must be a valid tkinter button with cget() and config() methods.
        
        Returns:
            None: Modifies button styling as side effect, no return value.
            
        Examples:
            >>> # Create a button and provide feedback
            >>> button = ttk.Button(parent, text="Test")
            >>> control_window._provide_button_feedback(button)
            >>> # Button briefly changes to active style, then returns to normal
            >>> 
            >>> # Safe to call with None button
            >>> control_window._provide_button_feedback(None)  # No effect
            
        Performance:
            Time Complexity: O(1) - Single button style changes and timer setup.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if not button:
            return
            
        try:
            # Store original style
            original_style = button.cget('style')
            
            # Change to active style temporarily
            button.config(style=self.theme_manager.get_button_style("active"))
            
            # Schedule return to original style after 200ms
            self.root.after(200, lambda: button.config(style=original_style))
        except Exception as e:
            if self.viewer:
                print(f"Button feedback error: {e}")
