

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

# ============================================================================
# MORPHOLOGICAL OPERATIONS TRACKBARS
# ============================================================================

def make_morphology_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.morphologyEx()"""
    return [
        make_int_trackbar("Morph Op", "morph_op", 6, 2),  # cv2.MORPH_OPENING
        make_odd_trackbar("Kernel Size", "kernel_size", 31, 5),
        make_int_trackbar("Shape", "kernel_shape", 2, 0),  # cv2.MORPH_RECT
        make_int_trackbar("Iterations", "iterations", 10, 1)
    ]

def make_erode_dilate_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.erode() and cv2.dilate()"""
    return [
        make_int_trackbar("Operation", "operation", 1, 0),  # 0=erode, 1=dilate
        make_odd_trackbar("Kernel Size", "kernel_size", 31, 5),
        make_int_trackbar("Shape", "kernel_shape", 2, 0),  # cv2.MORPH_RECT
        make_int_trackbar("Iterations", "iterations", 10, 1)
    ]

# ============================================================================
# EDGE DETECTION TRACKBARS
# ============================================================================

def make_canny_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.Canny()"""
    return [
        make_int_trackbar("Lower Threshold", "lower_threshold", 300, 50),
        make_int_trackbar("Upper Threshold", "upper_threshold", 300, 150),
        make_odd_trackbar("Aperture Size", "aperture_size", 7, 3),
        make_int_trackbar("L2 Gradient", "l2_gradient", 1, 0)  # boolean
    ]

def make_sobel_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.Sobel()"""
    return [
        make_int_trackbar("dx", "dx", 2, 1),
        make_int_trackbar("dy", "dy", 2, 0),
        make_odd_trackbar("Kernel Size", "ksize", 31, 3),
        make_int_trackbar("Scale", "scale", 10, 1),
        make_int_trackbar("Delta", "delta", 100, 0)
    ]

def make_laplacian_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.Laplacian()"""
    return [
        make_odd_trackbar("Kernel Size", "ksize", 31, 1),
        make_int_trackbar("Scale", "scale", 10, 1),
        make_int_trackbar("Delta", "delta", 100, 0)
    ]

def make_scharr_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.Scharr()"""
    return [
        make_int_trackbar("dx", "dx", 1, 1),
        make_int_trackbar("dy", "dy", 1, 0),
        make_int_trackbar("Scale", "scale", 10, 1),
        make_int_trackbar("Delta", "delta", 100, 0)
    ]

# ============================================================================
# FILTERING TRACKBARS
# ============================================================================

def make_gaussian_blur_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.GaussianBlur()"""
    return [
        make_odd_trackbar("Kernel Size X", "ksize_x", 99, 5),
        make_odd_trackbar("Kernel Size Y", "ksize_y", 99, 5),
        make_int_trackbar("Sigma X", "sigma_x", 100, 0),  # 0 = calculate from kernel size
        make_int_trackbar("Sigma Y", "sigma_y", 100, 0)   # 0 = calculate from kernel size
    ]

def make_bilateral_filter_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.bilateralFilter()"""
    return [
        make_int_trackbar("d", "d", 20, 5),
        make_int_trackbar("Sigma Color", "sigma_color", 150, 80),
        make_int_trackbar("Sigma Space", "sigma_space", 150, 80)
    ]

def make_median_blur_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.medianBlur()"""
    return [
        make_odd_trackbar("Kernel Size", "ksize", 31, 5)
    ]

def make_blur_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.blur()"""
    return [
        make_int_trackbar("Kernel Width", "ksize_width", 31, 5),
        make_int_trackbar("Kernel Height", "ksize_height", 31, 5)
    ]

# ============================================================================
# THRESHOLDING TRACKBARS
# ============================================================================

def make_threshold_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.threshold()"""
    return [
        make_int_trackbar("Threshold", "thresh", 255, 128),
        make_int_trackbar("Max Value", "maxval", 255, 255),
        make_int_trackbar("Type", "type", 4, 0)  # cv2.THRESH_BINARY
    ]

def make_adaptive_threshold_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.adaptiveThreshold()"""
    return [
        make_int_trackbar("Max Value", "maxValue", 255, 255),
        make_int_trackbar("Adaptive Method", "adaptiveMethod", 1, 0),  # cv2.ADAPTIVE_THRESH_MEAN_C
        make_int_trackbar("Threshold Type", "thresholdType", 1, 0),   # cv2.THRESH_BINARY
        make_odd_trackbar("Block Size", "blockSize", 99, 11),
        make_int_trackbar("C", "C", 50, 2)
    ]

