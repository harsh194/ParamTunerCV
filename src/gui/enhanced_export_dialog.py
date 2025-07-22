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
        
        # Default values
        self.export_type = tk.StringVar(value=self.settings.get("last_export_type", "histogram"))
        self.export_format = tk.StringVar(value=self.settings.get("last_export_format", "json"))
        self.filename_prefix = tk.StringVar(value="")
        self.selected_directory = self.settings.get("last_directory", "")
        
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
                "recent_directories": [],
                "last_directory": "",
                "last_export_type": "histogram",
                "last_export_format": "json"
            }
        except Exception:
            # If there's any error loading settings, return defaults
            return {
                "recent_directories": [],
                "last_directory": "",
                "last_export_type": "histogram",
                "last_export_format": "json"
            }
            
    def _save_settings(self):
        """Save export settings to config file."""
        try:
            # Update settings with current values
            self.settings["last_export_type"] = self.export_type.get()
            self.settings["last_export_format"] = self.export_format.get()
            
            # Add current directory to recent directories if it exists
            if self.selected_directory and os.path.exists(self.selected_directory):
                self.settings["last_directory"] = self.selected_directory
                
                # Add to recent directories if not already there
                if self.selected_directory not in self.settings["recent_directories"]:
                    self.settings["recent_directories"].insert(0, self.selected_directory)
                    # Keep only the 5 most recent directories
                    self.settings["recent_directories"] = self.settings["recent_directories"][:5]
            
            # Save settings to file
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            # Silently fail if we can't save settings
            pass
            
    def show(self, filename_prefix="", on_export=None, on_cancel=None):
        """
        Show the export dialog.
        
        Args:
            filename_prefix: Default filename prefix
            on_export: Callback function when export is confirmed
            on_cancel: Callback function when export is canceled
        """
        self.filename_prefix.set(filename_prefix)
        self.on_export_callback = on_export
        self.on_cancel_callback = on_cancel
        
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("450x400")
        self.dialog.minsize(400, 350)
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
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title label
        title_label = ttk.Label(
            main_frame, 
            text="Export Analysis Data", 
            style=self.theme_manager.get_label_style("header")
        )
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        # Create sections
        self._create_export_type_section(main_frame)
        self._create_format_section(main_frame)
        self._create_filename_section(main_frame)
        self._create_directory_section(main_frame)
        self._create_button_section(main_frame)
        
    def _create_export_type_section(self, parent):
        """Create the export type selection section."""
        # Section frame
        section_frame = ttk.LabelFrame(
            parent, 
            text="Analysis Type", 
            style=self.theme_manager.get_frame_style()
        )
        section_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Radio buttons for export type
        histogram_radio = ttk.Radiobutton(
            section_frame, 
            text="Histogram", 
            variable=self.export_type, 
            value="histogram"
        )
        histogram_radio.pack(anchor=tk.W, pady=2)
        self.theme_manager.create_tooltip(histogram_radio, "Export histogram data")
        
        profile_radio = ttk.Radiobutton(
            section_frame, 
            text="Pixel Profile", 
            variable=self.export_type, 
            value="profile"
        )
        profile_radio.pack(anchor=tk.W, pady=2)
        self.theme_manager.create_tooltip(profile_radio, "Export pixel profile data")
        
        polygon_radio = ttk.Radiobutton(
            section_frame, 
            text="Polygon", 
            variable=self.export_type, 
            value="polygon"
        )
        polygon_radio.pack(anchor=tk.W, pady=2)
        self.theme_manager.create_tooltip(polygon_radio, "Export polygon coordinates")
        
    def _create_format_section(self, parent):
        """Create the format selection section."""
        # Section frame
        section_frame = ttk.LabelFrame(
            parent, 
            text="Export Format", 
            style=self.theme_manager.get_frame_style()
        )
        section_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Format options
        format_frame = ttk.Frame(section_frame, style=self.theme_manager.get_frame_style())
        format_frame.pack(fill=tk.X)
        
        json_radio = ttk.Radiobutton(
            format_frame, 
            text="JSON", 
            variable=self.export_format, 
            value="json"
        )
        json_radio.pack(side=tk.LEFT, padx=(0, 20))
        self.theme_manager.create_tooltip(json_radio, "Export as JSON format (better for complex data)")
        
        csv_radio = ttk.Radiobutton(
            format_frame, 
            text="CSV", 
            variable=self.export_format, 
            value="csv"
        )
        csv_radio.pack(side=tk.LEFT)
        self.theme_manager.create_tooltip(csv_radio, "Export as CSV format (better for spreadsheet compatibility)")
        
    def _create_filename_section(self, parent):
        """Create the filename section."""
        # Section frame
        section_frame = ttk.LabelFrame(
            parent, 
            text="Filename", 
            style=self.theme_manager.get_frame_style()
        )
        section_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Filename prefix
        prefix_frame = ttk.Frame(section_frame, style=self.theme_manager.get_frame_style())
        prefix_frame.pack(fill=tk.X, pady=2)
        
        prefix_label = ttk.Label(prefix_frame, text="Prefix:")
        prefix_label.pack(side=tk.LEFT, padx=(0, 5))
        
        prefix_entry = ttk.Entry(prefix_frame, textvariable=self.filename_prefix)
        prefix_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.theme_manager.create_tooltip(prefix_entry, "Prefix for the exported filename")
        
        # Preview
        preview_frame = ttk.Frame(section_frame, style=self.theme_manager.get_frame_style())
        preview_frame.pack(fill=tk.X, pady=(5, 0))
        
        preview_label = ttk.Label(preview_frame, text="Preview:")
        preview_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.preview_var = tk.StringVar()
        self._update_filename_preview()
        
        preview_value = ttk.Label(preview_frame, textvariable=self.preview_var)
        preview_value.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Update preview when values change
        self.export_type.trace_add("write", lambda *args: self._update_filename_preview())
        self.export_format.trace_add("write", lambda *args: self._update_filename_preview())
        self.filename_prefix.trace_add("write", lambda *args: self._update_filename_preview())
        
    def _update_filename_preview(self):
        """Update the filename preview."""
        prefix = self.filename_prefix.get().strip()
        export_type = self.export_type.get()
        export_format = self.export_format.get()
        
        if prefix:
            filename = f"{prefix}_{export_type}.{export_format}"
        else:
            filename = f"{export_type}_export.{export_format}"
            
        self.preview_var.set(filename)
        
    def _create_directory_section(self, parent):
        """Create the directory selection section."""
        # Section frame
        section_frame = ttk.LabelFrame(
            parent, 
            text="Save Location", 
            style=self.theme_manager.get_frame_style()
        )
        section_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Directory selection
        dir_frame = ttk.Frame(section_frame, style=self.theme_manager.get_frame_style())
        dir_frame.pack(fill=tk.X, pady=2)
        
        self.dir_var = tk.StringVar(value=self.selected_directory)
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(
            dir_frame, 
            text="Browse...", 
            command=self._browse_directory,
            style=self.theme_manager.get_button_style()
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Recent directories
        if self.settings.get("recent_directories"):
            recent_label = ttk.Label(section_frame, text="Recent Locations:")
            recent_label.pack(anchor=tk.W, pady=(10, 5))
            
            # Create a frame with scrollbar for recent directories
            recent_frame = ttk.Frame(section_frame, style=self.theme_manager.get_frame_style())
            recent_frame.pack(fill=tk.BOTH, expand=True)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(recent_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Create listbox for recent directories
            recent_listbox = tk.Listbox(
                recent_frame,
                height=3,
                selectmode=tk.SINGLE,
                yscrollcommand=scrollbar.set
            )
            recent_listbox.pack(fill=tk.BOTH, expand=True)
            scrollbar.config(command=recent_listbox.yview)
            
            # Add recent directories to listbox
            for directory in self.settings.get("recent_directories", []):
                if os.path.exists(directory):
                    recent_listbox.insert(tk.END, directory)
            
            # Bind selection event
            recent_listbox.bind('<<ListboxSelect>>', lambda e: self._select_recent_directory(recent_listbox))
            
    def _select_recent_directory(self, listbox):
        """Select a directory from the recent directories listbox."""
        selection = listbox.curselection()
        if selection:
            index = selection[0]
            directory = listbox.get(index)
            self.dir_var.set(directory)
            self.selected_directory = directory
            
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
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        cancel_btn = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self._on_cancel,
            style=self.theme_manager.get_button_style()
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        export_btn = ttk.Button(
            button_frame, 
            text="Export", 
            command=self._on_export,
            style=self.theme_manager.get_button_style("primary")
        )
        export_btn.pack(side=tk.RIGHT)
        
    def _on_export(self):
        """Handle export button click."""
        # Save settings
        self._save_settings()
        
        # Get export parameters
        export_type = self.export_type.get()
        export_format = self.export_format.get()
        
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
            
        # Full path
        full_path = os.path.join(directory, f"{filename}.{export_format}")
        
        # Close dialog
        self.dialog.destroy()
        
        # Call export callback if provided
        if self.on_export_callback:
            self.on_export_callback(export_type, export_format, full_path)
            
    def _on_cancel(self):
        """Handle cancel button click."""
        self.dialog.destroy()
        
        # Call cancel callback if provided
        if self.on_cancel_callback:
            self.on_cancel_callback()