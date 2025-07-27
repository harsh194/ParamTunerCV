#!/usr/bin/env python3
"""
Example 2: Window Control
=========================

This example demonstrates how to control which windows are displayed:
- Enable/disable text window
- Enable/disable analysis control window
- Different combinations of window settings
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import ImageViewer, ViewerConfig
import numpy as np
import cv2

def create_demo_image():
    """Create a simple demo image."""
    img = np.zeros((300, 400), dtype=np.uint8)
    cv2.rectangle(img, (50, 50), (200, 150), 255, -1)
    cv2.circle(img, (300, 200), 50, 128, -1)
    cv2.putText(img, 'DEMO', (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, 200, 2)
    return img

def demo_window_configuration(config_name, text_window, analysis_control_window):
    """Demo a specific window configuration."""
    print(f"\n=== {config_name} ===")
    print(f"Text window: {'ON' if text_window else 'OFF'}")
    print(f"Analysis control window: {'ON' if analysis_control_window else 'OFF'}")
    print("Press 'q' or ESC to continue to next configuration...")
    
    # Create configuration
    config = ViewerConfig()
    
    # Simple trackbar setup
    trackbar_definitions = [
        {"name": "Show Image", "param_name": "show", "max_value": "num_images-1", "initial_value": 0},
        {"name": "Brightness", "param_name": "brightness", "max_value": 100, "initial_value": 0},
        {"name": "Contrast", "param_name": "contrast", "max_value": 300, "initial_value": 100}
    ]
    
    # Create viewer with specific window settings
    viewer = ImageViewer(config, trackbar_definitions, 
                        text_window=text_window, 
                        analysis_control_window=analysis_control_window)
    
    # Get demo image
    demo_img = create_demo_image()
    
    # Simple processing loop
    while viewer.should_loop_continue():
        params = viewer.trackbar.parameters
        
        brightness = params.get("brightness")
        contrast = params.get("contrast")
        
        # Apply brightness and contrast
        processed = demo_img.astype(np.float32)
        processed = processed * (contrast / 100.0) + brightness
        processed = np.clip(processed, 0, 255).astype(np.uint8)
        
        # Display images
        viewer.display_images = [
            (demo_img, "Original"),
            (processed, f"Adjusted (B:{brightness}, C:{contrast})")
        ]
        
        # Log to text window (if enabled)
        viewer.log(f"Current config: {config_name}")
        viewer.log(f"Brightness: {brightness}, Contrast: {contrast}")
    
    viewer.cleanup_viewer()

def main():
    print("Window Control Demo")
    print("This demo shows 4 different window configurations:")
    print("1. Both windows enabled (default)")
    print("2. Text window disabled")
    print("3. Analysis control window disabled") 
    print("4. Both windows disabled (minimal UI)")
    
    # Configuration 1: Both windows enabled (default behavior)
    demo_window_configuration(
        "Both Windows Enabled", 
        text_window=True, 
        analysis_control_window=True
    )
    
    # Configuration 2: Text window disabled
    demo_window_configuration(
        "Text Window Disabled", 
        text_window=False, 
        analysis_control_window=True
    )
    
    # Configuration 3: Analysis control window disabled
    demo_window_configuration(
        "Analysis Control Window Disabled", 
        text_window=True, 
        analysis_control_window=False
    )
    
    # Configuration 4: Both windows disabled (minimal UI)
    demo_window_configuration(
        "Both Windows Disabled (Minimal UI)", 
        text_window=False, 
        analysis_control_window=False
    )
    
    print("\nWindow control demo completed!")
    print("\nKey points:")
    print("- text_window=True/False controls the text logging window")
    print("- analysis_control_window=True/False controls the analysis panel")
    print("- Both default to True if not specified")
    print("- Use False for cleaner UI when you don't need those features")

if __name__ == "__main__":
    main()