# ============================================================================
# FEATURE DETECTION TRACKBARS
# ============================================================================

def make_hough_lines_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.HoughLines()"""
    return [
        make_int_trackbar("Rho", "rho", 5, 1),
        make_int_trackbar("Theta (deg)", "theta_deg", 180, 1),
        make_int_trackbar("Threshold", "threshold", 200, 100)
    ]

def make_hough_lines_p_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.HoughLinesP()"""
    return [
        make_int_trackbar("Rho", "rho", 5, 1),
        make_int_trackbar("Theta (deg)", "theta_deg", 180, 1),
        make_int_trackbar("Threshold", "threshold", 200, 100),
        make_int_trackbar("Min Line Length", "minLineLength", 200, 50),
        make_int_trackbar("Max Line Gap", "maxLineGap", 50, 10)
    ]

def make_hough_circles_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.HoughCircles()"""
    return [
        make_int_trackbar("DP", "dp", 10, 1),
        make_int_trackbar("Min Dist", "minDist", 200, 50),
        make_int_trackbar("Param1", "param1", 300, 100),
        make_int_trackbar("Param2", "param2", 100, 30),
        make_int_trackbar("Min Radius", "minRadius", 100, 0),
        make_int_trackbar("Max Radius", "maxRadius", 200, 0)
    ]

def make_good_features_to_track_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.goodFeaturesToTrack()"""
    return [
        make_int_trackbar("Max Corners", "maxCorners", 1000, 100),
        make_int_trackbar("Quality Level", "qualityLevel", 100, 1),  # divide by 1000
        make_int_trackbar("Min Distance", "minDistance", 50, 10),
        make_odd_trackbar("Block Size", "blockSize", 23, 3),
        make_int_trackbar("Use Harris", "useHarrisDetector", 1, 0),
        make_int_trackbar("Harris k", "k", 40, 4)  # divide by 1000
    ]

def make_corner_harris_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.cornerHarris()"""
    return [
        make_odd_trackbar("Block Size", "blockSize", 23, 2),
        make_odd_trackbar("Ksize", "ksize", 31, 3),
        make_int_trackbar("k", "k", 40, 4),  # divide by 100
        make_int_trackbar("Threshold", "threshold", 100, 1)  # for result > threshold
    ]

# ============================================================================
# COLOR SPACE TRACKBARS
# ============================================================================

def make_hsv_range_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for HSV color filtering with cv2.inRange()"""
    return [
        make_int_trackbar("H Min", "h_min", 179, 0),
        make_int_trackbar("S Min", "s_min", 255, 0),
        make_int_trackbar("V Min", "v_min", 255, 0),
        make_int_trackbar("H Max", "h_max", 179, 179),
        make_int_trackbar("S Max", "s_max", 255, 255),
        make_int_trackbar("V Max", "v_max", 255, 255)
    ]

def make_lab_range_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for LAB color filtering"""
    return [
        make_int_trackbar("L Min", "l_min", 255, 0),
        make_int_trackbar("A Min", "a_min", 255, 0),
        make_int_trackbar("B Min", "b_min", 255, 0),
        make_int_trackbar("L Max", "l_max", 255, 255),
        make_int_trackbar("A Max", "a_max", 255, 255),
        make_int_trackbar("B Max", "b_max", 255, 255)
    ]

# ============================================================================
# CONTOUR TRACKBARS
# ============================================================================

def make_find_contours_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.findContours()"""
    return [
        make_int_trackbar("Threshold", "threshold", 255, 128),
        make_int_trackbar("Mode", "mode", 3, 1),  # cv2.RETR_LIST
        make_int_trackbar("Method", "method", 4, 2),  # cv2.CHAIN_APPROX_SIMPLE
        make_int_trackbar("Min Area", "min_area", 10000, 100),
        make_int_trackbar("Max Area", "max_area", 50000, 10000)
    ]

def make_contour_approximation_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.approxPolyDP()"""
    return [
        make_int_trackbar("Epsilon Factor", "epsilon_factor", 50, 2),  # divide by 1000
        make_int_trackbar("Closed", "closed", 1, 1)  # boolean
    ]

# ============================================================================
# GEOMETRIC TRANSFORMATION TRACKBARS
# ============================================================================

def make_rotation_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for rotation with cv2.getRotationMatrix2D()"""
    return [
        make_int_trackbar("Angle", "angle", 360, 0),
        make_int_trackbar("Scale", "scale", 300, 100),  # divide by 100
        make_int_trackbar("Center X", "center_x", 1000, 500),
        make_int_trackbar("Center Y", "center_y", 1000, 500)
    ]

