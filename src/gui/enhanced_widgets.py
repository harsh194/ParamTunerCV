"""
Enhanced GUI widgets module for the Parameter image viewer application.

This module provides improved tkinter widgets with enhanced functionality, visual
indicators, and better user experience features. The widgets are theme-aware and
integrate seamlessly with the application's styling system.

Main Classes:
    - ComboboxWithIndicator: Enhanced combobox with visual selection indicators,
      improved dropdown handling, and theme integration

Features:
    - Visual indicators for selected items
    - Configurable dropdown height for long lists
    - Theme-aware styling and colors
    - Hover and focus state feedback
    - Cross-platform compatibility
    - Improved selection handling

Dependencies:
    - tkinter: GUI framework
    - typing: Type hints support
    - platform: Cross-platform compatibility detection

Usage:
    combo = ComboboxWithIndicator(
        parent, 
        theme_manager=theme_manager,
        max_dropdown_items=8
    )
    combo.set_values(['Option 1', 'Option 2', 'Option 3'])
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable, Any, Dict, Tuple
import platform

class ComboboxWithIndicator(ttk.Combobox):
    """
    Enhanced combobox widget with visual indicators and improved user experience.
    
    This class extends the standard ttk.Combobox to provide visual feedback for
    selected items, configurable dropdown height for long lists, and theme-aware
    styling. It includes hover and focus state indicators, cross-platform
    compatibility, and enhanced selection handling.
    
    The widget displays a colored indicator strip on the left side that changes
    based on the selection state, focus, and hover status. The dropdown height
    is automatically configured based on the number of items to prevent
    excessively long dropdown lists.
    
    Attributes:
        theme_manager: ThemeManager instance for styling integration.
        max_dropdown_items (int): Maximum items to show in dropdown before scrolling.
        master: Parent widget reference.
        indicator: Canvas widget for visual indicator display.
        indicator_frame: Frame container for indicator positioning.
        _colors (dict): Color scheme for different widget states.
        _all_values (list): Complete list of available values.
        _has_selection (bool): Whether an item is currently selected.
        _is_hovered (bool): Whether the widget is being hovered.
        _is_focused (bool): Whether the widget has focus.
    
    Examples:
        >>> combo = ComboboxWithIndicator(
        ...     parent, 
        ...     theme_manager=theme_manager,
        ...     max_dropdown_items=10
        ... )
        >>> combo.set_values(['Item 1', 'Item 2', 'Item 3'])
        >>> combo.select_by_index(1)
        # Visual indicator will show selection state
    """
    def __init__(self, master=None, theme_manager=None, max_dropdown_items: int = 10, **kwargs) -> None:
        """
        Initialize the enhanced combobox with visual indicators and theme support.
        
        Sets up the combobox with enhanced functionality including visual indicators,
        configurable dropdown height, theme-aware colors, and event bindings for
        improved user interaction feedback. Creates cross-platform compatible
        indicator positioning and applies theme styling.
        
        Args:
            master: The parent tkinter widget to contain this combobox.
            theme_manager: ThemeManager instance for consistent styling integration.
                         If None, default styling will be used.
            max_dropdown_items (int): Maximum number of items to display in dropdown
                                    before enabling scrolling. Default is 10.
            **kwargs: Additional keyword arguments passed to ttk.Combobox constructor.
        
        Returns:
            None: Constructor initializes instance, no return value.
        
        Examples:
            >>> combo = ComboboxWithIndicator(
            ...     parent, 
            ...     theme_manager=theme_mgr,
            ...     max_dropdown_items=8
            ... )
            >>> combo.set_values(['Option A', 'Option B', 'Option C'])
            >>> # Enhanced combobox created with visual indicators
            
        Performance:
            Time Complexity: O(1) - Fixed initialization operations.
            Space Complexity: O(1) - Fixed memory allocation for widget components.
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
        
    def _create_indicator(self) -> None:
        """
        Create a visual indicator canvas for selection state feedback.
        
        Creates a small canvas widget positioned adjacent to the combobox that
        displays colored indicators based on the widget's state. Uses platform-specific
        positioning strategies to handle windowing system limitations on different OS.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Creates UI components as side effect, no return value.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr)
            >>> combo._create_indicator()
            >>> # Visual indicator canvas created and positioned
            >>> # Color changes based on selection/focus/hover state
            
        Performance:
            Time Complexity: O(1) - Fixed widget creation operations.
            Space Complexity: O(1) - Single canvas widget and frame allocation.
        """
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
        
    def _on_selection(self, event) -> None:
        """
        Handle combobox selection events and update visual feedback.
        
        Called when the user selects an item from the dropdown. Updates the
        internal selection state and refreshes the visual indicator to show
        selection status with appropriate color coding.
        
        Args:
            event: The tkinter ComboboxSelected event object.
        
        Returns:
            None: Updates widget state as side effect, no return value.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr)
            >>> combo.set_values(['A', 'B', 'C'])
            >>> # User selects 'B' from dropdown
            >>> # _on_selection automatically called
            >>> # Visual indicator changes to selection color
            
        Performance:
            Time Complexity: O(1) - Simple state update and indicator refresh.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self._has_selection = True
        self._update_visual_indicator()
        
    def _on_focus_in(self, event) -> None:
        """
        Handle focus gain events and update visual feedback.
        
        Called when the combobox gains keyboard focus through tab navigation
        or direct clicking. Updates the focus state and refreshes the visual
        indicator to show focused state with appropriate styling.
        
        Args:
            event: The tkinter FocusIn event object.
        
        Returns:
            None: Updates widget state as side effect, no return value.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr)
            >>> # User tabs to combobox or clicks on it
            >>> # _on_focus_in automatically called
            >>> # Visual indicator shows focus color
            
        Performance:
            Time Complexity: O(1) - Simple state update and indicator refresh.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self._is_focused = True
        self._update_visual_indicator()
        
    def _on_focus_out(self, event) -> None:
        """
        Handle focus loss events and update visual feedback.
        
        Called when the combobox loses keyboard focus through tab navigation
        or clicking elsewhere. Updates the focus state and refreshes the visual
        indicator to remove focused styling and return to normal appearance.
        
        Args:
            event: The tkinter FocusOut event object.
        
        Returns:
            None: Updates widget state as side effect, no return value.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr)
            >>> # User tabs away from combobox or clicks elsewhere
            >>> # _on_focus_out automatically called
            >>> # Visual indicator returns to normal/selection color
            
        Performance:
            Time Complexity: O(1) - Simple state update and indicator refresh.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self._is_focused = False
        self._update_visual_indicator()
        
    def _on_enter(self, event) -> None:
        """
        Handle mouse enter events and update visual feedback.
        
        Called when the mouse cursor enters the combobox widget area. Updates the
        hover state and refreshes the visual indicator to show hover styling,
        providing immediate visual feedback for mouse interaction.
        
        Args:
            event: The tkinter Enter event object containing mouse position data.
        
        Returns:
            None: Updates widget state as side effect, no return value.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr)
            >>> # User moves mouse over combobox
            >>> # _on_enter automatically called
            >>> # Visual indicator shows hover color
            
        Performance:
            Time Complexity: O(1) - Simple state update and indicator refresh.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self._is_hovered = True
        self._update_visual_indicator()
        
    def _on_leave(self, event) -> None:
        """
        Handle mouse leave events and update visual feedback.
        
        Called when the mouse cursor leaves the combobox widget area. Updates the
        hover state and refreshes the visual indicator to remove hover styling,
        returning to normal or focused appearance as appropriate.
        
        Args:
            event: The tkinter Leave event object containing mouse position data.
        
        Returns:
            None: Updates widget state as side effect, no return value.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr)
            >>> # User moves mouse away from combobox
            >>> # _on_leave automatically called
            >>> # Visual indicator returns to normal/focused/selected color
            
        Performance:
            Time Complexity: O(1) - Simple state update and indicator refresh.
            Space Complexity: O(1) - No additional memory allocation.
        """
        self._is_hovered = False
        self._update_visual_indicator()
        
    def _update_visual_indicator(self) -> None:
        """
        Update the visual indicator based on current widget state.
        
        Determines the appropriate indicator color based on the combination of
        selection, focus, and hover states, then updates the indicator canvas
        background color accordingly. Uses priority-based color selection.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates indicator appearance as side effect, no return value.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr)
            >>> combo._has_selection = True
            >>> combo._update_visual_indicator()
            >>> # Indicator shows selection color (primary blue)
            >>> combo._is_focused = True
            >>> combo._update_visual_indicator()
            >>> # Indicator shows focus color (hover background)
            
        Performance:
            Time Complexity: O(1) - Simple conditional checks and color update.
            Space Complexity: O(1) - No additional memory allocation.
        """
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
            
    def _configure_dropdown_height(self) -> None:
        """
        Configure the dropdown height based on the number of available values.
        
        Automatically sets the dropdown height to show a reasonable number of
        items without creating excessively long dropdowns. Uses the minimum of
        max_dropdown_items and the actual number of values for optimal UX.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            None: Updates combobox configuration as side effect, no return value.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr, max_dropdown_items=5)
            >>> combo['values'] = ['A', 'B', 'C']  # 3 items
            >>> combo._configure_dropdown_height()
            >>> print(combo['height'])  # 3 (shows all items)
            >>> combo['values'] = ['A', 'B', 'C', 'D', 'E', 'F', 'G']  # 7 items
            >>> combo._configure_dropdown_height()
            >>> print(combo['height'])  # 5 (max_dropdown_items limit)
            
        Performance:
            Time Complexity: O(1) - Simple length check and minimum calculation.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if not self['values']:
            return
            
        # Set the height to the minimum of max_dropdown_items and the number of values
        height = min(len(self['values']), self.max_dropdown_items)
        # Use dictionary-style configuration to avoid positional argument issues
        self['height'] = height
        
    def set_values(self, values: List[str]) -> None:
        """
        Set the combobox values and configure the interface accordingly.
        
        Updates the combobox with new values, configures the dropdown height
        for optimal display, and refreshes the visual indicator. Maintains
        internal copy of values for potential filtering operations.
        
        Args:
            values (List[str]): List of string values to display in the combobox dropdown.
                              Empty list is allowed and will create empty dropdown.
        
        Returns:
            None: Updates combobox configuration as side effect, no return value.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr)
            >>> combo.set_values(['Option 1', 'Option 2', 'Option 3'])
            >>> # Combobox now shows 3 options with height=3
            >>> combo.set_values([])
            >>> # Combobox cleared, no dropdown options
            
        Performance:
            Time Complexity: O(n) where n is length of values list (for list copy).
            Space Complexity: O(n) - Stores copy of values list internally.
        """
        self._all_values = values.copy()
        self['values'] = values
        self._configure_dropdown_height()
        
        # Update the visual indicator
        self._update_visual_indicator()
        
    def get_selected_index(self) -> int:
        """
        Get the index of the currently selected item in the values list.
        
        Determines the position of the currently selected value within the
        list of available values. Handles cases where no selection exists
        or the current value is not in the values list.
        
        Args:
            None: This method takes no arguments.
        
        Returns:
            int: Zero-based index of the selected item, or -1 if no item is
                selected or the selected value is not found in the values list.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr)
            >>> combo.set_values(['Apple', 'Banana', 'Cherry'])
            >>> combo.set('Banana')
            >>> print(combo.get_selected_index())  # 1
            >>> combo.set('Orange')  # Not in values list
            >>> print(combo.get_selected_index())  # -1
            >>> combo.set('')  # No selection
            >>> print(combo.get_selected_index())  # -1
            
        Performance:
            Time Complexity: O(n) where n is length of values list (list.index search).
            Space Complexity: O(1) - No additional memory allocation.
        """
        if not self.get() or not self['values']:
            return -1
            
        try:
            return self['values'].index(self.get())
        except ValueError:
            return -1
            
    def select_by_index(self, index: int) -> None:
        """
        Select an item by its zero-based index in the values list.
        
        Programmatically selects the item at the specified index and updates
        the visual state accordingly. Validates index bounds before selection
        and silently ignores invalid indices.
        
        Args:
            index (int): Zero-based index of the item to select. Must be within
                        the valid range [0, len(values)-1]. Negative indices or
                        indices >= len(values) are ignored.
        
        Returns:
            None: Updates combobox selection as side effect, no return value.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr)
            >>> combo.set_values(['Red', 'Green', 'Blue'])
            >>> combo.select_by_index(1)
            >>> print(combo.get())  # 'Green'
            >>> combo.select_by_index(5)  # Invalid index, ignored
            >>> print(combo.get())  # Still 'Green'
            >>> combo.select_by_index(-1)  # Invalid index, ignored
            
        Performance:
            Time Complexity: O(1) - Direct list indexing and widget update.
            Space Complexity: O(1) - No additional memory allocation.
        """
        if index < 0 or not self['values'] or index >= len(self['values']):
            return
            
        self.set(self['values'][index])
        self._has_selection = True
        self._update_visual_indicator()
        
    def config(self, *args, **kwargs):
        """
        Override the config method to maintain indicator synchronization.
        
        Handles configuration changes while ensuring the visual indicator
        remains properly sized and positioned relative to the combobox.
        Maintains indicator height synchronization after configuration changes.
        
        Args:
            *args: Positional arguments passed to parent ttk.Combobox config method.
            **kwargs: Keyword arguments passed to parent config method. Can include
                     any standard ttk.Combobox configuration options like width,
                     height, font, etc.
        
        Returns:
            Any: The result of the parent config method call, typically None for
                configuration operations or current values for queries.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr)
            >>> combo.config(width=20, font=('Arial', 12))
            >>> # Combobox configured and indicator height updated
            >>> current_width = combo.config('width')
            >>> print(current_width)  # Returns current width configuration
            
        Performance:
            Time Complexity: O(1) - Configuration update and indicator sync.
            Space Complexity: O(1) - No additional memory allocation.
        """
        result = super().config(*args, **kwargs)
        
        # Update indicator height if it exists
        if hasattr(self, 'indicator'):
            self.indicator.configure(height=self.winfo_reqheight())
            
        return result
        
    # Alias configure to config for compatibility
    configure = config
            
    def pack(self, **kwargs):
        """
        Override the pack geometry manager to maintain indicator positioning.
        
        Ensures the visual indicator remains properly positioned after the
        combobox is packed, handling platform-specific positioning requirements.
        Forces geometry updates on Windows to ensure proper indicator placement.
        
        Args:
            **kwargs: Keyword arguments passed to parent ttk.Combobox pack method.
                     Supports all standard pack options like side, fill, expand,
                     padx, pady, anchor, etc.
        
        Returns:
            None: Manages widget geometry as side effect, no return value.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr)
            >>> combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            >>> # Combobox packed with indicator properly positioned
            >>> combo.pack(side=tk.TOP, pady=10)
            >>> # Repacked with different options, indicator updated
            
        Performance:
            Time Complexity: O(1) - Geometry management and positioning updates.
            Space Complexity: O(1) - No additional memory allocation.
        """
        super().pack(**kwargs)
        
        # Update indicator position if needed
        if platform.system() == 'Windows' and hasattr(self, 'indicator'):
            self.update_idletasks()  # Ensure geometry is updated
            self.indicator.place(x=0, y=0, relheight=1)
            
    def grid(self, **kwargs):
        """
        Override the grid geometry manager to maintain indicator positioning.
        
        Ensures the visual indicator remains properly positioned after the
        combobox is gridded, handling platform-specific positioning requirements.
        Forces geometry updates on Windows to ensure proper indicator placement.
        
        Args:
            **kwargs: Keyword arguments passed to parent ttk.Combobox grid method.
                     Supports all standard grid options like row, column, rowspan,
                     columnspan, sticky, padx, pady, ipadx, ipady, etc.
        
        Returns:
            None: Manages widget geometry as side effect, no return value.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr)
            >>> combo.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
            >>> # Combobox gridded with indicator properly positioned
            >>> combo.grid(row=1, column=0, columnspan=2)
            >>> # Repositioned with different grid options, indicator updated
            
        Performance:
            Time Complexity: O(1) - Geometry management and positioning updates.
            Space Complexity: O(1) - No additional memory allocation.
        """
        super().grid(**kwargs)
        
        # Update indicator position if needed
        if platform.system() == 'Windows' and hasattr(self, 'indicator'):
            self.update_idletasks()  # Ensure geometry is updated
            self.indicator.place(x=0, y=0, relheight=1)
            
    def place(self, **kwargs):
        """
        Override the place geometry manager to maintain indicator positioning.
        
        Ensures the visual indicator remains properly positioned after the
        combobox is placed, handling platform-specific positioning requirements.
        Forces geometry updates on Windows to ensure proper indicator placement.
        
        Args:
            **kwargs: Keyword arguments passed to parent ttk.Combobox place method.
                     Supports all standard place options like x, y, relx, rely,
                     width, height, relwidth, relheight, anchor, bordermode, etc.
        
        Returns:
            None: Manages widget geometry as side effect, no return value.
        
        Examples:
            >>> combo = ComboboxWithIndicator(parent, theme_mgr)
            >>> combo.place(x=10, y=20, width=200)
            >>> # Combobox placed at absolute position with indicator positioned
            >>> combo.place(relx=0.5, rely=0.5, anchor='center')
            >>> # Repositioned to center with relative coordinates, indicator updated
            
        Performance:
            Time Complexity: O(1) - Geometry management and positioning updates.
            Space Complexity: O(1) - No additional memory allocation.
        """
        super().place(**kwargs)
        
        # Update indicator position if needed
        if platform.system() == 'Windows' and hasattr(self, 'indicator'):
            self.update_idletasks()  # Ensure geometry is updated
            self.indicator.place(x=0, y=0, relheight=1)