import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable, Any, Dict, Tuple
import platform

class ComboboxWithIndicator(ttk.Combobox):
    """
    Enhanced combobox with visual indicators for selected items and improved handling for long lists.
    """
    def __init__(self, master=None, theme_manager=None, max_dropdown_items=10, **kwargs):
        """
        Initialize the enhanced combobox.
        
        Args:
            master: Parent widget
            theme_manager: ThemeManager instance for styling
            max_dropdown_items: Maximum number of items to show in dropdown before scrolling
            **kwargs: Additional arguments to pass to ttk.Combobox
        """
        self.theme_manager = theme_manager
        self.max_dropdown_items = max_dropdown_items
        self.master = master
        
        # Store colors for visual indicators
        self._colors = {
            'normal_bg': '#ffffff',
            'normal_fg': '#000000',
            'selected_bg': '#e2f0ff',
            'selected_fg': '#000000',
            'hover_bg': '#f0f7ff',
            'hover_fg': '#000000',
            'indicator': '#007bff'
        }
        
        # Update colors from theme manager if available
        if theme_manager:
            self._colors.update({
                'normal_bg': theme_manager.theme.get('frame_bg', '#ffffff'),
                'normal_fg': theme_manager.theme.get('fg', '#000000'),
                'selected_bg': theme_manager.theme.get('selection_bg', '#e2f0ff'),
                'selected_fg': theme_manager.theme.get('selection_fg', '#000000'),
                'hover_bg': theme_manager.theme.get('button_hover', '#f0f7ff'),
                'hover_fg': theme_manager.theme.get('fg', '#000000'),
                'indicator': theme_manager.theme.get('primary', '#007bff')
            })
            
            # Apply enhanced style if theme manager is provided
            kwargs['style'] = theme_manager.get_combobox_style(enhanced=True)
        
        # Initialize the combobox
        super().__init__(master, **kwargs)
        
        # Configure dropdown height based on values
        self._configure_dropdown_height()
        
        # Create indicator canvas for selected item
        self._create_indicator()
        
        # Bind events for visual feedback
        self.bind('<<ComboboxSelected>>', self._on_selection)
        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<FocusOut>', self._on_focus_out)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        
        # Store original values for filtering
        self._all_values = []
        
        # Visual indicator state
        self._has_selection = False
        self._is_hovered = False
        self._is_focused = False
        
    def _create_indicator(self):
        """Create a visual indicator for the combobox."""
        # Create a frame to hold the combobox and indicator
        self.indicator_frame = tk.Frame(self.master)
        
        # Create a small canvas for the indicator
        self.indicator = tk.Canvas(
            self.indicator_frame, 
            width=4, 
            height=self.winfo_reqheight(),
            highlightthickness=0,
            background=self._colors['normal_bg']
        )
        
        # Place the indicator to the left of the combobox
        self.indicator.pack(side=tk.LEFT, fill=tk.Y)
        
        # We need to reparent the combobox to our indicator frame
        # This is a bit tricky and platform-dependent
        if platform.system() == 'Windows':
            # On Windows, we can't easily reparent, so we'll use a different approach
            # We'll keep the indicator separate and position it next to the combobox
            self.indicator.pack_forget()
            self.indicator = tk.Canvas(
                self.master, 
                width=6, 
                height=self.winfo_reqheight(),
                highlightthickness=0,
                background=self._colors['normal_bg']
            )
            self.indicator.place(x=0, y=0, relheight=1)
            # Instead of using padding, adjust the width of the indicator
        
    def _on_selection(self, event):
        """Handle selection event to update visual indicator."""
        self._has_selection = True
        self._update_visual_indicator()
        
    def _on_focus_in(self, event):
        """Handle focus in event."""
        self._is_focused = True
        self._update_visual_indicator()
        
    def _on_focus_out(self, event):
        """Handle focus out event."""
        self._is_focused = False
        self._update_visual_indicator()
        
    def _on_enter(self, event):
        """Handle mouse enter event."""
        self._is_hovered = True
        self._update_visual_indicator()
        
    def _on_leave(self, event):
        """Handle mouse leave event."""
        self._is_hovered = False
        self._update_visual_indicator()
        
    def _update_visual_indicator(self):
        """Update the visual indicator for the combobox."""
        if not hasattr(self, 'indicator'):
            return
            
        # Determine the indicator color based on state
        if self._has_selection and self.get() and self['values'] and len(self['values']) > 0 and self.get() != self['values'][0]:
            # Show indicator for selected items (except the default/first item)
            self.indicator.configure(background=self._colors['indicator'])
        elif self._is_focused:
            # Show a subtle indicator when focused
            self.indicator.configure(background=self._colors['hover_bg'])
        elif self._is_hovered:
            # Show a very subtle indicator when hovered
            self.indicator.configure(background=self._colors['hover_bg'])
        else:
            # No indicator in normal state
            self.indicator.configure(background=self._colors['normal_bg'])
            
    def _configure_dropdown_height(self):
        """Configure the dropdown height based on the number of values."""
        if not self['values']:
            return
            
        # Set the height to the minimum of max_dropdown_items and the number of values
        height = min(len(self['values']), self.max_dropdown_items)
        # Use dictionary-style configuration to avoid positional argument issues
        self['height'] = height
        
    def set_values(self, values: List[str]):
        """
        Set the combobox values and configure dropdown height.
        
        Args:
            values: List of values to display in the combobox
        """
        self._all_values = values.copy()
        self['values'] = values
        self._configure_dropdown_height()
        
        # Update the visual indicator
        self._update_visual_indicator()
        
    def get_selected_index(self) -> int:
        """
        Get the index of the currently selected item.
        
        Returns:
            int: Index of selected item, or -1 if no selection
        """
        if not self.get() or not self['values']:
            return -1
            
        try:
            return self['values'].index(self.get())
        except ValueError:
            return -1
            
    def select_by_index(self, index: int):
        """
        Select an item by its index.
        
        Args:
            index: Index of the item to select
        """
        if index < 0 or not self['values'] or index >= len(self['values']):
            return
            
        self.set(self['values'][index])
        self._has_selection = True
        self._update_visual_indicator()
        
    def config(self, *args, **kwargs):
        """Override config to handle both dictionary and keyword arguments."""
        result = super().config(*args, **kwargs)
        
        # Update indicator height if it exists
        if hasattr(self, 'indicator'):
            self.indicator.configure(height=self.winfo_reqheight())
            
        return result
        
    # Alias configure to config for compatibility
    configure = config
            
    def pack(self, **kwargs):
        """Override pack to ensure the indicator is properly positioned."""
        super().pack(**kwargs)
        
        # Update indicator position if needed
        if platform.system() == 'Windows' and hasattr(self, 'indicator'):
            self.update_idletasks()  # Ensure geometry is updated
            self.indicator.place(x=0, y=0, relheight=1)
            
    def grid(self, **kwargs):
        """Override grid to ensure the indicator is properly positioned."""
        super().grid(**kwargs)
        
        # Update indicator position if needed
        if platform.system() == 'Windows' and hasattr(self, 'indicator'):
            self.update_idletasks()  # Ensure geometry is updated
            self.indicator.place(x=0, y=0, relheight=1)
            
    def place(self, **kwargs):
        """Override place to ensure the indicator is properly positioned."""
        super().place(**kwargs)
        
        # Update indicator position if needed
        if platform.system() == 'Windows' and hasattr(self, 'indicator'):
            self.update_idletasks()  # Ensure geometry is updated
            self.indicator.place(x=0, y=0, relheight=1)