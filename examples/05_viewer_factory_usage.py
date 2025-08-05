"""
Example: Using ViewerFactory Functions

This example demonstrates how to use the different viewer factory functions
available in src.utils.viewer_factory for various computer vision tasks.
Each factory function creates a viewer pre-configured with appropriate trackbars
for specific image processing operations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cv2
import numpy as np

from src import (
    create_viewer_with_common_controls,
    create_viewer_for_filtering,
    create_viewer_for_morphology,
    create_viewer_for_canny,
    create_viewer_for_hsv_filtering,
)

def demonstrate_common_controls():
    """Example 2: Viewer with common image processing controls"""
    print("Example 2: Common Controls Viewer")
    viewer = create_viewer_with_common_controls()
    
    # Load multiple images for selector
    images = []
    for i in range(3):
        img = np.random.randint(0, 255, (400, 600, 3), dtype=np.uint8)
        cv2.putText(img, f"Image {i+1}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        images.append(img)
    
    while viewer.should_loop_continue():
        params = viewer.trackbar.parameters
        
        # Use image selector
        selected_image = images[params['show']]
        
        # Apply threshold
        gray = cv2.cvtColor(selected_image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, params['threshold'], 255, cv2.THRESH_BINARY)
        
        # Apply morphological operations with kernel size and iterations
        kernel = np.ones((params['kernel_size'], params['kernel_size']), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=params['iterations'])
        
        viewer.display_images = [
            (selected_image, "Original"),
            (thresh, "Thresholded"),
            (processed, "Morphology Applied")
        ]
    
    viewer.cleanup_viewer()

def demonstrate_filtering_viewer():
    """Example 3: Image filtering operations"""
    print("Example 3: Filtering Viewer")
    viewer = create_viewer_for_filtering()
    
    # Create noisy image
    image = np.random.randint(0, 255, (400, 600, 3), dtype=np.uint8)
    noise = np.random.normal(0, 25, image.shape).astype(np.uint8)
    noisy_image = cv2.add(image, noise)
    
    while viewer.should_loop_continue():
        params = viewer.trackbar.parameters
        
        # Apply different filters
        gaussian = cv2.GaussianBlur(noisy_image, (params['gaussian_size'], params['gaussian_size']), 0)
        median = cv2.medianBlur(noisy_image, params['median_size'])
        bilateral = cv2.bilateralFilter(noisy_image, params['bilateral_d'], 
                                      params['bilateral_sigma_color'], 
                                      params['bilateral_sigma_space'])
        
        viewer.display_images = [
            (noisy_image, "Noisy Original"),
            (gaussian, "Gaussian Blur"),
            (median, "Median Filter"),
            (bilateral, "Bilateral Filter")
        ]
    
    viewer.cleanup_viewer()

def demonstrate_canny_viewer():
    """Example 4: Canny edge detection"""
    print("Example 4: Canny Edge Detection")
    viewer = create_viewer_for_canny()
    
    # Create image with shapes
    image = np.zeros((400, 600, 3), dtype=np.uint8)
    cv2.rectangle(image, (100, 100), (300, 200), (255, 255, 255), -1)
    cv2.circle(image, (450, 150), 80, (128, 128, 128), -1)
    
    while viewer.should_loop_continue():
        params = viewer.trackbar.parameters
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 
                         params['lower_threshold'], 
                         params['upper_threshold'],
                         apertureSize=params['aperture_size'],
                         L2gradient=bool(params['l2_gradient']))
        
        viewer.display_images = [
            (image, "Original"),
            (edges, "Canny Edges")
        ]
    
    viewer.cleanup_viewer()

def demonstrate_morphology_viewer():
    """Example 5: Morphological operations"""
    print("Example 5: Morphological Operations")
    viewer = create_viewer_for_morphology()
    
    # Create binary image with text
    image = np.zeros((400, 600), dtype=np.uint8)
    cv2.putText(image, "MORPHOLOGY", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, 255, 3)
    
    morph_ops = {
        0: cv2.MORPH_ERODE,
        1: cv2.MORPH_DILATE, 
        2: cv2.MORPH_OPEN,
        3: cv2.MORPH_CLOSE,
        4: cv2.MORPH_GRADIENT,
        5: cv2.MORPH_TOPHAT,
        6: cv2.MORPH_BLACKHAT
    }
    
    kernel_shapes = {
        0: cv2.MORPH_RECT,
        1: cv2.MORPH_ELLIPSE,
        2: cv2.MORPH_CROSS
    }
    
    while viewer.should_loop_continue():
        params = viewer.trackbar.parameters
        
        kernel = cv2.getStructuringElement(
            kernel_shapes[params['kernel_shape']],
            (params['kernel_size'], params['kernel_size'])
        )
        
        processed = cv2.morphologyEx(image, 
                                   morph_ops[params['morph_op']], 
                                   kernel, 
                                   iterations=params['iterations'])
        
        viewer.display_images = [
            (image, "Original"),
            (processed, f"Morphology Op: {params['morph_op']}")
        ]
    
    viewer.cleanup_viewer()

def demonstrate_hsv_filtering():
    """Example 6: HSV color filtering"""
    print("Example 6: HSV Color Filtering")
    viewer = create_viewer_for_hsv_filtering()
    
    # Create colorful image
    image = np.zeros((400, 600, 3), dtype=np.uint8)
    cv2.rectangle(image, (50, 50), (150, 150), (0, 0, 255), -1)    # Red
    cv2.rectangle(image, (200, 50), (300, 150), (0, 255, 0), -1)   # Green  
    cv2.rectangle(image, (350, 50), (450, 150), (255, 0, 0), -1)   # Blue
    cv2.rectangle(image, (125, 200), (225, 300), (0, 255, 255), -1) # Yellow
    cv2.rectangle(image, (275, 200), (375, 300), (255, 0, 255), -1) # Magenta
    
    while viewer.should_loop_continue():
        params = viewer.trackbar.parameters
        
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Create mask based on HSV range
        lower = np.array([params['h_min'], params['s_min'], params['v_min']])
        upper = np.array([params['h_max'], params['s_max'], params['v_max']])
        mask = cv2.inRange(hsv, lower, upper)
        
        # Apply mask
        filtered = cv2.bitwise_and(image, image, mask=mask)
        
        viewer.display_images = [
            (image, "Original"),
            (mask, "HSV Mask"),
            (filtered, "Filtered Result")
        ]
    
    viewer.cleanup_viewer()

if __name__ == "__main__":
    print("ViewerFactory Examples")
    print("Choose an example to run:")
    print("1. Common Controls")
    print("2. Filtering Operations")
    print("3. Canny Edge Detection")
    print("4. Morphological Operations")
    print("5. HSV Color Filtering")
    
    choice = input("Enter choice (1-6): ")
    
    examples = {
        '1': demonstrate_common_controls,
        '2': demonstrate_filtering_viewer,
        '3': demonstrate_canny_viewer,
        '4': demonstrate_morphology_viewer,
        '5': demonstrate_hsv_filtering
    }
    
    if choice in examples:
        examples[choice]()
    else:
        print("Invalid choice. Running common controls example...")
        demonstrate_common_controls()