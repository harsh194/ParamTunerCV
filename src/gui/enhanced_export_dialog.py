"""
Enhanced export dialog module for the Parameter image viewer application.

This module provides a sophisticated GUI dialog for exporting analysis data from
the Parameter project. It supports multiple export formats (JSON, CSV, PNG), 
various data sources (full image, ROIs, polygons, lines), and maintains user
preferences between sessions.

Main Classes:
    - EnhancedExportDialog: Advanced export dialog with theme support, data source
      selection, format options, and settings persistence

Features:
    - Multi-format export support (JSON, CSV, PNG images)
    - Dynamic data source selection based on available analysis objects
    - Settings persistence across sessions
    - Theme-aware styling and tooltips
    - Real-time filename preview
    - Validation of export requirements
    - Visual feedback for user interactions

Dependencies:
    - tkinter: GUI framework
    - typing: Type hints support
    - json: Settings persistence
    - os: File system operations

Usage:
    export_dialog = EnhancedExportDialog(parent, theme_manager)
    export_dialog.show(filename_prefix="analysis", on_export=export_handler, viewer=viewer)
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os
import json
from typing import Dict, Any, List, Optional, Callable

class EnhancedExportDialog:
    """
    Enhanced export dialog with comprehensive export options and user experience features.
    
    This class provides a sophisticated interface for exporting analysis data from the
    Parameter image viewer. It supports multiple export formats, dynamic data source
    selection, settings persistence, and theme-aware styling.
    
    The dialog features organized sections for analysis type selection, data source
    selection, format options, filename customization, and directory selection.
    User preferences are automatically saved and restored between sessions.
    
    Attributes:
        parent: The parent tkinter window.
        theme_manager: ThemeManager instance for consistent styling.
        title (str): Dialog window title.
        dialog: The tkinter Toplevel dialog window.
        settings (dict): Persistent user settings loaded from config file.
        export_type (tk.StringVar): Selected analysis type ('histogram', 'profile', 'polygon').
        export_format (tk.StringVar): Selected export format ('json', 'csv').
        export_as_image (tk.BooleanVar): Whether to export as PNG image.
        data_source (tk.StringVar): Selected data source identifier.
        filename_prefix (tk.StringVar): User-defined filename prefix.
        selected_directory (str): Currently selected export directory.
        on_export_callback: Callback function for export confirmation.
        on_cancel_callback: Callback function for dialog cancellation.
        viewer: Reference to ImageViewer for data validation.
    
    Examples:
        >>> dialog = EnhancedExportDialog(root, theme_manager, title="Export Data")
        >>> dialog.show(
        ...     filename_prefix="my_analysis",
        ...     on_export=handle_export,
        ...     viewer=image_viewer
        ... )
        # Shows modal dialog with export options
    """
    
    CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".parameter_export_settings.json")
    
    def __init__(self, parent, theme_manager, title: str = "Export Analysis Data") -> None:
        """
        Initialize the enhanced export dialog with theme support and settings persistence.
        
        Sets up the dialog's initial state, loads user settings from the config file,
        and initializes all UI variables. The dialog is not displayed until show() is called.
        
        Args:
            parent: The parent tkinter window that will own this dialog.
                   Must be a valid tkinter window or root widget.
            theme_manager: ThemeManager instance for consistent styling across the application.
                          Must have required styling methods.
            title: The title text displayed in the dialog window title bar.
                  Defaults to "Export Analysis Data" if not specified.
        
        Returns:
            None: This is a constructor method.
            
        Examples:
            >>> from theme_manager import ThemeManager
            >>> root = tk.Tk()
            >>> theme_mgr = ThemeManager()
            >>> dialog = EnhancedExportDialog(root, theme_mgr, "Custom Export")
            >>> # Dialog created but not shown until show() is called
            
        Performance:
            Time Complexity: O(1) - Simple initialization and settings loading.
            Space Complexity: O(1) - Fixed memory allocation for dialog state.
        """
        self.parent = parent
        self.theme_manager = theme_manager
        self.title = title
        self.dialog = None
        self.settings = self._load_settings()
        
        # Default values - start with no selection to keep all buttons blue initially
        self.export_type = tk.StringVar(value="")
        self.export_format = tk.StringVar(value="")
        self.export_as_image = tk.BooleanVar(value=False)
        self.data_source = tk.StringVar(value="")  # New: which specific data to export
        self.filename_prefix = tk.StringVar(value="")
        self.selected_directory = ""  # Start with no directory selected
        
        # Callback functions
        self.on_export_callback = None
        self.on_cancel_callback = None
        
    def _load_settings(self) -> Dict[str, Any]:
        """
        Load export settings from the user's config file.
        
        Attempts to load previously saved export preferences from a JSON config file
        in the user's home directory. If the file doesn't exist or cannot be read,
        returns default settings with histogram, JSON format, and no image export.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            Dict[str, Any]: Settings dictionary containing export preferences with keys:
                - last_directory: str, previously used export directory path
                - last_export_type: str, last selected export type (histogram/profile/roi)
                - last_export_format: str, last selected format (json/csv/xml)
                - last_export_as_image: bool, whether image export was enabled
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> settings = dialog._load_settings()
            >>> print(settings['last_export_type'])  # 'histogram'
            >>> print(settings['last_directory'])    # '' or saved path
            
        Performance:
            Time Complexity: O(1) - File I/O operation with constant-size config.
            Space Complexity: O(1) - Fixed-size dictionary with configuration data.
        """
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            return {
                "last_directory": "",
                "last_export_type": "histogram",
                "last_export_format": "json",
                "last_export_as_image": False
            }
        except Exception:
            # If there's any error loading settings, return defaults
            return {
                "last_directory": "",
                "last_export_type": "histogram",
                "last_export_format": "json",
                "last_export_as_image": False
            }
            
    def _save_settings(self) -> None:
        """
        Save current export settings to the user's config file.
        
        Persists the current dialog settings to a JSON file in the user's home
        directory for restoration in future sessions. Only saves non-empty values
        that have been explicitly selected by the user to avoid overwriting with defaults.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Saves settings as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog.export_type.set('histogram')
            >>> dialog.export_format.set('csv')
            >>> dialog.selected_directory = '/home/user/exports'
            >>> dialog._save_settings()
            >>> # Settings saved to ~/.parameter_export_settings.json
            
        Performance:
            Time Complexity: O(1) - File I/O with constant-size config data.
            Space Complexity: O(1) - No additional memory allocation.
        """
        try:
            # Update settings with current values only if they were selected
            export_type = self.export_type.get()
            export_format = self.export_format.get()
            export_as_image = self.export_as_image.get()
            
            if export_type:
                self.settings["last_export_type"] = export_type
            if export_format:
                self.settings["last_export_format"] = export_format
            self.settings["last_export_as_image"] = export_as_image
            
            # Save current directory if it exists
            if self.selected_directory and os.path.exists(self.selected_directory):
                self.settings["last_directory"] = self.selected_directory
            
            # Save settings to file
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            # Silently fail if we can't save settings
            pass
            
    def show(self, filename_prefix: str = "", on_export: Optional[Callable] = None, 
             on_cancel: Optional[Callable] = None, viewer = None) -> None:
        """
        Display the export dialog as a modal window.
        
        Creates and displays the complete export interface with all sections and options.
        The dialog is modal and blocks parent interaction until user makes selection.
        Automatically centers on parent window and applies current theme styling.
        
        Args:
            filename_prefix (str): Default prefix for the exported filename.
            on_export (Optional[Callable]): Callback function called when export is confirmed.
                Signature: on_export(export_type, export_format, full_path, data_source)
            on_cancel (Optional[Callable]): Callback function called when dialog is canceled.
            viewer: ImageViewer instance used to validate available analysis data
                   and populate data source options.
        
        Returns:
            None: Displays dialog as side effect, blocks until user interaction.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> def export_handler(exp_type, format, path, source):
            ...     print(f"Exporting {exp_type} as {format} to {path}")
            >>> dialog.show("analysis_", export_handler, None, viewer)
            >>> # Dialog displays and waits for user interaction
            
        Performance:
            Time Complexity: O(1) - UI creation with fixed widget count.
            Space Complexity: O(1) - Fixed memory for dialog components.
        """
        self.filename_prefix.set(filename_prefix)
        self.on_export_callback = on_export
        self.on_cancel_callback = on_cancel
        self.viewer = viewer  # Store viewer reference for data validation
        
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("520x620")
        self.dialog.minsize(500, 600)
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Apply theme
        self.theme_manager.configure_theme(self.dialog)
        
        # Center the dialog on parent
        self._center_on_parent()
        
        # Create dialog content
        self._create_dialog_content()
        
        # Wait for the dialog to be closed
        self.parent.wait_window(self.dialog)
        
    def _check_data_availability(self, export_type: str) -> tuple[bool, str]:
        """
        Check if the requested analysis data is available in the viewer.
        
        Validates whether the viewer has the necessary drawn objects (ROIs, polygons,
        lines) to perform the requested export type. Returns availability status with
        user-friendly messages for missing data or fallback options.
        
        Args:
            export_type (str): Type of export requested. Must be one of:
                - 'histogram': Requires ROIs, polygons, or uses full image
                - 'profile': Requires line profiles to be drawn
                - 'polygon': Requires polygon regions to be drawn
        
        Returns:
            tuple[bool, str]: A tuple containing:
                - bool: True if data is available for export, False if missing required data
                - str: Informational or warning message for user feedback
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> available, msg = dialog._check_data_availability('histogram')
            >>> print(available, msg)  # True, "Note: No ROIs..." or True, ""
            >>> 
            >>> available, msg = dialog._check_data_availability('profile')
            >>> print(available, msg)  # False, "No line profiles..." if none drawn
            
        Performance:
            Time Complexity: O(1) - Simple list length checks and conditionals.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if not self.viewer:
            return True, ""  # If no viewer provided, assume data is available
            
        if export_type == "histogram":
            # For histogram, we need either ROIs, polygons, or can use full image
            has_rois = bool(self.viewer.mouse.draw_rects)
            has_polygons = bool(self.viewer.mouse.draw_polygons)
            if not has_rois and not has_polygons:
                return True, "Note: No ROIs or polygons drawn. Histogram will be calculated for the full image."
            return True, ""
            
        elif export_type == "profile":
            # For pixel profiles, we need drawn lines
            has_lines = bool(self.viewer.mouse.draw_lines)
            if not has_lines:
                return False, "No line profiles available for export.\n\nTo create pixel profiles:\n1. Switch to Line Mode in Analysis Controls\n2. Draw lines on the image\n3. Return here to export the profile data"
            return True, ""
            
        return True, ""
        
    def _center_on_parent(self) -> None:
        """
        Center the dialog window on its parent window.
        
        Calculates the appropriate position to center the dialog on the parent
        window, taking into account both window dimensions and screen positioning.
        Handles cases where parent window information is not available.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Modifies dialog position as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog.dialog = tk.Toplevel(root)
            >>> dialog._center_on_parent()
            >>> # Dialog now positioned at center of parent window
            
        Performance:
            Time Complexity: O(1) - Simple arithmetic calculations.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if not self.dialog or not self.parent:
            return
            
        # Get parent geometry
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate dialog position
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Position dialog in the center of parent
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        # Set dialog position
        self.dialog.geometry(f"+{x}+{y}")
        
    def _create_dialog_content(self) -> None:
        """
        Create and arrange all sections of the dialog content.
        
        Builds the complete dialog interface including title, analysis type selection,
        data source selection, format options, filename customization, directory
        selection, and action buttons. Applies theme styling throughout.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates UI components as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog.dialog = tk.Toplevel(root)
            >>> dialog._create_dialog_content()
            >>> # Complete dialog interface created with all sections
            
        Performance:
            Time Complexity: O(1) - Fixed number of UI widget creations.
            Space Complexity: O(1) - Fixed memory allocation for dialog components.
        """
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, style=self.theme_manager.get_frame_style())
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title label
        title_label = ttk.Label(
            main_frame, 
            text="Export Analysis Data", 
            style=self.theme_manager.get_label_style("header")
        )
        title_label.pack(fill=tk.X, pady=(0, 8))
        
        # Create sections
        self._create_export_type_section(main_frame)
        self._create_data_source_section(main_frame)  # New: integrated data selection
        self._create_format_section(main_frame)
        self._create_image_section(main_frame)
        self._create_filename_section(main_frame)
        self._create_directory_section(main_frame)
        self._create_button_section(main_frame)
        
    def _create_export_type_section(self, parent) -> None:
        """
        Create the analysis type selection section with interactive buttons.
        
        Builds buttons for selecting the type of analysis data to export
        (histogram or pixel profile). Buttons use visual feedback to show
        the current selection state and include helpful tooltips.
        
        Args:
            parent: The parent tkinter widget to contain this section.
        
        Returns:
            None: Creates UI components as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> main_frame = ttk.Frame(dialog.dialog)
            >>> dialog._create_export_type_section(main_frame)
            >>> # Section created with histogram and profile buttons
            
        Performance:
            Time Complexity: O(1) - Fixed number of button widgets created.
            Space Complexity: O(1) - Fixed memory for button references and tooltips.
        """
        # Section frame
        section_frame = ttk.LabelFrame(
            parent, 
            text="Analysis Type", 
            style=self.theme_manager.get_frame_style()
        )
        section_frame.pack(fill=tk.X, padx=12, pady=6)
        
        # Container for buttons with proper spacing
        button_container = ttk.Frame(section_frame, style=self.theme_manager.get_frame_style())
        button_container.pack(fill=tk.X, padx=8, pady=6)
        
        # Configure grid for 2 equal columns
        button_container.columnconfigure(0, weight=1)
        button_container.columnconfigure(1, weight=1)
        
        # Store button references for styling
        self.type_buttons = {}
        
        # Create buttons using ttk.Button with primary blue style
        histogram_btn = ttk.Button(
            button_container,
            text="📊 Histogram",
            command=lambda: self._select_type("histogram"),
            style=self.theme_manager.get_button_style("primary")
        )
        histogram_btn.grid(row=0, column=0, padx=3, pady=2, sticky="ew")
        self.type_buttons["histogram"] = histogram_btn
        self.theme_manager.create_tooltip(histogram_btn, "Export histogram data for full image, ROIs, or polygons")
        
        profile_btn = ttk.Button(
            button_container,
            text="📈 Pixel Profile", 
            command=lambda: self._select_type("profile"),
            style=self.theme_manager.get_button_style("primary")
        )
        profile_btn.grid(row=0, column=1, padx=3, pady=2, sticky="ew")
        self.type_buttons["profile"] = profile_btn
        self.theme_manager.create_tooltip(profile_btn, "Export pixel profile data for drawn lines")
        
        # Set initial selection
        self._update_type_selection()
        
    def _create_data_source_section(self, parent) -> None:
        """
        Create the data source selection section with dynamic content.
        
        Builds a section that dynamically updates based on the selected analysis
        type, showing appropriate data source options (full image, ROIs, polygons,
        or lines) depending on what's available in the viewer.
        
        Args:
            parent: The parent tkinter widget to contain this section.
        
        Returns:
            None: Creates UI components as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> main_frame = ttk.Frame(dialog.dialog)
            >>> dialog._create_data_source_section(main_frame)
            >>> # Data source section created, will be populated when type selected
            
        Performance:
            Time Complexity: O(1) - Creates fixed container structure.
            Space Complexity: O(1) - Fixed memory for frame and container widgets.
        """
        # Section frame
        self.data_source_frame = ttk.LabelFrame(
            parent, 
            text="Data Source", 
            style=self.theme_manager.get_frame_style()
        )
        self.data_source_frame.pack(fill=tk.X, padx=12, pady=6)
        
        # Container for dropdown and info
        self.data_source_container = ttk.Frame(
            self.data_source_frame, 
            style=self.theme_manager.get_frame_style()
        )
        self.data_source_container.pack(fill=tk.X, padx=8, pady=6)
        
        # Initially empty - will be populated when analysis type is selected
        self._create_placeholder_content()
        
    def _create_placeholder_content(self) -> None:
        """
        Create placeholder content for the data source section.
        
        Displays informational text when no analysis type has been selected,
        guiding the user to make a selection first. Clears any existing content
        and creates a styled instructional message.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates UI components as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog._create_placeholder_content()
            >>> # Placeholder label created with instruction text
            
        Performance:
            Time Complexity: O(k) where k is number of existing widgets to clear.
            Space Complexity: O(1) - Single label widget created.
        """
        # Clear existing content
        for widget in self.data_source_container.winfo_children():
            widget.destroy()
        
        placeholder_label = tk.Label(
            self.data_source_container,
            text="Select an Analysis Type above to see available data sources",
            fg='#666666',
            bg=self.theme_manager.theme.get('frame_bg', '#ffffff'),
            font=('TkDefaultFont', 9, 'italic')
        )
        placeholder_label.pack(pady=20)
        
    def _update_data_source_section(self) -> None:
        """
        Update data source options based on the currently selected analysis type.
        
        Dynamically rebuilds the data source selection interface based on the
        chosen analysis type, showing relevant options and hiding irrelevant ones.
        Calls appropriate section builders for histogram or profile types.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates UI components as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog.export_type.set('histogram')
            >>> dialog._update_data_source_section()
            >>> # Data source section rebuilt for histogram options
            
        Performance:
            Time Complexity: O(k) where k is number of widgets to clear and recreate.
            Space Complexity: O(1) - Fixed memory for new widget set.
        """
        analysis_type = self.export_type.get()
        
        if not analysis_type:
            self._create_placeholder_content()
            return
            
        # Clear existing content
        for widget in self.data_source_container.winfo_children():
            widget.destroy()
        
        # Reset data source selection
        self.data_source.set("")
        
        if analysis_type == "histogram":
            self._create_histogram_data_sources()
        elif analysis_type == "profile":
            self._create_profile_data_sources()
            
    def _create_histogram_data_sources(self) -> None:
        """
        Create data source selection interface for histogram analysis.
        
        Builds a dropdown showing available histogram data sources including
        full image, drawn ROIs, and drawn polygons. Provides detailed information
        about each option and shows warnings if no ROIs or polygons are available.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates UI components as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog._create_histogram_data_sources()
            >>> # Dropdown created with available histogram data sources
            
        Performance:
            Time Complexity: O(n) where n is number of ROIs + polygons for dropdown.
            Space Complexity: O(n) - Memory for dropdown options and widgets.
        """
        # Create dropdown label and combobox
        dropdown_frame = ttk.Frame(self.data_source_container, style=self.theme_manager.get_frame_style())
        dropdown_frame.pack(fill='x', pady=(0, 5))
        
        label = ttk.Label(dropdown_frame, text="Select data source:", style=self.theme_manager.get_label_style())
        label.pack(anchor='w', pady=(0, 3))
        
        # Create dropdown options
        options = []
        
        # Always add full image option
        options.append(f"🖼️ Full Image ({self._get_image_dimensions()})")
        
        # Add ROI options if available
        if self.viewer and hasattr(self.viewer, 'mouse') and len(self.viewer.mouse.draw_rects) > 0:
            for i, roi in enumerate(self.viewer.mouse.draw_rects):
                x, y, w, h = roi
                options.append(f"📦 ROI {i+1}: Rectangle {w}×{h} at ({x},{y})")
        
        # Add polygon options if available  
        if self.viewer and hasattr(self.viewer, 'mouse') and len(self.viewer.mouse.draw_polygons) > 0:
            for i, polygon in enumerate(self.viewer.mouse.draw_polygons):
                points_count = len(polygon)
                options.append(f"🔺 Polygon {i+1}: Shape with {points_count} points")
        
        # Create the dropdown - use regular ttk.Combobox to avoid text overlap with indicator
        self.data_source_combo = ttk.Combobox(
            dropdown_frame,
            textvariable=self.data_source,
            state="readonly",
            height=8,
            style=self.theme_manager.get_combobox_style(enhanced=True)
        )
        self.data_source_combo['values'] = options
        self.data_source_combo.pack(fill='x', pady=2)
        self.data_source_combo.bind('<<ComboboxSelected>>', self._on_data_source_select)
        
        # Bind dropdown events for dynamic resizing
        self._bind_dropdown_resize_events(self.data_source_combo)
        
        # Set default selection (first option)
        if options:
            self.data_source_combo.current(0)
            self.data_source.set(self._get_value_from_display_text(options[0]))
        
        # Show info about capabilities
        info_label = tk.Label(
            self.data_source_container,
            text="💡 Histogram can analyze full image, ROIs (rectangles), or polygons (any shape)",
            fg='#0066cc',
            bg=self.theme_manager.theme.get('frame_bg', '#ffffff'),
            font=('TkDefaultFont', 8)
        )
        info_label.pack(anchor='w', pady=(5, 0))
        
        # Show warning if no ROIs/polygons
        if len(options) == 1:  # Only full image
            warning_label = tk.Label(
                self.data_source_container,
                text="⚠️ No ROIs or polygons drawn - only full image analysis available",
                fg='#ff8800',
                bg=self.theme_manager.theme.get('frame_bg', '#ffffff'),
                font=('TkDefaultFont', 8)
            )
            warning_label.pack(anchor='w', pady=(3, 0))
        
    def _create_profile_data_sources(self) -> None:
        """
        Create data source selection interface for pixel profile analysis.
        
        Builds a dropdown showing available line profiles for export, or displays
        an error message if no lines have been drawn. Includes options for individual
        lines or all lines if multiple are available.
        
        Side Effects:
            - Creates dropdown with line profile options or error message
            - Sets up event bindings for selection handling
            - Shows informational messages about pixel profiles
            - Sets default selection if lines are available
        """
        # Create dropdown label and combobox
        dropdown_frame = ttk.Frame(self.data_source_container, style=self.theme_manager.get_frame_style())
        dropdown_frame.pack(fill='x', pady=(0, 5))
        
        label = ttk.Label(dropdown_frame, text="Select line profile:", style=self.theme_manager.get_label_style())
        label.pack(anchor='w', pady=(0, 3))
        
        # Check if lines are available
        if not (self.viewer and hasattr(self.viewer, 'mouse') and len(self.viewer.mouse.draw_lines) > 0):
            # No lines available - show error message
            error_label = tk.Label(
                self.data_source_container,
                text="❌ No line profiles available\n\nTo create line profiles:\n1. Switch to Line Mode in Analysis Controls\n2. Draw lines on the image\n3. Return here to export",
                fg='#cc0000',
                bg=self.theme_manager.theme.get('frame_bg', '#ffffff'),
                font=('TkDefaultFont', 9),
                justify='left'
            )
            error_label.pack(anchor='w', pady=10)
            return
        
        # Create dropdown options
        options = []
        
        # Add "all lines" option if multiple lines exist
        if len(self.viewer.mouse.draw_lines) > 1:
            options.append(f"📏 All Lines: Export all {len(self.viewer.mouse.draw_lines)} line profiles")
        
        # Add individual line options
        for i, line in enumerate(self.viewer.mouse.draw_lines):
            x1, y1, x2, y2 = line  # Line is stored as (x1, y1, x2, y2)
            length = int(((x2 - x1)**2 + (y2 - y1)**2)**0.5)
            options.append(f"📏 Line {i+1}: From ({x1},{y1}) to ({x2},{y2}), length: {length}px")
        
        # Create the dropdown - use regular ttk.Combobox to avoid text overlap with indicator
        self.data_source_combo = ttk.Combobox(
            dropdown_frame,
            textvariable=self.data_source,
            state="readonly",
            height=8,
            style=self.theme_manager.get_combobox_style(enhanced=True)
        )
        self.data_source_combo['values'] = options
        self.data_source_combo.pack(fill='x', pady=2)
        self.data_source_combo.bind('<<ComboboxSelected>>', self._on_data_source_select)
        
        # Bind dropdown events for dynamic resizing
        self._bind_dropdown_resize_events(self.data_source_combo)
        
        # Set default selection (first option)
        if options:
            self.data_source_combo.current(0)
            self.data_source.set(self._get_value_from_display_text(options[0]))
        
        # Show info about pixel profiles
        info_label = tk.Label(
            self.data_source_container,
            text="💡 Pixel profiles show intensity values along drawn lines",
            fg='#0066cc',
            bg=self.theme_manager.theme.get('frame_bg', '#ffffff'),
            font=('TkDefaultFont', 8)
        )
        info_label.pack(anchor='w', pady=(5, 0))
        
    def _get_value_from_display_text(self, display_text: str) -> str:
        """
        Convert user-friendly display text to internal data source identifiers.
        
        Translates the descriptive text shown in dropdowns to standardized
        internal identifiers used by the export backend. Handles all data source
        types including full image, ROIs, polygons, and line profiles.
        
        Args:
            display_text (str): The user-friendly text from the dropdown selection.
                Examples: "🖼️ Full Image", "📦 ROI 1: (10,10)-(50,50)", "📏 Line 1: From (0,0)..."
        
        Returns:
            str: Internal identifier for the data source. Format examples:
                - 'full_image' for full image analysis
                - 'roi_0', 'roi_1' for individual ROIs (zero-indexed)
                - 'polygon_0', 'polygon_1' for polygons (zero-indexed)
                - 'line_0', 'line_1' for individual lines (zero-indexed)
                - 'all_lines' for combined line profile export
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> result = dialog._get_value_from_display_text("📦 ROI 1: (10,10)-(50,50)")
            >>> print(result)  # "roi_0"
            >>> result = dialog._get_value_from_display_text("🖼️ Full Image: Complete histogram")
            >>> print(result)  # "full_image"
            
        Performance:
            Time Complexity: O(1) - String parsing with fixed operations.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if display_text.startswith("🖼️ Full Image"):
            return "full_image"
        elif display_text.startswith("📦 ROI"):
            # Extract ROI number (e.g., "📦 ROI 1:" -> "roi_0")
            roi_num = int(display_text.split("ROI ")[1].split(":")[0])
            return f"roi_{roi_num - 1}"
        elif display_text.startswith("🔺 Polygon"):
            # Extract polygon number (e.g., "🔺 Polygon 1:" -> "polygon_0") 
            poly_num = int(display_text.split("Polygon ")[1].split(":")[0])
            return f"polygon_{poly_num - 1}"
        elif display_text.startswith("📏 All Lines"):
            return "all_lines"
        elif display_text.startswith("📏 Line"):
            # Extract line number (e.g., "📏 Line 1:" -> "line_0")
            line_num = int(display_text.split("Line ")[1].split(":")[0])
            return f"line_{line_num - 1}"
        else:
            # Fallback - return display text as-is
            return display_text
    
    def _bind_dropdown_resize_events(self, dropdown_widget) -> None:
        """
        Bind events to handle dynamic dialog resizing for dropdown interactions.
        
        Sets up event handlers to automatically expand the dialog when dropdowns
        open (to accommodate long option lists) and restore the original size
        when dropdowns close.
        
        Args:
            dropdown_widget: The combobox widget to bind resize events to.
        
        Side Effects:
            - Binds multiple event handlers to the dropdown widget
            - May modify dialog geometry during dropdown interactions
        """
        try:
            # Store original dialog height for restoration
            if not hasattr(self, '_original_dialog_height'):
                self._original_dialog_height = 620  # Current height
            
            def on_dropdown_open(event=None):
                """Handle dropdown opening - expand dialog if needed."""
                try:
                    # Get the dropdown widget position and estimated dropdown height
                    dropdown_values = dropdown_widget['values']
                    if dropdown_values:
                        # Calculate needed extra space (roughly 25px per item + padding)
                        # For regular ttk.Combobox, use height attribute or default to 8
                        max_items = min(len(dropdown_values), getattr(dropdown_widget, 'max_dropdown_items', dropdown_widget['height']))
                        dropdown_height = max_items * 25 + 20  # 25px per item + padding
                        
                        # Get current dialog geometry
                        geometry = self.dialog.geometry()
                        # Format is "widthxheight+x+y" or "widthxheight-x-y"
                        size_part = geometry.split('+')[0].split('-')[0]  # Get just "widthxheight"
                        current_width, current_height = map(int, size_part.split('x'))
                        
                        # Calculate if we need more space (dropdown position + dropdown height vs dialog height)
                        dropdown_y = dropdown_widget.winfo_rooty() - self.dialog.winfo_rooty()
                        needed_height = dropdown_y + dropdown_widget.winfo_height() + dropdown_height + 50  # extra padding
                        
                        if needed_height > current_height:
                            # Expand dialog to accommodate dropdown
                            new_height = min(needed_height, 900)  # Cap at 900px
                            self.dialog.geometry(f"{current_width}x{new_height}")
                except Exception as e:
                    print(f"Error in dropdown open handler: {e}")
            
            def on_dropdown_close(event=None):
                """Handle dropdown closing - restore original dialog size."""
                try:
                    # Restore original height after a brief delay to avoid flicker
                    self.dialog.after(100, lambda: self._restore_dialog_size())
                except Exception as e:
                    print(f"Error in dropdown close handler: {e}")
            
            # Bind to various events that indicate dropdown interaction
            dropdown_widget.bind('<Button-1>', on_dropdown_open)  # Click to open
            dropdown_widget.bind('<Down>', on_dropdown_open)  # Arrow key to open
            dropdown_widget.bind('<space>', on_dropdown_open)  # Space to open
            dropdown_widget.bind('<<ComboboxSelected>>', on_dropdown_close)  # Selection made
            dropdown_widget.bind('<Escape>', on_dropdown_close)  # Escape pressed
            dropdown_widget.bind('<FocusOut>', on_dropdown_close)  # Lost focus
            
        except Exception as e:
            print(f"Error binding dropdown resize events: {e}")
    
    def _restore_dialog_size(self) -> None:
        """
        Restore the dialog to its original size after dropdown interaction.
        
        Returns the dialog window to its standard size after it may have been
        expanded to accommodate dropdown content. Uses stored original height
        to ensure consistent dialog appearance.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Modifies dialog geometry as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog._original_dialog_height = 620
            >>> dialog._restore_dialog_size()
            >>> # Dialog restored to original 620px height
            
        Performance:
            Time Complexity: O(1) - Simple geometry update operation.
            Space Complexity: O(1) - No additional memory allocation.
        """
        try:
            if hasattr(self, '_original_dialog_height'):
                geometry = self.dialog.geometry()
                # Format is "widthxheight+x+y" or "widthxheight-x-y"
                size_part = geometry.split('+')[0].split('-')[0]  # Get just "widthxheight"
                current_width = size_part.split('x')[0]
                self.dialog.geometry(f"{current_width}x{self._original_dialog_height}")
        except Exception as e:
            print(f"Error restoring dialog size: {e}")
                
    def _on_data_source_select(self, event=None) -> None:
        """
        Handle data source selection changes from the dropdown.
        
        Processes user selection of data sources, converts display text to internal
        identifiers, and updates the filename preview accordingly. Handles both
        programmatic and user-initiated selection events.
        
        Args:
            event (Optional): The tkinter ComboboxSelected event. None for programmatic calls.
        
        Returns:
            None: Updates dialog state as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> # User selects "ROI 1" from dropdown
            >>> dialog._on_data_source_select()  # Called automatically
            >>> print(dialog.data_source.get())  # "roi_0"
            
        Performance:
            Time Complexity: O(1) - Simple string processing and variable updates.
            Space Complexity: O(1) - No additional memory allocation.
        """
        # Get the selected display text from the dropdown
        if hasattr(self, 'data_source_combo'):
            selected_display = self.data_source_combo.get()
            if selected_display:
                # Convert display text to internal value
                internal_value = self._get_value_from_display_text(selected_display)
                self.data_source.set(internal_value)
        
        # Update filename preview if needed
        self._update_filename_preview()
        
    def _get_image_dimensions(self) -> str:
        """
        Get the current image dimensions for display in the interface.
        
        Retrieves the width and height of the currently selected image from
        the viewer for display in data source descriptions. Handles cases where
        viewer or image data may not be available.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            str: Formatted dimensions string (e.g., "1920×1080") or "unknown size"
                if dimensions cannot be determined.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog.viewer = image_viewer_instance
            >>> dims = dialog._get_image_dimensions()
            >>> print(dims)  # "1280×720" or "unknown size"
            
        Performance:
            Time Complexity: O(1) - Simple array access and formatting.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if self.viewer and hasattr(self.viewer, '_internal_images') and self.viewer._internal_images:
            current_idx = self.viewer.trackbar.parameters.get('show', 0) if hasattr(self.viewer, 'trackbar') else 0
            if current_idx < len(self.viewer._internal_images):
                image, _ = self.viewer._internal_images[current_idx]
                if image is not None:
                    h, w = image.shape[:2]
                    return f"{w}×{h}"
        return "unknown size"
    
    def _select_type(self, type_name: str) -> None:
        """
        Handle analysis type selection and update the interface accordingly.
        
        Updates the selected analysis type and triggers updates to button styling
        and data source options. Serves as the primary handler for type selection
        from the user interface buttons.
        
        Args:
            type_name (str): The selected analysis type. Must be one of:
                - 'histogram': For intensity distribution analysis
                - 'profile': For pixel profile analysis along lines
        
        Returns:
            None: Updates dialog state as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog._select_type('histogram')
            >>> print(dialog.export_type.get())  # "histogram"
            >>> # Button styling and data source options updated automatically
            
        Performance:
            Time Complexity: O(1) - Simple variable updates and method calls.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self.export_type.set(type_name)
        self._update_type_selection()
        self._update_data_source_section()  # Update data source options
        
    def _update_type_selection(self) -> None:
        """
        Update the visual selection state of analysis type buttons.
        
        Applies appropriate styling to show which analysis type is currently
        selected, using active styling for selected buttons and default styling
        for unselected ones. Provides clear visual feedback for user selections.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates button styling as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog.export_type.set('histogram')
            >>> dialog._update_type_selection()
            >>> # Histogram button now shows active style, others show default
            
        Performance:
            Time Complexity: O(n) where n is number of type buttons (typically 2).
            Space Complexity: O(1) - No additional memory allocation.
        """
        current_type = self.export_type.get()
        for type_name, button in self.type_buttons.items():
            if current_type and type_name == current_type:
                # Selected style - active green style
                button.config(style=self.theme_manager.get_button_style("active"))
            else:
                # Unselected style - primary blue style
                button.config(style=self.theme_manager.get_button_style("primary"))
        
    def _create_format_section(self, parent) -> None:
        """
        Create the export format selection section with interactive buttons.
        
        Builds buttons for selecting the export format (JSON or CSV) with
        tooltips explaining the benefits of each format. Provides clear visual
        feedback for format selection state.
        
        Args:
            parent: The parent tkinter widget to contain this section.
        
        Returns:
            None: Creates UI components as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> main_frame = ttk.Frame(dialog.dialog)
            >>> dialog._create_format_section(main_frame)
            >>> # Format section created with JSON and CSV buttons
            
        Performance:
            Time Complexity: O(1) - Fixed number of button widgets created.
            Space Complexity: O(1) - Fixed memory for button references and tooltips.
        """
        # Section frame
        section_frame = ttk.LabelFrame(
            parent, 
            text="Export Format", 
            style=self.theme_manager.get_frame_style()
        )
        section_frame.pack(fill=tk.X, padx=12, pady=6)
        
        # Container for buttons
        button_container = ttk.Frame(section_frame, style=self.theme_manager.get_frame_style())
        button_container.pack(fill=tk.X, padx=8, pady=6)
        
        # Configure grid for 2 equal columns
        button_container.columnconfigure(0, weight=1)
        button_container.columnconfigure(1, weight=1)
        
        # Store button references for styling
        self.format_buttons = {}
        
        # JSON button
        json_btn = ttk.Button(
            button_container,
            text="📄 JSON",
            command=lambda: self._select_format("json"),
            style=self.theme_manager.get_button_style("primary")
        )
        json_btn.grid(row=0, column=0, padx=3, pady=2, sticky="ew")
        self.format_buttons["json"] = json_btn
        self.theme_manager.create_tooltip(json_btn, "Export as JSON format (better for complex data)")
        
        # CSV button
        csv_btn = ttk.Button(
            button_container,
            text="📊 CSV",
            command=lambda: self._select_format("csv"),
            style=self.theme_manager.get_button_style("primary")
        )
        csv_btn.grid(row=0, column=1, padx=3, pady=2, sticky="ew")
        self.format_buttons["csv"] = csv_btn
        self.theme_manager.create_tooltip(csv_btn, "Export as CSV format (better for spreadsheet compatibility)")
        
        # Set initial selection
        self._update_format_selection()
    
    def _select_format(self, format_name: str) -> None:
        """
        Handle export format selection and update the interface accordingly.
        
        Updates the selected export format, deselects image export option if
        a data format is chosen, and updates visual styling. Ensures mutually
        exclusive selection between data formats and image export.
        
        Args:
            format_name (str): The selected format. Must be one of:
                - 'json': JavaScript Object Notation format
                - 'csv': Comma-Separated Values format
        
        Returns:
            None: Updates dialog state as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog._select_format('json')
            >>> print(dialog.export_format.get())  # "json"
            >>> print(dialog.export_as_image.get())  # False (auto-deselected)
            
        Performance:
            Time Complexity: O(1) - Simple variable updates and method calls.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self.export_format.set(format_name)
        # When selecting a format, deselect PNG image option
        self.export_as_image.set(False)
        self._update_format_selection()
        self._update_image_selection()
        
    def _update_format_selection(self) -> None:
        """
        Update the visual selection state of export format buttons.
        
        Applies appropriate styling to show which export format is currently
        selected, using active styling for selected buttons and default styling
        for unselected ones. Provides clear visual feedback for format choices.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates button styling as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog.export_format.set('csv')
            >>> dialog._update_format_selection()
            >>> # CSV button now shows active style, JSON shows default
            
        Performance:
            Time Complexity: O(n) where n is number of format buttons (typically 2).
            Space Complexity: O(1) - No additional memory allocation.
        """
        current_format = self.export_format.get()
        for format_name, button in self.format_buttons.items():
            if current_format and format_name == current_format:
                # Selected style - active green style
                button.config(style=self.theme_manager.get_button_style("active"))
            else:
                # Unselected style - primary blue style
                button.config(style=self.theme_manager.get_button_style("primary"))
        
    def _create_image_section(self, parent) -> None:
        """
        Create the image export option section with toggle functionality.
        
        Builds a section for toggling PNG image export, which saves plot
        visualizations instead of raw data. Includes explanatory text about
        the difference between image and data export formats.
        
        Args:
            parent: The parent tkinter widget to contain this section.
        
        Returns:
            None: Creates UI components as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> main_frame = ttk.Frame(dialog.dialog)
            >>> dialog._create_image_section(main_frame)
            >>> # Image export section created with PNG toggle button
            
        Performance:
            Time Complexity: O(1) - Fixed UI widget creation.
            Space Complexity: O(1) - Fixed memory for button and text widgets.
        """
        # Section frame
        section_frame = ttk.LabelFrame(
            parent, 
            text="Export Options", 
            style=self.theme_manager.get_frame_style()
        )
        section_frame.pack(fill=tk.X, padx=12, pady=6)
        
        # Container for checkbox button
        button_container = ttk.Frame(section_frame, style=self.theme_manager.get_frame_style())
        button_container.pack(fill=tk.X, padx=8, pady=6)
        
        # Store button reference for styling
        self.image_button = ttk.Button(
            button_container,
            text="💾 Save as PNG Image",
            command=self._toggle_image_export,
            style=self.theme_manager.get_button_style("primary")
        )
        self.image_button.pack(fill='x', pady=2)
        self.theme_manager.create_tooltip(self.image_button, "Save the plot visualization as a high-quality PNG image")
        
        # Note label
        note_label = tk.Label(
            section_frame,
            text="💡 Image export saves the plot visualization, data export saves the raw numbers",
            font=('TkDefaultFont', 8),
            bg='#f8f9fa',
            fg='#666666'
        )
        note_label.pack(anchor=tk.CENTER, pady=(1, 3))
        
        # Set initial selection
        self._update_image_selection()
    
    def _toggle_image_export(self) -> None:
        """
        Toggle the image export option and update the interface accordingly.
        
        Toggles the PNG image export option, deselects data format options if
        image export is enabled, and updates visual styling. Ensures mutually
        exclusive behavior between image and data format exports.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates dialog state as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog.export_as_image.set(False)
            >>> dialog._toggle_image_export()
            >>> print(dialog.export_as_image.get())  # True
            >>> print(dialog.export_format.get())  # "" (cleared)
            
        Performance:
            Time Complexity: O(1) - Simple boolean toggle and method calls.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self.export_as_image.set(not self.export_as_image.get())
        # When selecting PNG image, deselect any export format
        if self.export_as_image.get():
            self.export_format.set("")
            self._update_format_selection()
        self._update_image_selection()
        
    def _update_image_selection(self) -> None:
        """
        Update the visual selection state of the image export button.
        
        Applies appropriate styling to show whether image export is currently
        enabled, using active styling when selected and default styling when not.
        Provides clear visual feedback for image export selection state.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates button styling as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog.export_as_image.set(True)
            >>> dialog._update_image_selection()
            >>> # Image button now shows active green style
            
        Performance:
            Time Complexity: O(1) - Simple conditional styling update.
            Space Complexity: O(1) - No additional memory allocation.
        """
        is_selected = self.export_as_image.get()
        if is_selected:
            # Selected style - active green style
            self.image_button.config(style=self.theme_manager.get_button_style("active"))
        else:
            # Unselected style - primary blue style
            self.image_button.config(style=self.theme_manager.get_button_style("primary"))
        
    def _create_filename_section(self, parent) -> None:
        """
        Create the filename customization section with preview functionality.
        
        Builds input fields for filename prefix customization and displays a
        real-time preview of the final filename based on current selections.
        Includes automatic filename generation based on export type and data source.
        
        Args:
            parent: The parent tkinter widget to contain this section.
        
        Returns:
            None: Creates UI components as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> main_frame = ttk.Frame(dialog.dialog)
            >>> dialog._create_filename_section(main_frame)
            >>> # Filename section created with prefix input and preview
            
        Performance:
            Time Complexity: O(1) - Fixed UI widget creation.
            Space Complexity: O(1) - Fixed memory for entry and preview widgets.
        """
        # Section frame
        section_frame = ttk.LabelFrame(
            parent, 
            text="Filename", 
            style=self.theme_manager.get_frame_style()
        )
        section_frame.pack(fill=tk.X, padx=12, pady=6)
        
        # Filename prefix
        prefix_frame = tk.Frame(section_frame, bg='#f8f9fa')
        prefix_frame.pack(fill=tk.X, padx=8, pady=4)
        
        prefix_label = tk.Label(
            prefix_frame, 
            text="Prefix:",
            bg='#f8f9fa',
            fg='#333333',
            font=('TkDefaultFont', 9)
        )
        prefix_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Use tk.Entry instead of ttk.Entry for better color control
        prefix_entry = tk.Entry(
            prefix_frame, 
            textvariable=self.filename_prefix,
            bg='white',
            fg='#333333',
            insertbackground='#333333',  # Cursor color
            selectbackground='#007bff',  # Selection highlight
            selectforeground='white',    # Selected text color
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#007bff',    # Focus border color
            highlightbackground='#ddd',  # Unfocused border color
            font=('TkDefaultFont', 9)
        )
        prefix_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.theme_manager.create_tooltip(prefix_entry, "Prefix for the exported filename")
        
        # Preview
        preview_frame = tk.Frame(section_frame, bg='#f8f9fa')
        preview_frame.pack(fill=tk.X, padx=8, pady=(2, 4))
        
        preview_label = tk.Label(
            preview_frame, 
            text="Preview:",
            bg='#f8f9fa',
            fg='#333333',
            font=('TkDefaultFont', 9)
        )
        preview_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.preview_var = tk.StringVar()
        self._update_filename_preview()
        
        preview_value = tk.Label(
            preview_frame, 
            textvariable=self.preview_var,
            bg='#f8f9fa',
            fg='#666666',
            font=('TkDefaultFont', 9, 'italic')
        )
        preview_value.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Update preview when values change
        self.export_type.trace_add("write", lambda *args: self._update_all())
        self.export_format.trace_add("write", lambda *args: self._update_all())
        self.export_as_image.trace_add("write", lambda *args: self._update_all())
        self.filename_prefix.trace_add("write", lambda *args: self._update_filename_preview())
        
    def _update_filename_preview(self) -> None:
        """
        Update the filename preview based on current selections.
        
        Generates and displays a preview of the final filename based on the
        current prefix, analysis type, and export format selections. Automatically
        determines appropriate file extension based on export type.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates preview display as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog.filename_prefix.set("analysis")
            >>> dialog.export_type.set("histogram")
            >>> dialog.export_format.set("json")
            >>> dialog._update_filename_preview()
            >>> print(dialog.preview_var.get())  # "analysis_histogram.json"
            
        Performance:
            Time Complexity: O(1) - Simple string operations and variable access.
            Space Complexity: O(1) - No additional memory allocation.
        """
        prefix = self.filename_prefix.get().strip()
        export_type = self.export_type.get()
        export_format = self.export_format.get()
        is_image = self.export_as_image.get()
        
        # Choose file extension based on export type
        if is_image:
            extension = "png"
        else:
            extension = export_format
        
        if prefix:
            filename = f"{prefix}_{export_type}.{extension}"
        else:
            filename = f"{export_type}_export.{extension}"
            
        self.preview_var.set(filename)
    
    def _update_all(self) -> None:
        """
        Update all visual selections and filename preview.
        
        Comprehensive update method that refreshes all button styling states
        and the filename preview to ensure consistency across the interface.
        Called when major dialog state changes occur.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates UI state as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog.export_type.set("histogram")
            >>> dialog._update_all()
            >>> # All button states and filename preview updated consistently
            
        Performance:
            Time Complexity: O(1) - Fixed number of update method calls.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self._update_type_selection()
        self._update_format_selection()
        self._update_image_selection()
        self._update_filename_preview()
        
    def _create_directory_section(self, parent) -> None:
        """
        Create the directory selection section with browse functionality.
        
        Builds an input field for directory selection with a browse button
        that opens a directory selection dialog. Provides clear visual styling
        and user-friendly directory selection interface.
        
        Args:
            parent: The parent tkinter widget to contain this section.
        
        Returns:
            None: Creates UI components as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> main_frame = ttk.Frame(dialog.dialog)
            >>> dialog._create_directory_section(main_frame)
            >>> # Directory section created with input field and browse button
            
        Performance:
            Time Complexity: O(1) - Fixed UI widget creation.
            Space Complexity: O(1) - Fixed memory for entry and button widgets.
        """
        # Section frame
        section_frame = ttk.LabelFrame(
            parent, 
            text="Save Location", 
            style=self.theme_manager.get_frame_style()
        )
        section_frame.pack(fill=tk.X, padx=12, pady=6)
        
        # Directory selection
        dir_frame = tk.Frame(section_frame, bg='#f8f9fa')
        dir_frame.pack(fill=tk.X, padx=8, pady=4)
        
        # Directory label
        dir_label = tk.Label(
            dir_frame,
            text="Directory:",
            bg='#f8f9fa',
            fg='#333333',
            font=('TkDefaultFont', 9)
        )
        dir_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.dir_var = tk.StringVar(value=self.selected_directory)
        # Use tk.Entry instead of ttk.Entry for better color control
        dir_entry = tk.Entry(
            dir_frame, 
            textvariable=self.dir_var,
            bg='white',
            fg='#333333',
            insertbackground='#333333',  # Cursor color
            selectbackground='#007bff',  # Selection highlight
            selectforeground='white',    # Selected text color
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#007bff',    # Focus border color
            highlightbackground='#ddd',  # Unfocused border color
            font=('TkDefaultFont', 9)
        )
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(
            dir_frame, 
            text="Browse...", 
            command=self._browse_directory,
            style=self.theme_manager.get_button_style()
        )
        browse_btn.pack(side=tk.RIGHT)
        
    def _browse_directory(self) -> None:
        """
        Open a directory selection dialog for the user.
        
        Displays a directory browser dialog and updates the directory field
        with the user's selection. Uses the current directory as initial location
        or falls back to user's home directory.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates directory selection as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog._browse_directory()
            >>> # Directory selection dialog opens for user interaction
            >>> # If user selects folder, dialog.selected_directory is updated
            
        Performance:
            Time Complexity: O(1) - Simple dialog operation (blocking).
            Space Complexity: O(1) - No additional memory allocation.
        """
        directory = filedialog.askdirectory(
            initialdir=self.selected_directory if self.selected_directory else os.path.expanduser("~")
        )
        if directory:
            self.dir_var.set(directory)
            self.selected_directory = directory
            
    def _create_button_section(self, parent) -> None:
        """
        Create the action button section with export and cancel options.
        
        Builds the final section containing the export and cancel buttons
        with appropriate styling and tooltips. Buttons are positioned with
        proper spacing and visual hierarchy.
        
        Args:
            parent: The parent tkinter widget to contain this section.
        
        Returns:
            None: Creates UI components as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> main_frame = ttk.Frame(dialog.dialog)
            >>> dialog._create_button_section(main_frame)
            >>> # Export and cancel buttons created with proper styling
            
        Performance:
            Time Complexity: O(1) - Fixed button widget creation.
            Space Complexity: O(1) - Fixed memory for button widgets and tooltips.
        """
        button_frame = ttk.Frame(parent, style=self.theme_manager.get_frame_style())
        button_frame.pack(fill=tk.X, padx=12, pady=(10, 8))
        
        # Store button references for styling
        self.export_btn = ttk.Button(
            button_frame,
            text="📊 Export",
            command=self._on_export_clicked,
            style=self.theme_manager.get_button_style("primary")
        )
        self.export_btn.pack(side=tk.RIGHT, padx=(8, 0))
        self.theme_manager.create_tooltip(self.export_btn, "Execute the export with selected options")
        
        self.cancel_btn = ttk.Button(
            button_frame,
            text="❌ Cancel", 
            command=self._on_cancel_clicked,
            style=self.theme_manager.get_button_style("secondary")
        )
        self.cancel_btn.pack(side=tk.RIGHT, padx=(0, 8))
        self.theme_manager.create_tooltip(self.cancel_btn, "Cancel export and close dialog")
    
    def _on_export_clicked(self) -> None:
        """
        Handle export button click with visual feedback.
        
        Provides immediate visual feedback by changing button styling to show
        user interaction, then schedules the actual export operation after a
        brief delay to ensure smooth UI response.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Schedules export operation as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog._on_export_clicked()
            >>> # Button changes to active style, export scheduled after 150ms
            
        Performance:
            Time Complexity: O(1) - Simple styling update and timer scheduling.
            Space Complexity: O(1) - No additional memory allocation.
        """
        # Change to active green style to show action
        self.export_btn.config(style=self.theme_manager.get_button_style("active"))
        # Schedule the actual export after brief feedback
        self.dialog.after(150, self._on_export)
    
    def _on_cancel_clicked(self) -> None:
        """
        Handle cancel button click with visual feedback.
        
        Provides immediate visual feedback by changing button styling to show
        user interaction, then schedules the actual cancel operation after a
        brief delay to ensure smooth UI response.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Schedules cancel operation as side effect, no return value.
        
        Examples:
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog._on_cancel_clicked()
            >>> # Button changes to active style, cancel scheduled after 150ms
            
        Performance:
            Time Complexity: O(1) - Simple styling update and timer scheduling.
            Space Complexity: O(1) - No additional memory allocation.
        """
        # Change to active style to show action
        self.cancel_btn.config(style=self.theme_manager.get_button_style("active"))
        # Schedule the actual cancel after brief feedback
        self.dialog.after(150, self._on_cancel)
        
    def _on_export(self) -> None:
        """
        Execute the export operation with validation and callback invocation.
        
        Validates all required selections, saves user settings, constructs the
        full file path, and invokes the export callback with the selected parameters.
        Performs comprehensive validation before attempting export.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Executes export operation as side effect, no return value.
        
        Examples:
            >>> def export_handler(exp_type, format, path, source):
            ...     print(f"Exporting {exp_type} as {format}")
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog.on_export_callback = export_handler
            >>> dialog._on_export()
            >>> # Validates selections and calls export_handler if valid
            
        Performance:
            Time Complexity: O(1) - Validation checks and file path operations.
            Space Complexity: O(1) - No additional memory allocation.
        """
        # Get export parameters
        export_type = self.export_type.get()
        export_format = self.export_format.get()
        is_image = self.export_as_image.get()
        
        # Validate required selections
        if not export_type:
            from tkinter import messagebox
            messagebox.showwarning("Selection Required", "Please select an Analysis Type (Histogram, Pixel Profile, or Polygon).")
            return
            
        data_source = self.data_source.get()
        if not data_source:
            from tkinter import messagebox
            messagebox.showwarning("Selection Required", "Please select a Data Source to export.")
            return
            
        if not is_image and not export_format:
            from tkinter import messagebox
            messagebox.showwarning("Selection Required", "Please select either an Export Format (JSON or CSV) or choose to save as PNG image.")
            return
        
        # Save settings
        self._save_settings()
        
        # Get directory
        directory = self.dir_var.get()
        if not directory or not os.path.exists(directory):
            directory = os.path.expanduser("~")
            
        # Get filename
        prefix = self.filename_prefix.get().strip()
        if prefix:
            filename = f"{prefix}_{export_type}"
        else:
            filename = f"{export_type}_export"
            
        # Choose file extension
        if is_image:
            extension = "png"
            final_format = "image"
        else:
            extension = export_format
            final_format = export_format
            
        # Full path
        full_path = os.path.join(directory, f"{filename}.{extension}")
        
        # Close dialog
        self.dialog.destroy()
        
        # Call export callback if provided
        if self.on_export_callback:
            if is_image:
                self.on_export_callback(export_type, "image", full_path, data_source)
            else:
                self.on_export_callback(export_type, export_format, full_path, data_source)
            
    def _on_cancel(self) -> None:
        """
        Execute the cancel operation and cleanup.
        
        Closes the dialog window and invokes the cancel callback if provided.
        Provides clean cancellation without saving any changes or selections.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Performs cleanup as side effect, no return value.
        
        Examples:
            >>> def cancel_handler():
            ...     print("Export cancelled")
            >>> dialog = EnhancedExportDialog(root, theme_mgr)
            >>> dialog.on_cancel_callback = cancel_handler
            >>> dialog._on_cancel()
            >>> # Dialog closed and cancel_handler called
            
        Performance:
            Time Complexity: O(1) - Simple dialog destruction and callback.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self.dialog.destroy()
        
        # Call cancel callback if provided
        if self.on_cancel_callback:
            self.on_cancel_callback()