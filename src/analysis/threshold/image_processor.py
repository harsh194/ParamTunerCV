import cv2
import numpy as np

class ThresholdProcessor:
    def __init__(self, image):
        self.image = image
        self.is_grayscale = len(image.shape) == 2

    def convert_color_space(self, color_space):
        if self.is_grayscale:
            if color_space == "Grayscale":
                return self.image
            else:
                # Convert grayscale to BGR first, then to target color space
                bgr_image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
                return self._convert_bgr_to_colorspace(bgr_image, color_space)
        else:
            # Color image - convert to target color space
            return self._convert_bgr_to_colorspace(self.image, color_space)
    
    def _convert_bgr_to_colorspace(self, bgr_image, color_space):
        """Convert BGR image to specified color space."""
        if color_space == "BGR":
            return bgr_image
        elif color_space == "HSV":
            return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)
        elif color_space == "HLS":
            return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HLS)
        elif color_space == "Lab":
            return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2Lab)
        elif color_space == "Luv":
            return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2Luv)
        elif color_space == "YCrCb":
            return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2YCrCb)
        elif color_space == "XYZ":
            return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2XYZ)
        elif color_space == "Grayscale":
            return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        return bgr_image

    def apply_range_threshold(self, converted_image, lower_bounds, upper_bounds):
        """Applies a threshold based on a lower and upper range for each channel."""
        lower_bounds = np.array(lower_bounds, dtype=np.uint8)
        upper_bounds = np.array(upper_bounds, dtype=np.uint8)
        mask = cv2.inRange(converted_image, lower_bounds, upper_bounds)
        return cv2.bitwise_and(self.image, self.image, mask=mask)

    def apply_binary_threshold(self, gray_image, threshold_value, use_otsu):
        """Applies a binary threshold to a grayscale image."""
        if use_otsu:
            # When using Otsu, the threshold value is calculated automatically
            ret, mask = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            ret, mask = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY)
        return mask
    
    def apply_advanced_threshold(self, gray_image, threshold_value, max_value, threshold_type, use_otsu=False, use_triangle=False):
        """Applies various OpenCV thresholding types."""
        # Map threshold type names to OpenCV constants
        threshold_types = {
            "BINARY": cv2.THRESH_BINARY,
            "BINARY_INV": cv2.THRESH_BINARY_INV,
            "TRUNC": cv2.THRESH_TRUNC,
            "TOZERO": cv2.THRESH_TOZERO,
            "TOZERO_INV": cv2.THRESH_TOZERO_INV
        }
        
        thresh_type = threshold_types.get(threshold_type, cv2.THRESH_BINARY)
        
        if use_otsu:
            thresh_type += cv2.THRESH_OTSU
            threshold_value = 0  # Otsu calculates automatically
        elif use_triangle:
            thresh_type += cv2.THRESH_TRIANGLE
            threshold_value = 0  # Triangle calculates automatically
            
        ret, thresholded = cv2.threshold(gray_image, threshold_value, max_value, thresh_type)
        return thresholded
    
    def apply_adaptive_threshold(self, gray_image, max_value, adaptive_method, threshold_type, block_size, c_constant):
        """Applies adaptive thresholding."""
        # Map method names to OpenCV constants
        adaptive_methods = {
            "MEAN_C": cv2.ADAPTIVE_THRESH_MEAN_C,
            "GAUSSIAN_C": cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        }
        
        # Map threshold types
        threshold_types = {
            "BINARY": cv2.THRESH_BINARY,
            "BINARY_INV": cv2.THRESH_BINARY_INV
        }
        
        method = adaptive_methods.get(adaptive_method, cv2.ADAPTIVE_THRESH_MEAN_C)
        thresh_type = threshold_types.get(threshold_type, cv2.THRESH_BINARY)
        
        # Ensure block_size is odd and >= 3
        if block_size % 2 == 0:
            block_size += 1
        if block_size < 3:
            block_size = 3
            
        thresholded = cv2.adaptiveThreshold(gray_image, max_value, method, thresh_type, block_size, c_constant)
        return thresholded
    
    def apply_multi_channel_threshold(self, converted_image, thresholding_params):
        """
        Applies advanced thresholding to each channel of a multi-channel image.
        
        thresholding_params should contain:
        - method: "Simple", "Otsu", "Triangle", "Adaptive", or "Range"
        - threshold_type: OpenCV threshold type
        - channels: list of channel-specific parameters
        """
        if len(converted_image.shape) == 2:
            # Single channel - use existing methods
            return self.apply_single_channel_advanced_threshold(converted_image, thresholding_params)
        
        method = thresholding_params.get('method', 'Range')
        
        if method == 'Range':
            # Use existing range thresholding
            lower_bounds = thresholding_params.get('lower_bounds', [0, 0, 0])
            upper_bounds = thresholding_params.get('upper_bounds', [255, 255, 255])
            return self.apply_range_threshold(converted_image, lower_bounds, upper_bounds)
        
        # Advanced per-channel thresholding
        channels = cv2.split(converted_image)
        thresholded_channels = []
        
        for i, channel in enumerate(channels):
            channel_params = thresholding_params.get('channels', [{}])[i] if i < len(thresholding_params.get('channels', [])) else {}
            
            if method == "Simple":
                threshold_val = channel_params.get('threshold', 127)
                max_val = channel_params.get('max_value', 255)
                thresh_type = channel_params.get('threshold_type', 'BINARY')
                thresholded_channel = self.apply_advanced_threshold(channel, threshold_val, max_val, thresh_type)
            
            elif method == "Otsu":
                threshold_val = channel_params.get('threshold', 127)
                max_val = channel_params.get('max_value', 255)
                thresh_type = channel_params.get('threshold_type', 'BINARY')
                thresholded_channel = self.apply_advanced_threshold(channel, threshold_val, max_val, thresh_type, use_otsu=True)
            
            elif method == "Triangle":
                threshold_val = channel_params.get('threshold', 127)
                max_val = channel_params.get('max_value', 255)
                thresh_type = channel_params.get('threshold_type', 'BINARY')
                thresholded_channel = self.apply_advanced_threshold(channel, threshold_val, max_val, thresh_type, use_triangle=True)
            
            elif method == "Adaptive":
                max_val = channel_params.get('max_value', 255)
                adaptive_method = channel_params.get('adaptive_method', 'MEAN_C')
                thresh_type = channel_params.get('threshold_type', 'BINARY')
                block_size = channel_params.get('block_size', 11)
                c_constant = channel_params.get('c_constant', 2)
                thresholded_channel = self.apply_adaptive_threshold(channel, max_val, adaptive_method, thresh_type, block_size, c_constant)
            
            else:
                # Fallback to original channel
                thresholded_channel = channel
            
            thresholded_channels.append(thresholded_channel)
        
        # Merge channels back
        if len(thresholded_channels) == 3:
            return cv2.merge(thresholded_channels)
        else:
            return thresholded_channels[0]
    
    def apply_single_channel_advanced_threshold(self, gray_image, params):
        """Apply advanced thresholding to a single channel image."""
        method = params.get('method', 'Simple')
        threshold_val = params.get('threshold', 127)
        max_val = params.get('max_value', 255)
        thresh_type = params.get('threshold_type', 'BINARY')
        
        if method == "Simple":
            return self.apply_advanced_threshold(gray_image, threshold_val, max_val, thresh_type)
        elif method == "Otsu":
            return self.apply_advanced_threshold(gray_image, threshold_val, max_val, thresh_type, use_otsu=True)
        elif method == "Triangle":
            return self.apply_advanced_threshold(gray_image, threshold_val, max_val, thresh_type, use_triangle=True)
        elif method == "Adaptive":
            adaptive_method = params.get('adaptive_method', 'MEAN_C')
            block_size = params.get('block_size', 11)
            c_constant = params.get('c_constant', 2)
            return self.apply_adaptive_threshold(gray_image, max_val, adaptive_method, thresh_type, block_size, c_constant)
        else:
            return self.apply_binary_threshold(gray_image, threshold_val, False)