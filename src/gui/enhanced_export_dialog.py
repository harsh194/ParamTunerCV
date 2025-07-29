import tkinter as tk
from tkinter import ttk, filedialog
import os
import json
from typing import Dict, Any, List, Optional, Callable

class EnhancedExportDialog:
    """
    Enhanced export dialog with better layout, recent directories and format memory.
    """
    
    CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".parameter_export_settings.json")
    
    def __init__(self, parent, theme_manager, title="Export Analysis Data"):
        """
        Initialize the enhanced export dialog.
        
        Args:
            parent: Parent window
            theme_manager: ThemeManager instance for styling
            title: Dialog title
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
        self.filename_prefix = tk.StringVar(value="")
        self.selected_directory = ""  # Start with no directory selected
        
        # Callback functions
        self.on_export_callback = None
        self.on_cancel_callback = None
        
    def _load_settings(self) -> Dict[str, Any]:
        """Load export settings from config file."""
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
            
    def _save_settings(self):
        """Save export settings to config file."""
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
            
    def show(self, filename_prefix="", on_export=None, on_cancel=None, viewer=None):
        """
        Show the export dialog.
        
        Args:
            filename_prefix: Default filename prefix
            on_export: Callback function when export is confirmed
            on_cancel: Callback function when export is canceled
            viewer: ImageViewer instance to check for available analysis data
        """
        self.filename_prefix.set(filename_prefix)
        self.on_export_callback = on_export
        self.on_cancel_callback = on_cancel
        self.viewer = viewer  # Store viewer reference for data validation
        
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("520x580")
        self.dialog.minsize(500, 560)
        self.dialog.resizable(False, False)
        
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
        
    def _check_data_availability(self, export_type):
        """
        Check if the requested analysis data is available.
        
        Args:
            export_type: Type of export requested ('histogram', 'profile', 'polygon')
            
        Returns:
            tuple: (has_data, warning_message)
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
            
        elif export_type == "polygon":
            # For polygon export, we need drawn polygons
            has_polygons = bool(self.viewer.mouse.draw_polygons)
            if not has_polygons:
                return False, "No polygons available for export.\n\nTo create polygons:\n1. Switch to Polygon Mode in Analysis Controls\n2. Draw polygons on the image\n3. Return here to export the polygon coordinates"
            return True, ""
            
        return True, ""
        
    def _center_on_parent(self):
        """Center the dialog on the parent window."""
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
        
    def _create_dialog_content(self):
        """Create the dialog content."""
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
        self._create_format_section(main_frame)
        self._create_image_section(main_frame)
        self._create_filename_section(main_frame)
        self._create_directory_section(main_frame)
        self._create_button_section(main_frame)
        
    def _create_export_type_section(self, parent):
        """Create the export type selection section with square buttons."""
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
        
        # Configure grid for 3 equal columns
        button_container.columnconfigure(0, weight=1)
        button_container.columnconfigure(1, weight=1) 
        button_container.columnconfigure(2, weight=1)
        
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
        self.theme_manager.create_tooltip(histogram_btn, "Export histogram data")
        
        profile_btn = ttk.Button(
            button_container,
            text="📈 Pixel Profile", 
            command=lambda: self._select_type("profile"),
            style=self.theme_manager.get_button_style("primary")
        )
        profile_btn.grid(row=0, column=1, padx=3, pady=2, sticky="ew")
        self.type_buttons["profile"] = profile_btn
        self.theme_manager.create_tooltip(profile_btn, "Export pixel profile data")
        
        polygon_btn = ttk.Button(
            button_container,
            text="📐 Polygon",
            command=lambda: self._select_type("polygon"),
            style=self.theme_manager.get_button_style("primary")
        )
        polygon_btn.grid(row=0, column=2, padx=3, pady=2, sticky="ew") 
        self.type_buttons["polygon"] = polygon_btn
        self.theme_manager.create_tooltip(polygon_btn, "Export polygon coordinates")
        
        # Set initial selection
        self._update_type_selection()
    
    def _select_type(self, type_name):
        """Handle analysis type selection."""
        self.export_type.set(type_name)
        self._update_type_selection()
        
    def _update_type_selection(self):
        """Update visual selection for analysis type."""
        current_type = self.export_type.get()
        for type_name, button in self.type_buttons.items():
            if current_type and type_name == current_type:
                # Selected style - active green style
                button.config(style=self.theme_manager.get_button_style("active"))
            else:
                # Unselected style - primary blue style
                button.config(style=self.theme_manager.get_button_style("primary"))
        
    def _create_format_section(self, parent):
        """Create the format selection section with square buttons."""
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
    
    def _select_format(self, format_name):
        """Handle export format selection."""
        self.export_format.set(format_name)
        # When selecting a format, deselect PNG image option
        self.export_as_image.set(False)
        self._update_format_selection()
        self._update_image_selection()
        
    def _update_format_selection(self):
        """Update visual selection for export format."""
        current_format = self.export_format.get()
        for format_name, button in self.format_buttons.items():
            if current_format and format_name == current_format:
                # Selected style - active green style
                button.config(style=self.theme_manager.get_button_style("active"))
            else:
                # Unselected style - primary blue style
                button.config(style=self.theme_manager.get_button_style("primary"))
        
    def _create_image_section(self, parent):
        """Create the image export option section with square button."""
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
    
    def _toggle_image_export(self):
        """Toggle image export option."""
        self.export_as_image.set(not self.export_as_image.get())
        # When selecting PNG image, deselect any export format
        if self.export_as_image.get():
            self.export_format.set("")
            self._update_format_selection()
        self._update_image_selection()
        
    def _update_image_selection(self):
        """Update visual selection for image export."""
        is_selected = self.export_as_image.get()
        if is_selected:
            # Selected style - active green style
            self.image_button.config(style=self.theme_manager.get_button_style("active"))
        else:
            # Unselected style - primary blue style
            self.image_button.config(style=self.theme_manager.get_button_style("primary"))
        
    def _create_filename_section(self, parent):
        """Create the filename section."""
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
        
    def _update_filename_preview(self):
        """Update the filename preview."""
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
    
    def _update_all(self):
        """Update all visual selections and filename preview."""
        self._update_type_selection()
        self._update_format_selection()
        self._update_image_selection()
        self._update_filename_preview()
        
    def _create_directory_section(self, parent):
        """Create the directory selection section."""
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
        
    def _browse_directory(self):
        """Browse for a directory."""
        directory = filedialog.askdirectory(
            initialdir=self.selected_directory if self.selected_directory else os.path.expanduser("~")
        )
        if directory:
            self.dir_var.set(directory)
            self.selected_directory = directory
            
    def _create_button_section(self, parent):
        """Create the button section."""
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
    
    def _on_export_clicked(self):
        """Handle export button click with visual feedback."""
        # Change to active green style to show action
        self.export_btn.config(style=self.theme_manager.get_button_style("active"))
        # Schedule the actual export after brief feedback
        self.dialog.after(150, self._on_export)
    
    def _on_cancel_clicked(self):
        """Handle cancel button click with visual feedback."""
        # Change to active style to show action
        self.cancel_btn.config(style=self.theme_manager.get_button_style("active"))
        # Schedule the actual cancel after brief feedback
        self.dialog.after(150, self._on_cancel)
        
    def _on_export(self):
        """Handle export button click."""
        # Get export parameters
        export_type = self.export_type.get()
        export_format = self.export_format.get()
        is_image = self.export_as_image.get()
        
        # Validate required selections
        if not export_type:
            from tkinter import messagebox
            messagebox.showwarning("Selection Required", "Please select an Analysis Type (Histogram, Pixel Profile, or Polygon).")
            return
            
        if not is_image and not export_format:
            from tkinter import messagebox
            messagebox.showwarning("Selection Required", "Please select either an Export Format (JSON or CSV) or choose to save as PNG image.")
            return
            
        # Check if the requested analysis data is available
        has_data, warning_message = self._check_data_availability(export_type)
        
        if not has_data:
            from tkinter import messagebox
            messagebox.showwarning("No Data Available", warning_message)
            return
            
        # Show informational message if there's a warning (but data is still available)
        if warning_message:
            from tkinter import messagebox
            result = messagebox.askquestion("Export Confirmation", 
                                          f"{warning_message}\n\nDo you want to continue with the export?",
                                          icon='question')
            if result != 'yes':
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
                self.on_export_callback(export_type, "image", full_path)
            else:
                self.on_export_callback(export_type, export_format, full_path)
            
    def _on_cancel(self):
        """Handle cancel button click."""
        self.dialog.destroy()
        
        # Call cancel callback if provided
        if self.on_cancel_callback:
            self.on_cancel_callback()