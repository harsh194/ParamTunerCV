"""Mouse interaction management for the Parameter project ImageViewer.

This module provides comprehensive mouse interaction handling including coordinate tracking,
interactive drawing of analysis regions (ROIs, lines, polygons), selection management,
and visual feedback systems. It supports multi-modal drawing operations with sophisticated
selection highlighting and animation effects.

The module handles three primary analysis element types:
- Rectangular ROIs (Regions of Interest) for area-based analysis
- Line profiles for intensity analysis along paths
- Polygon regions for complex geometric analysis

Key Features:
- Multi-modal drawing states (rectangle, line, polygon modes)
- Selection management with visual highlighting and animations
- Color-coded visual feedback for different element types
- Coordinate transformation and bounds management
- Interactive element manipulation and validation

Main Classes:
    MouseHandler: Central manager for all mouse interactions and drawing state

Usage:
    mouse = MouseHandler()
    mouse.is_line_mode = True  # Switch to line drawing mode
    mouse.handle_item_added('line')  # Manage selections when items are added
    color = mouse.get_line_color(0)  # Get appropriate display color
"""

from typing import List, Tuple, Optional

class MouseHandler:
    """Comprehensive mouse interaction and drawing state manager for image analysis.
    
    This class manages all aspects of mouse-driven interaction within the ImageViewer,
    including coordinate tracking, multi-modal drawing operations (rectangles, lines, 
    polygons), selection management, and sophisticated visual feedback systems with
    animations and color coding.
    
    The MouseHandler supports three primary analysis modes:
    - Rectangle mode: Draw rectangular ROIs for area-based analysis
    - Line mode: Draw line profiles for intensity analysis along paths
    - Polygon mode: Draw complex polygonal regions for advanced geometric analysis
    
    Key capabilities include:
    - Real-time coordinate tracking and transformation
    - Interactive drawing with immediate visual feedback
    - Selection management with highlighting and animations
    - Multi-state drawing operations with mode switching
    - Color-coded visual distinction between element types
    - Animation effects for selected elements (pulsing, transparency)
    - Validation and bounds checking for all interactions
    
    Attributes:
        mouse_point (Tuple[int, int]): Current mouse position in view coordinates
        scale_ptr (Tuple[int, int]): Current mouse position in original image coordinates
        bright_str (str): Current pixel value information string
        mouse_rect (Optional[Tuple[int, int, int, int]]): Current rectangle being drawn
        draw_rects (List[Tuple[int, int, int, int]]): List of completed rectangular ROIs
        draw_lines (List[Tuple[int, int, int, int]]): List of completed line profiles
        draw_polygons (List[List[Tuple[int, int]]]): List of completed polygon regions
        is_line_mode (bool): Whether line drawing mode is active
        is_polygon_mode (bool): Whether polygon drawing mode is active
        selected_roi (Optional[int]): Index of currently selected ROI
        selected_line (Optional[int]): Index of currently selected line
        selected_polygon (Optional[int]): Index of currently selected polygon
        highlight_colors (dict): Color configuration for visual feedback
        selection_animation (dict): Animation configuration for selection effects
    
    Examples:
        >>> # Basic mouse handler setup
        >>> mouse = MouseHandler()
        >>> mouse.mouse_point = (100, 150)
        >>> mouse.bright_str = "BGR:(120,130,140)"
        
        >>> # Rectangle drawing
        >>> mouse.draw_rects.append((10, 10, 50, 30))
        >>> mouse.handle_item_added('roi')
        >>> color = mouse.get_roi_color(0)  # Get display color
        
        >>> # Line drawing mode
        >>> mouse.is_line_mode = True
        >>> mouse.draw_lines.append((0, 0, 100, 100))
        >>> thickness = mouse.get_line_thickness(0)
        
        >>> # Selection management
        >>> mouse.selected_roi = 0
        >>> mouse.update_selection_animation()
        >>> alpha = mouse.get_selection_alpha('roi', 0)
    """
    def __init__(self):
        """Initialize the MouseHandler with default state and configuration.
        
        Creates a new MouseHandler instance with all interaction states reset to defaults,
        empty drawing lists, and predefined color schemes for visual feedback. The
        initialization sets up comprehensive state tracking for multi-modal drawing
        operations and selection management.
        
        The initialization includes:
        - Coordinate tracking variables (mouse_point, scale_ptr)
        - Pixel value display string (bright_str)
        - Drawing state management (button states, drawing modes)
        - Collections for completed drawings (rectangles, lines, polygons)
        - Selection tracking with indices for each element type
        - Color configuration for visual feedback and highlighting
        - Animation system configuration for selection effects
        
        All drawing lists start empty, no selections are active, and the handler
        defaults to rectangle drawing mode. The color scheme provides distinct
        visual feedback for normal, selected, and animated states.
        
        Examples:
            >>> mouse = MouseHandler()
            >>> print(mouse.mouse_point)  # (0, 0)
            >>> print(len(mouse.draw_rects))  # 0
            >>> print(mouse.is_line_mode)  # False
            >>> print(mouse.selected_roi)  # None
            
        Performance:
            Time Complexity: O(1) - constant time initialization.
            Space Complexity: O(1) - fixed memory allocation for state variables.
        """
        self.mouse_point: Tuple[int, int] = (0, 0)
        self.scale_ptr: Tuple[int, int] = (0, 0)
        self.bright_str: str = "Gray: 0"
        self.mouse_rect: Optional[Tuple[int, int, int, int]] = None
        self.draw_rects: List[Tuple[int, int, int, int]] = []
        self.is_left_button_down: bool = False
        self.is_middle_button_down: bool = False
        self.left_button_start: Optional[Tuple[int, int]] = None
        self.middle_button_start: Optional[Tuple[int, int]] = None
        self.middle_button_area_start: Optional[Tuple[int, int]] = None
        
        # Line drawing for pixel profiles
        self.draw_lines: List[Tuple[int, int, int, int]] = []
        self.is_line_mode: bool = False
        self.current_line: Optional[Tuple[int, int, int, int]] = None
        self.line_start: Optional[Tuple[int, int]] = None

        # Polygon drawing
        self.is_polygon_mode: bool = False
        self.current_polygon: List[Tuple[int, int]] = []
        self.draw_polygons: List[List[Tuple[int, int]]] = []

        # Selections
        self.selected_roi: Optional[int] = None
        self.selected_line: Optional[int] = None
        self.selected_polygon: Optional[int] = None
        
        # Selection highlighting colors and styles
        self.highlight_colors = {
            'roi': {
                'selected': (0, 255, 0),     # Green for selected ROI
                'normal': (0, 0, 255),       # Blue for normal ROI
                'thickness': 2,              # Line thickness for ROI
                'alpha': 0.2,                # Transparency for fill
                'label_color': (255, 255, 0) # Yellow for label text
            },
            'line': {
                'selected': (0, 255, 0),     # Green for selected line
                'normal': (255, 0, 255),     # Magenta for normal line
                'thickness': 2,              # Line thickness for lines
                'endpoint_radius': 5,        # Radius for endpoint circles
                'label_color': (255, 255, 0) # Yellow for label text
            },
            'polygon': {
                'selected': (0, 255, 0),     # Green for selected polygon
                'normal': (0, 255, 255),     # Yellow for normal polygon
                'thickness': 2,              # Line thickness for polygons
                'alpha': 0.15,               # Transparency for fill
                'vertex_radius': 4,          # Radius for vertex circles
                'label_color': (255, 255, 0) # Yellow for label text
            }
        }
        
        # Selection animation properties
        self.selection_animation = {
            'enabled': True,           # Whether to animate selections
            'pulse_count': 0,          # Counter for pulsing effect
            'pulse_max': 30,           # Maximum pulse count
            'pulse_direction': 1,      # 1 for increasing, -1 for decreasing
            'pulse_speed': 1,          # Speed of pulsing
            'pulse_min_alpha': 0.1,    # Minimum alpha for pulsing
            'pulse_max_alpha': 0.4     # Maximum alpha for pulsing
        }

    def undo_last_point(self):
        """Remove the last point from the current polygon being drawn.
        
        This method provides undo functionality during polygon drawing operations
        by removing the most recently added point from the current polygon. It
        allows users to correct mistakes while drawing complex polygonal regions
        without having to restart the entire polygon.
        
        The method only operates when a polygon is currently being drawn and
        has at least one point. It safely removes the last point from the
        current_polygon list, effectively undoing the last click operation.
        
        This is typically called in response to keyboard shortcuts (like Ctrl+Z)
        or right-click operations during polygon drawing mode.
        
        Examples:
            >>> mouse = MouseHandler()
            >>> mouse.is_polygon_mode = True
            >>> mouse.current_polygon = [(10, 10), (20, 20), (30, 10)]
            >>> mouse.undo_last_point()
            >>> print(mouse.current_polygon)  # [(10, 10), (20, 20)]
            >>> 
            >>> # Safe to call on empty polygon
            >>> mouse.current_polygon = []
            >>> mouse.undo_last_point()  # No effect
        
        Performance:
            Time Complexity: O(1) - simple list pop operation.
            Space Complexity: O(1) - no additional memory allocation.
        """
        if self.current_polygon:
            self.current_polygon.pop()

    def clear_selections(self):
        """Clear all current selections for ROIs, lines, and polygons.
        
        This method resets all selection states by setting the selected indices
        for ROIs, lines, and polygons to None. This effectively deselects all
        currently selected analysis elements, removing their visual highlighting
        and animation effects.
        
        The method is useful for:
        - Deselecting all elements when switching modes
        - Clearing selections before loading new analysis data
        - Resetting selection state after completing operations
        - Providing a clean slate for new selection operations
        
        After calling this method, no elements will be highlighted as selected,
        and all animation effects will stop until new selections are made.
        
        Examples:
            >>> mouse = MouseHandler()
            >>> mouse.selected_roi = 0
            >>> mouse.selected_line = 1
            >>> mouse.selected_polygon = 0
            >>> mouse.clear_selections()
            >>> print(mouse.has_selections())  # False
            >>> print(mouse.selected_roi)  # None
            
        Performance:
            Time Complexity: O(1) - simple variable assignments.
            Space Complexity: O(1) - no additional memory allocation.
        """
        self.selected_roi = None
        self.selected_line = None
        self.selected_polygon = None
        
    def validate_selections(self):
        """Validate that all selections are within valid ranges and reset invalid ones.
        
        This method ensures that all selection indices (ROI, line, polygon) are within
        valid bounds based on the current number of drawn elements. If any selection
        index is out of bounds (negative or beyond the list length), it is reset to None.
        
        The validation process:
        1. Stores previous selection states to detect changes
        2. Checks each selection type against its corresponding list length
        3. Resets invalid selections to None
        4. Returns information about what selections changed
        
        This method is automatically called by color and styling methods to ensure
        that visual feedback is only applied to valid, existing elements. It prevents
        errors that could occur when elements are deleted or lists are modified.
        
        Returns:
            dict: Information about selection changes with keys:
                - 'roi_changed': bool indicating if ROI selection changed
                - 'line_changed': bool indicating if line selection changed
                - 'polygon_changed': bool indicating if polygon selection changed
                - 'any_changed': bool indicating if any selection changed
                
        Examples:
            >>> mouse = MouseHandler()
            >>> mouse.draw_rects = [(0, 0, 10, 10)]
            >>> mouse.selected_roi = 0  # Valid selection
            >>> changes = mouse.validate_selections()
            >>> print(changes['roi_changed'])  # False (still valid)
            >>> 
            >>> mouse.selected_roi = 5  # Invalid selection
            >>> changes = mouse.validate_selections()
            >>> print(mouse.selected_roi)  # None (reset)
            >>> print(changes['roi_changed'])  # True (changed)
            
        Performance:
            Time Complexity: O(1) - simple bounds checking operations.
            Space Complexity: O(1) - temporary variables for change detection.
        """
        # Store previous selections to detect changes
        prev_roi = self.selected_roi
        prev_line = self.selected_line
        prev_polygon = self.selected_polygon
        
        # Check ROI selection
        if self.selected_roi is not None:
            if self.selected_roi < 0 or self.selected_roi >= len(self.draw_rects):
                self.selected_roi = None
                
        # Check line selection
        if self.selected_line is not None:
            if self.selected_line < 0 or self.selected_line >= len(self.draw_lines):
                self.selected_line = None
                
        # Check polygon selection
        if self.selected_polygon is not None:
            if self.selected_polygon < 0 or self.selected_polygon >= len(self.draw_polygons):
                self.selected_polygon = None
                
        # Return information about what changed
        return {
            'roi_changed': prev_roi != self.selected_roi,
            'line_changed': prev_line != self.selected_line,
            'polygon_changed': prev_polygon != self.selected_polygon,
            'any_changed': (prev_roi != self.selected_roi or 
                           prev_line != self.selected_line or 
                           prev_polygon != self.selected_polygon)
        }
                
    def handle_item_added(self, item_type: str):
        """Handle selection management when a new analysis element is added.
        
        This method automatically selects the most recently added element of the
        specified type, providing immediate visual feedback and focus on newly
        created analysis elements. It follows the principle that users typically
        want to work with the element they just created.
        
        The method updates the appropriate selection index to point to the
        last element in the corresponding list, making it the active selection
        for visual highlighting and potential further operations.
        
        Args:
            item_type: Type of analysis element that was added. Must be one of:
                - 'roi': Rectangular region of interest
                - 'line': Line profile for intensity analysis
                - 'polygon': Polygonal region for complex analysis
                
        Examples:
            >>> mouse = MouseHandler()
            >>> mouse.draw_rects.append((10, 10, 50, 30))
            >>> mouse.handle_item_added('roi')
            >>> print(mouse.selected_roi)  # 0 (first and only ROI selected)
            >>> 
            >>> mouse.draw_lines.append((0, 0, 100, 100))
            >>> mouse.handle_item_added('line')
            >>> print(mouse.selected_line)  # 0 (line now selected)
            >>> 
            >>> # Multiple items - always selects the newest
            >>> mouse.draw_rects.append((20, 20, 60, 40))
            >>> mouse.handle_item_added('roi')
            >>> print(mouse.selected_roi)  # 1 (newest ROI selected)
            
        Performance:
            Time Complexity: O(1) - simple list length check and assignment.
            Space Complexity: O(1) - no additional memory allocation.
        """
        if item_type == 'roi' and self.draw_rects:
            # Select the newly added ROI
            self.selected_roi = len(self.draw_rects) - 1
        elif item_type == 'line' and self.draw_lines:
            # Select the newly added line
            self.selected_line = len(self.draw_lines) - 1
        elif item_type == 'polygon' and self.draw_polygons:
            # Select the newly added polygon
            self.selected_polygon = len(self.draw_polygons) - 1
        
    def get_roi_color(self, index: int) -> Tuple[int, int, int]:
        """Get the appropriate display color for an ROI based on its selection state.
        
        This method returns the correct BGR color tuple for displaying an ROI rectangle,
        automatically selecting between normal and selected colors based on the current
        selection state. It validates selections before determining the color to ensure
        consistency with the actual element list.
        
        Args:
            index: Zero-based index of the ROI in the draw_rects list.
            
        Returns:
            Tuple[int, int, int]: BGR color tuple for OpenCV drawing operations.
                Returns selected color (green) if this ROI is currently selected,
                otherwise returns normal color (blue).
                
        Examples:
            >>> mouse = MouseHandler()
            >>> mouse.draw_rects = [(10, 10, 50, 30), (20, 20, 60, 40)]
            >>> mouse.selected_roi = 0
            >>> color = mouse.get_roi_color(0)
            >>> print(color)  # (0, 255, 0) - green for selected
            >>> color = mouse.get_roi_color(1) 
            >>> print(color)  # (0, 0, 255) - blue for normal
            
        Performance:
            Time Complexity: O(1) - simple comparison and dictionary lookup.
            Space Complexity: O(1) - returns reference to existing color tuple.
        """
        self.validate_selections()
        if index == self.selected_roi:
            return self.highlight_colors['roi']['selected']
        return self.highlight_colors['roi']['normal']
        
    def get_line_color(self, index: int) -> Tuple[int, int, int]:
        """Get the appropriate display color for a line based on its selection state.
        
        This method returns the correct BGR color tuple for displaying a line profile,
        automatically selecting between normal and selected colors based on the current
        selection state. It validates selections before determining the color to ensure
        consistency with the actual element list.
        
        Args:
            index: Zero-based index of the line in the draw_lines list.
            
        Returns:
            Tuple[int, int, int]: BGR color tuple for OpenCV drawing operations.
                Returns selected color (green) if this line is currently selected,
                otherwise returns normal color (magenta).
                
        Examples:
            >>> mouse = MouseHandler()
            >>> mouse.draw_lines = [(0, 0, 100, 100), (50, 50, 150, 150)]
            >>> mouse.selected_line = 1
            >>> color = mouse.get_line_color(1)
            >>> print(color)  # (0, 255, 0) - green for selected
            >>> color = mouse.get_line_color(0)
            >>> print(color)  # (255, 0, 255) - magenta for normal
            
        Performance:
            Time Complexity: O(1) - simple comparison and dictionary lookup.
            Space Complexity: O(1) - returns reference to existing color tuple.
        """
        self.validate_selections()
        if index == self.selected_line:
            return self.highlight_colors['line']['selected']
        return self.highlight_colors['line']['normal']
        
    def get_polygon_color(self, index: int) -> Tuple[int, int, int]:
        """Get the appropriate display color for a polygon based on its selection state.
        
        This method returns the correct BGR color tuple for displaying a polygon region,
        automatically selecting between normal and selected colors based on the current
        selection state. It validates selections before determining the color to ensure
        consistency with the actual element list.
        
        Args:
            index: Zero-based index of the polygon in the draw_polygons list.
            
        Returns:
            Tuple[int, int, int]: BGR color tuple for OpenCV drawing operations.
                Returns selected color (green) if this polygon is currently selected,
                otherwise returns normal color (cyan).
                
        Examples:
            >>> mouse = MouseHandler()
            >>> mouse.draw_polygons = [[(10, 10), (20, 10), (15, 20)], [(30, 30), (40, 30), (35, 40)]]
            >>> mouse.selected_polygon = 0
            >>> color = mouse.get_polygon_color(0)
            >>> print(color)  # (0, 255, 0) - green for selected
            >>> color = mouse.get_polygon_color(1)
            >>> print(color)  # (0, 255, 255) - cyan for normal
            
        Performance:
            Time Complexity: O(1) - simple comparison and dictionary lookup.
            Space Complexity: O(1) - returns reference to existing color tuple.
        """
        self.validate_selections()
        if index == self.selected_polygon:
            return self.highlight_colors['polygon']['selected']
        return self.highlight_colors['polygon']['normal']
        
    def get_roi_thickness(self, index: int) -> int:
        """Get the appropriate line thickness for an ROI based on its selection state.
        
        This method returns the correct line thickness for drawing ROI rectangles,
        providing enhanced visual feedback for selected elements by increasing
        their thickness. Selected ROIs are drawn with thicker lines to make
        them more prominent and easier to identify.
        
        Args:
            index: Zero-based index of the ROI in the draw_rects list.
            
        Returns:
            int: Line thickness in pixels. Returns base thickness + 1 for selected ROI,
                base thickness for normal ROI.
                
        Examples:
            >>> mouse = MouseHandler()
            >>> mouse.draw_rects = [(10, 10, 50, 30), (20, 20, 60, 40)]
            >>> mouse.selected_roi = 0
            >>> thickness = mouse.get_roi_thickness(0)
            >>> print(thickness)  # 3 (base 2 + 1 for selected)
            >>> thickness = mouse.get_roi_thickness(1)
            >>> print(thickness)  # 2 (base thickness for normal)
            
        Performance:
            Time Complexity: O(1) - simple comparison and arithmetic.
            Space Complexity: O(1) - no additional memory allocation.
        """
        base_thickness = self.highlight_colors['roi']['thickness']
        return base_thickness + 1 if index == self.selected_roi else base_thickness
        
    def get_line_thickness(self, index: int) -> int:
        """Get the appropriate line thickness for a line profile based on its selection state.
        
        This method returns the correct line thickness for drawing line profiles,
        providing enhanced visual feedback for selected elements by increasing
        their thickness. Selected lines are drawn with thicker strokes to make
        them more prominent and easier to identify during analysis.
        
        Args:
            index: Zero-based index of the line in the draw_lines list.
            
        Returns:
            int: Line thickness in pixels. Returns base thickness + 1 for selected line,
                base thickness for normal line.
                
        Examples:
            >>> mouse = MouseHandler()
            >>> mouse.draw_lines = [(0, 0, 100, 100), (50, 50, 150, 150)]
            >>> mouse.selected_line = 1
            >>> thickness = mouse.get_line_thickness(1)
            >>> print(thickness)  # 3 (base 2 + 1 for selected)
            >>> thickness = mouse.get_line_thickness(0)
            >>> print(thickness)  # 2 (base thickness for normal)
            
        Performance:
            Time Complexity: O(1) - simple comparison and arithmetic.
            Space Complexity: O(1) - no additional memory allocation.
        """
        base_thickness = self.highlight_colors['line']['thickness']
        return base_thickness + 1 if index == self.selected_line else base_thickness
        
    def get_polygon_thickness(self, index: int) -> int:
        """Get the appropriate line thickness for a polygon based on its selection state.
        
        This method returns the correct line thickness for drawing polygon outlines,
        providing enhanced visual feedback for selected elements by increasing
        their thickness. Selected polygons are drawn with thicker lines to make
        them more prominent and easier to identify during complex region analysis.
        
        Args:
            index: Zero-based index of the polygon in the draw_polygons list.
            
        Returns:
            int: Line thickness in pixels. Returns base thickness + 1 for selected polygon,
                base thickness for normal polygon.
                
        Examples:
            >>> mouse = MouseHandler()
            >>> mouse.draw_polygons = [[(10, 10), (20, 10), (15, 20)], [(30, 30), (40, 30), (35, 40)]]
            >>> mouse.selected_polygon = 0
            >>> thickness = mouse.get_polygon_thickness(0)
            >>> print(thickness)  # 3 (base 2 + 1 for selected)
            >>> thickness = mouse.get_polygon_thickness(1)
            >>> print(thickness)  # 2 (base thickness for normal)
            
        Performance:
            Time Complexity: O(1) - simple comparison and arithmetic.
            Space Complexity: O(1) - no additional memory allocation.
        """
        base_thickness = self.highlight_colors['polygon']['thickness']
        return base_thickness + 1 if index == self.selected_polygon else base_thickness
        
    def update_selection_animation(self):
        """Update the animation state for selection highlighting effects.
        
        This method advances the animation frame for selection highlighting,
        creating a pulsing transparency effect for selected elements. The
        animation uses a counter that oscillates between minimum and maximum
        values, reversing direction at the limits to create a smooth pulsing effect.
        
        The animation system is controlled by the selection_animation configuration
        dictionary and can be disabled by setting 'enabled' to False. When enabled,
        it updates the pulse counter based on speed and direction settings.
        
        This method should be called regularly (typically in the main display loop)
        to maintain smooth animation effects. The updated animation state is used
        by get_selection_alpha() to calculate transparency values.
        
        Examples:
            >>> mouse = MouseHandler()
            >>> # Enable animation and update in main loop
            >>> mouse.selection_animation['enabled'] = True
            >>> for frame in range(100):
            ...     mouse.update_selection_animation()
            ...     alpha = mouse.get_selection_alpha('roi', 0)
            ...     # Use alpha for rendering with pulsing effect
            
        Performance:
            Time Complexity: O(1) - simple arithmetic operations.
            Space Complexity: O(1) - modifies existing animation state.
        """
        if not self.selection_animation['enabled']:
            return
            
        # Update pulse counter
        self.selection_animation['pulse_count'] += self.selection_animation['pulse_direction'] * self.selection_animation['pulse_speed']
        
        # Reverse direction at limits
        if self.selection_animation['pulse_count'] >= self.selection_animation['pulse_max']:
            self.selection_animation['pulse_direction'] = -1
        elif self.selection_animation['pulse_count'] <= 0:
            self.selection_animation['pulse_direction'] = 1
            
    def get_selection_alpha(self, item_type: str, index: int) -> float:
        """Get the current alpha transparency value for selection highlighting based on animation state.
        
        This method calculates the appropriate alpha (transparency) value for rendering
        selected elements with pulsing animation effects. For non-selected elements,
        it returns the base alpha value from the color configuration. For selected
        elements, it calculates an animated alpha value based on the current animation
        frame, creating a smooth pulsing effect.
        
        The animation creates a visual heartbeat effect that makes selected elements
        pulse between minimum and maximum alpha values, providing clear visual feedback
        about which elements are currently selected.
        
        Args:
            item_type: Type of analysis element. Must be one of 'roi', 'line', or 'polygon'.
            index: Zero-based index of the element in the corresponding list.
            
        Returns:
            float: Alpha transparency value between 0.0 (fully transparent) and 1.0
                (fully opaque). For non-selected items, returns the base alpha value.
                For selected items, returns an animated alpha value creating pulsing effects.
                
        Examples:
            >>> mouse = MouseHandler()
            >>> mouse.draw_rects = [(10, 10, 50, 30)]
            >>> mouse.selected_roi = 0
            >>> mouse.selection_animation['enabled'] = True
            >>> alpha = mouse.get_selection_alpha('roi', 0)
            >>> print(f"Alpha: {alpha:.2f}")  # Animated value between min and max
            >>> 
            >>> alpha = mouse.get_selection_alpha('roi', 1)  # Non-selected
            >>> print(f"Alpha: {alpha:.2f}")  # Base alpha value
            
        Performance:
            Time Complexity: O(1) - simple calculations and comparisons.
            Space Complexity: O(1) - no additional memory allocation.
        """
        # Check if this item is selected
        is_selected = False
        if item_type == 'roi' and index == self.selected_roi:
            is_selected = True
        elif item_type == 'line' and index == self.selected_line:
            is_selected = True
        elif item_type == 'polygon' and index == self.selected_polygon:
            is_selected = True
            
        if not is_selected:
            # Return base alpha for non-selected items
            return self.highlight_colors[item_type]['alpha']
            
        # For selected items, calculate animated alpha
        if not self.selection_animation['enabled']:
            return self.highlight_colors[item_type]['alpha'] * 2  # Higher alpha for selected items
            
        # Calculate alpha based on pulse animation
        min_alpha = self.selection_animation['pulse_min_alpha']
        max_alpha = self.selection_animation['pulse_max_alpha']
        pulse_ratio = self.selection_animation['pulse_count'] / self.selection_animation['pulse_max']
        
        return min_alpha + (max_alpha - min_alpha) * pulse_ratio
        
    def has_selections(self) -> bool:
        """Check if any analysis elements are currently selected.
        
        This method provides a quick way to determine if any ROIs, lines, or polygons
        are currently selected for highlighting or operations. It's useful for
        conditional rendering, enabling/disabling UI elements, and determining
        whether selection-specific operations should be available.
        
        Returns:
            bool: True if at least one element (ROI, line, or polygon) is currently
                selected, False if no elements are selected.
                
        Examples:
            >>> mouse = MouseHandler()
            >>> print(mouse.has_selections())  # False - no selections
            >>> mouse.selected_roi = 0
            >>> print(mouse.has_selections())  # True - ROI selected
            >>> mouse.clear_selections()
            >>> print(mouse.has_selections())  # False - all cleared
            
        Performance:
            Time Complexity: O(1) - simple boolean checks.
            Space Complexity: O(1) - no additional memory allocation.
        """
        return self.selected_roi is not None or self.selected_line is not None or self.selected_polygon is not None
        
    def get_selection_info(self) -> dict:
        """Get comprehensive information about current selections and element counts.
        
        This method provides a detailed summary of the current selection state,
        including which specific elements are selected and the total count of
        each element type. It validates selections first to ensure the returned
        information is accurate and consistent with the actual element lists.
        
        The returned information is useful for UI updates, status displays,
        analytics reporting, and debugging selection-related issues.
        
        Returns:
            dict: Comprehensive selection information with the following structure:
                - 'has_selection': bool indicating if any elements are selected
                - 'roi': dict with 'selected' (index or None) and 'count' (total ROIs)
                - 'line': dict with 'selected' (index or None) and 'count' (total lines)
                - 'polygon': dict with 'selected' (index or None) and 'count' (total polygons)
                
        Examples:
            >>> mouse = MouseHandler()
            >>> mouse.draw_rects = [(10, 10, 50, 30), (20, 20, 60, 40)]
            >>> mouse.draw_lines = [(0, 0, 100, 100)]
            >>> mouse.selected_roi = 1
            >>> info = mouse.get_selection_info()
            >>> print(info)
            {
                'has_selection': True,
                'roi': {'selected': 1, 'count': 2},
                'line': {'selected': None, 'count': 1},
                'polygon': {'selected': None, 'count': 0}
            }
            
        Performance:
            Time Complexity: O(1) - simple attribute access and dictionary creation.
            Space Complexity: O(1) - fixed-size dictionary structure.
        """
        self.validate_selections()
        
        info = {
            'has_selection': self.has_selections(),
            'roi': {
                'selected': self.selected_roi,
                'count': len(self.draw_rects)
            },
            'line': {
                'selected': self.selected_line,
                'count': len(self.draw_lines)
            },
            'polygon': {
                'selected': self.selected_polygon,
                'count': len(self.draw_polygons)
            }
        }
        
        return info