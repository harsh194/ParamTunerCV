
from typing import List, Dict, Any
from ..core.image_viewer import ImageViewer
from ..controls.trackbar_manager import make_image_selector, make_int_trackbar, make_odd_trackbar
from ..config.viewer_config import ViewerConfig

def create_basic_viewer(enable_ui: bool = True) -> ImageViewer:
    """Create a basic ImageViewer with no trackbars."""
    return ImageViewer.create_simple(enable_ui)

def create_viewer_with_common_controls(enable_ui: bool = True) -> ImageViewer:
    """Create ImageViewer with commonly used trackbars."""
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Threshold", "threshold", 255, 128),
        make_odd_trackbar("Kernel Size", "kernel_size", 31, 5),
        make_int_trackbar("Iterations", "iterations", 10, 1)
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_filtering(enable_ui: bool = True) -> ImageViewer:
    """Create ImageViewer optimized for image filtering tasks."""
    trackbars = [
        make_image_selector(),
        make_odd_trackbar("Gaussian Size", "gaussian_size", 31, 5),
        make_odd_trackbar("Median Size", "median_size", 15, 3),
        make_int_trackbar("Bilateral d", "bilateral_d", 20, 5),
        make_int_trackbar("Bilateral Sigma Color", "bilateral_sigma_color", 150, 80),
        make_int_trackbar("Bilateral Sigma Space", "bilateral_sigma_space", 150, 80)
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_morphology(enable_ui: bool = True) -> ImageViewer:
    """Create ImageViewer for morphological operations (erode, dilate, opening, closing, gradient, tophat, blackhat)."""
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Morph Op", "morph_op", 6, 2),  # 0=erode, 1=dilate, 2=opening, 3=closing, 4=gradient, 5=tophat, 6=blackhat
        make_odd_trackbar("Kernel Size", "kernel_size", 31, 5),
        make_int_trackbar("Shape", "kernel_shape", 2, 0),  # 0=rect, 1=ellipse, 2=cross
        make_int_trackbar("Iterations", "iterations", 10, 1)
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_canny(enable_ui: bool = True) -> ImageViewer:
    """Create ImageViewer for Canny edge detection."""
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Lower Threshold", "lower_threshold", 300, 50),
        make_int_trackbar("Upper Threshold", "upper_threshold", 300, 150),
        make_odd_trackbar("Aperture Size", "aperture_size", 7, 3),
        make_int_trackbar("L2 Gradient", "l2_gradient", 1, 0)  # 0=False, 1=True
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_adaptive_threshold(enable_ui: bool = True) -> ImageViewer:
    """Create ImageViewer for adaptive thresholding."""
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Max Value", "max_value", 255, 255),
        make_int_trackbar("Adaptive Method", "adaptive_method", 1, 0),  # 0=mean, 1=gaussian
        make_int_trackbar("Threshold Type", "threshold_type", 1, 0),  # 0=binary, 1=binary_inv
        make_odd_trackbar("Block Size", "block_size", 99, 11),
        make_int_trackbar("C", "C", 50, 2)
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_hough_lines(enable_ui: bool = True) -> ImageViewer:
    """Create ImageViewer for Hough line detection."""
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Rho", "rho", 5, 1),
        make_int_trackbar("Theta (deg)", "theta_deg", 180, 1),
        make_int_trackbar("Threshold", "threshold", 200, 100),
        make_int_trackbar("Min Line Length", "min_line_length", 200, 50),
        make_int_trackbar("Max Line Gap", "max_line_gap", 50, 10)
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_hough_circles(enable_ui: bool = True) -> ImageViewer:
    """Create ImageViewer for Hough circle detection."""
    trackbars = [
        make_image_selector(),
        make_int_trackbar("DP", "dp", 10, 1),
        make_int_trackbar("Min Dist", "min_dist", 200, 50),
        make_int_trackbar("Param1", "param1", 300, 100),
        make_int_trackbar("Param2", "param2", 100, 30),
        make_int_trackbar("Min Radius", "min_radius", 100, 0),
        make_int_trackbar("Max Radius", "max_radius", 200, 0)
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_hsv_filtering(enable_ui: bool = True) -> ImageViewer:
    """Create ImageViewer for HSV color filtering."""
    trackbars = [
        make_image_selector(),
        make_int_trackbar("H Min", "h_min", 179, 0),
        make_int_trackbar("S Min", "s_min", 255, 0),
        make_int_trackbar("V Min", "v_min", 255, 0),
        make_int_trackbar("H Max", "h_max", 179, 179),
        make_int_trackbar("S Max", "s_max", 255, 255),
        make_int_trackbar("V Max", "v_max", 255, 255)
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_contours(enable_ui: bool = True) -> ImageViewer:
    """Create ImageViewer for contour detection and analysis."""
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Threshold", "threshold", 255, 128),
        make_int_trackbar("Retrieval Mode", "retrieval_mode", 3, 1),  # 0=external, 1=list, 2=ccomp, 3=tree
        make_int_trackbar("Approximation", "approximation", 4, 2),  # 1=none, 2=simple, 3=tc89_l1, 4=tc89_kcos
        make_int_trackbar("Min Area", "min_area", 10000, 100),
        make_int_trackbar("Max Area", "max_area", 50000, 10000)
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_corner_detection(enable_ui: bool = True) -> ImageViewer:
    """Create ImageViewer for Harris and Shi-Tomasi corner detection."""
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Max Corners", "max_corners", 1000, 100),
        make_int_trackbar("Quality Level", "quality_level", 100, 1),  # Divide by 1000
        make_int_trackbar("Min Distance", "min_distance", 50, 10),
        make_odd_trackbar("Block Size", "block_size", 23, 3),
        make_int_trackbar("Use Harris", "use_harris", 1, 0),  # 0=Shi-Tomasi, 1=Harris
        make_int_trackbar("Harris k", "harris_k", 40, 4)  # Divide by 1000
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_geometric_transform(enable_ui: bool = True) -> ImageViewer:
    """Create ImageViewer for geometric transformations (rotation, scaling, translation)."""
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Angle", "angle", 360, 0),
        make_int_trackbar("Scale X", "scale_x", 300, 100),  # Divide by 100
        make_int_trackbar("Scale Y", "scale_y", 300, 100),  # Divide by 100
        make_int_trackbar("Translate X", "translate_x", 500, 250),  # Subtract 250
        make_int_trackbar("Translate Y", "translate_y", 500, 250)   # Subtract 250
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_sobel_laplacian(enable_ui: bool = True) -> ImageViewer:
    """Create ImageViewer for Sobel and Laplacian edge detection."""
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Detector", "detector", 2, 0),  # 0=Sobel X, 1=Sobel Y, 2=Laplacian
        make_odd_trackbar("Kernel Size", "kernel_size", 31, 3),
        make_int_trackbar("Scale", "scale", 10, 1),
        make_int_trackbar("Delta", "delta", 100, 0)
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_histogram_equalization(enable_ui: bool = True) -> ImageViewer:
    """Create ImageViewer for histogram equalization and CLAHE."""
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Method", "method", 2, 0),  # 0=none, 1=global, 2=CLAHE
        make_int_trackbar("Clip Limit", "clip_limit", 40, 20),  # Divide by 10
        make_int_trackbar("Tile Grid X", "tile_grid_x", 16, 8),
        make_int_trackbar("Tile Grid Y", "tile_grid_y", 16, 8)
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_auto_viewer(config: ViewerConfig, trackbar_definitions: List[Dict[str, Any]], app_debug_mode: bool, max_headless_iterations: int = 1) -> ImageViewer:
    """
    Create an ImageViewer that automatically handles setup and headless iterations.
    This is designed to match the exact user workflow.
    """
    return ImageViewer(config, trackbar_definitions, app_debug_mode, max_headless_iterations)
