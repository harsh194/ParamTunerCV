#!/usr/bin/env python3
"""
Example 1: Basic Usage
======================

This example shows the most basic usage of the Parameter library:
- How to set up a simple viewer
- Basic trackbar definitions
- Main processing loop
- How to display images and access parameters
"""

from ParamTunerCV import ImageViewer, ViewerConfig
import numpy as np
import cv2

def main():
    # Create configuration
    config = ViewerConfig()
    
    # Define trackbars - this is the core of parameter control
    trackbar_definitions = [
        {"name": "Show Image", "param_name": "show", "max_value": "num_images-1", "initial_value": 0},
        {"name": "Threshold", "param_name": "threshold", "max_value": 255, "initial_value": 128},
        {"name": "Kernel Size", "param_name": "kernel_size", "max_value": 31, "callback": "odd", "initial_value": 5},
        {"name": "Iterations", "param_name": "iterations", "max_value": 10, "initial_value": 2}
    ]
    
    # Create the viewer
    viewer = ImageViewer(config, trackbar_definitions)
    
    # Create some test images
    img_width, img_height = 400, 300
    
    # Original image with shapes
    original = np.zeros((img_height, img_width), dtype=np.uint8)
    cv2.rectangle(original, (50, 50), (200, 150), 255, -1)
    cv2.circle(original, (300, 200), 50, 128, -1)
    
    # Add some noise
    noise = np.random.normal(0, 20, original.shape).astype(np.int16)
    noisy = np.clip(original.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    print("Basic Parameter Demo")
    print("- Use trackbars to adjust parameters in real-time")
    print("- 'Show Image' switches between different processed results")
    print("- Press 'q' or ESC to quit")
    
    # Main processing loop - this is the standard pattern
    while viewer.should_loop_continue():
        # Get current parameter values from trackbars
        params = viewer.trackbar.parameters
        
        threshold_val = params.get("threshold")
        kernel_size = params.get("kernel_size")
        iterations = params.get("iterations")
        
        # Process the image based on parameters
        _, thresholded = cv2.threshold(noisy, threshold_val, 255, cv2.THRESH_BINARY)
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        processed = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel, iterations=iterations)
        
        # Set the images to display - the trackbar will choose which one to show
        viewer.display_images = [
            (original, "Original"),
            (noisy, "Noisy"),
            (thresholded, f"Thresholded (T={threshold_val})"),
            (processed, f"Processed (K={kernel_size}, I={iterations})")
        ]
        
        # Optional: Log current parameters to text window
        viewer.log(f"Parameters: threshold={threshold_val}, kernel={kernel_size}, iterations={iterations}")
    
    # Clean up when done
    viewer.cleanup_viewer()
    print("Basic usage example completed!")

if __name__ == "__main__":
    main()