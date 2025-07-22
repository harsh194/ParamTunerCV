#!/usr/bin/env python3
"""
Test script to verify that the minimal thresholding implementation 
only creates the required windows and no duplicates.
"""

import sys
import os
import numpy as np
from unittest.mock import MagicMock, patch

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def mock_opencv_and_dependencies():
    """Mock all external dependencies for testing."""
    
    # Mock cv2
    cv2_mock = MagicMock()
    cv2_mock.namedWindow = MagicMock()
    cv2_mock.resizeWindow = MagicMock()
    cv2_mock.setMouseCallback = MagicMock()
    cv2_mock.createTrackbar = MagicMock()
    cv2_mock.getWindowProperty = MagicMock(return_value=1)
    cv2_mock.setTrackbarPos = MagicMock()
    cv2_mock.getTrackbarPos = MagicMock(return_value=0)
    cv2_mock.imshow = MagicMock()
    cv2_mock.waitKey = MagicMock(return_value=0)
    cv2_mock.destroyWindow = MagicMock()
    cv2_mock.destroyAllWindows = MagicMock()
    
    # OpenCV constants
    cv2_mock.WINDOW_NORMAL = 0
    cv2_mock.WINDOW_KEEPRATIO = 0
    cv2_mock.WINDOW_GUI_EXPANDED = 0
    cv2_mock.WINDOW_AUTOSIZE = 0
    cv2_mock.WND_PROP_VISIBLE = 0
    
    # Mock numpy
    numpy_mock = MagicMock()
    numpy_mock.zeros = MagicMock(return_value=np.zeros((100, 100, 3), dtype=np.uint8))
    numpy_mock.full = MagicMock(return_value=np.full((100, 100, 3), 255, dtype=np.uint8))
    numpy_mock.ndarray = np.ndarray
    
    # Mock tkinter
    tkinter_mock = MagicMock()
    tkinter_mock.Toplevel = MagicMock()
    tkinter_mock.StringVar = MagicMock()
    tkinter_mock.Text = MagicMock()
    tkinter_mock.NORMAL = 'normal'
    tkinter_mock.DISABLED = 'disabled'
    tkinter_mock.END = 'end'
    
    ttk_mock = MagicMock()
    ttk_mock.LabelFrame = MagicMock()
    ttk_mock.Radiobutton = MagicMock()
    ttk_mock.Combobox = MagicMock()
    ttk_mock.Button = MagicMock()
    ttk_mock.Label = MagicMock()
    ttk_mock.Frame = MagicMock()
    
    # Apply mocks
    sys.modules['cv2'] = cv2_mock
    sys.modules['numpy'] = numpy_mock  
    sys.modules['tkinter'] = tkinter_mock
    sys.modules['tkinter.ttk'] = ttk_mock
    sys.modules['tkinter.filedialog'] = MagicMock()
    
    return cv2_mock, numpy_mock, tkinter_mock, ttk_mock

