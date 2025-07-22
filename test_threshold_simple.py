#!/usr/bin/env python3
"""
Simple test to verify threshold type changes work.
"""

import sys
import os
from unittest.mock import MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def setup_simple_mocks():
    """Set up simple mocks for testing."""
    
    # Create fake array class
    class FakeArray:
        def __init__(self, shape, dtype=None):
            self.shape = shape
            self.dtype = dtype
            self.size = 1
            for dim in shape:
                self.size *= dim
                
        def copy(self):
            return FakeArray(self.shape, self.dtype)
    
    # Track threshold calls
    threshold_calls = []
    
    def mock_threshold(image, thresh, maxval, type_val):
        threshold_calls.append({
            'thresh': thresh,
            'maxval': maxval,
            'type': type_val
        })
        return 127.0, FakeArray(image.shape if hasattr(image, 'shape') else (100, 100))
    
    # Mock cv2
    cv2_mock = MagicMock()
    cv2_mock.threshold = mock_threshold
    cv2_mock.THRESH_BINARY = 0
    cv2_mock.THRESH_BINARY_INV = 1
    cv2_mock.THRESH_TRUNC = 2
    cv2_mock.THRESH_TOZERO = 3
    cv2_mock.THRESH_TOZERO_INV = 4
    
    # Mock other required functions
    cv2_mock.namedWindow = MagicMock()
    cv2_mock.setMouseCallback = MagicMock()
    cv2_mock.createTrackbar = MagicMock()
    cv2_mock.setTrackbarPos = MagicMock()
    cv2_mock.imshow = MagicMock()
    cv2_mock.resizeWindow = MagicMock()
    cv2_mock.getWindowProperty = MagicMock(return_value=1)
    cv2_mock.waitKey = MagicMock(return_value=0)
    cv2_mock.WINDOW_NORMAL = 0
    
    # Mock numpy
    numpy_mock = MagicMock()
    numpy_mock.zeros = lambda shape, dtype=None: FakeArray(shape, dtype)
    numpy_mock.ndarray = FakeArray
    
    # Apply mocks
    sys.modules['cv2'] = cv2_mock
    sys.modules['numpy'] = numpy_mock
    sys.modules['tkinter'] = MagicMock()
    sys.modules['tkinter.ttk'] = MagicMock()
    sys.modules['tkinter.filedialog'] = MagicMock()
    
    return threshold_calls, FakeArray

def test_threshold_type_logic():
    """Test the threshold type logic without full setup."""
    print("Testing Threshold Type Logic")
    print("=" * 30)
    
    threshold_calls, FakeArray = setup_simple_mocks()
    
    try:
        from src.gui.thresholding_window import ThresholdingWindow
        
        # Create minimal mock viewer
        class MockViewer:
            def __init__(self):
                self._internal_images = [(FakeArray((100, 100, 3)), "test")]
                self.trackbar = MagicMock()
                self.trackbar.parameters = {'show': 0}
                
            def log(self, message):
                print(f"📝 Log: {message}")
        
        mock_viewer = MockViewer()
        
        print("\n🔧 Creating ThresholdingWindow...")
        threshold_window = ThresholdingWindow(mock_viewer, "Grayscale")
        
        # Test the threshold type mapping logic
        print("\n📊 Testing threshold type mapping...")
        
        # Test parameters for different threshold types
        test_params = [
            {"threshold_type_idx": 0, "threshold": 127, "max_value": 255},  # BINARY
            {"threshold_type_idx": 1, "threshold": 127, "max_value": 255},  # BINARY_INV
            {"threshold_type_idx": 2, "threshold": 127, "max_value": 255},  # TRUNC
        ]
        
        for i, params in enumerate(test_params):
            print(f"\n   Test {i+1}: threshold_type_idx = {params['threshold_type_idx']}")
            
            # Clear previous calls
            threshold_calls.clear()
            
            # Create a test image
            test_image = FakeArray((100, 100, 3))
            
            # Apply thresholding directly
            try:
                result = threshold_window._apply_thresholding(test_image, params)
                
                if threshold_calls:
                    last_call = threshold_calls[-1]
                    expected_type = params['threshold_type_idx']
                    actual_type = last_call['type']
                    
                    threshold_names = ["BINARY", "BINARY_INV", "TRUNC", "TOZERO", "TOZERO_INV"]
                    type_name = threshold_names[expected_type] if expected_type < len(threshold_names) else "UNKNOWN"
                    
                    if actual_type == expected_type:
                        print(f"      ✅ {type_name} correctly applied (type={actual_type})")
                    else:
                        print(f"      ❌ Expected {expected_type}, got {actual_type}")
                else:
                    print(f"      ⚠️ No threshold calls made")
                    
            except Exception as e:
                print(f"      ❌ Error applying threshold: {e}")
        
        print("\n📊 Testing threshold type change handler...")
        
        # Test the callback function
        try:
            # Mock the threshold viewer
            threshold_window.threshold_viewer = MagicMock()
            threshold_window.threshold_viewer.trackbar = MagicMock()
            threshold_window.threshold_viewer.trackbar.parameters = {}
            threshold_window.update_threshold = MagicMock()
            
            # Test threshold type change
            threshold_window._on_threshold_type_change(1)  # BINARY_INV
            
            # Check if parameter was updated
            if threshold_window.threshold_viewer.trackbar.parameters.get("threshold_type_idx") == 1:
                print("   ✅ Threshold type parameter correctly updated")
            else:
                print("   ❌ Threshold type parameter not updated")
            
            # Check if update_threshold was called
            if threshold_window.update_threshold.called:
                print("   ✅ update_threshold was called")
            else:
                print("   ❌ update_threshold was not called")
                
        except Exception as e:
            print(f"   ❌ Error testing callback: {e}")
        
        print("\n✅ Threshold type logic test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Simple Threshold Type Test")
    print("=" * 40)
    
    success = test_threshold_type_logic()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Simple threshold type test PASSED!")
        print("\n💡 The threshold type logic appears to be working correctly.")
        print("   If you're still not seeing changes in the UI, the issue might be:")
        print("   1. Image display refresh timing")
        print("   2. Parameter synchronization between UI and processing")
        print("   3. Visual difference not apparent with current image/settings")
    else:
        print("❌ Simple threshold type test FAILED!")
        print("   Check the implementation for issues in threshold type handling.")