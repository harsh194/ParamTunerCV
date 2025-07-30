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
        self.data_source = tk.StringVar(value="")  # New: which specific data to export
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
        self._create_data_source_section(main_frame)  # New: integrated data selection
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
        
    def _create_data_source_section(self, parent):
        """Create the data source selection section."""
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
        
    def _create_placeholder_content(self):
        """Create placeholder content when no analysis type is selected."""
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
        
    def _update_data_source_section(self):
        """Update data source options based on selected analysis type."""
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
            
    def _create_histogram_data_sources(self):
        """Create data source dropdown for histogram analysis."""
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
        
        # Create the dropdown
        from .enhanced_widgets import ComboboxWithIndicator
        self.data_source_combo = ComboboxWithIndicator(
            dropdown_frame,
            theme_manager=self.theme_manager,
            textvariable=self.data_source,
            state="readonly",
            max_dropdown_items=8
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
        
    def _create_profile_data_sources(self):
        """Create data source dropdown for pixel profile analysis."""
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
        
        # Create the dropdown
        from .enhanced_widgets import ComboboxWithIndicator
        self.data_source_combo = ComboboxWithIndicator(
            dropdown_frame,
            theme_manager=self.theme_manager,
            textvariable=self.data_source,
            state="readonly",
            max_dropdown_items=8
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
        
    def _get_value_from_display_text(self, display_text):
        """Convert display text back to internal value for backend processing."""
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
    
    def _bind_dropdown_resize_events(self, dropdown_widget):
        """Bind events to handle dynamic dialog resizing when dropdown opens/closes."""
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
                        max_items = min(len(dropdown_values), dropdown_widget.max_dropdown_items)
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
    
    def _restore_dialog_size(self):
        """Restore dialog to its original size."""
        try:
            if hasattr(self, '_original_dialog_height'):
                geometry = self.dialog.geometry()
                # Format is "widthxheight+x+y" or "widthxheight-x-y"
                size_part = geometry.split('+')[0].split('-')[0]  # Get just "widthxheight"
                current_width = size_part.split('x')[0]
                self.dialog.geometry(f"{current_width}x{self._original_dialog_height}")
        except Exception as e:
            print(f"Error restoring dialog size: {e}")
                
    def _on_data_source_select(self, event=None):
        """Handle data source selection."""
        # Get the selected display text from the dropdown
        if hasattr(self, 'data_source_combo'):
            selected_display = self.data_source_combo.get()
            if selected_display:
                # Convert display text to internal value
                internal_value = self._get_value_from_display_text(selected_display)
                self.data_source.set(internal_value)
        
        # Update filename preview if needed
        self._update_filename_preview()
        
    def _get_image_dimensions(self):
        """Get current image dimensions for display."""
        if self.viewer and hasattr(self.viewer, '_internal_images') and self.viewer._internal_images:
            current_idx = self.viewer.trackbar.parameters.get('show', 0) if hasattr(self.viewer, 'trackbar') else 0
            if current_idx < len(self.viewer._internal_images):
                image, _ = self.viewer._internal_images[current_idx]
                if image is not None:
                    h, w = image.shape[:2]
                    return f"{w}×{h}"
        return "unknown size"
    
    def _select_type(self, type_name):
        """Handle analysis type selection."""
        self.export_type.set(type_name)
        self._update_type_selection()
        self._update_data_source_section()  # Update data source options
        
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
            
    def _on_cancel(self):
        """Handle cancel button click."""
        self.dialog.destroy()
        
        # Call cancel callback if provided
        if self.on_cancel_callback:
            self.on_cancel_callback()