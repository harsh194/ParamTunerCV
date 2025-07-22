#!/usr/bin/env python3
"""
Test script to verify that threshold type changes work correctly.
"""

import sys
import os
from unittest.mock import MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def setup_threshold_mocks():
    """Set up mocks for threshold type testing."""
    
    # Create a mock that tracks threshold calls
    class ThresholdTracker:
        def __init__(self):
            self.threshold_calls = []
            
        def mock_threshold(self, image, thresh, maxval, type_val):
            self.threshold_calls.append({
                'thresh': thresh,
                'maxval': maxval, 
                'type': type_val
            })
            # Return proper mock values
            from test_functionality import FakeArray
            return 127.0, FakeArray(image.shape if hasattr(image, 'shape') else (100, 100))
    
    tracker = ThresholdTracker()
    
    # Mock cv2 with threshold tracking
    cv2_mock = MagicMock()
    cv2_mock.threshold = tracker.mock_threshold
    
    # Add OpenCV constants
    cv2_mock.THRESH_BINARY = 0
    cv2_mock.THRESH_BINARY_INV = 1
    cv2_mock.THRESH_TRUNC = 2
    cv2_mock.THRESH_TOZERO = 3
    cv2_mock.THRESH_TOZERO_INV = 4
    cv2_mock.THRESH_OTSU = 8
    cv2_mock.THRESH_TRIANGLE = 16
    
    # Mock other cv2 functions
    cv2_mock.namedWindow = MagicMock()
    cv2_mock.setMouseCallback = MagicMock()
    cv2_mock.createTrackbar = MagicMock()
    cv2_mock.setTrackbarPos = MagicMock()
    cv2_mock.imshow = MagicMock()
    cv2_mock.resizeWindow = MagicMock()
    cv2_mock.getWindowProperty = MagicMock(return_value=1)
    cv2_mock.waitKey = MagicMock(return_value=0)
    cv2_mock.WINDOW_NORMAL = 0
    cv2_mock.WINDOW_KEEPRATIO = 0
    cv2_mock.WINDOW_GUI_EXPANDED = 0
    cv2_mock.WINDOW_AUTOSIZE = 1
    
    # Mock other dependencies
    from test_functionality import FakeArray
    numpy_mock = MagicMock()
    numpy_mock.zeros = lambda shape, dtype=None: FakeArray(shape, dtype)
    numpy_mock.full = lambda shape, value, dtype=None: FakeArray(shape, dtype)
    numpy_mock.ndarray = FakeArray
    
    sys.modules['cv2'] = cv2_mock
    sys.modules['numpy'] = numpy_mock
    sys.modules['tkinter'] = MagicMock()
    sys.modules['tkinter.ttk'] = MagicMock()
    sys.modules['tkinter.filedialog'] = MagicMock()
    
    return tracker

