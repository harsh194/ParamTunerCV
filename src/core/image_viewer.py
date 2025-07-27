import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Union, Callable, Protocol, TypeVar
import textwrap
import traceback
# Removed threading import - not needed for single-threaded architecture

from ..config.viewer_config import ViewerConfig
from ..events.mouse_handler import MouseHandler
from ..controls.trackbar_manager import TrackbarManager
from ..gui.window_manager import WindowManager
from ..analysis import ImageAnalyzer
from ..analysis.plotting.plot_analyzer import MATPLOTLIB_AVAILABLE
from ..gui.analysis_control_window import AnalysisControlWindow, TKINTER_AVAILABLE

T = TypeVar('T')

class ImageProcessor(Protocol):
    def __call__(self, params: Dict[str, Any], log_func: Callable[[str], None]) -> List[Tuple[np.ndarray, str]]: ...

class ImageViewer:
    """
    A flexible image viewer with interactive features.
    """
    def __init__(self, config: ViewerConfig = None, trackbar_definitions: List[Dict[str, Any]] = None, app_debug_mode: bool = True, max_headless_iterations: int = 1, text_window: bool = True, analysis_control_window: bool = True):
        self.config = config if config else ViewerConfig()
        
        if trackbar_definitions:
            self.config.trackbar = trackbar_definitions
        
        self.config.enable_debug = app_debug_mode
        
        self.max_headless_iterations = max_headless_iterations
        self._headless_iteration_count = 0
        self._app_debug_mode = app_debug_mode
        self._show_text_window_enabled = text_window
        self._show_analysis_control_window_enabled = analysis_control_window
        
        self.mouse = MouseHandler()
        self.trackbar = TrackbarManager(self.config.trackbar_window_name)
        self.windows = WindowManager(self.config)
        self.analyzer = ImageAnalyzer()
        if self._show_analysis_control_window_enabled:
            self.analysis_window = AnalysisControlWindow(self)
        else:
            self.analysis_window = None
        
        self._internal_images: List[Tuple[np.ndarray, str]] = []
        self._should_continue_loop: bool = True
        self._auto_initialized = False

        self.current_image_dims: Optional[Tuple[int, int]] = None
        self.size_ratio: float = 1.0
        self.show_area: List[int] = [0, 0, self.config.screen_width, self.config.screen_height]
        self.address: str = "(0,0)"
        self.text_image: np.ndarray = np.full(
            (self.config.text_window_height, self.config.text_window_width, 3), 255, dtype=np.uint8
        )
        self.log_texts: List[str] = []
        self.initial_window_size: Tuple[int, int] = (self.config.screen_width, self.config.screen_height)
        self.user_image_processor: Optional[ImageProcessor] = None
        self.image_processing_func_internal: Optional[ImageProcessor] = None
        self._params_changed: bool = False
        self._cached_scaled_image = None
        self._cached_size_ratio = None
        self._cached_show_area = None
        # Removed locks - not needed for single-threaded architecture
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        self._auto_setup()

    def _auto_setup(self):
        if not self._auto_initialized and self.config.trackbar:
            self.setup_viewer()
            self._auto_initialized = True

    @property
    def display_images(self) -> List[Tuple[np.ndarray, str]]:
        return self._internal_images

    @display_images.setter
    def display_images(self, image_list: List[Tuple[np.ndarray, str]]):
        if not isinstance(image_list, list) or \
           not all(isinstance(item, tuple) and len(item) == 2 and \
                    isinstance(item[0], np.ndarray) and item[0].size > 0 for item in image_list):
            print(f"Error: display_images with invalid format/empty image. Input type: {type(image_list)}")
            self._internal_images = [(np.zeros((self.config.min_window_size[1],self.config.min_window_size[0],1), dtype=np.uint8), "Image Set Error")]
        else:
            self._internal_images = image_list
        
        if self.config.enable_debug and self._should_continue_loop:
            # Process both OpenCV and tkinter events in proper sequence
            try:
                if hasattr(self, '_process_frame_and_check_quit'):
                    self._process_frame_and_check_quit()
                # Process tkinter events after OpenCV operations
                self._process_tk_events()
            except Exception as e:
                print(f"Error in process_frame: {e}")
        
        if not self.config.enable_debug:
            self._headless_iteration_count += 1

    def _process_frame_and_check_quit(self):
        if not self.config.enable_debug: return
        if not self._should_continue_loop: return
        if not self.windows.windows_created:
             print("Warning: _process_frame_and_check_quit called but windows not created (debug on).")
             self._should_continue_loop = False
             return

        if not self._internal_images:
            self._internal_images = [(np.zeros((100,100,1), dtype=np.uint8), "No Images (internal)")]
        
        try:
            # Only call OpenCV-related functions
            self._update_show_trackbar()
            self._process_image_for_display()
            if self._show_text_window_enabled:
                self._show_text_window()
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:
                pass
                self._should_continue_loop = False
            elif key == ord('r'): 
                self.reset_view()
        except Exception as e:
            print(f"Error in process_frame: {e}")
        
        try:
            if self._should_continue_loop and \
               cv2.getWindowProperty(self.config.process_window_name, cv2.WND_PROP_VISIBLE) < 1:
                pass
                self._should_continue_loop = False
        except cv2.error:
            if self._should_continue_loop:
                 pass
                 self._should_continue_loop = False

    def should_loop_continue(self) -> bool:
        if not self.config.enable_debug:
            if self._headless_iteration_count >= self.max_headless_iterations:
                pass
                return False
            return True
        else:
            return self._should_continue_loop

    def setup_viewer(
                     self,
                     initial_images_for_first_frame: Optional[List[Tuple[np.ndarray, str]]] = None,
                     image_processor_func: Optional[ImageProcessor] = None):
        self.clear_log()
        pass
        self._should_continue_loop = True
        self.user_image_processor = image_processor_func
        self._initialize_parameters()

        if self.config.enable_debug:
            self.windows.create_windows(self._mouse_callback, self._text_mouse_callback, self._show_text_window_enabled)
            if not self.windows.windows_created:
                pass
                print("FATAL: UI Mode: ImageViewer failed to create windows.")
                self._should_continue_loop = False
            else:
                if self._show_analysis_control_window_enabled and self.analysis_window:
                    self.analysis_window.create_window()

        temp_images = []
        if self.user_image_processor:
            pass
            try:
                temp_images = self.user_image_processor(dict(self.trackbar.parameters), self.log)
            except Exception as e:
                print(f"ERROR in user processor (initial frame): {e}\n{traceback.format_exc()}")
                temp_images = [(np.zeros((100,100,1), dtype=np.uint8), "Init Proc Error")]
        elif initial_images_for_first_frame is not None:
            temp_images = initial_images_for_first_frame
        else:
            temp_images = [(np.zeros((100,100,1), dtype=np.uint8), "Initial Empty")]
        self._internal_images = temp_images

        if self.config.enable_debug and self.config.trackbar and self.windows.windows_created:
            pass
            for trackbar_config_item in self.config.trackbar:
                self.trackbar.create_trackbar(trackbar_config_item, self)
        
        if self.config.enable_debug and self._should_continue_loop:
            self._process_frame_and_check_quit()
        
        pass

    def update_display(self, image_list: Optional[List[Tuple[np.ndarray, str]]] = None):
        if self.user_image_processor:
            if not self._should_continue_loop and self.config.enable_debug: return
            try:
                processed_images = self.user_image_processor(dict(self.trackbar.parameters), self.log)
                self.display_images = processed_images
            except Exception as e:
                print(f"ERROR in user_image_processor: {e}\n{traceback.format_exc()}")
                self.display_images = [(np.zeros((100,100,1), dtype=np.uint8), "Proc Error")]
        elif image_list is not None:
            self.display_images = image_list
        elif self.config.enable_debug and self._should_continue_loop:
            self._process_frame_and_check_quit()

    def _initialize_parameters(self):
        if not self.config.trackbar:
            return

        for tb_conf in self.config.trackbar:
            param_name = tb_conf.get('param_name')
            if not param_name:
                print(f"Warning: Trackbar config item missing 'param_name': {tb_conf}")
                continue
            initial_value_from_config = tb_conf.get('initial_value', 0)
            callback_spec = tb_conf.get('callback')
            if callback_spec == 'odd':
                temp_val = max(1, initial_value_from_config)
                if temp_val % 2 == 0: temp_val += 1
                initial_value_from_config = temp_val
            if param_name in self.trackbar.persistent_values:
                self.trackbar.parameters[param_name] = self.trackbar.persistent_values[param_name]
            else:
                self.trackbar.parameters[param_name] = initial_value_from_config
                self.trackbar.persistent_values[param_name] = initial_value_from_config

    def clear_log(self):
        self.log_texts = []
        self.text_image = np.full((self.config.text_window_height, self.config.text_window_width, 3), 255, dtype=np.uint8)

    def log(self, message: str):
        if self.config.enable_debug:
            max_log_entries = 200 
            message_str = str(message)
            char_width_approx = 8 
            wrap_width = (self.config.text_window_width - 20) // char_width_approx
            if wrap_width <=0: wrap_width = 10
            wrapped_lines = [line for msg_line in message_str.strip().split('\n') 
                             for line in textwrap.wrap(msg_line, width=wrap_width, 
                                                        replace_whitespace=False, drop_whitespace=False)]
            self.log_texts.extend(wrapped_lines)
            if len(self.log_texts) > max_log_entries:
                self.log_texts = self.log_texts[-max_log_entries:]
            required_height = len(self.log_texts) * self.config.text_line_height + self.config.text_line_height 
            current_height, current_width, _ = self.text_image.shape
            if required_height > current_height or \
               (required_height < current_height / 1.5 and current_height > self.config.text_window_height * 1.2) :
                new_height = max(self.config.text_window_height, required_height)
                try:
                    self.text_image = np.full((new_height, current_width, 3), 255, dtype=np.uint8)
                except (ValueError, MemoryError) as e: 
                    print(f"Error resizing text_image for log: {e}.")
                    self.text_image = np.full((self.config.text_window_height, current_width, 3), 255, dtype=np.uint8)
            self.text_image.fill(255) 
            y_pos = self.config.text_line_height
            for line_text in self.log_texts:
                if y_pos > self.text_image.shape[0] - self.config.text_line_height: break
                cv2.putText(self.text_image, line_text, (5, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                y_pos += self.config.text_line_height
        else:
            print(f"LOG-HL: {message}")
    
    def reset_view(self):
        if not self.config.enable_debug: return
        self.size_ratio = 1.0
        self.show_area[0], self.show_area[1] = 0, 0
        if self.current_image_dims:
            self.windows.resize_process_window(self.current_image_dims[1], self.current_image_dims[0])
        else:
             self.windows.resize_process_window(self.initial_window_size[0], self.initial_window_size[1])
        pass

    def _update_show_trackbar(self):
        if not self.config.enable_debug or not self.windows.windows_created or not self.config.trackbar: return
        show_tb_config = next((tc for tc in self.config.trackbar if tc.get('param_name') == 'show'), None)
        if not show_tb_config or show_tb_config.get('max_value') != 'num_images-1': return
        show_tb_display_name = show_tb_config.get('name')
        if not show_tb_display_name: return
        new_max_show = max(0, len(self.display_images) - 1 if self.display_images else 0)
        try:
            if cv2.getWindowProperty(self.config.trackbar_window_name, cv2.WND_PROP_VISIBLE) >= 1:
                cv2.setTrackbarMax(show_tb_display_name, self.config.trackbar_window_name, new_max_show)
                current_show_val = self.trackbar.parameters.get('show', 0)
                if current_show_val > new_max_show:
                    self.trackbar.parameters['show'] = new_max_show
                    self.trackbar.persistent_values['show'] = new_max_show
                    cv2.setTrackbarPos(show_tb_display_name, self.config.trackbar_window_name, new_max_show)
        except cv2.error: pass

    def _process_image_for_display(self) -> Optional[Tuple[np.ndarray, float, Tuple[int, int]]]:
        try:
            if not self.config.enable_debug or not self.windows.windows_created: return None
            if not self.display_images:
                placeholder = np.full((self.config.screen_height, self.config.screen_width, 3), 50, dtype=np.uint8)
                cv2.putText(placeholder, "No images loaded", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                if self.windows.windows_created and cv2.getWindowProperty(self.config.process_window_name, cv2.WND_PROP_VISIBLE) >=1:
                     cv2.imshow(self.config.process_window_name, placeholder)
                return None

            current_idx = self.trackbar.parameters.get('show', 0)
            current_idx = max(0, min(current_idx, len(self.display_images) - 1))
            
            if not (0 <= current_idx < len(self.display_images) and \
                    isinstance(self.display_images[current_idx], tuple) and \
                    len(self.display_images[current_idx]) == 2 and\
                    isinstance(self.display_images[current_idx][0], np.ndarray) and\
                    self.display_images[current_idx][0].size > 0 ):
                print(f"Error: Invalid image data at index {current_idx}.")
                return None

            original_image, name = self.display_images[current_idx]
            self.current_image_dims = original_image.shape[:2]

            try:
                display_image = original_image.copy()
                if len(display_image.shape) == 2: display_image = cv2.cvtColor(display_image, cv2.COLOR_GRAY2BGR)
                elif display_image.shape[2] == 1: display_image = cv2.cvtColor(display_image, cv2.COLOR_GRAY2BGR)
                elif display_image.shape[2] == 4: display_image = cv2.cvtColor(display_image, cv2.COLOR_BGRA2BGR)
                elif display_image.shape[2] != 3:
                     display_image = display_image[:,:,:3] if display_image.shape[2] > 3 else cv2.cvtColor(display_image, cv2.COLOR_GRAY2BGR)

                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                font_thickness = 1
                text_color_rect_info = (0, 255, 255)

                if self.mouse.mouse_rect:
                    x, y, w, h = self.mouse.mouse_rect
                    if w > 0 and h > 0:
                        cv2.rectangle(display_image, (x, y), (x + w, y + h), (0, 255, 0), 1)
                        roi_info_text = f"({x},{y}) {w}x{h}"
                        text_y_pos = y - 5 if y - 5 > 10 else y + 15
                        cv2.putText(display_image, roi_info_text, (x, text_y_pos), \
                                    font, font_scale, text_color_rect_info, font_thickness, cv2.LINE_AA)

                # Update selection animation state
                self.mouse.update_selection_animation()
                
                for i, rect_coords in enumerate(self.mouse.draw_rects):
                    x, y, w, h = rect_coords
                    if w > 0 and h > 0:
                        color = self.mouse.get_roi_color(i)
                        thickness = self.mouse.get_roi_thickness(i)
                        
                        # Draw the ROI rectangle
                        cv2.rectangle(display_image, (x, y), (x + w, y + h), color, thickness)
                        
                        # Add a semi-transparent highlight fill for selected ROI
                        if i == self.mouse.selected_roi:
                            overlay = display_image.copy()
                            cv2.rectangle(overlay, (x, y), (x + w, y + h), color, -1)  # Filled rectangle
                            alpha = self.mouse.get_selection_alpha('roi', i)  # Get animated alpha
                            cv2.addWeighted(overlay, alpha, display_image, 1 - alpha, 0, display_image)
                            
                            # Add a pulsing border for better visibility
                            cv2.rectangle(display_image, 
                                         (x-2, y-2), 
                                         (x + w + 2, y + h + 2), 
                                         color, 
                                         1, 
                                         cv2.LINE_AA)
                        
                        # Add ROI info text
                        roi_info_text = f"R{i+1}: ({x},{y}) {w}x{h}"
                        text_y_pos = y - 7 if y - 7 > 10 else y + 20
                        
                        # Use different text color for selected ROI
                        text_color = self.mouse.highlight_colors['roi']['label_color'] if i == self.mouse.selected_roi else text_color_rect_info
                        
                        cv2.putText(display_image, roi_info_text, (x, text_y_pos), \
                                    font, font_scale, text_color, font_thickness, cv2.LINE_AA)

                if self.mouse.current_line and self.mouse.is_line_mode:
                    x1, y1, x2, y2 = self.mouse.current_line
                    cv2.line(display_image, (x1, y1), (x2, y2), (255, 255, 0), 2)
                    line_info_text = f"({x1},{y1})-({x2},{y2})"
                    cv2.putText(display_image, line_info_text, (x1, y1 - 10), \
                                font, font_scale, (255, 255, 0), font_thickness, cv2.LINE_AA)

                for i, line_coords in enumerate(self.mouse.draw_lines):
                    x1, y1, x2, y2 = line_coords
                    color = self.mouse.get_line_color(i)
                    thickness = self.mouse.get_line_thickness(i)
                    
                    # Draw the line with appropriate color and thickness
                    cv2.line(display_image, (x1, y1), (x2, y2), color, thickness)
                    
                    # Add visual emphasis for selected line
                    if i == self.mouse.selected_line:
                        # Draw small circles at the endpoints for better visibility
                        endpoint_radius = self.mouse.highlight_colors['line']['endpoint_radius']
                        cv2.circle(display_image, (x1, y1), endpoint_radius, color, -1)  # Filled circle at start
                        cv2.circle(display_image, (x2, y2), endpoint_radius, color, -1)  # Filled circle at end
                        
                        # Draw a slightly thicker line for better visibility
                        cv2.line(display_image, (x1, y1), (x2, y2), color, thickness + 1, cv2.LINE_AA)
                        
                        # Draw a parallel line with animation effect
                        # Calculate perpendicular vector for offset
                        dx, dy = x2 - x1, y2 - y1
                        length = max(1, (dx**2 + dy**2)**0.5)
                        perpx, perpy = -dy/length * 3, dx/length * 3  # Perpendicular vector with length 3
                        
                        # Draw parallel line with slight offset
                        cv2.line(display_image, 
                                (int(x1 + perpx), int(y1 + perpy)), 
                                (int(x2 + perpx), int(y2 + perpy)), 
                                color, 1, cv2.LINE_AA)
                    
                    # Add line info text
                    line_info_text = f"L{i+1}: ({x1},{y1})-({x2},{y2})"
                    text_x = x1 + 5
                    text_y = y1 - 5 if y1 - 5 > 10 else y1 + 15
                    
                    # Use different text color for selected line
                    text_color = self.mouse.highlight_colors['line']['label_color'] if i == self.mouse.selected_line else color
                    
                    cv2.putText(display_image, line_info_text, (text_x, text_y), \
                                font, font_scale, text_color, font_thickness, cv2.LINE_AA)

                # Draw polygons
                for i, polygon in enumerate(self.mouse.draw_polygons):
                    if len(polygon) > 1:
                        pts = np.array(polygon, np.int32)
                        pts = pts.reshape((-1, 1, 2))
                        color = self.mouse.get_polygon_color(i)
                        thickness = self.mouse.get_polygon_thickness(i)
                        
                        # Draw the polygon outline
                        cv2.polylines(display_image, [pts], True, color, thickness)
                        
                        # Add visual emphasis for selected polygon
                        if i == self.mouse.selected_polygon:
                            # Fill polygon with semi-transparent color
                            overlay = display_image.copy()
                            cv2.fillPoly(overlay, [pts], color)
                            alpha = self.mouse.get_selection_alpha('polygon', i)  # Get animated alpha
                            cv2.addWeighted(overlay, alpha, display_image, 1 - alpha, 0, display_image)
                            
                            # Draw vertices with circles for better visibility
                            for point in polygon:
                                cv2.circle(display_image, point, 
                                          self.mouse.highlight_colors['polygon']['vertex_radius'], 
                                          color, -1)  # Filled circle at each vertex
                            
                            # Draw a slightly larger outline for better visibility
                            cv2.polylines(display_image, [pts], True, color, thickness + 1, cv2.LINE_AA)
                                
                        # Add polygon info text
                        if len(polygon) > 0:
                            text_x, text_y = polygon[0]
                            text_y = text_y - 10 if text_y - 10 > 10 else text_y + 20
                            
                            # Use different text color for selected polygon
                            text_color = self.mouse.highlight_colors['polygon']['label_color'] if i == self.mouse.selected_polygon else color
                            
                            cv2.putText(display_image, f"Polygon {i+1}: {len(polygon)} points", 
                                        (text_x, text_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

                # Draw current polygon
                if self.mouse.is_polygon_mode and len(self.mouse.current_polygon) > 0:
                    # Draw lines between vertices
                    pts = np.array(self.mouse.current_polygon, np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(display_image, [pts], False, (255, 255, 0), 1)

                    # Draw a hollow circle at each vertex
                    for point in self.mouse.current_polygon:
                        cv2.circle(display_image, point, 5, (0, 255, 255), 1) # Yellow hollow circle

                    # Draw a line to the current mouse position to show the next segment
                    if self.mouse.scale_ptr:
                        cv2.line(display_image, self.mouse.current_polygon[-1], self.mouse.scale_ptr, (255, 255, 0), 1)

                    # Draw a line from the last point to the first point to show how to close it
                    if len(self.mouse.current_polygon) > 1:
                        cv2.line(display_image, self.mouse.current_polygon[-1], self.mouse.current_polygon[0], (0, 255, 255), 1, cv2.LINE_AA)

                orig_h, orig_w = display_image.shape[:2]
                scaled_w, scaled_h = int(orig_w * self.size_ratio), int(orig_h * self.size_ratio)
                
                if scaled_w <= 0 or scaled_h <= 0: 
                    min_dim_on_screen = 10 
                    self.size_ratio = max(self.config.min_size_ratio, float(min_dim_on_screen) / max(orig_w, orig_h, 1))
                    scaled_w = max(min_dim_on_screen, int(orig_w * self.size_ratio))
                    scaled_h = max(min_dim_on_screen, int(orig_h * self.size_ratio))
                
                view_w, view_h = self.config.screen_width, self.config.screen_height
                try: 
                    _wx, _wy, current_win_w, current_win_h = cv2.getWindowImageRect(self.config.process_window_name)
                    max_win_w = self.config.desktop_resolution[0] if self.config.desktop_resolution else self.config.screen_width * 2
                    max_win_h = self.config.desktop_resolution[1] if self.config.desktop_resolution else self.config.screen_height * 2
                    target_win_w = max(self.config.min_window_size[0], min(scaled_w, max_win_w))
                    target_win_h = max(self.config.min_window_size[1], min(scaled_h, max_win_h))

                    if abs(current_win_w - target_win_w) > 1 or abs(current_win_h - target_win_h) > 1 :
                        self.windows.resize_process_window(target_win_w, target_win_h)
                    _wx, _wy, view_w, view_h = cv2.getWindowImageRect(self.config.process_window_name)
                except cv2.error: pass 
                view_w, view_h = max(1, view_w), max(1, view_h)

                scaled_image_for_roi = cv2.resize(display_image, (scaled_w, scaled_h), interpolation=cv2.INTER_NEAREST)
                
                max_show_x = max(0, scaled_w - view_w)
                max_show_y = max(0, scaled_h - view_h)
                self.show_area[0] = max(0, min(self.show_area[0], max_show_x))
                self.show_area[1] = max(0, min(self.show_area[1], max_show_y))
                
                roi_x_start, roi_y_start = self.show_area[0], self.show_area[1]
                roi_w_actual = min(view_w, scaled_w - roi_x_start)
                roi_h_actual = min(view_h, scaled_h - roi_y_start)

                if roi_w_actual <= 0 or roi_h_actual <= 0:
                    print(f"Error: Invalid ROI dimensions for view in '{name}'.")
                    return None
                
                image_roi_content = scaled_image_for_roi[roi_y_start : roi_y_start + roi_h_actual, \
                                                         roi_x_start : roi_x_start + roi_w_actual]

                if image_roi_content.size == 0:
                    print(f"Error: View ROI content is empty for '{name}'.")
                    return None

                display_canvas = np.full((view_h, view_w, 3), 0, dtype=image_roi_content.dtype)
                paste_h, paste_w = image_roi_content.shape[:2]
                display_canvas[0:paste_h, 0:paste_w] = image_roi_content
                
                text_color_info = (220,220,220)
                text_base_y = display_canvas.shape[0] - 10
                cv2.putText(display_canvas, name, (10, 20), font, 0.6, text_color_info, font_thickness, cv2.LINE_AA)
                cv2.putText(display_canvas, self.mouse.bright_str, (10, max(35, text_base_y)), font, 0.6, text_color_info, font_thickness, cv2.LINE_AA)
                cv2.putText(display_canvas, f"Coords:{self.address}", (10, max(35, text_base_y - 20)), font, 0.6, text_color_info, font_thickness, cv2.LINE_AA)
                cv2.putText(display_canvas, f"Zoom:{self.size_ratio:.2f}", (10, max(35, text_base_y - 40)), font, 0.6, text_color_info, font_thickness, cv2.LINE_AA)
                
                if self.windows.windows_created and cv2.getWindowProperty(self.config.process_window_name, cv2.WND_PROP_VISIBLE) >=1:
                     cv2.imshow(self.config.process_window_name, display_canvas)
                return display_canvas, self.size_ratio, self.mouse.mouse_point
            except Exception as e:
                print(f"Error in _process_image_for_display for '{name}': {e}\n{traceback.format_exc()}")
                error_img = np.full((self.config.screen_height, self.config.screen_width, 3), 10, dtype=np.uint8)
                cv2.putText(error_img, f"Display Error: {name}", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1)
                if self.windows.windows_created and cv2.getWindowProperty(self.config.process_window_name, cv2.WND_PROP_VISIBLE) >=1:
                    cv2.imshow(self.config.process_window_name, error_img)
                return None
        except Exception as e:
            print(f"Error in _process_image_for_display: {e}")
            self._recover_from_error()
            return None

    def _recover_from_error(self):
        self.size_ratio = 1.0
        self.show_area = [0, 0, self.config.screen_width, self.config.screen_height]
        self._cached_scaled_image = None

    def _show_text_window(self):
        if not self.config.enable_debug or not self.windows.windows_created: return
        if not self._show_text_window_enabled: return
        try:
            # Check if text window exists before trying to access it
            if cv2.getWindowProperty(self.config.text_window_name, cv2.WND_PROP_VISIBLE) < 0:
                return
            _x, _y, view_w, view_h = cv2.getWindowImageRect(self.config.text_window_name)
            view_h = max(1, view_h) 
            text_img_h, text_img_w = self.text_image.shape[:2]
            max_scroll = max(0, text_img_h - view_h)
            scroll_param_name = "_text_log_scroll_pos"
            if scroll_param_name not in self.trackbar.parameters: self.trackbar.parameters[scroll_param_name] = 0 
            current_scroll = self.trackbar.parameters[scroll_param_name]
            current_scroll = max(0, min(current_scroll, max_scroll))
            self.trackbar.parameters[scroll_param_name] = current_scroll
            start_y, end_y = current_scroll, min(text_img_h, current_scroll + view_h)
            if start_y >= end_y or start_y < 0 or end_y > text_img_h :
                 text_roi_content = np.full((view_h, text_img_w, 3), 255, dtype=np.uint8)
            else:
                 text_roi_content = self.text_image[start_y:end_y, :]
            if text_roi_content.size == 0 or text_roi_content.shape[0] == 0:
                text_canvas = np.full((view_h, text_img_w, 3), 250, dtype=np.uint8)
            else:
                text_canvas = np.full((view_h, text_img_w, 3), 255, dtype=text_roi_content.dtype)
                paste_h, paste_w = text_roi_content.shape[:2]
                text_canvas[0:paste_h, 0:paste_w] = text_roi_content
            cv2.imshow(self.config.text_window_name, text_canvas)
        except Exception as e: 
            print(f"CRITICAL: Text window display error: {e}\n{traceback.format_exc()}")


    def _mouse_callback(self, event: int, x: int, y: int, flags: int, userdata: Any):
        if not self.display_images or not self.current_image_dims : return
        orig_img_h, orig_img_w = self.current_image_dims
        if orig_img_h <= 0 or orig_img_w <= 0: return
        try:
            _wx, _wy, view_w, view_h = cv2.getWindowImageRect(self.config.process_window_name)
            if view_w <= 0 or view_h <= 0: return
        except cv2.error: return 
        x_view, y_view = max(0, min(x, view_w - 1)), max(0, min(y, view_h - 1))
        x_on_scaled_img, y_on_scaled_img = self.show_area[0] + x_view, self.show_area[1] + y_view
        current_size_ratio = self.size_ratio if abs(self.size_ratio) > 1e-6 else 1e-6
        ptr_x_orig, ptr_y_orig = int(x_on_scaled_img / current_size_ratio), int(y_on_scaled_img / current_size_ratio)
        ptr_x_orig, ptr_y_orig = max(0, min(ptr_x_orig, orig_img_w - 1)), max(0, min(ptr_y_orig, orig_img_h - 1))
        self.mouse.mouse_point, self.mouse.scale_ptr = (x_view, y_view), (ptr_x_orig, ptr_y_orig)
        self.address = f"({ptr_x_orig},{ptr_y_orig})"
        current_idx = max(0, min(self.trackbar.parameters.get('show', 0), len(self.display_images) - 1))
        if not (0 <= current_idx < len(self.display_images)): return
        image_data, _ = self.display_images[current_idx]
        if image_data is None or not isinstance(image_data, np.ndarray) or image_data.size == 0: return
        try:
            if 0 <= ptr_y_orig < image_data.shape[0] and 0 <= ptr_x_orig < image_data.shape[1]:
                pixel_value = image_data[ptr_y_orig, ptr_x_orig]
                if isinstance(pixel_value, np.ndarray): 
                    if len(pixel_value) >= 3: self.mouse.bright_str = f"BGR:({pixel_value[0]},{pixel_value[1]},{pixel_value[2]})"
                    elif len(pixel_value) == 1: self.mouse.bright_str = f"Gray:{int(pixel_value[0])}"
                    else: self.mouse.bright_str = "Pixel N/A"
                else: self.mouse.bright_str = f"Gray:{int(pixel_value)}"
            else: self.mouse.bright_str = "Out of Bounds"
        except IndexError: self.mouse.bright_str = "Pixel IndexErr"
        except Exception:  self.mouse.bright_str = "Pixel ReadErr"
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse.is_left_button_down = True
            self.mouse.left_button_start = (ptr_x_orig, ptr_y_orig)
            self.mouse.mouse_rect = None
            if self.mouse.is_polygon_mode:
                # If the user clicks near the first point, close the polygon
                if (len(self.mouse.current_polygon) > 2 and
                    np.linalg.norm(np.array(self.mouse.current_polygon[0]) - np.array((ptr_x_orig, ptr_y_orig))) < 10):
                    self.mouse.draw_polygons.append(self.mouse.current_polygon.copy())
                    pass
                    self.mouse.current_polygon.clear()
                    if self.analysis_window:
                        self.analysis_window.update_selectors()
                else:
                    self.mouse.current_polygon.append((ptr_x_orig, ptr_y_orig))
                    pass
            elif self.mouse.is_line_mode:
                self.mouse.line_start = (ptr_x_orig, ptr_y_orig)
        elif event == cv2.EVENT_LBUTTONUP:
            if self.mouse.is_left_button_down and self.mouse.left_button_start and not self.mouse.is_polygon_mode:
                if self.mouse.is_line_mode:
                    if self.mouse.line_start:
                        line_coords = (*self.mouse.line_start, ptr_x_orig, ptr_y_orig)
                        line_length = np.sqrt((ptr_x_orig - self.mouse.line_start[0])**2 + \
                                            (ptr_y_orig - self.mouse.line_start[1])**2)
                        if line_length > 5:
                            self.mouse.draw_lines.append(line_coords)
                            pass
                            if self.analysis_window:
                                self.analysis_window.update_selectors()
                else:
                    rect_x = min(self.mouse.left_button_start[0], ptr_x_orig)
                    rect_y = min(self.mouse.left_button_start[1], ptr_y_orig)
                    rect_w = abs(self.mouse.left_button_start[0] - ptr_x_orig)
                    rect_h = abs(self.mouse.left_button_start[1] - ptr_y_orig)
                    if rect_w > 0 and rect_h > 0:
                        self.mouse.draw_rects.append((rect_x, rect_y, rect_w, rect_h))
                        pass
                        if self.analysis_window:
                            self.analysis_window.update_selectors()
            self.mouse.is_left_button_down = False
            self.mouse.left_button_start = None
            self.mouse.mouse_rect = None
            self.mouse.line_start = None
            self.mouse.current_line = None
        elif event == cv2.EVENT_RBUTTONDOWN:
            if self.mouse.is_polygon_mode:
                if len(self.mouse.current_polygon) > 2:
                    self.mouse.draw_polygons.append(self.mouse.current_polygon.copy())
                    pass
                    self.mouse.current_polygon.clear()
                    if self.analysis_window:
                        self.analysis_window.update_selectors()
            elif self.mouse.is_line_mode:
                if self.mouse.draw_lines: 
                    removed_line = self.mouse.draw_lines.pop()
                    pass
                    if self.analysis_window:
                        self.analysis_window.update_selectors()
                self.mouse.current_line = None
            else:
                if self.mouse.draw_rects: 
                    removed_rect = self.mouse.draw_rects.pop()
                    pass
                    if self.analysis_window:
                        self.analysis_window.update_selectors()
        elif event == cv2.EVENT_RBUTTONDBLCLK:
            if self.mouse.is_polygon_mode:
                self.mouse.draw_polygons.clear()
                self.mouse.current_polygon.clear()
                pass
                if self.analysis_window:
                    self.analysis_window.update_selectors()
            elif self.mouse.is_line_mode:
                if self.mouse.draw_lines: 
                    self.mouse.draw_lines.clear()
                    pass
                    if self.analysis_window:
                        self.analysis_window.update_selectors()
                self.mouse.current_line = None
            else:
                if self.mouse.draw_rects: 
                    self.mouse.draw_rects.clear()
                    pass
                    if self.analysis_window:
                        self.analysis_window.update_selectors()
        elif event == cv2.EVENT_MBUTTONDOWN:
            self.mouse.is_middle_button_down = True
            self.mouse.middle_button_start = (x_view, y_view)
            self.mouse.middle_button_area_start = (self.show_area[0], self.show_area[1])
        elif event == cv2.EVENT_MBUTTONUP:
            self.mouse.is_middle_button_down = False
        elif event == cv2.EVENT_MOUSEWHEEL:
            delta = flags 
            ctrl_key = (flags & cv2.EVENT_FLAG_CTRLKEY) != 0
            zoom_factor = 1.15 if not ctrl_key else 1.40
            if delta > 0: self.size_ratio *= zoom_factor
            else: self.size_ratio /= zoom_factor
            self.size_ratio = max(self.config.min_size_ratio, min(self.size_ratio, self.config.max_size_ratio))
            self.show_area[0] = int(ptr_x_orig * self.size_ratio - x_view)
            self.show_area[1] = int(ptr_y_orig * self.size_ratio - y_view)
        if self.mouse.is_left_button_down and self.mouse.left_button_start:
            if self.mouse.is_line_mode and self.mouse.line_start:
                self.mouse.current_line = (*self.mouse.line_start, ptr_x_orig, ptr_y_orig)
            else:
                rect_x = min(self.mouse.left_button_start[0], ptr_x_orig)
                rect_y = min(self.mouse.left_button_start[1], ptr_y_orig)
                rect_w = abs(self.mouse.left_button_start[0] - ptr_x_orig)
                rect_h = abs(self.mouse.left_button_start[1] - ptr_y_orig)
                self.mouse.mouse_rect = (rect_x, rect_y, rect_w, rect_h)
        elif self.mouse.is_middle_button_down and self.mouse.middle_button_start and self.mouse.middle_button_area_start:
            dx = x_view - self.mouse.middle_button_start[0]
            dy = y_view - self.mouse.middle_button_start[1]
            self.show_area[0] = self.mouse.middle_button_area_start[0] - dx
            self.show_area[1] = self.mouse.middle_button_area_start[1] - dy

    def _text_mouse_callback(self, event: int, x: int, y: int, flags: int, userdata: Any):
        scroll_param_name = "_text_log_scroll_pos"
        if scroll_param_name not in self.trackbar.parameters: self.trackbar.parameters[scroll_param_name] = 0
        if event == cv2.EVENT_MOUSEWHEEL:
            delta = flags 
            scroll_amount = self.config.text_line_height * 3 
            current_scroll = self.trackbar.parameters.get(scroll_param_name, 0)
            if delta > 0: self.trackbar.parameters[scroll_param_name] = max(0, current_scroll - scroll_amount)
            else: self.trackbar.parameters[scroll_param_name] = current_scroll + scroll_amount

    def _process_tk_events(self):
        """Process Tkinter events safely in single-threaded architecture."""
        try:
            if TKINTER_AVAILABLE and hasattr(self, 'analysis_window') and self.analysis_window and self.analysis_window.root:
                # Process tkinter events without blocking
                self.analysis_window.root.update_idletasks()
                self.analysis_window.root.update()
        except Exception:
            # Don't crash if tkinter events fail - just continue silently
            pass
            # Don't re-raise the exception to avoid crashing the application
    
    def get_drawn_rois(self) -> List[Tuple[int, int, int, int]]:
        return self.mouse.draw_rects.copy()
    
    def get_drawn_lines(self) -> List[Tuple[int, int, int, int]]:
        return self.mouse.draw_lines.copy()

    def get_drawn_polygons(self) -> List[List[Tuple[int, int]]]:
        return self.mouse.draw_polygons.copy()

    def cleanup_viewer(self):
        self.windows.destroy_all_windows()
        if self.analysis_window:
            self.analysis_window.destroy_window()
        self.analyzer.close_all_plots()
        self._internal_images.clear()
        self._cached_scaled_image = None
        self.text_image = None
        self.log_texts.clear()
        self._should_continue_loop = False

    def signal_params_changed(self):
        self._params_changed = True

    def run_with_internal_loop(self, 
                       images_or_processor: Union[List[Tuple[np.ndarray, str]], Callable[[Dict[str, Any]], List[Tuple[np.ndarray, str]]]], 
                       title: str = ""):
        original_debug_state = self.config.enable_debug
        self.config.enable_debug = True

        self.clear_log()
        pass
        self._should_continue_loop = True 
        self._initialize_parameters()

        if callable(images_or_processor):
            self.image_processing_func_internal = images_or_processor
            self._params_changed = True 
        elif isinstance(images_or_processor, list):
            self._internal_images = [(img.copy(), name) for img, name in images_or_processor if isinstance(img, np.ndarray)]
        elif isinstance(images_or_processor, np.ndarray):
             self._internal_images = [(images_or_processor.copy(), title or "Image")]
        else:
            print(f"Error: `images_or_processor` type invalid for internal loop. Got {type(images_or_processor)}")
            self._internal_images = [(np.zeros((100,100,1), dtype=np.uint8), "Input Error")]

        if not self.windows.windows_created:
            self.windows.create_windows(self._mouse_callback, self._text_mouse_callback, self._show_text_window_enabled)
            if not self.windows.windows_created:
                print("FATAL: Failed to create OpenCV windows for internal loop.")
                self.config.enable_debug = original_debug_state
                return
        
        if self.image_processing_func_internal and self._params_changed:
            try:
                self._internal_images = self.image_processing_func_internal(dict(self.trackbar.parameters))
                self._params_changed = False
            except Exception as e:
                print(f"ERROR during initial image processing (internal loop): {e}\n{traceback.format_exc()}")
                self._internal_images = [(np.zeros((100,100,3), dtype=np.uint8), "Processing Error")]

        if self.config.trackbar:
            for trackbar_config_item in self.config.trackbar:
                self.trackbar.create_trackbar(trackbar_config_item, self)
        
        while self._should_continue_loop:
            if self.image_processing_func_internal and self._params_changed:
                try:
                    self._internal_images = self.image_processing_func_internal(dict(self.trackbar.parameters))
                    self._params_changed = False
                except Exception as e:
                    print(f"ERROR image re-processing (internal loop): {e}\n{traceback.format_exc()}")
                    self._params_changed = False
            self._process_frame_and_check_quit()
            if not self.windows.windows_created : self._should_continue_loop = False 
        
        self.cleanup_viewer()
        self.config.enable_debug = original_debug_state
        pass

    def register_event_handler(self, event_name: str, handler: Callable):
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)
        
    def _trigger_event(self, event_name: str, *args, **kwargs):
        for handler in self._event_handlers.get(event_name, []):
            try:
                handler(*args, **kwargs)
            except Exception as e:
                print(f"Error in event handler: {e}")

    def get_current_state(self) -> Dict[str, Any]:
        return {
            'size_ratio': self.size_ratio,
            'show_area': self.show_area.copy(),
            'mouse_point': self.mouse.mouse_point,
            'parameters': dict(self.trackbar.parameters)
        }
        
    def set_state(self, state: Dict[str, Any]):
        self.size_ratio = state['size_ratio']
        self.show_area = state['show_area'].copy()
        self.mouse.mouse_point = state['mouse_point']
        self.trackbar.parameters.update(state['parameters'])

    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_viewer()

    @classmethod
    def create_simple(cls, enable_ui: bool = True, window_size: Tuple[int, int] = (800, 600)) -> 'ImageViewer':
        config = ViewerConfig.create_simple(enable_ui, window_size)
        return cls(config)

    @classmethod
    def create_with_trackbars(cls, trackbars: List[Dict[str, Any]], enable_ui: bool = True) -> 'ImageViewer':
        config = ViewerConfig.create_with_trackbars(trackbars, enable_ui)
        return cls(config)

    def add_trackbar_config(self, trackbar_config: Dict[str, Any]) -> 'ImageViewer':
        self.config.trackbar.append(trackbar_config)
        return self

    def get_param(self, name: str, default: Any = None) -> Any:
        return self.trackbar.parameters.get(name, default)

    def set_param(self, name: str, value: Any) -> 'ImageViewer':
        self.trackbar.parameters[name] = value
        if name in self.trackbar.persistent_values:
            self.trackbar.persistent_values[name] = value
        return self

    def get_all_params(self) -> Dict[str, Any]:
        return dict(self.trackbar.parameters)

    def quick_setup(self, trackbars: List[Dict[str, Any]] = None, enable_ui: bool = True) -> 'ImageViewer':
        if trackbars:
            self.config.trackbar = trackbars
        self.config.enable_debug = enable_ui
        self.setup_viewer()
        return self

    def run_simple_loop(self, image_processor: Optional[ImageProcessor] = None) -> Dict[str, Any]:
        if image_processor:
            self.user_image_processor = image_processor

        try:
            while self.should_loop_continue():
                if self.user_image_processor:
                    self.update_display()
                elif self.config.enable_debug:
                    self._process_frame_and_check_quit()
                    
                if not self.config.enable_debug:
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            return self.get_all_params()
