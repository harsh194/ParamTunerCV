

import cv2
import functools
import traceback
from typing import Dict, Any, Optional, List, Union

# Convenience factory functions for common trackbar configurations
def make_trackbar(name: str, param_name: str, max_value: Union[int, str] = 100, initial_value: int = 0, callback: str = None, custom_callback=None) -> Dict[str, Any]:
    """Create a trackbar configuration dictionary."""
    return {
        "name": name,
        "param_name": param_name,
        "max_value": max_value,
        "initial_value": initial_value,
        "callback": callback,
        "custom_callback": custom_callback
    }

def make_int_trackbar(name: str, param_name: str, max_value: int = 100, initial_value: int = 0) -> Dict[str, Any]:
    """Create an integer trackbar configuration."""
    return make_trackbar(name, param_name, max_value, initial_value)

def make_odd_trackbar(name: str, param_name: str, max_value: int = 100, initial_value: int = 1) -> Dict[str, Any]:
    """Create an odd-number trackbar configuration (useful for kernel sizes)."""
    initial_value = initial_value if initial_value % 2 == 1 else initial_value + 1
    return make_trackbar(name, param_name, max_value, initial_value, "odd")

def make_image_selector(name: str = "Show Image", param_name: str = "show") -> Dict[str, Any]:
    """Create an image selector trackbar."""
    return make_trackbar(name, param_name, "num_images-1", 0)

def make_roi_trackbars() -> List[Dict[str, Any]]:
    """Create a set of ROI control trackbars."""
    return [
        make_trackbar("RectX", "roi_x", 1000, 0, "roi_x"),
        make_trackbar("RectY", "roi_y", 1000, 0, "roi_y"),
        make_trackbar("RectWidth", "roi_width", 1000, 100, "roi_width"),
        make_trackbar("RectHeight", "roi_height", 1000, 100, "roi_height")
    ]

