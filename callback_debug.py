#!/usr/bin/env python3
"""
Debug script to help identify callback issues in thresholding functionality.
Run this if you encounter "'str' object is not callable" errors.
"""

def test_callback_definitions():
    """Test that all callback definitions are properly structured."""
    print("Testing callback definitions...")
    
    # Mock cv2, numpy, and tkinter to avoid dependency issues
    import sys
    from unittest.mock import MagicMock
    
    cv2_mock = MagicMock()
    numpy_mock = MagicMock()
    tkinter_mock = MagicMock()
    
    sys.modules['cv2'] = cv2_mock
    sys.modules['numpy'] = numpy_mock
    sys.modules['tkinter'] = tkinter_mock
    sys.modules['tkinter.ttk'] = MagicMock()
    sys.modules['tkinter.filedialog'] = MagicMock()
    
    try:
        from src.gui.thresholding_window import ThresholdingWindow
        from src.config.viewer_config import ViewerConfig
        
        # Create a mock viewer
        class MockViewer:
            def __init__(self):
                self._internal_images = [(MagicMock(), "test")]
                self.trackbar = MagicMock()
                self.trackbar.parameters = {'show': 0}
            def log(self, message): pass
        
        # Test creating ThresholdingWindow
        mock_viewer = MockViewer()
        threshold_window = ThresholdingWindow(mock_viewer, "Grayscale")
        
        # Test initial trackbar generation
        grayscale_trackbars = threshold_window._get_initial_grayscale_trackbars()
        color_trackbars = threshold_window._get_initial_color_trackbars()
        
        print(f"✓ Generated {len(grayscale_trackbars)} grayscale trackbars")
        print(f"✓ Generated {len(color_trackbars)} color trackbars")
        
        # Test callback function types
        for trackbar in grayscale_trackbars:
            callback = trackbar.get('custom_callback')
            if callback:
                print(f"✓ Grayscale trackbar '{trackbar['name']}' has callback: {type(callback)}")
                if not callable(callback):
                    print(f"✗ ERROR: Callback is not callable: {callback}")
                    return False
        
        for trackbar in color_trackbars:
            callback = trackbar.get('custom_callback')
            if callback:
                print(f"✓ Color trackbar '{trackbar['name']}' has callback: {type(callback)}")
                if not callable(callback):
                    print(f"✗ ERROR: Callback is not callable: {callback}")
                    return False
        
        # Test method callbacks
        test_methods = ['_on_param_change', '_on_threshold_type_change', '_on_adaptive_method_change', 'update_threshold']
        for method_name in test_methods:
            if hasattr(threshold_window, method_name):
                method = getattr(threshold_window, method_name)
                if callable(method):
                    print(f"✓ Method '{method_name}' is callable")
                else:
                    print(f"✗ ERROR: Method '{method_name}' is not callable: {method}")
                    return False
            else:
                print(f"✗ ERROR: Method '{method_name}' does not exist")
                return False
        
        print("✓ All callback definitions are properly structured!")
        return True
        
    except Exception as e:
        print(f"✗ Error testing callbacks: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_lambda_callbacks():
    """Test that lambda callbacks work correctly."""
    print("\\nTesting lambda callback execution...")
    
    class TestWindow:
        def __init__(self):
            self.call_count = 0
            
        def test_callback(self, value):
            self.call_count += 1
            print(f"  Callback called with value: {value}")
            return f"Result: {value}"
    
    test_window = TestWindow()
    
    # Test lambda callback
    lambda_callback = lambda v: test_window.test_callback(v)
    
    if callable(lambda_callback):
        print("✓ Lambda callback is callable")
        result = lambda_callback(42)
        if test_window.call_count == 1:
            print("✓ Lambda callback executed successfully")
            return True
        else:
            print("✗ Lambda callback did not execute properly")
            return False
    else:
        print("✗ Lambda callback is not callable")
        return False

if __name__ == "__main__":
    print("Callback Debug Script")
    print("=" * 30)
    
    success = True
    success &= test_callback_definitions()
    success &= test_lambda_callbacks()
    
    print("\\n" + "=" * 30)
    if success:
        print("🎉 All callback tests passed!")
        print("\\nIf you're still getting 'str' object is not callable errors:")
        print("1. Check that trackbar definitions are created after object initialization")
        print("2. Ensure callback methods exist before trackbar creation")
        print("3. Verify that strings aren't being passed where functions are expected")
    else:
        print("❌ Some callback tests failed. Check the implementation.")