# check.py
from src import ImageViewer, ViewerConfig
import numpy as np
import cv2
import time 

# --- Configuration ---
config = ViewerConfig()

# Global flag for the application to decide if it wants UI
APP_DEBUG_MODE = True  # Set to True to see windows, False for headless processing

trackbar_definitions = [
    {"name": "Show Image", "param_name": "show", "max_value": "num_images-1", "initial_value": 0},
    {"name": "Count", "param_name": "count", "max_value": 50, "initial_value": 10}, # Initial value 10
    {"name": "Gauss Size", "param_name": "GaussianSize", "max_value": 31, "callback": "odd", "initial_value": 5}, # Initial value 5
    {"name": "Thresh Val", "param_name": "g_thresh", "max_value": 255, "initial_value": 128}, # Initial value 128
]

IMG_HEIGHT, IMG_WIDTH = 600, 800

# Initialize the viewer with a try-except block to handle potential GIL issues
try:
    # Examples of window control:
    # Both windows enabled (default): 
    # viewer = ImageViewer(config, trackbar_definitions, APP_DEBUG_MODE, max_headless_iterations=1)
    
    # Text window disabled: 
    # viewer = ImageViewer(config, trackbar_definitions, APP_DEBUG_MODE, max_headless_iterations=1, text_window=False)
    
    # Analysis control window disabled: 
    # viewer = ImageViewer(config, trackbar_definitions, APP_DEBUG_MODE, max_headless_iterations=1, analysis_control_window=False)
    
    # Both windows disabled: 
    # viewer = ImageViewer(config, trackbar_definitions, APP_DEBUG_MODE, max_headless_iterations=1)
    viewer = ImageViewer(config, trackbar_definitions, APP_DEBUG_MODE)
    # viewer = ImageViewer(config, trackbar_definitions)
except Exception as e:
    print(f"Error initializing viewer: {e}")
    import sys
    sys.exit(1)

while viewer.should_loop_continue():
    params = viewer.trackbar.parameters
    
    current_thresh = params.get("g_thresh") 
    current_gaussian_size = params.get("GaussianSize", 5)
    block_count = params.get("count", 10)

    base_color_image = np.full((IMG_HEIGHT, IMG_WIDTH, 3), (block_count * 5, 0, 0), dtype=np.uint8)
    cv2.rectangle(base_color_image, (50, 50), (IMG_WIDTH - 50, IMG_HEIGHT - 50), (0, 255, 0), 3)

    gray_image = cv2.cvtColor(base_color_image, cv2.COLOR_BGR2GRAY)
    viewer.log(f"shape of grayscale image - {gray_image.shape}")
    gauss_image = gray_image.copy()
    if current_gaussian_size > 0:
        try:
            gauss_image = cv2.GaussianBlur(gray_image, (current_gaussian_size, current_gaussian_size), 0)
        except cv2.error as e:
            print(f"GaussianBlur Error: {e}. Size: {current_gaussian_size}")

    _, thresh_image = cv2.threshold(gauss_image, current_thresh, 255, cv2.THRESH_BINARY)
    

    viewer.display_images = [
        (base_color_image, "Color"),
        (gray_image, "Grayscale Image"),
        (gauss_image, f"Gaussian Blur (Size: {current_gaussian_size})"),
        (thresh_image, f"Threshold (Val: {current_thresh})")
    ]

viewer.cleanup_viewer()
