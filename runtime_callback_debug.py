#!/usr/bin/env python3
"""
Runtime debug script for thresholding callback issues.
Run this alongside your main application to debug callback problems.
"""

import sys
from unittest.mock import MagicMock, patch

def mock_cv2_for_debug():
    """Mock cv2 with debug tracking."""
    
    class DebugTrackbar:
        def __init__(self):
            self.callbacks = {}
            self.call_count = 0
            
        def createTrackbar(self, name, window, initial, max_val, callback):
            print(f"📊 Creating trackbar: '{name}' in '{window}'")
            print(f"   Initial: {initial}, Max: {max_val}")
            print(f"   Callback: {callback} (type: {type(callback)})")
            
            if callback:
                if callable(callback):
                    print(f"   ✅ Callback is callable")
                    self.callbacks[name] = callback
                    
                    # Test the callback immediately
                    try:
                        print(f"   🧪 Testing callback with value 0...")
                        callback(0)
                        print(f"   ✅ Callback test successful")
                    except Exception as e:
                        print(f"   ❌ Callback test failed: {e}")
                        import traceback
                        traceback.print_exc()
                        
                else:
                    print(f"   ❌ Callback is NOT callable: {callback}")
                    
            self.call_count += 1
            
        def simulate_trackbar_change(self, trackbar_name, value):
            """Simulate a trackbar change for testing."""
            print(f"🎛️  Simulating trackbar change: '{trackbar_name}' = {value}")
            if trackbar_name in self.callbacks:
                callback = self.callbacks[trackbar_name]
                try:
                    callback(value)
                    print(f"   ✅ Callback executed successfully")
                except Exception as e:
                    print(f"   ❌ Callback execution failed: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"   ⚠️  No callback registered for '{trackbar_name}'")
    
    debug_trackbar = DebugTrackbar()
    
    cv2_mock = MagicMock()
    cv2_mock.createTrackbar = debug_trackbar.createTrackbar
    cv2_mock.namedWindow = MagicMock()
    cv2_mock.destroyWindow = MagicMock()
    cv2_mock.destroyAllWindows = MagicMock()
    cv2_mock.resizeWindow = MagicMock()
    cv2_mock.setMouseCallback = MagicMock()
    cv2_mock.getWindowProperty = MagicMock(return_value=1)
    cv2_mock.setTrackbarPos = MagicMock()
    cv2_mock.getTrackbarPos = MagicMock(return_value=0)
    cv2_mock.imshow = MagicMock()
    cv2_mock.waitKey = MagicMock(return_value=0)
    
    # OpenCV constants
    cv2_mock.WINDOW_NORMAL = 0
    cv2_mock.WINDOW_KEEPRATIO = 0
    cv2_mock.WINDOW_GUI_EXPANDED = 0
    cv2_mock.WINDOW_AUTOSIZE = 0
    cv2_mock.WND_PROP_VISIBLE = 0
    
    return cv2_mock, debug_trackbar

def test_runtime_callbacks():
    """Test runtime callback behavior."""
    print("Runtime Callback Debug Test")
    print("=" * 40)
    
    # Mock dependencies
    cv2_mock, debug_trackbar = mock_cv2_for_debug()
    numpy_mock = MagicMock()
    tkinter_mock = MagicMock()
    
    sys.modules['cv2'] = cv2_mock
    sys.modules['numpy'] = numpy_mock
    sys.modules['tkinter'] = tkinter_mock
    sys.modules['tkinter.ttk'] = MagicMock()
    sys.modules['tkinter.filedialog'] = MagicMock()
    
    try:
        print("\\n📦 Importing thresholding components...")
        from src.gui.thresholding_window import ThresholdingWindow
        
        # Create mock viewer
        class MockViewer:
            def __init__(self):
                self._internal_images = [(numpy_mock.zeros((100, 100, 3)), "test")]
                self.trackbar = MagicMock()
                self.trackbar.parameters = {'show': 0}
                
            def log(self, message):
                print(f"📝 Viewer log: {message}")
        
        mock_viewer = MockViewer()
        
        print("\\n🔧 Creating ThresholdingWindow...")
        threshold_window = ThresholdingWindow(mock_viewer, "Grayscale")
        
        print("\\n🎛️  Creating threshold viewer...")
        threshold_window._create_threshold_viewer()
        
        print(f"\\n📊 Total trackbars created: {debug_trackbar.call_count}")
        
        # Test method switching
        print("\\n🔄 Testing method switching...")
        threshold_window._switch_to_method("Adaptive")
        
        print(f"\\n📊 Total trackbars after switch: {debug_trackbar.call_count}")
        
        # Simulate some trackbar changes
        print("\\n🧪 Simulating trackbar interactions...")
        for trackbar_name in list(debug_trackbar.callbacks.keys())[:3]:  # Test first 3
            debug_trackbar.simulate_trackbar_change(trackbar_name, 50)
            
        print("\\n✅ Runtime callback test completed!")
        return True
        
    except Exception as e:
        print(f"\\n❌ Runtime test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_runtime_callbacks()
    
    print("\\n" + "=" * 40)
    if success:
        print("🎉 Runtime callback debugging completed successfully!")
        print("\\nIf you're still getting errors:")
        print("1. The issue might be in the actual OpenCV trackbar creation")
        print("2. Check for string/function confusion in callback parameters") 
        print("3. Ensure self references are properly captured in lambdas")
        print("4. Run this script alongside your main app for real-time debugging")
    else:
        print("❌ Runtime callback debugging failed. Check the implementation.")
        
    print("\\n💡 To use this for debugging:")
    print("   1. Run your main app: python check.py")
    print("   2. Open thresholding and watch console output")
    print("   3. Look for callback creation and execution messages")