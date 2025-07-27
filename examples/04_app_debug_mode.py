"""
Example 4: APP_DEBUG_MODE - Development vs Production
====================================================

This example demonstrates the difference between development and production modes:
- APP_DEBUG_MODE = True: For development, parameter tuning, and analysis
- APP_DEBUG_MODE = False: For production deployment without GUI or interaction

Key differences:
- True: Shows windows, allows parameter tuning, enables analysis
- False: No windows, fixed parameters, production-ready processing
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import ImageViewer, ViewerConfig
import numpy as np
import cv2
import time

def create_test_images():
    """Create sample images for processing."""
    images = []
    img_width, img_height = 400, 300
    
    for i in range(3):
        img = np.zeros((img_height, img_width), dtype=np.uint8)
        
        # Add shapes with different characteristics
        cv2.rectangle(img, (50 + i*20, 50 + i*10), (200 + i*30, 150 + i*20), 200, -1)
        cv2.circle(img, (300 - i*30, 200 + i*15), 40 - i*8, 150, -1)
        
        # Add realistic noise
        noise = np.random.normal(0, 20, img.shape).astype(np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        images.append((img, f"test_image_{i+1}"))
    
    return images

def development_mode_example():
    """
    APP_DEBUG_MODE = True
    
    Use this mode for:
    - Parameter tuning and experimentation
    - Visual feedback and analysis
    - Development and debugging
    - Understanding optimal parameters
    """
    print("=== DEVELOPMENT MODE (APP_DEBUG_MODE = True) ===")
    print("✓ Shows GUI windows for visual feedback")
    print("✓ Allows real-time parameter adjustment")
    print("✓ Enables analysis and experimentation")
    print("✓ Manual control over processing loop")
    print()
    
    # Get test images
    test_images = create_test_images()
    
    # Configuration for development
    config = ViewerConfig()
    
    # Trackbars with wide ranges for experimentation
    trackbar_definitions = [
        {"name": "Show Image", "param_name": "show", "max_value": "num_images-1", "initial_value": 0},
        {"name": "Image Selector", "param_name": "image_idx", "max_value": len(test_images) - 1, "initial_value": 0},
        {"name": "Threshold", "param_name": "threshold", "max_value": 255, "initial_value": 128},
        {"name": "Kernel Size", "param_name": "kernel_size", "max_value": 21, "callback": "odd", "initial_value": 5},
        {"name": "Iterations", "param_name": "iterations", "max_value": 10, "initial_value": 2}
    ]
    
    # Create viewer with GUI enabled (APP_DEBUG_MODE = True)
    viewer = ImageViewer(config, trackbar_definitions, enable_ui=True)
    
    print("GUI windows should now be visible...")
    print("You can adjust parameters using trackbars")
    print("Press ESC or close window to continue")
    print()
    
    iteration_count = 0
    start_time = time.time()
    
    # Interactive loop - user controls when to exit
    while viewer.should_loop_continue():
        # Get current parameters from trackbars (user can adjust in real-time)
        params = viewer.trackbar.parameters
        image_idx = params.get("image_idx", 0)
        threshold_val = params.get("threshold", 128)
        kernel_size = params.get("kernel_size", 5)
        iterations = params.get("iterations", 2)
        
        # Process current image
        current_image, image_name = test_images[image_idx]
        
        # Apply processing pipeline
        _, thresholded = cv2.threshold(current_image, threshold_val, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        cleaned = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel, iterations=iterations)
        final_result = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        
        # Display multiple processing stages for analysis
        viewer.display_images = [
            (current_image, f"Original: {image_name}"),
            (thresholded, f"Threshold: {threshold_val}"),
            (cleaned, f"Opened (K:{kernel_size}, I:{iterations})"),
            (final_result, f"Final Result")
        ]
        
        iteration_count += 1
        
        # Limit demo time but allow user interaction
        if time.time() - start_time > 10:  # 10 second demo
            print("Demo time limit reached...")
            break
    
    viewer.cleanup_viewer()
    
    print(f"Development mode completed:")
    print(f"  Iterations: {iteration_count}")
    print(f"  Final parameters found:")
    print(f"    - Threshold: {params.get('threshold')}")
    print(f"    - Kernel Size: {params.get('kernel_size')}")
    print(f"    - Iterations: {params.get('iterations')}")
    print()

def production_mode_example():
    """
    APP_DEBUG_MODE = False
    
    Use this mode for:
    - Production deployment
    - Server environments (no display)
    - Batch processing with known parameters
    - Automated pipelines
    """
    print("=== PRODUCTION MODE (APP_DEBUG_MODE = False) ===")
    print("✓ No GUI windows (headless)")
    print("✓ Fixed parameters (no interaction)")
    print("✓ Automatic processing")
    print("✓ Production-ready deployment")
    print()
    
    # Get test images
    test_images = create_test_images()
    
    # Configuration for production
    config = ViewerConfig()
    
    # Fixed parameters determined from development phase
    OPTIMAL_THRESHOLD = 145      # Found during development
    OPTIMAL_KERNEL_SIZE = 7      # Optimal for this use case
    OPTIMAL_ITERATIONS = 3       # Balance of quality vs speed
    
    print(f"Using production parameters:")
    print(f"  THRESHOLD = {OPTIMAL_THRESHOLD}")
    print(f"  KERNEL_SIZE = {OPTIMAL_KERNEL_SIZE}")
    print(f"  ITERATIONS = {OPTIMAL_ITERATIONS}")
    print()
    
    # Trackbars with FIXED optimal values
    trackbar_definitions = [
        {"name": "Show Image", "param_name": "show", "max_value": "num_images-1", "initial_value": 0},
        {"name": "Image Selector", "param_name": "image_idx", "max_value": len(test_images) - 1, "initial_value": 0},
        {"name": "Threshold", "param_name": "threshold", "max_value": 255, "initial_value": OPTIMAL_THRESHOLD},
        {"name": "Kernel Size", "param_name": "kernel_size", "max_value": 21, "callback": "odd", "initial_value": OPTIMAL_KERNEL_SIZE},
        {"name": "Iterations", "param_name": "iterations", "max_value": 10, "initial_value": OPTIMAL_ITERATIONS}
    ]
    
    # Create viewer with GUI disabled (APP_DEBUG_MODE = False)
    viewer = ImageViewer(config, trackbar_definitions, 
                        enable_ui=False,  # No GUI
                        max_headless_iterations=len(test_images))  # Process all images
    
    print("Processing images in production mode (no windows)...")
    
    processed_results = []
    start_time = time.time()
    
    # Automatic processing loop
    while viewer.should_loop_continue():
        # Get FIXED parameters (no user interaction possible)
        params = viewer.trackbar.parameters
        image_idx = params.get("image_idx", 0)
        threshold_val = params.get("threshold")
        kernel_size = params.get("kernel_size")
        iterations = params.get("iterations")
        
        # Process current image
        current_image, image_name = test_images[image_idx]
        
        # Apply production processing pipeline
        _, thresholded = cv2.threshold(current_image, threshold_val, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        cleaned = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel, iterations=iterations)
        final_result = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        
        # Required: Set display images (even though no GUI)
        viewer.display_images = [
            (current_image, f"Input: {image_name}"),
            (final_result, f"Output: {image_name}")
        ]
        
        # Calculate metrics for production monitoring
        foreground_pixels = np.sum(final_result == 255)
        total_pixels = final_result.size
        foreground_ratio = foreground_pixels / total_pixels
        
        # Store result
        result = {
            "image_name": image_name,
            "foreground_ratio": foreground_ratio,
            "parameters": {
                "threshold": threshold_val,
                "kernel_size": kernel_size,
                "iterations": iterations
            }
        }
        processed_results.append(result)
        
        # Production logging
        print(f"✓ Processed {image_name}: {foreground_ratio:.3f} foreground ratio")
    
    total_time = time.time() - start_time
    viewer.cleanup_viewer()
    
    print(f"\nProduction processing completed:")
    print(f"  Images processed: {len(processed_results)}")
    print(f"  Total time: {total_time:.2f} seconds")
    print(f"  Average per image: {total_time/len(processed_results):.3f} seconds")
    print(f"  Fixed parameters used throughout")
    print()

def compare_modes():
    """Show side-by-side comparison of both modes."""
    print("=== COMPARISON: Development vs Production ===")
    print()
    
    print("DEVELOPMENT MODE (APP_DEBUG_MODE = True):")
    print("  ├─ GUI Windows: ✓ Visible")
    print("  ├─ Parameter Control: ✓ Interactive trackbars")
    print("  ├─ Visual Feedback: ✓ Real-time image display")
    print("  ├─ Analysis Tools: ✓ Available")
    print("  ├─ Loop Control: ✓ Manual (user decides when to exit)")
    print("  ├─ Processing Speed: ⚠ Slower (GUI overhead)")
    print("  └─ Use Case: Parameter tuning, debugging, experimentation")
    print()
    
    print("PRODUCTION MODE (APP_DEBUG_MODE = False):")
    print("  ├─ GUI Windows: ✗ None (headless)")
    print("  ├─ Parameter Control: ✗ Fixed values only")
    print("  ├─ Visual Feedback: ✗ No display")
    print("  ├─ Analysis Tools: ✗ Disabled")
    print("  ├─ Loop Control: ✓ Automatic (controlled iterations)")
    print("  ├─ Processing Speed: ✓ Fast (no GUI overhead)")
    print("  └─ Use Case: Production deployment, batch processing")
    print()

def workflow_example():
    """Show the typical development to production workflow."""
    print("=== TYPICAL WORKFLOW ===")
    print()
    
    print("Step 1: DEVELOPMENT PHASE")
    print("  └─ Set APP_DEBUG_MODE = True")
    print("     ├─ Use GUI to visualize results")
    print("     ├─ Experiment with different parameters")
    print("     ├─ Analyze processing quality")
    print("     └─ Find optimal parameter values")
    print()
    
    print("Step 2: PARAMETER OPTIMIZATION")
    print("  └─ Through experimentation, determine:")
    print("     ├─ OPTIMAL_THRESHOLD = 145")
    print("     ├─ OPTIMAL_KERNEL_SIZE = 7")
    print("     └─ OPTIMAL_ITERATIONS = 3")
    print()
    
    print("Step 3: PRODUCTION DEPLOYMENT")
    print("  └─ Set APP_DEBUG_MODE = False")
    print("     ├─ Use fixed optimal parameters")
    print("     ├─ No GUI (works on servers)")
    print("     ├─ Automatic batch processing")
    print("     └─ Production monitoring/logging")
    print()

def main():
    print("APP_DEBUG_MODE Example - Development vs Production")
    print("=" * 55)
    print()
    
    # Show comparison first
    compare_modes()
    
    # Show workflow
    workflow_example()
    
    print("LIVE DEMONSTRATIONS:")
    print("=" * 20)
    print()
    
    # Demo 1: Development mode (with GUI)
    development_mode_example()
    
    # Demo 2: Production mode (headless)
    production_mode_example()
    
    print("=" * 55)
    print("SUMMARY")
    print("=" * 55)
    print()
    print("✓ APP_DEBUG_MODE = True:")
    print("  Use for development, parameter tuning, and analysis")
    print("  Shows windows, allows interaction, enables experimentation")
    print()
    print("✓ APP_DEBUG_MODE = False:")
    print("  Use for production deployment")
    print("  No GUI, fixed parameters, automatic processing")
    print()
    print("Workflow: Develop with True → Deploy with False")
    print()

if __name__ == "__main__":
    main()