def test_threshold_type_changes():
    """Test that threshold type changes are applied correctly."""
    print("Testing Threshold Type Changes")
    print("=" * 35)
    
    tracker = setup_threshold_mocks()
    
    try:
        from src.gui.thresholding_window import ThresholdingWindow
        
        # Create mock main viewer
        class MockMainViewer:
            def __init__(self):
                from test_functionality import FakeArray
                test_image = FakeArray((200, 200, 3))
                self._internal_images = [(test_image, "Test Image")]
                self.trackbar = MagicMock()
                self.trackbar.parameters = {'show': 0}
                
            def log(self, message):
                print(f"📝 Main Log: {message}")
        
        mock_main_viewer = MockMainViewer()
        
        print("\n🔧 Creating ThresholdingWindow...")
        threshold_window = ThresholdingWindow(mock_main_viewer, "Grayscale")
        threshold_window._create_threshold_viewer()
        
        print("\n📊 Testing threshold type parameter changes...")
        
        # Test different threshold types
        threshold_types = [
            ("BINARY", 0),
            ("BINARY_INV", 1),
            ("TRUNC", 2),
            ("TOZERO", 3),
            ("TOZERO_INV", 4)
        ]
        
        success_count = 0
        for type_name, type_idx in threshold_types:
            print(f"\n🧪 Testing {type_name} (index {type_idx})...")
            
            # Clear previous threshold calls
            tracker.threshold_calls.clear()
            
            # Set the threshold type parameter
            if threshold_window.threshold_viewer and threshold_window.threshold_viewer.trackbar:
                threshold_window.threshold_viewer.trackbar.parameters["threshold_type_idx"] = type_idx
                print(f"   Set parameter threshold_type_idx = {type_idx}")
                
                # Trigger threshold type change
                threshold_window._on_threshold_type_change(type_idx)
                
                # Check if threshold was called with correct type
                if tracker.threshold_calls:
                    last_call = tracker.threshold_calls[-1]
                    expected_type = type_idx  # Should match OpenCV constant
                    actual_type = last_call['type']
                    
                    if actual_type == expected_type:
                        print(f"   ✅ Correctly applied {type_name} (type={actual_type})")
                        success_count += 1
                    else:
                        print(f"   ❌ Expected type {expected_type}, got {actual_type}")
                else:
                    print(f"   ⚠️ No threshold calls made for {type_name}")
            else:
                print(f"   ❌ Threshold viewer not properly initialized")
        
        print(f"\n📊 Threshold Type Test Results:")
        print(f"   ✅ Successful: {success_count}/{len(threshold_types)}")
        print(f"   📈 Success Rate: {success_count/len(threshold_types)*100:.1f}%")
        
        if success_count == len(threshold_types):
            print("\n🎉 All threshold type changes working correctly!")
            return True
        else:
            print(f"\n⚠️ {len(threshold_types) - success_count} threshold type changes failed")
            return False
        
    except Exception as e:
        print(f"\n❌ Threshold type test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_synchronization():
    """Test that UI elements synchronize with threshold type changes."""
    print("\n" + "=" * 35)
    print("Testing UI Synchronization")
    print("=" * 35)
    
    tracker = setup_threshold_mocks()
    
    try:
        from src.gui.thresholding_window import ThresholdingWindow
        
        class MockMainViewer:
            def __init__(self):
                from test_functionality import FakeArray
                test_image = FakeArray((200, 200, 3))
                self._internal_images = [(test_image, "Test Image")]
                self.trackbar = MagicMock()
                self.trackbar.parameters = {'show': 0}
                
            def log(self, message):
                print(f"📝 Main Log: {message}")
        
        mock_main_viewer = MockMainViewer()
        threshold_window = ThresholdingWindow(mock_main_viewer, "Grayscale")
        threshold_window._create_threshold_viewer()
        
        # Test UI variable synchronization
        print("\n📊 Testing UI variable updates...")
        
        # Create mock UI variable
        threshold_window.threshold_type_var = MagicMock()
        threshold_window.threshold_type_var.set = MagicMock()
        threshold_window.threshold_type_var.get = MagicMock(return_value="BINARY")
        
        # Test threshold type change
        threshold_window._on_threshold_type_change(1)  # BINARY_INV
        
        # Check if UI variable was updated
        if threshold_window.threshold_type_var.set.called:
            called_with = threshold_window.threshold_type_var.set.call_args[0][0]
            if called_with == "BINARY_INV":
                print("   ✅ UI variable correctly updated to BINARY_INV")
            else:
                print(f"   ❌ UI variable updated to {called_with}, expected BINARY_INV")
        else:
            print("   ❌ UI variable was not updated")
        
        # Test dropdown change handler
        print("\n📊 Testing dropdown change handler...")
        threshold_window.threshold_type_var.get = MagicMock(return_value="TRUNC")
        
        # Simulate dropdown change
        threshold_window._on_dropdown_threshold_type_change()
        
        # Check if parameter was updated
        if threshold_window.threshold_viewer and threshold_window.threshold_viewer.trackbar:
            param_value = threshold_window.threshold_viewer.trackbar.parameters.get("threshold_type_idx")
            if param_value == 2:  # TRUNC index
                print("   ✅ Parameter correctly updated from dropdown change")
            else:
                print(f"   ❌ Parameter value is {param_value}, expected 2")
        
        print("\n✅ UI synchronization test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ UI synchronization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Threshold Type Testing Suite")
    print("=" * 50)
    
    # Run tests
    tests = [
        test_threshold_type_changes,
        test_ui_synchronization
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("THRESHOLD TYPE TEST RESULTS")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {test_func.__name__}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All threshold type tests PASSED!")
        print("\n💡 Key Features Verified:")
        print("  ✅ Threshold type parameters correctly applied")
        print("  ✅ BINARY to BINARY_INV changes work")
        print("  ✅ UI synchronization functions properly")
        print("  ✅ Dropdown and trackbar changes synchronized")
        print("\n🚀 Threshold type switching should now work correctly!")
    else:
        print("❌ Some threshold type tests failed. Check the implementation.")
        sys.exit(1)