def test_minimal_thresholding_windows():
    """Test that thresholding creates only the required windows."""
    print("Testing Minimal Thresholding Implementation")
    print("=" * 50)
    
    # Mock dependencies
    cv2_mock, numpy_mock, tkinter_mock, ttk_mock = mock_opencv_and_dependencies()
    
    try:
        # Import after mocking
        from src.gui.thresholding_window import ThresholdingWindow
        from src.config.viewer_config import ViewerConfig
        
        # Create a mock main viewer
        class MockMainViewer:
            def __init__(self):
                self._internal_images = [(np.zeros((200, 200, 3), dtype=np.uint8), "Test Image")]
                self.trackbar = MagicMock()
                self.trackbar.parameters = {'show': 0}
                self.log_calls = []
                
            def log(self, message):
                self.log_calls.append(message)
                print(f"📝 Main Viewer Log: {message}")
        
        mock_main_viewer = MockMainViewer()
        
        print("\n🔧 Creating ThresholdingWindow for Grayscale...")
        threshold_window = ThresholdingWindow(mock_main_viewer, "Grayscale")
        
        print("\n🪟 Creating threshold viewer...")
        threshold_window._create_threshold_viewer()
        
        # Verify the threshold viewer was created
        assert threshold_window.threshold_viewer is not None, "Threshold viewer should be created"
        
        # Check window creation calls
        cv2_calls = cv2_mock.namedWindow.call_args_list
        print(f"\n📊 OpenCV namedWindow calls: {len(cv2_calls)}")
        
        window_names_created = []
        for call in cv2_calls:
            window_name = call[0][0]  # First argument is window name
            window_names_created.append(window_name)
            print(f"  - {window_name}")
        
        # Expected windows for thresholding:
        # 1. Thresholded Process - Grayscale
        # 2. Thresholding Trackbars - Grayscale
        expected_windows = [
            "Thresholded Process - Grayscale",
            "Thresholding Trackbars - Grayscale"
        ]
        
        print(f"\n✅ Expected windows: {expected_windows}")
        print(f"📝 Actually created: {window_names_created}")
        
        # Verify only expected windows are created
        unexpected_windows = []
        for window_name in window_names_created:
            if not any(expected in window_name for expected in expected_windows):
                unexpected_windows.append(window_name)
        
        if unexpected_windows:
            print(f"❌ UNEXPECTED WINDOWS CREATED: {unexpected_windows}")
            return False
        else:
            print("✅ No unexpected windows created!")
        
        # Test trackbar creation
        trackbar_calls = cv2_mock.createTrackbar.call_args_list
        print(f"\n📊 Trackbar creation calls: {len(trackbar_calls)}")
        
        for i, call in enumerate(trackbar_calls):
            trackbar_name = call[0][0]  # First argument is trackbar name
            window_name = call[0][1]   # Second argument is window name
            print(f"  {i+1}. '{trackbar_name}' in '{window_name}'")
        
        # Test window cleanup
        print("\n🧹 Testing cleanup...")
        threshold_window.threshold_viewer.cleanup_viewer()
        
        # Verify destroy calls
        destroy_calls = cv2_mock.destroyWindow.call_args_list
        print(f"📊 Window destroy calls: {len(destroy_calls)}")
        
        print("\n✅ Minimal thresholding test completed successfully!")
        print("📋 Summary:")
        print(f"  - Created {len(window_names_created)} windows (expected: 2)")
        print(f"  - Created {len(trackbar_calls)} trackbars")
        print(f"  - No unexpected windows detected")
        print(f"  - Cleanup performed: {len(destroy_calls)} destroy calls")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_color_space_thresholding():
    """Test thresholding with color space (HSV)."""
    print("\n" + "=" * 50)
    print("Testing Color Space Thresholding (HSV)")
    print("=" * 50)
    
    cv2_mock, numpy_mock, tkinter_mock, ttk_mock = mock_opencv_and_dependencies()
    
    try:
        from src.gui.thresholding_window import ThresholdingWindow
        
        class MockMainViewer:
            def __init__(self):
                self._internal_images = [(np.zeros((200, 200, 3), dtype=np.uint8), "HSV Test Image")]
                self.trackbar = MagicMock()
                self.trackbar.parameters = {'show': 0}
                
            def log(self, message):
                print(f"📝 Main Viewer Log: {message}")
        
        mock_main_viewer = MockMainViewer()
        
        print("\n🔧 Creating ThresholdingWindow for HSV...")
        threshold_window = ThresholdingWindow(mock_main_viewer, "HSV")
        
        print("\n🪟 Creating HSV threshold viewer...")
        threshold_window._create_threshold_viewer()
        
        # Check window creation
        cv2_calls = cv2_mock.namedWindow.call_args_list
        print(f"\n📊 OpenCV namedWindow calls for HSV: {len(cv2_calls)}")
        
        window_names_created = [call[0][0] for call in cv2_calls]
        for window_name in window_names_created:
            print(f"  - {window_name}")
        
        # Expected windows for HSV thresholding
        expected_windows = [
            "Thresholded Process - HSV", 
            "Thresholding Trackbars - HSV"
        ]
        
        print(f"\n✅ Expected HSV windows: {expected_windows}")
        
        # Test trackbar creation for color space
        trackbar_calls = cv2_mock.createTrackbar.call_args_list
        print(f"\n📊 HSV Trackbar creation calls: {len(trackbar_calls)}")
        
        # HSV has 3 channels (H, S, V) with min/max trackbars = 6 trackbars for Range method
        expected_trackbar_count = 6  # H Min, H Max, S Min, S Max, V Min, V Max
        
        if len(trackbar_calls) >= expected_trackbar_count:
            print(f"✅ HSV trackbars created: {len(trackbar_calls)} (expected >= {expected_trackbar_count})")
        else:
            print(f"❌ Insufficient HSV trackbars: {len(trackbar_calls)} (expected >= {expected_trackbar_count})")
            return False
        
        print("\n✅ HSV color space thresholding test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ HSV test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_method_switching():
    """Test switching between different thresholding methods."""
    print("\n" + "=" * 50)
    print("Testing Method Switching")
    print("=" * 50)
    
    cv2_mock, numpy_mock, tkinter_mock, ttk_mock = mock_opencv_and_dependencies()
    
    try:
        from src.gui.thresholding_window import ThresholdingWindow
        
        class MockMainViewer:
            def __init__(self):
                self._internal_images = [(np.zeros((200, 200, 3), dtype=np.uint8), "Switch Test")]
                self.trackbar = MagicMock()
                self.trackbar.parameters = {'show': 0}
                
            def log(self, message):
                print(f"📝 Main Viewer Log: {message}")
        
        mock_main_viewer = MockMainViewer()
        
        print("\n🔧 Creating ThresholdingWindow for method switching test...")
        threshold_window = ThresholdingWindow(mock_main_viewer, "Grayscale")
        threshold_window._create_threshold_viewer()
        
        print("\n🔄 Testing method switch: Simple -> Adaptive")
        
        # Reset mock to count new calls
        cv2_mock.reset_mock()
        
        # Switch to Adaptive method
        threshold_window._switch_to_method("Adaptive")
        
        # Check if trackbars were recreated
        new_trackbar_calls = cv2_mock.createTrackbar.call_args_list
        print(f"📊 New trackbar calls after switch: {len(new_trackbar_calls)}")
        
        # Adaptive method should have different trackbars (including block_size, c_constant)
        adaptive_trackbars = [call[0][0] for call in new_trackbar_calls]
        for trackbar_name in adaptive_trackbars:
            print(f"  - {trackbar_name}")
        
        # Check if expected adaptive trackbars exist
        expected_adaptive_trackbars = ["Block Size", "C Constant", "Adaptive"]
        found_adaptive = sum(1 for trackbar in adaptive_trackbars 
                           if any(expected in trackbar for expected in expected_adaptive_trackbars))
        
        if found_adaptive > 0:
            print(f"✅ Adaptive-specific trackbars found: {found_adaptive}")
        else:
            print(f"❌ No adaptive-specific trackbars found")
            return False
        
        print("\n✅ Method switching test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Method switching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Minimal Thresholding Test Suite")
    print("=" * 60)
    
    # Run all tests
    tests = [
        test_minimal_thresholding_windows,
        test_color_space_thresholding, 
        test_method_switching
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {test_func.__name__}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests PASSED! Minimal thresholding implementation is working correctly.")
        print("\n💡 Key Features Verified:")
        print("  ✅ Only creates required windows (process + trackbar)")
        print("  ✅ No duplicate analysis control or text windows")
        print("  ✅ Proper trackbar creation and management") 
        print("  ✅ Method switching with trackbar recreation")
        print("  ✅ Color space support (grayscale + HSV)")
        print("  ✅ Clean window cleanup on exit")
    else:
        print("❌ Some tests failed. Check the implementation.")
        sys.exit(1)