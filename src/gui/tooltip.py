"""
Simple tooltip functionality module for the Parameter image viewer application.

This module provides a basic tooltip implementation for tkinter widgets, displaying
helpful text when users hover over GUI elements. The tooltip appears as a small
popup window with a light yellow background and automatically positions itself
near the cursor.

Main Classes:
    - Tooltip: Simple tooltip widget that displays helpful text on hover

Features:
    - Automatic show/hide on mouse enter/leave events
    - Smart positioning relative to the widget
    - Consistent styling with light yellow background
    - Borderless popup window design
    - Automatic cleanup and resource management

Dependencies:
    - tkinter: GUI framework for popup window creation

Usage:
    button = ttk.Button(root, text="Click me")
    tooltip = Tooltip(button, "This button performs an action")
    # Tooltip will automatically appear on hover

Note:
    This is a simplified tooltip implementation. For more advanced tooltips
    with theme support and enhanced features, see ThemeManager.create_tooltip().
"""

import tkinter as tk

class Tooltip:
    """
    Simple tooltip widget that displays helpful text when hovering over GUI elements.
    
    This class provides basic tooltip functionality by creating a small popup window
    that appears when the mouse enters the associated widget and disappears when
    the mouse leaves. The tooltip uses a fixed light yellow background and positions
    itself automatically near the widget.
    
    The tooltip popup is created as a borderless top-level window that floats above
    other windows and follows standard tooltip behavior patterns.
    
    Attributes:
        widget: The tkinter widget this tooltip is attached to.
        text (str): The text content displayed in the tooltip.
        tooltip_window: The popup window displaying the tooltip (None when hidden).
    
    Examples:
        >>> button = ttk.Button(root, text="Save")
        >>> tooltip = Tooltip(button, "Save the current document")
        # Tooltip appears automatically on mouse hover
        
        >>> entry = ttk.Entry(root)
        >>> Tooltip(entry, "Enter your username here")
        # Tooltip provides input guidance
    """
    def __init__(self, widget, text: str) -> None:
        """
        Initialize a tooltip for the specified widget with the given text.
        
        Sets up event bindings for mouse enter and leave events to automatically
        show and hide the tooltip. The tooltip popup is not created until the
        first hover event.
        
        Args:
            widget: The tkinter widget to attach the tooltip to. Can be any
                   tkinter widget that supports event binding.
            text: The text content to display in the tooltip popup.
        
        Side Effects:
            - Binds mouse enter event to show_tooltip method
            - Binds mouse leave event to hide_tooltip method
        """
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event) -> None:
        """
        Display the tooltip popup window at an appropriate position.
        
        Creates and shows a popup window containing the tooltip text, positioned
        slightly offset from the widget to avoid obscuring the cursor. The popup
        uses a light yellow background with a solid border for visibility.
        
        Args:
            event: The tkinter mouse enter event that triggered the tooltip display.
        
        Side Effects:
            - Creates a new Toplevel window for the tooltip
            - Positions the window near the widget
            - Configures window styling and text display
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
        
        Removes the tooltip popup from the screen and cleans up the window
        resources. Safe to call multiple times or when no tooltip is visible.
        
        Args:
            event: The tkinter mouse leave event that triggered the tooltip hiding.
        
        Side Effects:
            - Destroys the tooltip window if it exists
            - Clears the tooltip_window reference
        """
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None
