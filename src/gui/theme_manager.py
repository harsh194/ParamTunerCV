import tkinter as tk
from tkinter import ttk

class ThemeManager:
    """Manages theme and styling for Tkinter interfaces."""

    def __init__(self, use_dark_mode=False):
        self.use_dark_mode = use_dark_mode
        # Theme colors will be set during configure_theme
        self.theme = {}
        # We will call configure_theme when a root window is available
        # to get the style object.
        self._tooltip_windows = {}  # Store tooltip windows

    def configure_theme(self, root):
        """Configure the ttk style with the current theme settings."""
        try:
            style = ttk.Style(root)
            if self.use_dark_mode:
                self._configure_dark_theme(style)
            else:
                self._configure_light_theme(style)
            self.get_root_style(root)
        except Exception as e:
            print(f"Theme configuration error: {e}")
            # Use minimal styling if advanced styling fails

    def _configure_light_theme(self, style):
        """Configure light theme colors and styles."""
        # Colors
        primary_color = "#007bff"
        secondary_color = "#6c757d"
        bg_color = "#f0f0f0"
        fg_color = "#000000"
        frame_bg_color = "#ffffff"
        button_fg_color = "#ffffff"
        button_hover_color = "#0056b3"
        selection_bg_color = "#e2f0ff"
        selection_fg_color = "#000000"
        
        # Store theme colors for later use
        self.theme = {
            'primary': primary_color,
            'secondary': secondary_color,
            'bg': bg_color,
            'fg': fg_color,
            'frame_bg': frame_bg_color,
            'button_fg': button_fg_color,
            'button_hover': button_hover_color,
            'tooltip_bg': '#ffffcc',
            'tooltip_fg': '#000000',
            'tooltip_border': '#999999',
            'selection_bg': selection_bg_color,
            'selection_fg': selection_fg_color,
            'combobox_border': primary_color,
            'combobox_arrow': primary_color
        }

        # Style configurations
        try:
            style.theme_use('default')
        except tk.TclError:
            # A theme is not available, so we can't do much.
            # This can happen in environments without full GUI support.
            return

        style.configure("TFrame", background=frame_bg_color)
        style.configure("TLabel", background=frame_bg_color, foreground=fg_color)
        style.configure("TButton")
        style.map("TButton",
                  foreground=[('!active', button_fg_color)],
                  background=[('!active', primary_color), ('active', button_hover_color)])

        # Configure combobox style
        style.configure("TCombobox", 
                        background=frame_bg_color,
                        foreground=fg_color,
                        fieldbackground=frame_bg_color,
                        selectbackground=selection_bg_color,
                        selectforeground=selection_fg_color,
                        arrowcolor=primary_color,
                        bordercolor=primary_color)
        
        style.map("TCombobox",
                  fieldbackground=[('readonly', frame_bg_color)],
                  selectbackground=[('readonly', selection_bg_color)],
                  selectforeground=[('readonly', selection_fg_color)])
                  
        # Configure enhanced combobox style
        style.configure("Enhanced.TCombobox", 
                        relief="flat",
                        borderwidth=1,
                        background=frame_bg_color,
                        foreground=fg_color,
                        fieldbackground=frame_bg_color,
                        selectbackground=selection_bg_color,
                        selectforeground=selection_fg_color,
                        arrowcolor=primary_color,
                        bordercolor=primary_color)
                        
        style.map("Enhanced.TCombobox",
                  fieldbackground=[('readonly', frame_bg_color)],
                  selectbackground=[('readonly', selection_bg_color)],
                  selectforeground=[('readonly', selection_fg_color)],
                  bordercolor=[('focus', primary_color), ('hover', primary_color)])

        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        style.configure("Primary.TButton")
        style.map("Primary.TButton",
                  foreground=[('!active', button_fg_color)],
                  background=[('!active', primary_color), ('active', button_hover_color)])

        style.configure("Secondary.TButton")
        style.map("Secondary.TButton",
                  foreground=[('!active', button_fg_color)],
                  background=[('!active', secondary_color), ('active', "#5a6268")])

    def _configure_dark_theme(self, style):
        """Configure dark theme colors and styles."""
        # Colors
        primary_color = "#0d6efd"
        secondary_color = "#6c757d"
        bg_color = "#212529"
        fg_color = "#ffffff"
        frame_bg_color = "#343a40"
        button_fg_color = "#ffffff"
        button_hover_color = "#0b5ed7"
        selection_bg_color = "#375a7f"
        selection_fg_color = "#ffffff"
        
        # Store theme colors for later use
        self.theme = {
            'primary': primary_color,
            'secondary': secondary_color,
            'bg': bg_color,
            'fg': fg_color,
            'frame_bg': frame_bg_color,
            'button_fg': button_fg_color,
            'button_hover': button_hover_color,
            'tooltip_bg': '#333333',
            'tooltip_fg': '#ffffff',
            'tooltip_border': '#555555',
            'selection_bg': selection_bg_color,
            'selection_fg': selection_fg_color,
            'combobox_border': primary_color,
            'combobox_arrow': primary_color
        }

        # Style configurations
        try:
            style.theme_use('default')
        except tk.TclError:
            return

        style.configure(".", background=bg_color, foreground=fg_color, fieldbackground=frame_bg_color, bordercolor=secondary_color)
        style.configure("TFrame", background=frame_bg_color)
        style.configure("TLabel", background=frame_bg_color, foreground=fg_color)
        style.configure("TButton")
        style.map("TButton",
                  foreground=[('!active', button_fg_color)],
                  background=[('!active', primary_color), ('active', button_hover_color)])
                  
        # Configure combobox style
        style.configure("TCombobox", 
                        background=frame_bg_color,
                        foreground=fg_color,
                        fieldbackground=frame_bg_color,
                        selectbackground=selection_bg_color,
                        selectforeground=selection_fg_color,
                        arrowcolor=primary_color,
                        bordercolor=primary_color)
        
        style.map("TCombobox",
                  fieldbackground=[('readonly', frame_bg_color)],
                  selectbackground=[('readonly', selection_bg_color)],
                  selectforeground=[('readonly', selection_fg_color)])
                  
        # Configure enhanced combobox style
        style.configure("Enhanced.TCombobox", 
                        relief="flat",
                        borderwidth=1,
                        background=frame_bg_color,
                        foreground=fg_color,
                        fieldbackground=frame_bg_color,
                        selectbackground=selection_bg_color,
                        selectforeground=selection_fg_color,
                        arrowcolor=primary_color,
                        bordercolor=primary_color)
                        
        style.map("Enhanced.TCombobox",
                  fieldbackground=[('readonly', frame_bg_color)],
                  selectbackground=[('readonly', selection_bg_color)],
                  selectforeground=[('readonly', selection_fg_color)],
                  bordercolor=[('focus', primary_color), ('hover', primary_color)])

        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        style.configure("Primary.TButton")
        style.map("Primary.TButton",
                  foreground=[('!active', button_fg_color)],
                  background=[('!active', primary_color), ('active', button_hover_color)])

        style.configure("Secondary.TButton")
        style.map("Secondary.TButton",
                  foreground=[('!active', button_fg_color)],
                  background=[('!active', secondary_color), ('active', "#5a6268")])

    def get_button_style(self, button_type="default"):
        """Get the appropriate button style name based on type."""
        if button_type == "primary":
            return "Primary.TButton"
        if button_type == "secondary":
            return "Secondary.TButton"
        return "TButton"

    def get_frame_style(self, frame_type="default"):
        """Get the appropriate frame style name based on type."""
        return "TFrame"
        
    def get_label_style(self, label_type="default"):
        """Get the appropriate label style name based on type."""
        if label_type == "header":
            return "Header.TLabel"
        return "TLabel"
        
    def get_combobox_style(self, enhanced=True):
        """Get the appropriate combobox style name."""
        if enhanced:
            return "Enhanced.TCombobox"
        return "TCombobox"

    def get_root_style(self, root):
        if self.use_dark_mode:
            root.configure(bg="#212529")
        else:
            root.configure(bg="#f0f0f0")
            
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.use_dark_mode = not self.use_dark_mode
        return self.use_dark_mode
        
    def create_tooltip(self, widget, text, delay=500, duration=5000):
        """
        Create a tooltip for a given widget with specified text.
        
        Args:
            widget: The widget to attach the tooltip to
            text: The tooltip text
            delay: Delay in milliseconds before showing tooltip
            duration: Duration in milliseconds to show tooltip (0 for indefinite)
        """
        # Ensure we don't have multiple tooltips for the same widget
        if widget in self._tooltip_windows:
            return
            
        def enter(event):
            # Schedule tooltip to appear after delay
            widget._tooltip_id = widget.after(delay, lambda: show_tooltip(event))
            
        def leave(event):
            # Cancel scheduled tooltip
            if hasattr(widget, '_tooltip_id'):
                widget.after_cancel(widget._tooltip_id)
                widget._tooltip_id = None
            # Hide tooltip if it's visible
            hide_tooltip()
            
        def show_tooltip(event):
            # Get screen position
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Create tooltip window
            tooltip_window = tk.Toplevel(widget)
            tooltip_window.wm_overrideredirect(True)  # Remove window decorations
            tooltip_window.wm_geometry(f"+{x}+{y}")
            
            # Configure tooltip appearance
            tooltip_bg = self.theme.get('tooltip_bg', '#ffffcc')
            tooltip_fg = self.theme.get('tooltip_fg', '#000000')
            tooltip_border = self.theme.get('tooltip_border', '#999999')
            
            # Create tooltip frame with border
            frame = tk.Frame(tooltip_window, 
                             background=tooltip_border,
                             borderwidth=1)
            frame.pack(fill="both", expand=True)
            
            # Create tooltip label
            label = tk.Label(frame, 
                            text=text, 
                            background=tooltip_bg,
                            foreground=tooltip_fg,
                            justify=tk.LEFT,
                            padx=5,
                            pady=3)
            label.pack()
            
            # Store the tooltip window
            self._tooltip_windows[widget] = tooltip_window
            
            # Auto-hide tooltip after duration (if specified)
            if duration > 0:
                widget.after(duration, hide_tooltip)
                
        def hide_tooltip():
            if widget in self._tooltip_windows:
                self._tooltip_windows[widget].destroy()
                del self._tooltip_windows[widget]
        
        # Bind events to widget
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
        widget.bind("<ButtonPress>", leave)  # Hide on click