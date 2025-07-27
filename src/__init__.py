from .core.image_viewer import ImageViewer, ImageProcessor
from .config.viewer_config import ViewerConfig

# Import all trackbar functions from controls
from .controls.trackbar_manager import (
    # Basic trackbar functions
    make_trackbar,
    make_int_trackbar,
    make_odd_trackbar,
    make_image_selector,
    make_roi_trackbars,
    
    # Morphological operations
    make_morphology_trackbars,
    make_erode_dilate_trackbars,
    
    # Edge detection
    make_canny_trackbars,
    make_sobel_trackbars,
    make_laplacian_trackbars,
    make_scharr_trackbars,
    
    # Filtering
    make_gaussian_blur_trackbars,
    make_bilateral_filter_trackbars,
    make_median_blur_trackbars,
    make_blur_trackbars,
    
    # Thresholding
    make_threshold_trackbars,
    make_adaptive_threshold_trackbars,
    
    # Feature detection
    make_hough_lines_trackbars,
    make_hough_lines_p_trackbars,
    make_hough_circles_trackbars,
    make_good_features_to_track_trackbars,
    make_corner_harris_trackbars,
    
    # Color operations
    make_hsv_range_trackbars,
    make_lab_range_trackbars,
    
    # Contours
    make_find_contours_trackbars,
    make_contour_approximation_trackbars,
    
    # Geometric transformations
    make_rotation_trackbars,
    make_affine_transform_trackbars,
    make_perspective_transform_trackbars,
    
    # Histogram operations
    make_histogram_equalization_trackbars,
    
    # Advanced operations
    make_watershed_trackbars,
    make_grabcut_trackbars,
    make_template_matching_trackbars,
    make_optical_flow_trackbars,
    
    # Manager class
    TrackbarManager
)

from .gui.window_manager import WindowManager
from .analysis import ImageAnalyzer, PlotAnalyzer, ExportManager
from .events.mouse_handler import MouseHandler
from .gui.analysis_control_window import AnalysisControlWindow

# Import all viewer factory functions from utils
from .utils.viewer_factory import (
    # Basic viewers
    create_basic_viewer,
    create_viewer_with_common_controls,
    create_viewer_for_filtering,
    create_auto_viewer,
    
    # Morphological operations viewers
    create_viewer_for_morphology,
    
    # Edge detection viewers
    create_viewer_for_canny,
    create_viewer_for_sobel_laplacian,
    
    # Thresholding viewers
    create_viewer_for_adaptive_threshold,
    
    # Feature detection viewers
    create_viewer_for_hough_lines,
    create_viewer_for_hough_circles,
    create_viewer_for_corner_detection,
    
    # Color processing viewers
    create_viewer_for_hsv_filtering,
    create_viewer_for_histogram_equalization,
    
    # Geometric transformation viewers
    create_viewer_for_geometric_transform,
    
    # Contour viewers
    create_viewer_for_contours
)

__all__ = [
    # Core classes
    'ImageViewer',
    'ImageProcessor',
    'ViewerConfig',
    'WindowManager',
    'ImageAnalyzer',
    'PlotAnalyzer',
    'ExportManager',
    'MouseHandler',
    'AnalysisControlWindow',
    'TrackbarManager',
    
    # Basic trackbar functions
    'make_trackbar',
    'make_int_trackbar',
    'make_odd_trackbar',
    'make_image_selector',
    'make_roi_trackbars',
    
    # Morphological operations trackbars
    'make_morphology_trackbars',
    'make_erode_dilate_trackbars',
    
    # Edge detection trackbars
    'make_canny_trackbars',
    'make_sobel_trackbars',
    'make_laplacian_trackbars',
    'make_scharr_trackbars',
    
    # Filtering trackbars
    'make_gaussian_blur_trackbars',
    'make_bilateral_filter_trackbars',
    'make_median_blur_trackbars',
    'make_blur_trackbars',
    
    # Thresholding trackbars
    'make_threshold_trackbars',
    'make_adaptive_threshold_trackbars',
    
    # Feature detection trackbars
    'make_hough_lines_trackbars',
    'make_hough_lines_p_trackbars',
    'make_hough_circles_trackbars',
    'make_good_features_to_track_trackbars',
    'make_corner_harris_trackbars',
    
    # Color operations trackbars
    'make_hsv_range_trackbars',
    'make_lab_range_trackbars',
    
    # Contours trackbars
    'make_find_contours_trackbars',
    'make_contour_approximation_trackbars',
    
    # Geometric transformations trackbars
    'make_rotation_trackbars',
    'make_affine_transform_trackbars',
    'make_perspective_transform_trackbars',
    
    # Histogram operations trackbars
    'make_histogram_equalization_trackbars',
    
    # Advanced operations trackbars
    'make_watershed_trackbars',
    'make_grabcut_trackbars',
    'make_template_matching_trackbars',
    'make_optical_flow_trackbars',
    
    # Basic viewer factories
    'create_basic_viewer',
    'create_viewer_with_common_controls',
    'create_viewer_for_filtering',
    'create_auto_viewer',
    
    # Specialized viewer factories
    'create_viewer_for_morphology',
    'create_viewer_for_canny',
    'create_viewer_for_sobel_laplacian',
    'create_viewer_for_adaptive_threshold',
    'create_viewer_for_hough_lines',
    'create_viewer_for_hough_circles',
    'create_viewer_for_corner_detection',
    'create_viewer_for_hsv_filtering',
    'create_viewer_for_histogram_equalization',
    'create_viewer_for_geometric_transform',
    'create_viewer_for_contours',
    
    # Legacy exports (from original file)
    'Polygon',
    'PolygonManager',
    'undo_last_point'
]