"""
Theme management module for the Parameter image viewer application.

This module provides comprehensive theme and styling management for tkinter
interfaces, supporting both light and dark themes with consistent color schemes,
widget styling, and tooltip functionality.

Main Classes:
    - ThemeManager: Central theme management system that handles widget styling,
      color schemes, and tooltip creation for consistent UI appearance

Features:
    - Light and dark theme support
    - Consistent color schemes across all widgets
    - Customizable button styles (primary, secondary, active)
    - Enhanced combobox styling
    - Theme-aware tooltip system
    - Dynamic theme switching
    - Cross-platform compatibility

Dependencies:
    - tkinter: GUI framework and widget styling

Usage:
    theme_manager = ThemeManager(use_dark_mode=False)
    theme_manager.configure_theme(root_window)
    button_style = theme_manager.get_button_style("primary")
    theme_manager.create_tooltip(widget, "Help text")
"""

import tkinter as tk
from tkinter import ttk

class ThemeManager:
    """
    Comprehensive theme and styling manager for tkinter interfaces.
    
    This class provides centralized management of themes, colors, and widget
    styles for the Parameter application. It supports both light and dark themes
    with consistent styling across all interface elements, including buttons,
    frames, labels, comboboxes, and tooltips.
    
    The theme manager maintains color schemes, configures ttk styles, and provides
    convenient methods for accessing appropriate style names for different widget
    types and states. It also includes a sophisticated tooltip system with
    theme-aware styling.
    
    Attributes:
        use_dark_mode (bool): Whether dark theme is currently active.
        theme (dict): Current theme color scheme with named color values.
        _tooltip_windows (dict): Tracking dictionary for active tooltip windows.
    
    Examples:
        >>> theme_manager = ThemeManager(use_dark_mode=True)
        >>> theme_manager.configure_theme(root)
        >>> primary_button = ttk.Button(
        ...     parent, 
        ...     text="Action", 
        ...     style=theme_manager.get_button_style("primary")
        ... )
        >>> theme_manager.create_tooltip(primary_button, "Performs primary action")
    """

    def __init__(self, use_dark_mode: bool = False) -> None:
        """
        Initialize the theme manager with the specified theme mode.
        
        Sets up the initial theme state and prepares for theme configuration.
        The actual theme styling is applied when configure_theme() is called
        with a root window. Initializes tooltip tracking system.
        
        Args:
            use_dark_mode (bool): Whether to use dark theme initially. Defaults to False
                                 for light theme. True enables dark mode with light text
                                 on dark backgrounds.
        
        Returns:
            None: Constructor initializes instance, no return value.
        
        Examples:
            >>> # Create light theme manager
            >>> light_theme = ThemeManager(use_dark_mode=False)
            >>> # Create dark theme manager
            >>> dark_theme = ThemeManager(use_dark_mode=True)
            >>> # Theme colors available after configure_theme() is called
            
        Performance:
            Time Complexity: O(1) - Simple initialization of instance variables.
            Space Complexity: O(1) - Fixed memory allocation for theme state.
        """
        self.use_dark_mode = use_dark_mode
        # Theme colors will be set during configure_theme
        self.theme = {}
        # We will call configure_theme when a root window is available
        # to get the style object.
        self._tooltip_windows = {}  # Store tooltip windows

    def configure_theme(self, root) -> None:
        """
        Configure the ttk style system with the current theme settings.
        
        Applies the complete theme configuration to the provided root window,
        including widget styles, color schemes, and root window styling.
        Handles both light and dark theme configurations with fallback support.
        
        Args:
            root: The root tkinter window to apply the theme to. Must be a valid
                 Tk root window instance.
        
        Returns:
            None: Configures theme as side effect, no return value.
        
        Examples:
            >>> import tkinter as tk
            >>> root = tk.Tk()
            >>> theme_mgr = ThemeManager(use_dark_mode=True)
            >>> theme_mgr.configure_theme(root)
            >>> # Root window and all ttk widgets now use dark theme
            >>> print(theme_mgr.theme['primary'])  # '#0d6efd'
            
        Performance:
            Time Complexity: O(1) - Fixed number of style configurations.
            Space Complexity: O(1) - Theme dictionary with fixed color entries.
        """
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

    def _configure_light_theme(self, style) -> None:
        """
        Configure light theme colors and widget styles.
        
        Sets up a professional light theme with blue primary colors, light
        backgrounds, and dark text. Configures all supported widget types
        including buttons, frames, labels, and comboboxes with proper state mappings.
        
        Args:
            style: The ttk.Style object to configure. Must be a valid ttk.Style instance.
        
        Returns:
            None: Configures theme styles as side effect, no return value.
        
        Examples:
            >>> import tkinter as tk
            >>> from tkinter import ttk
            >>> root = tk.Tk()
            >>> style = ttk.Style(root)
            >>> theme_mgr = ThemeManager()
            >>> theme_mgr._configure_light_theme(style)
            >>> # Light theme applied with blue primary colors
            >>> print(theme_mgr.theme['primary'])  # '#007bff'
            
        Performance:
            Time Complexity: O(1) - Fixed number of style configurations.
            Space Complexity: O(1) - Fixed theme dictionary with predefined colors.
        """
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

        # Active state button for drawing modes
        style.configure("Active.TButton")
        style.map("Active.TButton",
                  foreground=[('!active', '#ffffff')],
                  background=[('!active', '#28a745'), ('active', '#1e7e34')])  # Green for active

    def _configure_dark_theme(self, style) -> None:
        """
        Configure dark theme colors and widget styles.
        
        Sets up a professional dark theme with blue primary colors, dark
        backgrounds, and light text. Configures all supported widget types
        with appropriate contrast and readability for optimal dark mode experience.
        
        Args:
            style: The ttk.Style object to configure. Must be a valid ttk.Style instance.
        
        Returns:
            None: Configures theme styles as side effect, no return value.
        
        Examples:
            >>> import tkinter as tk
            >>> from tkinter import ttk
            >>> root = tk.Tk()
            >>> style = ttk.Style(root)
            >>> theme_mgr = ThemeManager(use_dark_mode=True)
            >>> theme_mgr._configure_dark_theme(style)
            >>> # Dark theme applied with light text on dark backgrounds
            >>> print(theme_mgr.theme['bg'])  # '#212529'
            
        Performance:
            Time Complexity: O(1) - Fixed number of style configurations.
            Space Complexity: O(1) - Fixed theme dictionary with predefined colors.
        """
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

        # Active state button for drawing modes
        style.configure("Active.TButton")
        style.map("Active.TButton",
                  foreground=[('!active', '#ffffff')],
                  background=[('!active', '#28a745'), ('active', '#1e7e34')])  # Green for active

    def get_button_style(self, button_type: str = "default") -> str:
        """
        Get the appropriate ttk button style name based on the button type.
        
        Returns the correct style identifier for different button types,
        enabling consistent styling across the application. Supports multiple
        button styles for different interaction contexts.
        
        Args:
            button_type (str): The type of button style requested. Options are:
                              - "primary": Main action buttons (blue background)
                              - "secondary": Secondary action buttons (gray background)
                              - "active": Active state buttons (green background)
                              - "default" or any other: Standard button style
        
        Returns:
            str: The ttk style name to use for the button. Always returns a valid
                style name, defaulting to "TButton" for unknown types.
        
        Examples:
            >>> theme_mgr = ThemeManager()
            >>> primary_style = theme_mgr.get_button_style("primary")
            >>> print(primary_style)  # "Primary.TButton"
            >>> default_style = theme_mgr.get_button_style("unknown")
            >>> print(default_style)  # "TButton"
            >>> active_style = theme_mgr.get_button_style("active")
            >>> print(active_style)  # "Active.TButton"
            
        Performance:
            Time Complexity: O(1) - Simple string comparison and return.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if button_type == "primary":
            return "Primary.TButton"
        if button_type == "secondary":
            return "Secondary.TButton"
        if button_type == "active":
            return "Active.TButton"
        return "TButton"

    def get_frame_style(self, frame_type: str = "default") -> str:
        """
        Get the appropriate ttk frame style name based on the frame type.
        
        Returns the correct style identifier for frame widgets, currently
        using a standard frame style for all types. Frame type parameter
        is reserved for future frame style variations.
        
        Args:
            frame_type (str): The type of frame style requested (currently unused,
                             reserved for future frame type variations like
                             "container", "panel", "toolbar", etc.).
        
        Returns:
            str: The ttk style name to use for the frame. Currently always
                returns "TFrame" regardless of frame_type.
        
        Examples:
            >>> theme_mgr = ThemeManager()
            >>> frame_style = theme_mgr.get_frame_style("default")
            >>> print(frame_style)  # "TFrame"
            >>> panel_style = theme_mgr.get_frame_style("panel")
            >>> print(panel_style)  # "TFrame" (same as default)
            
        Performance:
            Time Complexity: O(1) - Direct string return.
            Space Complexity: O(1) - No additional memory allocation.
        """
        return "TFrame"
        
    def get_label_style(self, label_type: str = "default") -> str:
        """
        Get the appropriate ttk label style name based on the label type.
        
        Returns the correct style identifier for different label types,
        supporting both standard and header label styles with appropriate
        font styling and visual hierarchy.
        
        Args:
            label_type (str): The type of label style requested. Options are:
                             - "header": Bold header labels with larger font (12pt bold)
                             - "default" or any other: Standard label style
        
        Returns:
            str: The ttk style name to use for the label. Always returns a valid
                style name, defaulting to "TLabel" for unknown types.
        
        Examples:
            >>> theme_mgr = ThemeManager()
            >>> header_style = theme_mgr.get_label_style("header")
            >>> print(header_style)  # "Header.TLabel"
            >>> default_style = theme_mgr.get_label_style("body")
            >>> print(default_style)  # "TLabel"
            >>> normal_style = theme_mgr.get_label_style()
            >>> print(normal_style)  # "TLabel"
            
        Performance:
            Time Complexity: O(1) - Simple string comparison and return.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if label_type == "header":
            return "Header.TLabel"
        return "TLabel"
        
    def get_combobox_style(self, enhanced: bool = True) -> str:
        """
        Get the appropriate ttk combobox style name.
        
        Returns the correct style identifier for combobox widgets, with
        options for standard or enhanced styling. Enhanced styling includes
        improved borders, hover effects, and better visual feedback.
        
        Args:
            enhanced (bool): Whether to use enhanced combobox styling with improved
                           borders and hover effects. Enhanced style includes flat
                           relief, custom border colors, and focus indicators.
                           Defaults to True.
        
        Returns:
            str: The ttk style name to use for the combobox. Returns either
                "Enhanced.TCombobox" or "TCombobox" based on enhanced parameter.
        
        Examples:
            >>> theme_mgr = ThemeManager()
            >>> enhanced_style = theme_mgr.get_combobox_style(enhanced=True)
            >>> print(enhanced_style)  # "Enhanced.TCombobox"
            >>> standard_style = theme_mgr.get_combobox_style(enhanced=False)
            >>> print(standard_style)  # "TCombobox"
            >>> default_style = theme_mgr.get_combobox_style()
            >>> print(default_style)  # "Enhanced.TCombobox" (enhanced=True default)
            
        Performance:
            Time Complexity: O(1) - Simple boolean check and string return.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if enhanced:
            return "Enhanced.TCombobox"
        return "TCombobox"

    def get_root_style(self, root) -> None:
        """
        Apply theme-appropriate styling to the root window.
        
        Sets the root window background color to match the current theme,
        ensuring consistent appearance throughout the application. Uses different
        background colors for light and dark themes.
        
        Args:
            root: The root tkinter window to style. Must be a valid Tk root window.
        
        Returns:
            None: Modifies root window styling as side effect, no return value.
        
        Examples:
            >>> import tkinter as tk
            >>> root = tk.Tk()
            >>> light_theme = ThemeManager(use_dark_mode=False)
            >>> light_theme.get_root_style(root)
            >>> # Root background set to light gray (#f0f0f0)
            >>> dark_theme = ThemeManager(use_dark_mode=True)
            >>> dark_theme.get_root_style(root)
            >>> # Root background set to dark gray (#212529)
            
        Performance:
            Time Complexity: O(1) - Single background color configuration.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if self.use_dark_mode:
            root.configure(bg="#212529")
        else:
            root.configure(bg="#f0f0f0")
            
    def toggle_theme(self) -> bool:
        """
        Toggle between light and dark theme modes.
        
        Switches the theme mode and returns the new state. Note that this
        only changes the internal state; configure_theme() must be called
        to apply the new theme to the interface widgets.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            bool: The new theme state (True for dark mode, False for light mode).
        
        Examples:
            >>> theme_mgr = ThemeManager(use_dark_mode=False)
            >>> print(theme_mgr.use_dark_mode)  # False
            >>> new_state = theme_mgr.toggle_theme()
            >>> print(new_state)  # True
            >>> print(theme_mgr.use_dark_mode)  # True
            >>> # Must call configure_theme(root) to apply changes
            
        Performance:
            Time Complexity: O(1) - Simple boolean toggle operation.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self.use_dark_mode = not self.use_dark_mode
        return self.use_dark_mode
        
    def create_tooltip(self, widget, text: str, delay: int = 500, duration: int = 5000) -> None:
        """
        Create a theme-aware tooltip for a widget with customizable behavior.
        
        Attaches a sophisticated tooltip system to the specified widget that
        displays helpful text on hover. The tooltip uses theme-appropriate
        colors and includes smart positioning, timing controls, and proper
        cleanup. Prevents duplicate tooltips on the same widget.
        
        Args:
            widget: The tkinter widget to attach the tooltip to. Can be any tkinter
                   widget that supports event binding (Button, Label, Entry, etc.).
            text (str): The help text to display in the tooltip. Multi-line text
                       is supported with \n characters.
            delay (int): Delay in milliseconds before showing the tooltip after
                        mouse enter. Must be >= 0. Defaults to 500ms.
            duration (int): Duration in milliseconds to show tooltip. Set to 0 for
                          indefinite display until mouse leave. Defaults to 5000ms.
        
        Returns:
            None: Configures tooltip system as side effect, no return value.
        
        Examples:
            >>> import tkinter as tk
            >>> from tkinter import ttk
            >>> root = tk.Tk()
            >>> theme_mgr = ThemeManager()
            >>> theme_mgr.configure_theme(root)
            >>> button = ttk.Button(root, text="Click me")
            >>> theme_mgr.create_tooltip(button, "This button performs an action")
            >>> # Tooltip appears after 500ms hover, disappears after 5 seconds
            >>> 
            >>> # Custom timing
            >>> theme_mgr.create_tooltip(button, "Quick tip", delay=100, duration=2000)
            >>> # Permanent tooltip (until mouse leave)
            >>> theme_mgr.create_tooltip(button, "Always visible", duration=0)
            
        Performance:
            Time Complexity: O(1) - Constant time tooltip creation and event binding.
            Space Complexity: O(1) - Single tooltip window per widget stored in dict.
        """
        # Ensure we don't have multiple tooltips for the same widget
        if widget in self._tooltip_windows:
            return
            
        def enter(event):
            # Schedule tooltip to appear after delay
            widget._tooltip_id = widget.after(delay, lambda: show_tooltip(event))
            
        def leave(event):
            # Cancel scheduled tooltip safely
            if hasattr(widget, '_tooltip_id') and widget._tooltip_id is not None:
                try:
                    widget.after_cancel(widget._tooltip_id)
                except (ValueError, tk.TclError):
                    # Timer ID is no longer valid (already executed or cancelled)
                    pass
                widget._tooltip_id = None
            # Hide tooltip if it's visible
            hide_tooltip()
            
        def show_tooltip(event):
            # Clear timer ID since tooltip is now being shown
            if hasattr(widget, '_tooltip_id'):
                widget._tooltip_id = None
                
            # Get screen position safely
            try:
                # Try to get cursor position from bbox if supported
                bbox = widget.bbox("insert")
                if bbox:
                    x, y, _, _ = bbox
                    x += widget.winfo_rootx() + 25
                    y += widget.winfo_rooty() + 25
                else:
                    raise tk.TclError("bbox not supported")
            except (tk.TclError, AttributeError):
                # Fallback to widget position if bbox not supported
                x = widget.winfo_rootx() + 25
                y = widget.winfo_rooty() + 25
            
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