
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

def create_auto_viewer(config: ViewerConfig, trackbar_definitions: List[Dict[str, Any]], app_debug_mode: bool, max_headless_iterations: int = 1) -> ImageViewer:
    """
    Create an ImageViewer that automatically handles setup and headless iterations.
    This is designed to match the exact user workflow.
    """
    return ImageViewer(config, trackbar_definitions, app_debug_mode, max_headless_iterations)