class TrackbarManager:
    """Manages trackbar creation and callbacks."""
    def __init__(self, window_name: str):
        self.window_name = window_name
        self.parameters: Dict[str, int] = {}
        self.persistent_values: Dict[str, int] = {}

    def create_trackbar(self, config: Dict[str, Any], viewer: 'ImageViewer'):
        # This method is only called if viewer.config.enable_debug is True
        # and viewer.config.trackbar is populated.
        name = config.get('name', '')
        param_name = config.get('param_name', '')
        max_value_spec = config.get('max_value', 100)
        config_initial_value = config.get('initial_value', 0)  # Get initial value from config
        initial_value_for_gui = self.parameters.get(param_name, config_initial_value)  # Use config default, not 0
        callback_spec = config.get('callback', None)
        custom_callback = config.get('custom_callback', None)

        if not name or not param_name:
            viewer.log(f"Trackbar config error: 'name' and 'param_name' are required. Got: {config}")
            return

        if isinstance(max_value_spec, str) and max_value_spec == 'num_images-1':
            max_value = max(0, len(viewer.display_images) - 1 if viewer.display_images else 0)
        elif callable(max_value_spec):
            max_value = int(max_value_spec(viewer))
        else:
            max_value = int(max_value_spec)
        
        initial_value_for_gui = max(0, min(initial_value_for_gui, max_value))
        self.parameters[param_name] = initial_value_for_gui

        on_change_handler = None
        if callback_spec == 'odd':
            on_change_handler = functools.partial(self._odd_size_callback, param_name=param_name, trackbar_display_name=name)
        elif callback_spec and callback_spec.startswith('roi_'):
            method_name = f"_{callback_spec}_callback"
            if hasattr(self, method_name):
                on_change_handler = functools.partial(getattr(self, method_name),
                                                      trackbar_display_name=name,
                                                      param_name_of_trigger=param_name)
        
        def _opencv_trackbar_callback(value: int):
            self.parameters[param_name] = value
            if custom_callback:
                custom_callback(value)
                return
            
            if on_change_handler:
                try:
                    on_change_handler(viewer, value) 
                except Exception as e:
                    viewer.log(f"Trackbar '{name}' specific callback error: {e}\n{traceback.format_exc()}")
            self.persistent_values[param_name] = self.parameters[param_name]
            if hasattr(viewer, 'signal_params_changed'): # For older internal loop
                 viewer.signal_params_changed()

        try:
            cv2.createTrackbar(name, self.window_name, initial_value_for_gui, max_value, _opencv_trackbar_callback)
        except Exception as e:
            viewer.log(f"Error creating trackbar '{name}': {e}\n{traceback.format_exc()}")

    def _odd_size_callback(self, viewer: 'ImageViewer', value: int, param_name: str, trackbar_display_name: str):
        new_val = max(1, value)
        if new_val % 2 == 0: new_val += 1
        current_param_val = self.parameters.get(param_name)
        if new_val != current_param_val:
            self.parameters[param_name] = new_val
            try:
                if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) >= 1:
                    current_gui_val = cv2.getTrackbarPos(trackbar_display_name, self.window_name)
                    if current_gui_val != new_val:
                        cv2.setTrackbarPos(trackbar_display_name, self.window_name, new_val)
            except cv2.error: pass

    def _get_param_name_for_display_name(self, viewer: 'ImageViewer', display_name: str) -> Optional[str]:
        for cfg in viewer.config.trackbar: # viewer.config.trackbar might be empty
            if cfg.get('name') == display_name: return cfg.get('param_name')
        return None

    # ... (ROI callbacks: _roi_x_callback, _roi_y_callback, etc. as before) ...
    def _roi_x_callback(self, viewer: 'ImageViewer', value: int, trackbar_display_name: str, param_name_of_trigger: str):
        if viewer.current_image_dims:
            img_w = viewer.current_image_dims[1]
            rect_width_param_name = self._get_param_name_for_display_name(viewer, "RectWidth")
            if not rect_width_param_name: return
            new_max_width = max(0, img_w - value)
            try:
                if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.setTrackbarMax("RectWidth", self.window_name, new_max_width)
                    if self.parameters.get(rect_width_param_name, 0) > new_max_width:
                        self.parameters[rect_width_param_name] = new_max_width
                        self.persistent_values[rect_width_param_name] = new_max_width
                        cv2.setTrackbarPos("RectWidth", self.window_name, new_max_width)
            except cv2.error: pass

    def _roi_y_callback(self, viewer: 'ImageViewer', value: int, trackbar_display_name: str, param_name_of_trigger: str):
        if viewer.current_image_dims:
            img_h = viewer.current_image_dims[0]
            rect_height_param_name = self._get_param_name_for_display_name(viewer, "RectHeight")
            if not rect_height_param_name: return
            new_max_height = max(0, img_h - value)
            try:
                if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.setTrackbarMax("RectHeight", self.window_name, new_max_height)
                    if self.parameters.get(rect_height_param_name, 0) > new_max_height:
                        self.parameters[rect_height_param_name] = new_max_height
                        self.persistent_values[rect_height_param_name] = new_max_height
                        cv2.setTrackbarPos("RectHeight", self.window_name, new_max_height)
            except cv2.error: pass

    def _roi_width_callback(self, viewer: 'ImageViewer', value: int, trackbar_display_name: str, param_name_of_trigger: str):
        if viewer.current_image_dims:
            img_w = viewer.current_image_dims[1]
            rect_x_param_name = self._get_param_name_for_display_name(viewer, "RectX")
            if not rect_x_param_name: return
            new_max_x = max(0, img_w - value)
            try:
                if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.setTrackbarMax("RectX", self.window_name, new_max_x)
                    if self.parameters.get(rect_x_param_name, 0) > new_max_x:
                        self.parameters[rect_x_param_name] = new_max_x
                        self.persistent_values[rect_x_param_name] = new_max_x
                        cv2.setTrackbarPos("RectX", self.window_name, new_max_x)
            except cv2.error: pass

    def _roi_height_callback(self, viewer: 'ImageViewer', value: int, trackbar_display_name: str, param_name_of_trigger: str):
        if viewer.current_image_dims:
            img_h = viewer.current_image_dims[0]
            rect_y_param_name = self._get_param_name_for_display_name(viewer, "RectY")
            if not rect_y_param_name: return
            new_max_y = max(0, img_h - value)
            try:
                if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.setTrackbarMax("RectY", self.window_name, new_max_y)
                    if self.parameters.get(rect_y_param_name, 0) > new_max_y:
                        self.parameters[rect_y_param_name] = new_max_y
                        self.persistent_values[rect_y_param_name] = new_max_y
                        cv2.setTrackbarPos("RectY", self.window_name, new_max_y)
            except cv2.error: pass

