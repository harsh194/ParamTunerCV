
"""Factory functions for creating specialized ImageViewer instances for the Parameter project.

This module provides a comprehensive collection of factory functions that create
pre-configured ImageViewer instances optimized for specific computer vision and
image processing tasks. Each factory function sets up appropriate trackbars and
parameters for different algorithms and workflows.

The factory functions follow a consistent pattern of accepting an enable_ui parameter
and returning fully configured ImageViewer instances ready for immediate use. This
approach simplifies the setup process for common image processing scenarios while
maintaining flexibility for advanced configurations.

Key Categories:
- Basic viewers: Simple configurations for general use
- Filtering: Gaussian, median, bilateral filtering with tunable parameters
- Morphology: Erosion, dilation, opening, closing operations
- Edge Detection: Canny, Sobel, Laplacian edge detection algorithms
- Feature Detection: Corner detection, line/circle detection via Hough transforms
- Color Processing: HSV filtering, histogram equalization, CLAHE
- Geometric Operations: Rotation, scaling, translation transformations
- Thresholding: Binary, adaptive, and advanced thresholding methods
- Contour Analysis: Contour detection with configurable parameters

Usage:
    # Basic viewer for general image analysis
    viewer = create_basic_viewer(enable_ui=True)
    
    # Specialized viewer for edge detection
    viewer = create_viewer_for_canny(enable_ui=True)
    
    # Custom viewer with auto-configuration
    viewer = create_auto_viewer(config, trackbars, debug_mode, iterations)

Main Functions:
    create_basic_viewer: Simple viewer with no trackbars
    create_viewer_with_common_controls: General-purpose viewer with common trackbars
    create_viewer_for_*: Specialized viewers for specific algorithms
    create_auto_viewer: Fully customizable viewer with manual configuration
"""

from typing import List, Dict, Any
from ..core.image_viewer import ImageViewer
from ..controls.trackbar_manager import make_image_selector, make_int_trackbar, make_odd_trackbar
from ..config.viewer_config import ViewerConfig

def create_basic_viewer(enable_ui: bool = True) -> ImageViewer:
    """Create a basic ImageViewer instance with minimal configuration and no trackbars.
    
    This factory function provides the simplest possible ImageViewer setup for
    basic image display and viewing tasks. It creates an ImageViewer with default
    settings and no interactive trackbars, making it suitable for simple image
    display scenarios or as a starting point for manual configuration.
    
    The basic viewer is ideal for:
    - Simple image viewing without parameter adjustment
    - Prototyping and testing image processing pipelines
    - Headless operation where trackbars are not needed
    - Base configuration that will be extended with custom trackbars
    
    Args:
        enable_ui: Whether to enable the user interface components including
            windows and interactive elements. True enables full UI mode for
            interactive use, False creates a headless configuration for
            automated processing. Defaults to True.
            
    Returns:
        ImageViewer: A configured ImageViewer instance with default settings
            and no trackbars, ready for immediate use or further configuration.
            
    Examples:
        >>> # Interactive basic viewer
        >>> viewer = create_basic_viewer(enable_ui=True)
        >>> viewer.add_image("image.jpg", "Original")
        >>> 
        >>> # Headless viewer for automation
        >>> viewer = create_basic_viewer(enable_ui=False)
        >>> # Process images without UI
        
    Performance:
        Time Complexity: O(1) - constant time factory method call.
        Space Complexity: O(1) - minimal memory allocation for viewer instance.
    """
    return ImageViewer.create_simple(enable_ui)

