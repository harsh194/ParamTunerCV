from typing import List, Tuple, Optional

class MouseHandler:
    """Manages mouse interactions and state."""
    def __init__(self):
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
        if self.current_polygon:
            self.current_polygon.pop()

    def clear_selections(self):
        self.selected_roi = None
        self.selected_line = None
        self.selected_polygon = None
        
    def validate_selections(self):
        """Validate that all selections are within valid ranges."""
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
        """
        Handle selection when a new item is added.
        
        Args:
            item_type: Type of item added ('roi', 'line', 'polygon')
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
        """Get the color for a ROI based on whether it's selected."""
        self.validate_selections()
        if index == self.selected_roi:
            return self.highlight_colors['roi']['selected']
        return self.highlight_colors['roi']['normal']
        
    def get_line_color(self, index: int) -> Tuple[int, int, int]:
        """Get the color for a line based on whether it's selected."""
        self.validate_selections()
        if index == self.selected_line:
            return self.highlight_colors['line']['selected']
        return self.highlight_colors['line']['normal']
        
    def get_polygon_color(self, index: int) -> Tuple[int, int, int]:
        """Get the color for a polygon based on whether it's selected."""
        self.validate_selections()
        if index == self.selected_polygon:
            return self.highlight_colors['polygon']['selected']
        return self.highlight_colors['polygon']['normal']
        
    def get_roi_thickness(self, index: int) -> int:
        """Get the line thickness for a ROI based on whether it's selected."""
        base_thickness = self.highlight_colors['roi']['thickness']
        return base_thickness + 1 if index == self.selected_roi else base_thickness
        
    def get_line_thickness(self, index: int) -> int:
        """Get the line thickness for a line based on whether it's selected."""
        base_thickness = self.highlight_colors['line']['thickness']
        return base_thickness + 1 if index == self.selected_line else base_thickness
        
    def get_polygon_thickness(self, index: int) -> int:
        """Get the line thickness for a polygon based on whether it's selected."""
        base_thickness = self.highlight_colors['polygon']['thickness']
        return base_thickness + 1 if index == self.selected_polygon else base_thickness
        
    def update_selection_animation(self):
        """Update the animation state for selection highlighting."""
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
        """
        Get the current alpha value for selection highlighting based on animation state.
        
        Args:
            item_type: Type of item ('roi', 'line', 'polygon')
            index: Index of the item
            
        Returns:
            float: Alpha value for transparency
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
        """Check if any selections are active."""
        return self.selected_roi is not None or self.selected_line is not None or self.selected_polygon is not None
        
    def get_selection_info(self) -> dict:
        """
        Get information about current selections.
        
        Returns:
            dict: Information about current selections
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