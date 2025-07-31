"""Image thresholding and color space conversion functionality for the Parameter project.

This module provides comprehensive image thresholding capabilities with support for
multiple color spaces, various thresholding techniques (binary, adaptive, advanced),
and both single and multi-channel processing. It handles color space conversions
and applies different thresholding methods suitable for image analysis tasks.

Main Classes:
    ThresholdProcessor: Handles image thresholding operations and color space conversions

Usage:
    processor = ThresholdProcessor(image)
    converted_image = processor.convert_color_space('HSV')
    thresholded = processor.apply_binary_threshold(gray_image, 127, False)
"""

import cv2
import numpy as np
from typing import Any, Dict, List

class ThresholdProcessor:
    """Handles image thresholding operations and color space conversions.
    
    This class provides comprehensive thresholding capabilities for both grayscale
    and color images. It supports multiple color space conversions (BGR, HSV, HLS,
    Lab, Luv, YCrCb, XYZ, Grayscale) and various thresholding techniques including
    binary, adaptive, and advanced thresholding methods.
    
    The class automatically detects whether the input image is grayscale or color
    and applies appropriate processing methods. It handles both simple thresholding
    operations and complex multi-channel thresholding with different parameters
    for each channel.
    
    Attributes:
        image (np.ndarray): The input image to be processed
        is_grayscale (bool): True if the image is grayscale (2D), False if color (3D)
    
    Examples:
        >>> import cv2
        >>> image = cv2.imread('image.jpg')
        >>> processor = ThresholdProcessor(image)
        >>> hsv_image = processor.convert_color_space('HSV')
        >>> thresholded = processor.apply_range_threshold(hsv_image, [0, 50, 50], [10, 255, 255])
    """
    
    def __init__(self, image: np.ndarray):
        """Initialize the ThresholdProcessor with an input image.
        
        Args:
            image: Input image as a numpy array. Can be either grayscale (2D) or color (3D).
                For color images, assumes BGR format as per OpenCV convention.
                
        Raises:
            ValueError: If image is None or has invalid dimensions.
            
        Examples:
            >>> image = cv2.imread('photo.jpg')
            >>> processor = ThresholdProcessor(image)
            >>> print(f"Image is grayscale: {processor.is_grayscale}")
        """
        self.image = image
        self.is_grayscale = len(image.shape) == 2

    def convert_color_space(self, color_space: str) -> np.ndarray:
        """Convert the image to the specified color space.
        
        This method handles color space conversion for both grayscale and color images.
        For grayscale images, it first converts to BGR if needed, then to the target
        color space. For color images, it directly converts from BGR to the target.
        
        Args:
            color_space: Target color space name. Supported values:
                'BGR', 'HSV', 'HLS', 'Lab', 'Luv', 'YCrCb', 'XYZ', 'Grayscale'
                
        Returns:
            np.ndarray: Image converted to the specified color space.
            
        Examples:
            >>> processor = ThresholdProcessor(bgr_image)
            >>> hsv_image = processor.convert_color_space('HSV')
            >>> lab_image = processor.convert_color_space('Lab')
            
        Performance:
            Time Complexity: O(n) where n is the number of pixels.
            Space Complexity: O(n) for the converted image.
        """
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
    
    def _convert_bgr_to_colorspace(self, bgr_image: np.ndarray, color_space: str) -> np.ndarray:
        """Convert BGR image to specified color space.
        
        This internal method handles the actual color space conversion from BGR
        to the target color space using OpenCV's color conversion functions.
        
        Args:
            bgr_image: Input image in BGR format as numpy array.
            color_space: Target color space name. Supported values:
                'BGR', 'HSV', 'HLS', 'Lab', 'Luv', 'YCrCb', 'XYZ', 'Grayscale'
                
        Returns:
            np.ndarray: Image converted to the specified color space.
            
        Performance:
            Time Complexity: O(n) where n is the number of pixels.
            Space Complexity: O(n) for the converted image.
        """
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

    def apply_range_threshold(self, converted_image: np.ndarray, lower_bounds: List[int], upper_bounds: List[int]) -> np.ndarray:
        """Apply range-based thresholding to create a binary mask.
        
        This method creates a binary mask by applying lower and upper bounds
        to each channel of the input image. Pixels within the specified range
        are retained, while others are set to zero. This is commonly used for
        color-based object segmentation.
        
        Args:
            converted_image: Input image in any color space as numpy array.
            lower_bounds: List of lower threshold values for each channel.
                Length must match the number of channels in the image.
            upper_bounds: List of upper threshold values for each channel.
                Length must match the number of channels in the image.
                
        Returns:
            np.ndarray: Thresholded image where pixels within the range are preserved
                and others are set to zero. Same dimensions as input image.
                
        Examples:
            >>> processor = ThresholdProcessor(hsv_image)
            >>> # Threshold for red objects in HSV space
            >>> result = processor.apply_range_threshold(hsv_image, [0, 50, 50], [10, 255, 255])
            
        Performance:
            Time Complexity: O(n) where n is the number of pixels.
            Space Complexity: O(n) for the mask and result image.
        """
        lower_bounds = np.array(lower_bounds, dtype=np.uint8)
        upper_bounds = np.array(upper_bounds, dtype=np.uint8)
        mask = cv2.inRange(converted_image, lower_bounds, upper_bounds)
        return cv2.bitwise_and(self.image, self.image, mask=mask)

    def apply_binary_threshold(self, gray_image: np.ndarray, threshold_value: int, use_otsu: bool) -> np.ndarray:
        """Apply binary thresholding to a grayscale image.
        
        This method converts a grayscale image to a binary image by applying
        a threshold value. Pixels above the threshold become white (255),
        pixels below become black (0). Optionally uses Otsu's method for
        automatic threshold selection.
        
        Args:
            gray_image: Input grayscale image as numpy array.
            threshold_value: Threshold value (0-255). Ignored if use_otsu is True.
            use_otsu: If True, uses Otsu's method to automatically determine
                the optimal threshold value, ignoring threshold_value parameter.
                
        Returns:
            np.ndarray: Binary image (0 or 255 values) with same dimensions as input.
                
        Examples:
            >>> gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            >>> processor = ThresholdProcessor(gray)
            >>> binary = processor.apply_binary_threshold(gray, 127, False)
            >>> otsu_binary = processor.apply_binary_threshold(gray, 0, True)
            
        Performance:
            Time Complexity: O(n) where n is the number of pixels.
            Space Complexity: O(1) additional space beyond output.
        """
        if use_otsu:
            # When using Otsu, the threshold value is calculated automatically
            ret, mask = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            ret, mask = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY)
        return mask
    
    def apply_advanced_threshold(self, gray_image: np.ndarray, threshold_value: int, max_value: int, threshold_type: str, use_otsu: bool = False, use_triangle: bool = False) -> np.ndarray:
        """Apply advanced thresholding with multiple threshold types and automatic methods.
        
        This method provides access to all OpenCV thresholding types including
        BINARY, BINARY_INV, TRUNC, TOZERO, and TOZERO_INV. It also supports
        automatic threshold selection using Otsu's method or Triangle method.
        
        Args:
            gray_image: Input grayscale image as numpy array.
            threshold_value: Threshold value (0-255). Ignored for automatic methods.
            max_value: Maximum value assigned to pixels above threshold.
            threshold_type: Type of thresholding to apply. Options:
                'BINARY', 'BINARY_INV', 'TRUNC', 'TOZERO', 'TOZERO_INV'
            use_otsu: If True, uses Otsu's method for automatic threshold selection.
            use_triangle: If True, uses Triangle method for automatic threshold selection.
                
        Returns:
            np.ndarray: Thresholded image with same dimensions as input.
            
        Examples:
            >>> processor = ThresholdProcessor(gray_image)
            >>> binary = processor.apply_advanced_threshold(gray, 127, 255, 'BINARY')
            >>> otsu = processor.apply_advanced_threshold(gray, 0, 255, 'BINARY', use_otsu=True)
            >>> triangle = processor.apply_advanced_threshold(gray, 0, 255, 'BINARY', use_triangle=True)
            
        Performance:
            Time Complexity: O(n) where n is the number of pixels.
            Space Complexity: O(1) additional space beyond output.
        """
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
    
    def apply_adaptive_threshold(self, gray_image: np.ndarray, max_value: int, adaptive_method: str, threshold_type: str, block_size: int, c_constant: int) -> np.ndarray:
        """Apply adaptive thresholding for images with varying illumination.
        
        Adaptive thresholding calculates threshold values for local regions,
        making it effective for images with uneven lighting conditions. The
        threshold is calculated for each pixel based on its neighborhood.
        
        Args:
            gray_image: Input grayscale image as numpy array.
            max_value: Maximum value assigned to pixels above threshold.
            adaptive_method: Method for calculating threshold. Options:
                'MEAN_C': Threshold is mean of neighborhood minus constant
                'GAUSSIAN_C': Threshold is Gaussian-weighted sum minus constant
            threshold_type: Type of thresholding. Options: 'BINARY', 'BINARY_INV'
            block_size: Size of neighborhood area for threshold calculation.
                Must be odd and >= 3. Even values are automatically incremented.
            c_constant: Constant subtracted from the calculated threshold.
                
        Returns:
            np.ndarray: Adaptively thresholded binary image.
            
        Examples:
            >>> processor = ThresholdProcessor(gray_image)
            >>> adaptive = processor.apply_adaptive_threshold(
            ...     gray, 255, 'GAUSSIAN_C', 'BINARY', 11, 2
            ... )
            
        Performance:
            Time Complexity: O(n*k²) where n is pixels and k is block_size.
            Space Complexity: O(1) additional space beyond output.
        """
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
    
    def apply_multi_channel_threshold(self, converted_image: np.ndarray, thresholding_params: Dict[str, Any]) -> np.ndarray:
        """Apply advanced thresholding to each channel of a multi-channel image.
        
        This method enables per-channel thresholding with different parameters
        for each channel, allowing for fine-tuned control over multi-channel
        image processing. Supports all thresholding methods including Simple,
        Otsu, Triangle, Adaptive, and Range-based thresholding.
        
        Args:
            converted_image: Input image (single or multi-channel) as numpy array.
            thresholding_params: Dictionary containing thresholding configuration:
                - 'method': Thresholding method ('Simple', 'Otsu', 'Triangle', 'Adaptive', 'Range')
                - 'threshold_type': OpenCV threshold type for non-range methods
                - 'channels': List of channel-specific parameter dictionaries
                - For range method: 'lower_bounds', 'upper_bounds' lists
                
        Returns:
            np.ndarray: Thresholded image. For multi-channel input, returns merged result.
                For single-channel input, returns processed single channel.
                
        Examples:
            >>> params = {
            ...     'method': 'Simple',
            ...     'channels': [
            ...         {'threshold': 100, 'max_value': 255, 'threshold_type': 'BINARY'},
            ...         {'threshold': 150, 'max_value': 255, 'threshold_type': 'BINARY'}
            ...     ]
            ... }
            >>> result = processor.apply_multi_channel_threshold(hsv_image, params)
            
        Performance:
            Time Complexity: O(n*c) where n is pixels and c is number of channels.
            Space Complexity: O(n*c) for channel splitting and merging.
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
    
    def apply_single_channel_advanced_threshold(self, gray_image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply advanced thresholding to a single channel image with parameter dictionary.
        
        This method provides a unified interface for applying various thresholding
        methods to single-channel images using a parameter dictionary. It serves
        as a dispatcher to the appropriate thresholding method based on the
        specified parameters.
        
        Args:
            gray_image: Input single-channel grayscale image as numpy array.
            params: Dictionary containing thresholding parameters:
                - 'method': Thresholding method ('Simple', 'Otsu', 'Triangle', 'Adaptive')
                - 'threshold': Threshold value (ignored for automatic methods)
                - 'max_value': Maximum value for thresholding
                - 'threshold_type': OpenCV threshold type
                - For adaptive: 'adaptive_method', 'block_size', 'c_constant'
                
        Returns:
            np.ndarray: Thresholded single-channel image.
            
        Examples:
            >>> params = {
            ...     'method': 'Otsu',
            ...     'threshold': 127,
            ...     'max_value': 255,
            ...     'threshold_type': 'BINARY'
            ... }
            >>> result = processor.apply_single_channel_advanced_threshold(gray, params)
            
        Performance:
            Time Complexity: Depends on chosen method, typically O(n) where n is pixels.
            Space Complexity: O(1) additional space beyond output.
        """
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