def make_affine_transform_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for affine transformation"""
    return [
        make_int_trackbar("Scale X", "scale_x", 300, 100),  # divide by 100
        make_int_trackbar("Scale Y", "scale_y", 300, 100),  # divide by 100
        make_int_trackbar("Translate X", "translate_x", 500, 250),  # subtract 250
        make_int_trackbar("Translate Y", "translate_y", 500, 250),  # subtract 250
        make_int_trackbar("Shear X", "shear_x", 100, 50),  # subtract 50, divide by 100
        make_int_trackbar("Shear Y", "shear_y", 100, 50)   # subtract 50, divide by 100
    ]

def make_perspective_transform_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for perspective transformation corner points"""
    return [
        make_int_trackbar("Top Left X", "tl_x", 1000, 100),
        make_int_trackbar("Top Left Y", "tl_y", 1000, 100),
        make_int_trackbar("Top Right X", "tr_x", 1000, 300),
        make_int_trackbar("Top Right Y", "tr_y", 1000, 100),
        make_int_trackbar("Bottom Right X", "br_x", 1000, 300),
        make_int_trackbar("Bottom Right Y", "br_y", 1000, 300),
        make_int_trackbar("Bottom Left X", "bl_x", 1000, 100),
        make_int_trackbar("Bottom Left Y", "bl_y", 1000, 300)
    ]

# ============================================================================
# HISTOGRAM TRACKBARS
# ============================================================================

def make_histogram_equalization_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for histogram equalization"""
    return [
        make_int_trackbar("Method", "method", 2, 0),  # 0=none, 1=global, 2=CLAHE
        make_int_trackbar("Clip Limit", "clipLimit", 40, 20),  # divide by 10
        make_int_trackbar("Tile Grid X", "tileGridSize_x", 16, 8),
        make_int_trackbar("Tile Grid Y", "tileGridSize_y", 16, 8)
    ]

# ============================================================================
# ADVANCED OPERATIONS TRACKBARS
# ============================================================================

def make_watershed_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for watershed segmentation"""
    return [
        make_int_trackbar("Threshold", "threshold", 255, 128),
        make_int_trackbar("Distance Transform", "dist_transform", 2, 1),  # cv2.DIST_L2
        make_int_trackbar("Noise Removal", "noise_removal", 10, 3),
        make_int_trackbar("Sure BG", "sure_bg", 20, 10),
        make_int_trackbar("Sure FG", "sure_fg", 70, 50)
    ]

def make_grabcut_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for GrabCut segmentation"""
    return [
        make_int_trackbar("Iterations", "iterCount", 10, 5),
        make_int_trackbar("Mode", "mode", 3, 0),  # cv2.GC_INIT_WITH_RECT
        make_roi_trackbars()[0],  # Use ROI trackbars for rectangle
        make_roi_trackbars()[1],
        make_roi_trackbars()[2],
        make_roi_trackbars()[3]
    ]

def make_template_matching_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for cv2.matchTemplate()"""
    return [
        make_int_trackbar("Method", "method", 5, 1),  # cv2.TM_CCOEFF_NORMED
        make_int_trackbar("Threshold", "threshold", 100, 80)  # divide by 100
    ]

def make_optical_flow_trackbars() -> List[Dict[str, Any]]:
    """Create trackbars for Lucas-Kanade optical flow"""
    return [
        make_odd_trackbar("Win Size", "winSize", 31, 15),
        make_int_trackbar("Max Level", "maxLevel", 5, 2),
        make_int_trackbar("Max Count", "maxCount", 100, 10),
        make_int_trackbar("Epsilon", "epsilon", 30, 3)  # divide by 1000
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
            print(f"Trackbar config error: 'name' and 'param_name' are required. Got: {config}")
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
                    print(f"Trackbar '{name}' specific callback error: {e}\n{traceback.format_exc()}")
            self.persistent_values[param_name] = self.parameters[param_name]
            if hasattr(viewer, 'signal_params_changed'): # For older internal loop
                 viewer.signal_params_changed()

        try:
            cv2.createTrackbar(name, self.window_name, initial_value_for_gui, max_value, _opencv_trackbar_callback)
        except Exception as e:
            print(f"Error creating trackbar '{name}': {e}\n{traceback.format_exc()}")

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