def create_viewer_with_common_controls(enable_ui: bool = True) -> ImageViewer:
    """Create an ImageViewer instance with commonly used trackbars for general image processing.
    
    This factory function creates an ImageViewer with a standard set of trackbars
    that are frequently used across many image processing tasks. It provides a
    good starting point for interactive image analysis with the most common
    parameters readily available for adjustment.
    
    The common controls include:
    - Image Selector: Choose between multiple loaded images
    - Threshold: Binary thresholding value (0-255, default 128)
    - Kernel Size: Morphological operation kernel size (odd values 1-31, default 5)
    - Iterations: Number of iterations for iterative operations (1-10, default 1)
    
    This configuration is suitable for:
    - General-purpose image processing experiments
    - Educational demonstrations of basic image processing
    - Rapid prototyping of image analysis workflows
    - Baseline configuration for custom processing pipelines
    
    Args:
        enable_ui: Whether to enable the user interface components including
            trackbars and interactive windows. True enables full UI mode for
            interactive parameter adjustment, False creates a headless configuration.
            Defaults to True.
            
    Returns:
        ImageViewer: A configured ImageViewer instance with common trackbars
            for threshold, kernel size, and iterations parameters.
            
    Examples:
        >>> # Interactive viewer with common controls
        >>> viewer = create_viewer_with_common_controls(enable_ui=True)
        >>> viewer.add_image("image.jpg", "Original")
        >>> # Use trackbars to adjust threshold, kernel size, iterations
        >>> 
        >>> # Access trackbar values in processing loop
        >>> while viewer.should_loop_continue():
        ...     params = viewer.trackbar.parameters
        ...     threshold = params['threshold']
        ...     kernel_size = params['kernel_size']
        ...     iterations = params['iterations']
        
    Performance:
        Time Complexity: O(1) - constant time setup with fixed number of trackbars.
        Space Complexity: O(1) - minimal memory for trackbar configuration.
    """
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Threshold", "threshold", 255, 128),
        make_odd_trackbar("Kernel Size", "kernel_size", 31, 5),
        make_int_trackbar("Iterations", "iterations", 10, 1)
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_filtering(enable_ui: bool = True) -> ImageViewer:
    """Create an ImageViewer instance optimized for image filtering and noise reduction tasks.
    
    This factory function creates an ImageViewer with trackbars specifically configured
    for various image filtering operations including Gaussian blur, median filtering,
    and bilateral filtering. It provides comprehensive control over the most important
    filtering parameters for noise reduction and image smoothing applications.
    
    The filtering controls include:
    - Image Selector: Choose between multiple loaded images
    - Gaussian Size: Kernel size for Gaussian blur (odd values 1-31, default 5)
    - Median Size: Kernel size for median filtering (odd values 1-15, default 3)
    - Bilateral d: Neighborhood diameter for bilateral filter (1-20, default 5)
    - Bilateral Sigma Color: Color similarity threshold (1-150, default 80)
    - Bilateral Sigma Space: Spatial proximity threshold (1-150, default 80)
    
    This configuration is ideal for:
    - Noise reduction experiments and parameter optimization
    - Comparing different filtering techniques on the same image
    - Educational demonstrations of filtering algorithms
    - Pre-processing images for further analysis operations
    
    Args:
        enable_ui: Whether to enable the user interface components including
            trackbars and interactive windows. True enables full UI mode for
            interactive parameter adjustment, False creates a headless configuration.
            Defaults to True.
            
    Returns:
        ImageViewer: A configured ImageViewer instance with trackbars for
            Gaussian, median, and bilateral filtering parameters.
            
    Examples:
        >>> # Interactive filtering viewer
        >>> viewer = create_viewer_for_filtering(enable_ui=True)
        >>> viewer.add_image("noisy_image.jpg", "Noisy Original")
        >>> 
        >>> # Access filtering parameters in processing loop
        >>> while viewer.should_loop_continue():
        ...     params = viewer.trackbar.parameters
        ...     gaussian_size = params['gaussian_size']
        ...     median_size = params['median_size']
        ...     bilateral_d = params['bilateral_d']
        ...     # Apply filtering operations with these parameters
        
    Performance:
        Time Complexity: O(1) - constant time setup with fixed trackbar count.
        Space Complexity: O(1) - minimal memory for trackbar configuration.
    """
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
    """Create an ImageViewer instance specialized for morphological image processing operations.
    
    This factory function creates an ImageViewer with trackbars configured for
    comprehensive morphological operations including erosion, dilation, opening,
    closing, gradient, top-hat, and black-hat transformations. It provides
    complete control over morphological parameters for shape analysis and
    structural image processing tasks.
    
    The morphological controls include:
    - Image Selector: Choose between multiple loaded images
    - Morph Op: Operation type (0=erode, 1=dilate, 2=opening, 3=closing, 4=gradient, 5=tophat, 6=blackhat)
    - Kernel Size: Structuring element size (odd values 1-31, default 5)
    - Shape: Kernel shape (0=rectangular, 1=elliptical, 2=cross, default 0)
    - Iterations: Number of morphological iterations (1-10, default 1)
    
    This configuration is ideal for:
    - Shape analysis and feature extraction
    - Binary image processing and cleanup
    - Structural element experiments
    - Noise removal using morphological operations
    
    Args:
        enable_ui: Whether to enable the user interface. Defaults to True.
        
    Returns:
        ImageViewer: Configured ImageViewer with morphological operation trackbars.
        
    Examples:
        >>> viewer = create_viewer_for_morphology(enable_ui=True)
        >>> # Access morphological parameters
        >>> params = viewer.trackbar.parameters
        >>> morph_op = params['morph_op']  # 0-6 for different operations
    """
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Morph Op", "morph_op", 6, 2),  # 0=erode, 1=dilate, 2=opening, 3=closing, 4=gradient, 5=tophat, 6=blackhat
        make_odd_trackbar("Kernel Size", "kernel_size", 31, 5),
        make_int_trackbar("Shape", "kernel_shape", 2, 0),  # 0=rect, 1=ellipse, 2=cross
        make_int_trackbar("Iterations", "iterations", 10, 1)
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_canny(enable_ui: bool = True) -> ImageViewer:
    """Create an ImageViewer instance specialized for Canny edge detection algorithm.
    
    This factory function creates an ImageViewer with trackbars specifically
    configured for the Canny edge detection algorithm, providing complete control
    over all Canny parameters for optimal edge detection results across different
    image types and noise conditions.
    
    The Canny edge detection controls include:
    - Image Selector: Choose between multiple loaded images
    - Lower Threshold: Lower hysteresis threshold (1-300, default 50)
    - Upper Threshold: Upper hysteresis threshold (1-300, default 150)
    - Aperture Size: Sobel operator aperture size (odd values 3-7, default 3)
    - L2 Gradient: Use L2 norm for gradient calculation (0=L1, 1=L2, default 0)
    
    This configuration is ideal for:
    - Edge detection parameter optimization
    - Comparing edge detection quality across threshold values
    - Educational demonstrations of Canny algorithm behavior
    - Pre-processing for shape analysis and contour detection
    
    Args:
        enable_ui: Whether to enable the user interface. Defaults to True.
        
    Returns:
        ImageViewer: Configured ImageViewer with Canny edge detection trackbars.
        
    Examples:
        >>> viewer = create_viewer_for_canny(enable_ui=True)
        >>> # Fine-tune edge detection parameters interactively
        >>> params = viewer.trackbar.parameters
        >>> lower_thresh = params['lower_threshold']
        >>> upper_thresh = params['upper_threshold']
    """
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Lower Threshold", "lower_threshold", 300, 50),
        make_int_trackbar("Upper Threshold", "upper_threshold", 300, 150),
        make_odd_trackbar("Aperture Size", "aperture_size", 7, 3),
        make_int_trackbar("L2 Gradient", "l2_gradient", 1, 0)  # 0=False, 1=True
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_adaptive_threshold(enable_ui: bool = True) -> ImageViewer:
    """Create an ImageViewer instance specialized for adaptive thresholding operations.
    
    This factory function creates an ImageViewer with trackbars configured for
    adaptive thresholding, which is particularly effective for images with
    varying illumination conditions. It provides complete control over adaptive
    thresholding parameters for optimal binarization results.
    
    The adaptive thresholding controls include:
    - Image Selector: Choose between multiple loaded images
    - Max Value: Maximum value assigned to pixels above threshold (1-255, default 255)
    - Adaptive Method: Calculation method (0=mean, 1=gaussian weighted, default 0)
    - Threshold Type: Binarization type (0=binary, 1=binary_inv, default 0)
    - Block Size: Neighborhood area size (odd values 3-99, default 11)
    - C: Constant subtracted from calculated threshold (-50 to 50, default 2)
    
    This configuration is ideal for:
    - Document image processing with uneven lighting
    - Text extraction from photographs
    - Binary image creation with local illumination adaptation
    - Comparing adaptive vs global thresholding techniques
    
    Args:
        enable_ui: Whether to enable the user interface. Defaults to True.
        
    Returns:
        ImageViewer: Configured ImageViewer with adaptive thresholding trackbars.
    """
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
    """Create an ImageViewer instance specialized for Hough line detection algorithm.
    
    This factory function creates an ImageViewer with trackbars configured for
    the Hough line detection algorithm, providing comprehensive control over
    line detection parameters for finding straight lines in edge-detected images.
    
    The Hough line detection controls include:
    - Image Selector: Choose between multiple loaded images
    - Rho: Distance resolution in pixels (1-5, default 1)
    - Theta (deg): Angular resolution in degrees (1-180, default 1)
    - Threshold: Minimum intersections to detect a line (1-200, default 100)
    - Min Line Length: Minimum line length in pixels (1-200, default 50)
    - Max Line Gap: Maximum gap between line segments (1-50, default 10)
    
    This configuration is ideal for:
    - Detecting straight lines in architectural images
    - Road lane detection in traffic images
    - Document structure analysis
    - Geometric shape detection and analysis
    
    Args:
        enable_ui: Whether to enable the user interface. Defaults to True.
        
    Returns:
        ImageViewer: Configured ImageViewer with Hough line detection trackbars.
    """
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
    """Create an ImageViewer instance specialized for Hough circle detection algorithm.
    
    This factory function creates an ImageViewer with trackbars configured for
    the Hough circle detection algorithm, providing complete control over circle
    detection parameters for finding circular objects in images.
    
    The Hough circle detection controls include:
    - Image Selector: Choose between multiple loaded images
    - DP: Inverse ratio of accumulator resolution (1-10, default 1)
    - Min Dist: Minimum distance between circle centers (1-200, default 50)
    - Param1: Upper threshold for edge detection (1-300, default 100)
    - Param2: Accumulator threshold for center detection (1-100, default 30)
    - Min Radius: Minimum circle radius in pixels (0-100, default 0)
    - Max Radius: Maximum circle radius in pixels (0-200, default 0, 0=no limit)
    
    This configuration is ideal for:
    - Detecting circular objects like coins, wheels, or balls
    - Medical image analysis for circular structures
    - Industrial inspection for circular components
    - Traffic sign detection (circular signs)
    
    Args:
        enable_ui: Whether to enable the user interface. Defaults to True.
        
    Returns:
        ImageViewer: Configured ImageViewer with Hough circle detection trackbars.
    """
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
    """Create an ImageViewer instance specialized for HSV color space filtering.
    
    This factory function creates an ImageViewer with trackbars configured for
    HSV (Hue, Saturation, Value) color filtering, which is highly effective for
    color-based object detection and segmentation tasks. HSV color space is more
    intuitive for color filtering than RGB.
    
    The HSV filtering controls include:
    - Image Selector: Choose between multiple loaded images
    - H Min: Minimum hue value (0-179, default 0)
    - S Min: Minimum saturation value (0-255, default 0)
    - V Min: Minimum value/brightness (0-255, default 0)
    - H Max: Maximum hue value (0-179, default 179)
    - S Max: Maximum saturation value (0-255, default 255)
    - V Max: Maximum value/brightness (0-255, default 255)
    
    This configuration is ideal for:
    - Color-based object detection and tracking
    - Skin tone detection in images
    - Traffic sign detection by color
    - Sports ball tracking and analysis
    
    Args:
        enable_ui: Whether to enable the user interface. Defaults to True.
        
    Returns:
        ImageViewer: Configured ImageViewer with HSV color filtering trackbars.
    """
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
    """Create an ImageViewer instance specialized for contour detection and analysis.
    
    This factory function creates an ImageViewer with trackbars configured for
    contour detection operations, providing comprehensive control over contour
    finding parameters, hierarchy modes, and area-based filtering for shape
    analysis and object detection.
    
    The contour detection controls include:
    - Image Selector: Choose between multiple loaded images
    - Threshold: Binary threshold for contour preprocessing (0-255, default 128)
    - Retrieval Mode: Contour hierarchy (0=external, 1=list, 2=ccomp, 3=tree, default 1)
    - Approximation: Chain approximation (1=none, 2=simple, 3=tc89_l1, 4=tc89_kcos, default 2)
    - Min Area: Minimum contour area filter (0-10000, default 100)
    - Max Area: Maximum contour area filter (0-50000, default 10000)
    
    This configuration is ideal for:
    - Object detection and shape analysis
    - Contour-based feature extraction
    - Area-based object filtering
    - Shape classification and measurement
    
    Args:
        enable_ui: Whether to enable the user interface. Defaults to True.
        
    Returns:
        ImageViewer: Configured ImageViewer with contour detection trackbars.
    """
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
    """Create an ImageViewer instance specialized for Harris and Shi-Tomasi corner detection.
    
    This factory function creates an ImageViewer with trackbars configured for
    corner detection algorithms, supporting both Harris corner detection and
    Shi-Tomasi (goodFeaturesToTrack) methods with comprehensive parameter control
    for feature point detection.
    
    The corner detection controls include:
    - Image Selector: Choose between multiple loaded images
    - Max Corners: Maximum number of corners to detect (1-1000, default 100)
    - Quality Level: Quality threshold (1-100, divide by 1000 for actual value, default 1)
    - Min Distance: Minimum distance between corners (1-50, default 10)
    - Block Size: Neighborhood size for corner calculation (odd values 3-23, default 3)
    - Use Harris: Algorithm selection (0=Shi-Tomasi, 1=Harris, default 0)
    - Harris k: Harris corner detection parameter (1-40, divide by 1000, default 4)
    
    This configuration is ideal for:
    - Feature point detection for image matching
    - Object tracking and recognition
    - Camera calibration and 3D reconstruction
    - Image registration and stitching
    
    Args:
        enable_ui: Whether to enable the user interface. Defaults to True.
        
    Returns:
        ImageViewer: Configured ImageViewer with corner detection trackbars.
    """
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
    """Create an ImageViewer instance specialized for geometric image transformations.
    
    This factory function creates an ImageViewer with trackbars configured for
    geometric transformations including rotation, scaling, and translation.
    These operations are fundamental for image registration, correction, and
    augmentation tasks.
    
    The geometric transformation controls include:
    - Image Selector: Choose between multiple loaded images
    - Angle: Rotation angle in degrees (0-360, default 0)
    - Scale X: Horizontal scaling factor (1-300, divide by 100 for actual scale, default 100)
    - Scale Y: Vertical scaling factor (1-300, divide by 100 for actual scale, default 100)
    - Translate X: Horizontal translation (-250 to 250, subtract 250 from value, default 0)
    - Translate Y: Vertical translation (-250 to 250, subtract 250 from value, default 0)
    
    This configuration is ideal for:
    - Image registration and alignment
    - Perspective correction and rectification
    - Data augmentation for machine learning
    - Image preprocessing for analysis
    
    Args:
        enable_ui: Whether to enable the user interface. Defaults to True.
        
    Returns:
        ImageViewer: Configured ImageViewer with geometric transformation trackbars.
    """
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
    """Create an ImageViewer instance specialized for Sobel and Laplacian edge detection.
    
    This factory function creates an ImageViewer with trackbars configured for
    Sobel and Laplacian edge detection algorithms, providing complete control
    over gradient-based edge detection parameters for different image analysis needs.
    
    The edge detection controls include:
    - Image Selector: Choose between multiple loaded images
    - Detector: Edge detection method (0=Sobel X, 1=Sobel Y, 2=Laplacian, default 0)
    - Kernel Size: Operator kernel size (odd values 1-31, default 3)
    - Scale: Scaling factor for computed derivatives (1-10, default 1)
    - Delta: Value added to results (0-100, default 0)
    
    This configuration is ideal for:
    - Directional edge detection with Sobel operators
    - Second-order edge detection with Laplacian
    - Feature extraction for texture analysis
    - Preprocessing for advanced edge detection algorithms
    
    Args:
        enable_ui: Whether to enable the user interface. Defaults to True.
        
    Returns:
        ImageViewer: Configured ImageViewer with Sobel/Laplacian edge detection trackbars.
    """
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Detector", "detector", 2, 0),  # 0=Sobel X, 1=Sobel Y, 2=Laplacian
        make_odd_trackbar("Kernel Size", "kernel_size", 31, 3),
        make_int_trackbar("Scale", "scale", 10, 1),
        make_int_trackbar("Delta", "delta", 100, 0)
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_viewer_for_histogram_equalization(enable_ui: bool = True) -> ImageViewer:
    """Create an ImageViewer instance specialized for histogram equalization and CLAHE.
    
    This factory function creates an ImageViewer with trackbars configured for
    histogram equalization techniques including global histogram equalization
    and Contrast Limited Adaptive Histogram Equalization (CLAHE) for improved
    image contrast and visibility.
    
    The histogram equalization controls include:
    - Image Selector: Choose between multiple loaded images
    - Method: Equalization method (0=none, 1=global, 2=CLAHE, default 0)
    - Clip Limit: CLAHE contrast limiting (1-40, divide by 10 for actual value, default 20)
    - Tile Grid X: CLAHE horizontal tile count (1-16, default 8)
    - Tile Grid Y: CLAHE vertical tile count (1-16, default 8)
    
    This configuration is ideal for:
    - Enhancing low-contrast images
    - Medical image processing and analysis
    - Improving visibility in dark or overexposed images
    - Preprocessing for feature detection algorithms
    
    Args:
        enable_ui: Whether to enable the user interface. Defaults to True.
        
    Returns:
        ImageViewer: Configured ImageViewer with histogram equalization trackbars.
    """
    trackbars = [
        make_image_selector(),
        make_int_trackbar("Method", "method", 2, 0),  # 0=none, 1=global, 2=CLAHE
        make_int_trackbar("Clip Limit", "clip_limit", 40, 20),  # Divide by 10
        make_int_trackbar("Tile Grid X", "tile_grid_x", 16, 8),
        make_int_trackbar("Tile Grid Y", "tile_grid_y", 16, 8)
    ]
    return ImageViewer.create_with_trackbars(trackbars, enable_ui)

