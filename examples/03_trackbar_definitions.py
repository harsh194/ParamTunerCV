#!/usr/bin/env python3
"""
Example 3: Trackbar Definitions
===============================

This example demonstrates all the ways to define trackbars and access parameters:
- Basic trackbar definition format
- Using helper functions (make_int_trackbar, make_odd_trackbar, etc.)
- Different callback types (odd, roi_x, roi_y, etc.)
- How to access parameter values
- Custom trackbar configurations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import ImageViewer, ViewerConfig
from src import make_int_trackbar, make_odd_trackbar, make_image_selector, make_roi_trackbars
import numpy as np
import cv2

def main():
    print("Trackbar Definitions Demo")
    print("This example shows all trackbar definition methods and parameter access")
    
    # Create configuration
    config = ViewerConfig()
    
    # Method 1: Manual trackbar definitions (full control)
    # Basic format: {"name": "Display Name", "param_name": "code_name", "max_value": max, "initial_value": initial}
    manual_trackbars = [
        # Image selector - special case with "num_images-1"
        {"name": "Show Image", "param_name": "show", "max_value": "num_images-1", "initial_value": 0},
        
        # Basic integer trackbar
        {"name": "Basic Integer", "param_name": "basic_int", "max_value": 100, "initial_value": 50},
        
        # Trackbar with odd callback (forces odd values, useful for kernel sizes)
        {"name": "Odd Values Only", "param_name": "odd_value", "max_value": 31, "callback": "odd", "initial_value": 5},
        
        # Enum-like trackbar (mode selector)
        {"name": "Processing Mode", "param_name": "mode", "max_value": 3, "initial_value": 0}
    ]
    
    # Method 2: Using helper functions (recommended for common cases)
    helper_trackbars = [
        # Integer trackbar helper
        make_int_trackbar("Helper Integer", "helper_int", max_value=255, initial_value=128),
        
        # Odd trackbar helper (automatically ensures odd values)
        make_odd_trackbar("Helper Odd", "helper_odd", max_value=21, initial_value=7),
        
        # Image selector helper
        make_image_selector("Image Selector", "image_sel")
    ]
    
    # Method 3: ROI trackbars (returns a list of 4 trackbars)
    roi_trackbars = make_roi_trackbars()  # Creates: roi_x, roi_y, roi_width, roi_height
    
    # Combine all trackbar definitions
    trackbar_definitions = manual_trackbars + helper_trackbars + roi_trackbars
    
    # Create viewer
    viewer = ImageViewer(config, trackbar_definitions)
    
    # Create test images to demonstrate different processing modes
    img_width, img_height = 400, 300
    
    # Test image 1: Simple shapes
    img1 = np.zeros((img_height, img_width), dtype=np.uint8)
    cv2.rectangle(img1, (50, 50), (200, 150), 255, -1)
    cv2.circle(img1, (300, 200), 50, 128, -1)
    
    # Test image 2: Gradient
    img2 = np.zeros((img_height, img_width), dtype=np.uint8)
    for x in range(img_width):
        intensity = int(255 * x / img_width)
        img2[:, x] = intensity
    
    # Test image 3: Text
    img3 = np.zeros((img_height, img_width), dtype=np.uint8)
    cv2.putText(img3, 'TRACKBARS', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, 255, 2)
    
    test_images = [img1, img2, img3]
    
    print("\nTrackbar Controls:")
    print("Manual Trackbars:")
    print("  - Show Image: Switches between test images")
    print("  - Basic Integer: 0-100 range")
    print("  - Odd Values Only: Forces odd numbers (3, 5, 7, 9, etc.)")
    print("  - Processing Mode: 0=Original, 1=Threshold, 2=Blur, 3=Both")
    print("\nHelper Trackbars:")
    print("  - Helper Integer: Made with make_int_trackbar()")
    print("  - Helper Odd: Made with make_odd_trackbar()")
    print("  - Image Selector: Made with make_image_selector()")
    print("\nROI Trackbars:")
    print("  - ROI X, Y, Width, Height: Made with make_roi_trackbars()")
    print("\nPress 'q' or ESC to quit")
    
    while viewer.should_loop_continue():
        # Accessing parameters - this is the key part!
        params = viewer.trackbar.parameters
        
        # Get values using .get() - no need for defaults since initial_value is set
        basic_int = params.get("basic_int")
        odd_value = params.get("odd_value")
        mode = params.get("mode")
        helper_int = params.get("helper_int")
        helper_odd = params.get("helper_odd")
        
        # ROI parameters
        roi_x = params.get("roi_x")
        roi_y = params.get("roi_y")
        roi_width = params.get("roi_width")
        roi_height = params.get("roi_height")
        
        # Select base image
        base_image = test_images[0]  # Default to first image
        
        # Process based on mode
        if mode == 0:  # Original
            processed = base_image.copy()
            mode_name = "Original"
        elif mode == 1:  # Threshold
            _, processed = cv2.threshold(base_image, helper_int, 255, cv2.THRESH_BINARY)
            mode_name = f"Threshold (T={helper_int})"
        elif mode == 2:  # Blur
            if helper_odd >= 3:
                processed = cv2.GaussianBlur(base_image, (helper_odd, helper_odd), 0)
                mode_name = f"Blur (K={helper_odd})"
            else:
                processed = base_image.copy()
                mode_name = "Blur (kernel too small)"
        else:  # Both
            _, thresholded = cv2.threshold(base_image, helper_int, 255, cv2.THRESH_BINARY)
            if helper_odd >= 3:
                processed = cv2.GaussianBlur(thresholded, (helper_odd, helper_odd), 0)
                mode_name = f"Threshold+Blur (T={helper_int}, K={helper_odd})"
            else:
                processed = thresholded
                mode_name = f"Threshold only (T={helper_int})"
        
        # Create ROI visualization
        roi_image = processed.copy()
        if len(roi_image.shape) == 2:  # Convert to color for colored ROI
            roi_image = cv2.cvtColor(roi_image, cv2.COLOR_GRAY2BGR)
        
        # Draw ROI rectangle
        cv2.rectangle(roi_image, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)
        cv2.putText(roi_image, f"ROI", (roi_x, roi_y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Set images for display
        viewer.display_images = [
            (base_image, "Base Image"),
            (processed, mode_name),
            (roi_image, f"With ROI ({roi_x},{roi_y}) {roi_width}x{roi_height}")
        ]
        
        # Log all parameter values to demonstrate access
        viewer.log("=== Parameter Values ===")
        viewer.log(f"Manual trackbars:")
        viewer.log(f"  basic_int = {basic_int}")
        viewer.log(f"  odd_value = {odd_value} (note: forced to be odd)")
        viewer.log(f"  mode = {mode}")
        viewer.log(f"Helper trackbars:")
        viewer.log(f"  helper_int = {helper_int}")
        viewer.log(f"  helper_odd = {helper_odd}")
        viewer.log(f"ROI trackbars:")
        viewer.log(f"  roi_x = {roi_x}, roi_y = {roi_y}")
        viewer.log(f"  roi_width = {roi_width}, roi_height = {roi_height}")
        viewer.log(f"Current mode: {mode_name}")
    
    viewer.cleanup_viewer()
    
    print("\nTrackbar Definitions Summary:")
    print("\n1. Manual Definition Format:")
    print("   {\"name\": \"Display Name\", \"param_name\": \"code_name\", \"max_value\": 100, \"initial_value\": 50}")
    print("\n2. Special Callbacks:")
    print("   - \"odd\": Forces odd values (useful for kernel sizes)")
    print("   - \"roi_x\", \"roi_y\", \"roi_width\", \"roi_height\": For ROI controls")
    print("\n3. Helper Functions:")
    print("   - make_int_trackbar(name, param_name, max_value, initial_value)")
    print("   - make_odd_trackbar(name, param_name, max_value, initial_value)")
    print("   - make_image_selector(name, param_name)")
    print("   - make_roi_trackbars() -> returns list of 4 ROI trackbars")
    print("\n4. Parameter Access:")
    print("   params = viewer.trackbar.parameters")
    print("   value = params.get(\"param_name\", default_value)")
    print("\nTrackbar definitions example completed!")

if __name__ == "__main__":
    main()