def create_auto_viewer(config: ViewerConfig, trackbar_definitions: List[Dict[str, Any]], app_debug_mode: bool, max_headless_iterations: int = 1) -> ImageViewer:
    """Create an ImageViewer instance with complete manual configuration control.
    
    This factory function provides the most flexible approach to creating an
    ImageViewer by accepting all configuration parameters directly. It is designed
    to match exact user workflows and provide complete control over all aspects
    of the viewer setup including configuration, trackbars, and execution modes.
    
    This function serves as the foundation for custom viewer configurations that
    don't fit the specialized factory patterns, or when precise control over
    all parameters is required for specific applications.
    
    Args:
        config: ViewerConfig instance containing window settings, debug modes,
            and display parameters. Must be pre-configured with desired settings.
        trackbar_definitions: List of trackbar configuration dictionaries,
            each containing trackbar setup parameters like name, param_name,
            max_value, initial_value, and optional callback functions.
        app_debug_mode: Whether to enable debug/UI mode. True enables full
            interactive mode with windows and trackbars, False enables headless
            operation for automated processing.
        max_headless_iterations: Maximum number of processing iterations in
            headless mode before automatic termination. Defaults to 1.
            
    Returns:
        ImageViewer: A fully configured ImageViewer instance ready for immediate
            use with the specified configuration and trackbar setup.
            
    Examples:
        >>> # Custom configuration with specific trackbars
        >>> config = ViewerConfig().set_window_size(1024, 768).set_debug_mode(True)
        >>> trackbars = [
        ...     {"name": "Custom Param", "param_name": "custom", "max_value": 100, "initial_value": 50}
        ... ]
        >>> viewer = create_auto_viewer(config, trackbars, True, 1)
        >>> 
        >>> # Headless processing configuration
        >>> config = ViewerConfig().set_debug_mode(False)
        >>> viewer = create_auto_viewer(config, [], False, 100)
        
    Performance:
        Time Complexity: O(n) where n is the number of trackbar definitions.
        Space Complexity: O(n) for trackbar configuration storage.
    """
    return ImageViewer(config, trackbar_definitions, app_debug_mode, max_headless_iterations)
