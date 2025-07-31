"""Interactive image viewer and processing framework for the Parameter project.

This module provides the core ImageViewer class which serves as the central orchestrator
for interactive image viewing, processing, and analysis. It combines OpenCV-based GUI
components with real-time parameter control through trackbars, mouse interaction handling,
and comprehensive analysis capabilities.

The module supports both interactive GUI mode and headless automation mode, making it
suitable for both development/debugging and production automation scenarios. The design
follows a modular architecture with clear separation of concerns between visualization,
control, analysis, and configuration management.

Key Components:
- ImageViewer: Main class orchestrating the entire application lifecycle
- ImageProcessor: Protocol defining the interface for image processing functions
- Integration with ViewerConfig, MouseHandler, TrackbarManager, and WindowManager
- Support for ROI selection, line drawing, polygon definition, and analysis
- Real-time parameter adjustment via trackbars with immediate visual feedback
- Text logging and analysis control windows for comprehensive debugging

Usage:
    # Simple viewer setup
    viewer = ImageViewer.create_simple(enable_ui=True, window_size=(800, 600))
    
    # Viewer with trackbars for parameter tuning
    trackbars = [{"name": "Threshold", "param_name": "thresh", "max_value": 255}]
    viewer = ImageViewer.create_with_trackbars(trackbars, enable_ui=True)
    
    # Main processing loop
    while viewer.should_loop_continue():
        # Process images using current parameters
        processed_images = process_function(viewer.get_all_params())
        viewer.display_images = processed_images
    viewer.cleanup_viewer()
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Union, Callable, Protocol, TypeVar
import textwrap
import traceback

from ..config.viewer_config import ViewerConfig
from ..events.mouse_handler import MouseHandler
from ..controls.trackbar_manager import TrackbarManager
from ..gui.window_manager import WindowManager
from ..analysis import ImageAnalyzer
from ..analysis.plotting.plot_analyzer import MATPLOTLIB_AVAILABLE
from ..gui.analysis_control_window import AnalysisControlWindow, TKINTER_AVAILABLE

T = TypeVar('T')

class ImageProcessor(Protocol):
    """Protocol defining the interface for image processing functions in the ImageViewer framework.
    
    This protocol establishes a standard interface for image processing functions that can be
    integrated with the ImageViewer system. Image processing functions implementing this protocol
    receive the current parameter state and a logging function, then return processed images
    with descriptive names for display.
    
    The protocol enables loose coupling between the ImageViewer and specific image processing
    algorithms, allowing for easy swapping of processing functions and supporting both simple
    transformations and complex multi-stage processing pipelines.
    
    Methods:
        __call__: Process images using current parameters and return results for display.
    
    Examples:
        >>> def my_processor(params: Dict[str, Any], log_func: Callable[[str], None]) -> List[Tuple[np.ndarray, str]]:
        ...     threshold = params.get('threshold', 127)
        ...     log_func(f"Applying threshold: {threshold}")
        ...     # Process image and return results
        ...     return [(processed_image, "Thresholded Image")]
        ...
        >>> # Use with ImageViewer
        >>> viewer = ImageViewer.create_simple()
        >>> viewer.user_image_processor = my_processor
    """
    def __call__(self, params: Dict[str, Any], log_func: Callable[[str], None]) -> List[Tuple[np.ndarray, str]]: ...

class ImageViewer:
    """Central orchestrator for interactive image viewing, processing, and analysis.
    
    This class serves as the main entry point for the Parameter project's image viewing
    and processing capabilities. It integrates multiple subsystems including OpenCV-based
    GUI components, real-time parameter control via trackbars, mouse interaction handling,
    comprehensive analysis tools, and both interactive and headless operation modes.
    
    The ImageViewer follows a modular architecture that enables:
    - Interactive image display with zoom, pan, and navigation controls
    - Real-time parameter adjustment through trackbars with immediate visual feedback
    - ROI selection, line drawing, and polygon definition for analysis
    - Comprehensive logging and debugging capabilities
    - Integration with analysis tools for histogram, profile, and geometric analysis
    - Support for both GUI mode (interactive) and headless mode (automation)
    - Context manager support for automatic resource cleanup
    
    The class supports various image processing workflows through the ImageProcessor
    protocol, enabling loose coupling between the viewer and specific algorithms.
    It can handle both static image sets and dynamic processing functions that
    generate images based on current parameter values.
    
    Key Subsystems:
        - ViewerConfig: Configuration management and window settings
        - MouseHandler: Mouse interaction and ROI management
        - TrackbarManager: Real-time parameter control interface
        - WindowManager: OpenCV window lifecycle management
        - ImageAnalyzer: Analysis tools for histograms, profiles, and metrics
        - AnalysisControlWindow: Advanced analysis control interface (if available)
    
    Attributes:
        config (ViewerConfig): Configuration settings for windows and behavior
        mouse (MouseHandler): Mouse interaction and ROI management
        trackbar (TrackbarManager): Parameter control interface
        windows (WindowManager): OpenCV window management
        analyzer (ImageAnalyzer): Analysis and plotting capabilities
        analysis_window (AnalysisControlWindow): Advanced analysis controls
        display_images (List[Tuple[np.ndarray, str]]): Current images for display
        user_image_processor (Optional[ImageProcessor]): Custom processing function
        
    Examples:
        >>> # Simple viewer for static images
        >>> viewer = ImageViewer.create_simple(enable_ui=True, window_size=(800, 600))
        >>> viewer.display_images = [(image, "My Image")]
        >>> while viewer.should_loop_continue():
        ...     pass  # Display image with basic controls
        >>> viewer.cleanup_viewer()
        
        >>> # Interactive parameter tuning
        >>> trackbars = [
        ...     {"name": "Threshold", "param_name": "thresh", "max_value": 255, "initial_value": 127},
        ...     {"name": "Kernel Size", "param_name": "kernel", "max_value": 31, "initial_value": 5}
        ... ]
        >>> viewer = ImageViewer.create_with_trackbars(trackbars, enable_ui=True)
        >>> 
        >>> def process_images(params, log_func):
        ...     thresh = params['thresh']
        ...     kernel = params['kernel']
        ...     log_func(f"Processing with threshold={thresh}, kernel={kernel}")
        ...     # Apply processing...
        ...     return [(processed_image, f"Processed (T={thresh})")]
        ...
        >>> viewer.setup_viewer(image_processor_func=process_images)
        >>> while viewer.should_loop_continue():
        ...     viewer.update_display()
        >>> viewer.cleanup_viewer()
        
        >>> # Context manager usage
        >>> with ImageViewer.create_simple() as viewer:
        ...     viewer.display_images = [(image, "Test")]
        ...     # Automatic cleanup on exit
    """
    def __init__(self, config: ViewerConfig = None, trackbar_definitions: List[Dict[str, Any]] = None, app_debug_mode: bool = True, max_headless_iterations: int = 1, text_window: bool = True, analysis_control_window: bool = True):
        """Initialize the ImageViewer with comprehensive configuration and subsystem setup.
        
        Creates a new ImageViewer instance with all necessary subsystems initialized
        and configured. This includes setting up mouse handling, trackbar management,
        window management, analysis capabilities, and optional UI components.
        
        The initialization process configures the viewer for either interactive GUI mode
        or headless automation mode based on the app_debug_mode parameter. It establishes
        connections between all subsystems and prepares the viewer for immediate use.
        
        Args:
            config: ViewerConfig instance containing window settings, trackbar definitions,
                and display parameters. If None, creates a default configuration.
            trackbar_definitions: List of trackbar configuration dictionaries. Each dictionary
                should contain 'name', 'param_name', 'max_value', and optionally 'initial_value'
                and 'callback'. Overrides trackbars in config if provided.
            app_debug_mode: Whether to enable interactive GUI mode (True) or headless mode (False).
                GUI mode provides full interactive capabilities while headless mode is suitable
                for automation and batch processing.
            max_headless_iterations: Maximum number of processing iterations in headless mode
                before automatically terminating. Prevents infinite loops in automation.
            text_window: Whether to enable the text logging window for debugging output.
                Only effective when app_debug_mode is True.
            analysis_control_window: Whether to enable the advanced analysis control window
                for histogram, profile, and geometric analysis. Requires tkinter availability.
                
        Examples:
            >>> # Basic interactive viewer
            >>> viewer = ImageViewer()
            
            >>> # Configured viewer with custom settings
            >>> config = ViewerConfig().set_window_size(1024, 768).set_debug_mode(True)
            >>> trackbars = [{"name": "Threshold", "param_name": "thresh", "max_value": 255}]
            >>> viewer = ImageViewer(config, trackbars, app_debug_mode=True)
            
            >>> # Headless viewer for automation
            >>> viewer = ImageViewer(app_debug_mode=False, max_headless_iterations=10)
            
        Performance:
            Time Complexity: O(n) where n is the number of trackbar definitions.
            Space Complexity: O(n) for storing trackbar configurations and subsystem objects.
        """
        self.config = config if config else ViewerConfig()
        
        if trackbar_definitions:
            self.config.trackbar = trackbar_definitions
        
        self.config.enable_debug = app_debug_mode
        
        self.max_headless_iterations = max_headless_iterations
        self._headless_iteration_count = 0
        self._app_debug_mode = app_debug_mode
        self._show_text_window_enabled = text_window
        self._show_analysis_control_window_enabled = analysis_control_window
        
        self.mouse = MouseHandler()
        self.trackbar = TrackbarManager(self.config.trackbar_window_name)
        self.windows = WindowManager(self.config)
        self.analyzer = ImageAnalyzer()
        if self._show_analysis_control_window_enabled:
            self.analysis_window = AnalysisControlWindow(self)
        else:
            self.analysis_window = None
        
        self._internal_images: List[Tuple[np.ndarray, str]] = []
        self._should_continue_loop: bool = True
        self._auto_initialized = False

        self.current_image_dims: Optional[Tuple[int, int]] = None
        self.size_ratio: float = 1.0
        self.show_area: List[int] = [0, 0, self.config.screen_width, self.config.screen_height]
        self.address: str = "(0,0)"
        self.text_image: np.ndarray = np.full(
            (self.config.text_window_height, self.config.text_window_width, 3), 255, dtype=np.uint8
        )
        self.log_texts: List[str] = []
        self.logged_messages: set = set()  # Track unique messages to prevent duplicates
        self.initial_window_size: Tuple[int, int] = (self.config.screen_width, self.config.screen_height)
        self.user_image_processor: Optional[ImageProcessor] = None
        self.image_processing_func_internal: Optional[ImageProcessor] = None
        self._params_changed: bool = False
        self._cached_scaled_image = None
        self._cached_size_ratio = None
        self._cached_show_area = None
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        self._auto_setup()

    def _auto_setup(self):
        """Automatically initialize the viewer if trackbars are configured.
        
        This internal method performs automatic initialization of the ImageViewer
        when trackbar configurations are present. It prevents duplicate initialization
        by checking the _auto_initialized flag and only runs setup_viewer() once
        when trackbars are defined in the configuration.
        
        This method is called during __init__ to provide seamless setup for viewers
        that have trackbar definitions, eliminating the need for manual setup_viewer()
        calls in common use cases.
        
        Performance:
            Time Complexity: O(1) - simple flag check and conditional setup call.
            Space Complexity: O(1) - no additional memory allocation.
        """
        if not self._auto_initialized and self.config.trackbar:
            self.setup_viewer()
            self._auto_initialized = True

    @property
    def display_images(self) -> List[Tuple[np.ndarray, str]]:
        """Get the current list of images for display.
        
        Returns the internal list of images that are currently loaded for display
        in the ImageViewer. Each image is represented as a tuple containing the
        numpy array image data and a descriptive string name.
        
        Returns:
            List[Tuple[np.ndarray, str]]: List of image tuples where each tuple
                contains (image_array, descriptive_name). The image_array is a
                numpy array representing the image data, and descriptive_name
                is a string used for display and identification purposes.
                
        Examples:
            >>> viewer = ImageViewer.create_simple()
            >>> images = viewer.display_images
            >>> if images:
            ...     image_array, name = images[0]
            ...     print(f"First image: {name}, shape: {image_array.shape}")
            
        Performance:
            Time Complexity: O(1) - direct attribute access.
            Space Complexity: O(1) - returns reference to existing list.
        """
        return self._internal_images

    @display_images.setter
    def display_images(self, image_list: List[Tuple[np.ndarray, str]]):
        """Set the list of images for display with validation and automatic processing.
        
        Updates the internal image list with new images and triggers display processing
        if the viewer is in interactive mode. Validates input format to ensure all images
        are properly formatted numpy arrays with descriptive names.
        
        This setter automatically triggers frame processing and event handling when
        in debug mode, providing immediate visual feedback. In headless mode, it
        increments the iteration counter for automation control.
        
        Args:
            image_list: List of image tuples where each tuple contains
                (image_array, descriptive_name). The image_array must be a non-empty
                numpy array representing image data, and descriptive_name should be
                a string for display purposes.
                
        Raises:
            Validation errors are handled gracefully by displaying an error image
            rather than raising exceptions, ensuring the viewer remains stable.
            
        Examples:
            >>> viewer = ImageViewer.create_simple()
            >>> # Set single image
            >>> viewer.display_images = [(cv2.imread('image.jpg'), "My Image")]
            >>> 
            >>> # Set multiple images
            >>> images = [
            ...     (processed_image1, "Original"),
            ...     (processed_image2, "Filtered"),
            ...     (processed_image3, "Result")
            ... ]
            >>> viewer.display_images = images
            
        Performance:
            Time Complexity: O(n) where n is the number of images for validation.
            Space Complexity: O(n) for storing the image list references.
        """
        if not isinstance(image_list, list) or \
           not all(isinstance(item, tuple) and len(item) == 2 and \
                    isinstance(item[0], np.ndarray) and item[0].size > 0 for item in image_list):
            print(f"Error: display_images with invalid format/empty image. Input type: {type(image_list)}")
            self._internal_images = [(np.zeros((self.config.min_window_size[1],self.config.min_window_size[0],1), dtype=np.uint8), "Image Set Error")]
        else:
            self._internal_images = image_list
        
        if self.config.enable_debug and self._should_continue_loop:
            # Process both OpenCV and tkinter events in proper sequence
            try:
                if hasattr(self, '_process_frame_and_check_quit'):
                    self._process_frame_and_check_quit()
                # Process tkinter events after OpenCV operations
                self._process_tk_events()
            except Exception as e:
                print(f"Error in process_frame: {e}")
        
        if not self.config.enable_debug:
            self._headless_iteration_count += 1

    def _process_frame_and_check_quit(self):
        """Process a single frame update and check for quit conditions in GUI mode.
        
        This internal method handles the core frame processing cycle for interactive
        GUI mode, including image display updates, keyboard input processing, and
        window state monitoring. It ensures the viewer remains responsive and handles
        user interactions appropriately.
        
        The processing cycle includes:
        - Updating show trackbar for multi-image navigation
        - Processing and displaying the current image with overlays
        - Updating the text window if enabled
        - Handling keyboard shortcuts (q/ESC to quit, r to reset view)
        - Monitoring window state to detect closure
        
        Key bindings:
        - 'q' or ESC: Quit the viewer
        - 'r': Reset view to default zoom and position
        
        This method only operates in debug/GUI mode and returns immediately
        in headless mode. It handles exceptions gracefully to maintain stability.
        
        Performance:
            Time Complexity: O(d) where d is the display processing time.
            Space Complexity: O(1) - processes existing image data in place.
        """
        if not self.config.enable_debug: return
        if not self._should_continue_loop: return
        if not self.windows.windows_created:
             print("Warning: _process_frame_and_check_quit called but windows not created (debug on).")
             self._should_continue_loop = False
             return

        if not self._internal_images:
            self._internal_images = [(np.zeros((100,100,1), dtype=np.uint8), "No Images (internal)")]
        
        try:
            # Only call OpenCV-related functions
            self._update_show_trackbar()
            self._process_image_for_display()
            if self._show_text_window_enabled:
                self._show_text_window()
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:
                pass
                self._should_continue_loop = False
            elif key == ord('r'): 
                self.reset_view()
        except Exception as e:
            print(f"Error in process_frame: {e}")
        
        try:
            if self._should_continue_loop and \
               cv2.getWindowProperty(self.config.process_window_name, cv2.WND_PROP_VISIBLE) < 1:
                pass
                self._should_continue_loop = False
        except cv2.error:
            if self._should_continue_loop:
                 pass
                 self._should_continue_loop = False

    def should_loop_continue(self) -> bool:
        """Check whether the main processing loop should continue execution.
        
        This method determines if the ImageViewer should continue processing frames
        based on the current mode and state. In interactive GUI mode, it checks if
        the user has closed windows or pressed quit keys. In headless mode, it
        enforces the maximum iteration limit to prevent infinite loops.
        
        The method provides a unified interface for loop control that works correctly
        in both interactive and automated scenarios, ensuring proper termination
        conditions are met for each mode.
        
        Returns:
            bool: True if the loop should continue processing, False if it should
                terminate. In GUI mode, returns False when windows are closed or
                quit conditions are met. In headless mode, returns False when
                the maximum iteration count is reached.
                
        Examples:
            >>> viewer = ImageViewer.create_simple()
            >>> while viewer.should_loop_continue():
            ...     # Process images
            ...     processed = process_function()
            ...     viewer.display_images = processed
            >>> viewer.cleanup_viewer()
            
            >>> # Headless mode with iteration limit
            >>> viewer = ImageViewer(app_debug_mode=False, max_headless_iterations=5)
            >>> iteration = 0
            >>> while viewer.should_loop_continue():
            ...     print(f"Processing iteration {iteration}")
            ...     iteration += 1
            
        Performance:
            Time Complexity: O(1) - simple flag and counter checks.
            Space Complexity: O(1) - no additional memory allocation.
        """
        if not self.config.enable_debug:
            if self._headless_iteration_count >= self.max_headless_iterations:
                pass
                return False
            return True
        else:
            return self._should_continue_loop

    def setup_viewer(
                     self,
                     initial_images_for_first_frame: Optional[List[Tuple[np.ndarray, str]]] = None,
                     image_processor_func: Optional[ImageProcessor] = None):
        """Initialize the ImageViewer for operation with windows, trackbars, and initial images.
        
        This method performs the complete setup process for the ImageViewer, including
        creating OpenCV windows, initializing trackbars, setting up the image processor,
        and displaying the first frame. It handles both static image display and
        dynamic image processing scenarios.
        
        The setup process includes parameter initialization, window creation (in GUI mode),
        trackbar creation, analysis window setup, and initial image processing. This method
        should be called before starting the main processing loop.
        
        Args:
            initial_images_for_first_frame: Optional list of image tuples to display
                initially. If provided, these images will be shown before any processing.
                Each tuple should contain (image_array, descriptive_name).
            image_processor_func: Optional ImageProcessor function that will be called
                to generate images based on current parameter values. This function
                receives the current parameters and a logging function, then returns
                a list of processed images for display.
                
        Examples:
            >>> # Setup with static images
            >>> initial_images = [(cv2.imread('test.jpg'), "Test Image")]
            >>> viewer.setup_viewer(initial_images_for_first_frame=initial_images)
            
            >>> # Setup with dynamic processing
            >>> def my_processor(params, log_func):
            ...     threshold = params.get('threshold', 127)
            ...     # Process images based on parameters
            ...     return [(processed_image, f"Threshold: {threshold}")]
            >>> 
            >>> viewer.setup_viewer(image_processor_func=my_processor)
            
            >>> # Setup with both
            >>> viewer.setup_viewer(initial_images, my_processor)
            
        Performance:
            Time Complexity: O(n + m) where n is the number of trackbars and m is the initial processing cost.
            Space Complexity: O(n + k) where n is trackbar count and k is the size of initial images.
        """
        self.clear_log()
        pass
        self._should_continue_loop = True
        self.user_image_processor = image_processor_func
        self._initialize_parameters()

        if self.config.enable_debug:
            self.windows.create_windows(self._mouse_callback, self._text_mouse_callback, self._show_text_window_enabled)
            if not self.windows.windows_created:
                pass
                print("FATAL: UI Mode: ImageViewer failed to create windows.")
                self._should_continue_loop = False
            else:
                if self._show_analysis_control_window_enabled and self.analysis_window:
                    self.analysis_window.create_window()

        temp_images = []
        if self.user_image_processor:
            pass
            try:
                temp_images = self.user_image_processor(dict(self.trackbar.parameters), self.log)
            except Exception as e:
                print(f"ERROR in user processor (initial frame): {e}\n{traceback.format_exc()}")
                temp_images = [(np.zeros((100,100,1), dtype=np.uint8), "Init Proc Error")]
        elif initial_images_for_first_frame is not None:
            temp_images = initial_images_for_first_frame
        else:
            temp_images = [(np.zeros((100,100,1), dtype=np.uint8), "Initial Empty")]
        self._internal_images = temp_images

        if self.config.enable_debug and self.config.trackbar and self.windows.windows_created:
            pass
            for trackbar_config_item in self.config.trackbar:
                self.trackbar.create_trackbar(trackbar_config_item, self)
        
        if self.config.enable_debug and self._should_continue_loop:
            self._process_frame_and_check_quit()
        
        pass

    def update_display(self, image_list: Optional[List[Tuple[np.ndarray, str]]] = None):
        """Update the displayed images using either a processor function or provided image list.
        
        This method refreshes the display by either calling the configured image processor
        function with current parameters, using a provided image list, or processing the
        current frame if in GUI mode. It handles errors gracefully and ensures the display
        remains functional even when processing fails.
        
        The method supports three update modes:
        1. Processor-based: Uses user_image_processor with current parameters
        2. Direct list: Uses provided image_list directly
        3. Frame processing: Triggers GUI frame processing and event handling
        
        Args:
            image_list: Optional list of image tuples to display directly.
                If provided, bypasses the image processor and displays these images.
                Each tuple should contain (image_array, descriptive_name).
                
        Examples:
            >>> # Update using configured processor
            >>> viewer.update_display()  # Uses current parameters
            
            >>> # Update with specific images
            >>> new_images = [(processed_img1, "Result 1"), (processed_img2, "Result 2")]
            >>> viewer.update_display(new_images)
            
            >>> # Typical usage in processing loop
            >>> while viewer.should_loop_continue():
            ...     viewer.update_display()  # Automatically processes with current params
            
        Performance:
            Time Complexity: O(p + d) where p is processing time and d is display time.
            Space Complexity: O(n) where n is the size of processed images.
        """
        if self.user_image_processor:
            if not self._should_continue_loop and self.config.enable_debug: return
            try:
                processed_images = self.user_image_processor(dict(self.trackbar.parameters), self.log)
                self.display_images = processed_images
            except Exception as e:
                print(f"ERROR in user_image_processor: {e}\n{traceback.format_exc()}")
                self.display_images = [(np.zeros((100,100,1), dtype=np.uint8), "Proc Error")]
        elif image_list is not None:
            self.display_images = image_list
        elif self.config.enable_debug and self._should_continue_loop:
            self._process_frame_and_check_quit()

    def _initialize_parameters(self):
        """Initialize trackbar parameters with default values and special callback handling.
        
        This internal method sets up initial parameter values for all configured trackbars.
        It handles special callback types (like 'odd' for ensuring odd values), manages
        persistent value storage, and validates trackbar configurations.
        
        The initialization process:
        1. Validates each trackbar configuration has required fields
        2. Processes special callback types to adjust initial values
        3. Uses persistent values if available, otherwise uses configured defaults
        4. Stores values in both active parameters and persistent storage
        
        Special callback handling:
        - 'odd': Ensures the initial value is odd, incrementing by 1 if even
        
        Performance:
            Time Complexity: O(n) where n is the number of trackbar configurations.
            Space Complexity: O(n) for parameter storage.
        """
        if not self.config.trackbar:
            return

        for tb_conf in self.config.trackbar:
            param_name = tb_conf.get('param_name')
            if not param_name:
                print(f"Warning: Trackbar config item missing 'param_name': {tb_conf}")
                continue
            initial_value_from_config = tb_conf.get('initial_value', 0)
            callback_spec = tb_conf.get('callback')
            if callback_spec == 'odd':
                temp_val = max(1, initial_value_from_config)
                if temp_val % 2 == 0: temp_val += 1
                initial_value_from_config = temp_val
            if param_name in self.trackbar.persistent_values:
                self.trackbar.parameters[param_name] = self.trackbar.persistent_values[param_name]
            else:
                self.trackbar.parameters[param_name] = initial_value_from_config
                self.trackbar.persistent_values[param_name] = initial_value_from_config

    def clear_log(self):
        """Clear all logged messages and reset the text display window.
        
        This method removes all logged messages from the text display system,
        including both the visible text lines and the deduplication set used
        to prevent duplicate messages. It also resets the text window image
        to a clean white background.
        
        The clearing process includes:
        - Removing all text lines from the log display
        - Clearing the message deduplication set
        - Resetting the text window image to white background
        
        Examples:
            >>> viewer = ImageViewer.create_simple()
            >>> viewer.log("Test message 1")
            >>> viewer.log("Test message 2")
            >>> viewer.clear_log()  # All messages removed
            
        Performance:
            Time Complexity: O(1) - simple list and set clearing operations.
            Space Complexity: O(w*h) where w,h are text window dimensions for image reset.
        """
        self.log_texts = []
        self.logged_messages.clear()  # Clear the deduplication set as well
        self.text_image = np.full((self.config.text_window_height, self.config.text_window_width, 3), 255, dtype=np.uint8)

    def log(self, message: str):
        """Log a message to the text display window with automatic formatting and deduplication.
        
        This method adds a message to the text log display with intelligent formatting,
        deduplication, and automatic text wrapping. In GUI mode, messages are displayed
        in the text window with proper line wrapping and scrolling. In headless mode,
        messages are printed to stdout with a special prefix.
        
        Features include:
        - Automatic message deduplication to prevent spam
        - Text wrapping based on window width and font characteristics
        - Dynamic text window resizing based on content
        - Line height management for optimal readability
        - Memory management with maximum log entry limits
        
        Args:
            message: The message string to log. Multi-line messages are supported
                and will be properly wrapped and displayed.
                
        Examples:
            >>> viewer = ImageViewer.create_simple()
            >>> viewer.log("Processing started")
            >>> viewer.log("Threshold value: 127")
            >>> viewer.log("Multi-line message\\nwith details\\nand more info")
            
            >>> # Used in image processor functions
            >>> def my_processor(params, log_func):
            ...     threshold = params.get('threshold', 127)
            ...     log_func(f"Applying threshold: {threshold}")
            ...     return [(processed_image, "Result")]
            
        Performance:
            Time Complexity: O(n) where n is the message length for text wrapping.
            Space Complexity: O(m) where m is the total size of logged messages.
        """
        if self.config.enable_debug:
            max_log_entries = 200 
            message_str = str(message)
            
            # Check if this message has already been logged (deduplication)
            if message_str in self.logged_messages:
                return  # Don't log duplicate messages
            
            # Add message to set of logged messages
            self.logged_messages.add(message_str)
            char_width_approx = 8 
            wrap_width = (self.config.text_window_width - 20) // char_width_approx
            if wrap_width <=0: wrap_width = 10
            wrapped_lines = [line for msg_line in message_str.strip().split('\n') 
                             for line in textwrap.wrap(msg_line, width=wrap_width, 
                                                        replace_whitespace=False, drop_whitespace=False)]
            self.log_texts.extend(wrapped_lines)
            if len(self.log_texts) > max_log_entries:
                self.log_texts = self.log_texts[-max_log_entries:]
            required_height = len(self.log_texts) * self.config.text_line_height + self.config.text_line_height 
            current_height, current_width, _ = self.text_image.shape
            if required_height > current_height or \
               (required_height < current_height / 1.5 and current_height > self.config.text_window_height * 1.2) :
                new_height = max(self.config.text_window_height, required_height)
                try:
                    self.text_image = np.full((new_height, current_width, 3), 255, dtype=np.uint8)
                except (ValueError, MemoryError) as e: 
                    print(f"Error resizing text_image for log: {e}.")
                    self.text_image = np.full((self.config.text_window_height, current_width, 3), 255, dtype=np.uint8)
            self.text_image.fill(255) 
            y_pos = self.config.text_line_height
            for line_text in self.log_texts:
                if y_pos > self.text_image.shape[0] - self.config.text_line_height: break
                cv2.putText(self.text_image, line_text, (5, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                y_pos += self.config.text_line_height
        else:
            print(f"LOG-HL: {message}")
    
    def reset_view(self):
        """Reset the image view to default zoom and position settings.
        
        This method restores the image display to its original state by resetting
        the zoom ratio to 1.0 and repositioning the view area to the top-left corner.
        It also resizes the display window to match either the current image dimensions
        or the initial window size if no image is loaded.
        
        The reset operation:
        - Sets zoom ratio back to 1.0 (original size)
        - Repositions view area to (0, 0) coordinates
        - Resizes window to fit current image or default size
        - Only operates in GUI mode (ignored in headless mode)
        
        This is typically triggered by pressing 'r' key during interactive use
        or can be called programmatically to restore the default view state.
        
        Examples:
            >>> viewer = ImageViewer.create_simple()
            >>> # User zooms and pans the image
            >>> viewer.reset_view()  # Returns to original view
            
        Performance:
            Time Complexity: O(1) - simple parameter reset operations.
            Space Complexity: O(1) - no additional memory allocation.
        """
        if not self.config.enable_debug: return
        self.size_ratio = 1.0
        self.show_area[0], self.show_area[1] = 0, 0
        if self.current_image_dims:
            self.windows.resize_process_window(self.current_image_dims[1], self.current_image_dims[0])
        else:
             self.windows.resize_process_window(self.initial_window_size[0], self.initial_window_size[1])
        pass

    def _update_show_trackbar(self):
        """Update the image selector trackbar range based on current image count.
        
        This internal method dynamically adjusts the maximum value of the 'show' trackbar
        to match the number of currently loaded images. It handles trackbars configured
        with 'max_value': 'num_images-1' by updating both the trackbar range and current
        position to ensure valid image selection.
        
        The update process:
        1. Locates trackbars with 'param_name': 'show' and dynamic max_value
        2. Calculates new maximum based on current image count
        3. Updates the OpenCV trackbar maximum value
        4. Adjusts current position if it exceeds the new maximum
        5. Synchronizes with persistent parameter storage
        
        This ensures that multi-image navigation trackbars remain functional and
        prevent out-of-bounds image access when the image list changes dynamically.
        
        Only operates in GUI mode with created windows and valid trackbar configurations.
        Handles OpenCV errors gracefully to maintain stability.
        
        Performance:
            Time Complexity: O(n) where n is the number of trackbar configurations to search.
            Space Complexity: O(1) - no additional memory allocation.
        """
        if not self.config.enable_debug or not self.windows.windows_created or not self.config.trackbar: return
        show_tb_config = next((tc for tc in self.config.trackbar if tc.get('param_name') == 'show'), None)
        if not show_tb_config or show_tb_config.get('max_value') != 'num_images-1': return
        show_tb_display_name = show_tb_config.get('name')
        if not show_tb_display_name: return
        new_max_show = max(0, len(self.display_images) - 1 if self.display_images else 0)
        try:
            if cv2.getWindowProperty(self.config.trackbar_window_name, cv2.WND_PROP_VISIBLE) >= 1:
                cv2.setTrackbarMax(show_tb_display_name, self.config.trackbar_window_name, new_max_show)
                current_show_val = self.trackbar.parameters.get('show', 0)
                if current_show_val > new_max_show:
                    self.trackbar.parameters['show'] = new_max_show
                    self.trackbar.persistent_values['show'] = new_max_show
                    cv2.setTrackbarPos(show_tb_display_name, self.config.trackbar_window_name, new_max_show)
        except cv2.error: pass

    def _process_image_for_display(self) -> Optional[Tuple[np.ndarray, float, Tuple[int, int]]]:
        """Process and render the current image with overlays, scaling, and interactive elements.
        
        This comprehensive method handles the complete image rendering pipeline for display
        in the main window. It manages image selection, format conversion, interactive overlay
        rendering (ROIs, lines, polygons), zoom/pan operations, window resizing, and final
        display output with comprehensive error handling.
        
        The processing pipeline includes:
        1. Image selection based on 'show' parameter
        2. Image format validation and conversion (grayscale/color normalization)
        3. Interactive overlay rendering (ROIs, lines, polygons with animations)
        4. Zoom and scaling calculations with bounds checking
        5. Window resizing and viewport management
        6. Pan/scroll area calculations and clamping
        7. Final display canvas creation and information overlays
        8. OpenCV window display with error recovery
        
        Interactive overlays rendered:
        - Current selection rectangle during mouse drag
        - Saved ROI rectangles with selection highlighting and animation
        - Line profiles with endpoint markers and selection emphasis
        - Polygon regions with vertex markers and fill animations
        - Current drawing states for active polygon/line creation
        - Mouse cursor information and pixel value display
        
        Returns:
            Optional[Tuple[np.ndarray, float, Tuple[int, int]]]: Tuple containing
                (display_canvas, size_ratio, mouse_point) if successful, None if error.
                - display_canvas: Final rendered image ready for display
                - size_ratio: Current zoom/scale ratio applied
                - mouse_point: Current mouse position in view coordinates
                
        The method handles numerous edge cases:
        - Empty or invalid image lists
        - Out-of-bounds image indices
        - Invalid image data or formats  
        - Window resize and scaling edge cases
        - OpenCV display errors and recovery
        - Memory constraints and performance optimization
        
        Performance:
            Time Complexity: O(p + o + s) where p is pixel count, o is overlay count, s is scaling cost.
            Space Complexity: O(w*h*c) where w,h are window dimensions and c is color channels.
        """
        try:
            if not self.config.enable_debug or not self.windows.windows_created: return None
            if not self.display_images:
                placeholder = np.full((self.config.screen_height, self.config.screen_width, 3), 50, dtype=np.uint8)
                cv2.putText(placeholder, "No images loaded", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                if self.windows.windows_created and cv2.getWindowProperty(self.config.process_window_name, cv2.WND_PROP_VISIBLE) >=1:
                     cv2.imshow(self.config.process_window_name, placeholder)
                return None

            current_idx = self.trackbar.parameters.get('show', 0)
            current_idx = max(0, min(current_idx, len(self.display_images) - 1))
            
            if not (0 <= current_idx < len(self.display_images) and \
                    isinstance(self.display_images[current_idx], tuple) and \
                    len(self.display_images[current_idx]) == 2 and\
                    isinstance(self.display_images[current_idx][0], np.ndarray) and\
                    self.display_images[current_idx][0].size > 0 ):
                print(f"Error: Invalid image data at index {current_idx}.")
                return None

            original_image, name = self.display_images[current_idx]
            self.current_image_dims = original_image.shape[:2]

            try:
                display_image = original_image.copy()
                if len(display_image.shape) == 2: display_image = cv2.cvtColor(display_image, cv2.COLOR_GRAY2BGR)
                elif display_image.shape[2] == 1: display_image = cv2.cvtColor(display_image, cv2.COLOR_GRAY2BGR)
                elif display_image.shape[2] == 4: display_image = cv2.cvtColor(display_image, cv2.COLOR_BGRA2BGR)
                elif display_image.shape[2] != 3:
                     display_image = display_image[:,:,:3] if display_image.shape[2] > 3 else cv2.cvtColor(display_image, cv2.COLOR_GRAY2BGR)

                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                font_thickness = 1
                text_color_rect_info = (0, 255, 255)

                if self.mouse.mouse_rect:
                    x, y, w, h = self.mouse.mouse_rect
                    if w > 0 and h > 0:
                        cv2.rectangle(display_image, (x, y), (x + w, y + h), (0, 255, 0), 1)
                        roi_info_text = f"({x},{y}) {w}x{h}"
                        text_y_pos = y - 5 if y - 5 > 10 else y + 15
                        cv2.putText(display_image, roi_info_text, (x, text_y_pos), \
                                    font, font_scale, text_color_rect_info, font_thickness, cv2.LINE_AA)

                # Update selection animation state
                self.mouse.update_selection_animation()
                
                for i, rect_coords in enumerate(self.mouse.draw_rects):
                    x, y, w, h = rect_coords
                    if w > 0 and h > 0:
                        color = self.mouse.get_roi_color(i)
                        thickness = self.mouse.get_roi_thickness(i)
                        
                        # Draw the ROI rectangle
                        cv2.rectangle(display_image, (x, y), (x + w, y + h), color, thickness)
                        
                        # Add a semi-transparent highlight fill for selected ROI
                        if i == self.mouse.selected_roi:
                            overlay = display_image.copy()
                            cv2.rectangle(overlay, (x, y), (x + w, y + h), color, -1)  # Filled rectangle
                            alpha = self.mouse.get_selection_alpha('roi', i)  # Get animated alpha
                            cv2.addWeighted(overlay, alpha, display_image, 1 - alpha, 0, display_image)
                            
                            # Add a pulsing border for better visibility
                            cv2.rectangle(display_image, 
                                         (x-2, y-2), 
                                         (x + w + 2, y + h + 2), 
                                         color, 
                                         1, 
                                         cv2.LINE_AA)
                        
                        # Add ROI info text
                        roi_info_text = f"R{i+1}: ({x},{y}) {w}x{h}"
                        text_y_pos = y - 7 if y - 7 > 10 else y + 20
                        
                        # Use different text color for selected ROI
                        text_color = self.mouse.highlight_colors['roi']['label_color'] if i == self.mouse.selected_roi else text_color_rect_info
                        
                        cv2.putText(display_image, roi_info_text, (x, text_y_pos), \
                                    font, font_scale, text_color, font_thickness, cv2.LINE_AA)

                if self.mouse.current_line and self.mouse.is_line_mode:
                    x1, y1, x2, y2 = self.mouse.current_line
                    cv2.line(display_image, (x1, y1), (x2, y2), (255, 255, 0), 2)
                    line_info_text = f"({x1},{y1})-({x2},{y2})"
                    cv2.putText(display_image, line_info_text, (x1, y1 - 10), \
                                font, font_scale, (255, 255, 0), font_thickness, cv2.LINE_AA)

                for i, line_coords in enumerate(self.mouse.draw_lines):
                    x1, y1, x2, y2 = line_coords
                    color = self.mouse.get_line_color(i)
                    thickness = self.mouse.get_line_thickness(i)
                    
                    # Draw the line with appropriate color and thickness
                    cv2.line(display_image, (x1, y1), (x2, y2), color, thickness)
                    
                    # Add visual emphasis for selected line
                    if i == self.mouse.selected_line:
                        # Draw small circles at the endpoints for better visibility
                        endpoint_radius = self.mouse.highlight_colors['line']['endpoint_radius']
                        cv2.circle(display_image, (x1, y1), endpoint_radius, color, -1)  # Filled circle at start
                        cv2.circle(display_image, (x2, y2), endpoint_radius, color, -1)  # Filled circle at end
                        
                        # Draw a slightly thicker line for better visibility
                        cv2.line(display_image, (x1, y1), (x2, y2), color, thickness + 1, cv2.LINE_AA)
                        
                        # Draw a parallel line with animation effect
                        # Calculate perpendicular vector for offset
                        dx, dy = x2 - x1, y2 - y1
                        length = max(1, (dx**2 + dy**2)**0.5)
                        perpx, perpy = -dy/length * 3, dx/length * 3  # Perpendicular vector with length 3
                        
                        # Draw parallel line with slight offset
                        cv2.line(display_image, 
                                (int(x1 + perpx), int(y1 + perpy)), 
                                (int(x2 + perpx), int(y2 + perpy)), 
                                color, 1, cv2.LINE_AA)
                    
                    # Add line info text
                    line_info_text = f"L{i+1}: ({x1},{y1})-({x2},{y2})"
                    text_x = x1 + 5
                    text_y = y1 - 5 if y1 - 5 > 10 else y1 + 15
                    
                    # Use different text color for selected line
                    text_color = self.mouse.highlight_colors['line']['label_color'] if i == self.mouse.selected_line else color
                    
                    cv2.putText(display_image, line_info_text, (text_x, text_y), \
                                font, font_scale, text_color, font_thickness, cv2.LINE_AA)

                # Draw polygons
                for i, polygon in enumerate(self.mouse.draw_polygons):
                    if len(polygon) > 1:
                        pts = np.array(polygon, np.int32)
                        pts = pts.reshape((-1, 1, 2))
                        color = self.mouse.get_polygon_color(i)
                        thickness = self.mouse.get_polygon_thickness(i)
                        
                        # Draw the polygon outline
                        cv2.polylines(display_image, [pts], True, color, thickness)
                        
                        # Add visual emphasis for selected polygon
                        if i == self.mouse.selected_polygon:
                            # Fill polygon with semi-transparent color
                            overlay = display_image.copy()
                            cv2.fillPoly(overlay, [pts], color)
                            alpha = self.mouse.get_selection_alpha('polygon', i)  # Get animated alpha
                            cv2.addWeighted(overlay, alpha, display_image, 1 - alpha, 0, display_image)
                            
                            # Draw vertices with circles for better visibility
                            for point in polygon:
                                cv2.circle(display_image, point, 
                                          self.mouse.highlight_colors['polygon']['vertex_radius'], 
                                          color, -1)  # Filled circle at each vertex
                            
                            # Draw a slightly larger outline for better visibility
                            cv2.polylines(display_image, [pts], True, color, thickness + 1, cv2.LINE_AA)
                                
                        # Add polygon info text
                        if len(polygon) > 0:
                            text_x, text_y = polygon[0]
                            text_y = text_y - 10 if text_y - 10 > 10 else text_y + 20
                            
                            # Use different text color for selected polygon
                            text_color = self.mouse.highlight_colors['polygon']['label_color'] if i == self.mouse.selected_polygon else color
                            
                            cv2.putText(display_image, f"Polygon {i+1}: {len(polygon)} points", 
                                        (text_x, text_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

                # Draw current polygon
                if self.mouse.is_polygon_mode and len(self.mouse.current_polygon) > 0:
                    # Draw lines between vertices
                    pts = np.array(self.mouse.current_polygon, np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(display_image, [pts], False, (255, 255, 0), 1)

                    # Draw a hollow circle at each vertex
                    for point in self.mouse.current_polygon:
                        cv2.circle(display_image, point, 5, (0, 255, 255), 1) # Yellow hollow circle

                    # Draw a line to the current mouse position to show the next segment
                    if self.mouse.scale_ptr:
                        cv2.line(display_image, self.mouse.current_polygon[-1], self.mouse.scale_ptr, (255, 255, 0), 1)

                    # Draw a line from the last point to the first point to show how to close it
                    if len(self.mouse.current_polygon) > 1:
                        cv2.line(display_image, self.mouse.current_polygon[-1], self.mouse.current_polygon[0], (0, 255, 255), 1, cv2.LINE_AA)

                orig_h, orig_w = display_image.shape[:2]
                scaled_w, scaled_h = int(orig_w * self.size_ratio), int(orig_h * self.size_ratio)
                
                if scaled_w <= 0 or scaled_h <= 0: 
                    min_dim_on_screen = 10 
                    self.size_ratio = max(self.config.min_size_ratio, float(min_dim_on_screen) / max(orig_w, orig_h, 1))
                    scaled_w = max(min_dim_on_screen, int(orig_w * self.size_ratio))
                    scaled_h = max(min_dim_on_screen, int(orig_h * self.size_ratio))
                
                view_w, view_h = self.config.screen_width, self.config.screen_height
                try: 
                    _wx, _wy, current_win_w, current_win_h = cv2.getWindowImageRect(self.config.process_window_name)
                    max_win_w = self.config.desktop_resolution[0] if self.config.desktop_resolution else self.config.screen_width * 2
                    max_win_h = self.config.desktop_resolution[1] if self.config.desktop_resolution else self.config.screen_height * 2
                    target_win_w = max(self.config.min_window_size[0], min(scaled_w, max_win_w))
                    target_win_h = max(self.config.min_window_size[1], min(scaled_h, max_win_h))

                    if abs(current_win_w - target_win_w) > 1 or abs(current_win_h - target_win_h) > 1 :
                        self.windows.resize_process_window(target_win_w, target_win_h)
                    _wx, _wy, view_w, view_h = cv2.getWindowImageRect(self.config.process_window_name)
                except cv2.error: pass 
                view_w, view_h = max(1, view_w), max(1, view_h)

                scaled_image_for_roi = cv2.resize(display_image, (scaled_w, scaled_h), interpolation=cv2.INTER_NEAREST)
                
                max_show_x = max(0, scaled_w - view_w)
                max_show_y = max(0, scaled_h - view_h)
                self.show_area[0] = max(0, min(self.show_area[0], max_show_x))
                self.show_area[1] = max(0, min(self.show_area[1], max_show_y))
                
                roi_x_start, roi_y_start = self.show_area[0], self.show_area[1]
                roi_w_actual = min(view_w, scaled_w - roi_x_start)
                roi_h_actual = min(view_h, scaled_h - roi_y_start)

                if roi_w_actual <= 0 or roi_h_actual <= 0:
                    print(f"Error: Invalid ROI dimensions for view in '{name}'.")
                    return None
                
                image_roi_content = scaled_image_for_roi[roi_y_start : roi_y_start + roi_h_actual, \
                                                         roi_x_start : roi_x_start + roi_w_actual]

                if image_roi_content.size == 0:
                    print(f"Error: View ROI content is empty for '{name}'.")
                    return None

                display_canvas = np.full((view_h, view_w, 3), 0, dtype=image_roi_content.dtype)
                paste_h, paste_w = image_roi_content.shape[:2]
                display_canvas[0:paste_h, 0:paste_w] = image_roi_content
                
                text_color_info = (220,220,220)
                text_base_y = display_canvas.shape[0] - 10
                cv2.putText(display_canvas, name, (10, 20), font, 0.6, text_color_info, font_thickness, cv2.LINE_AA)
                cv2.putText(display_canvas, self.mouse.bright_str, (10, max(35, text_base_y)), font, 0.6, text_color_info, font_thickness, cv2.LINE_AA)
                cv2.putText(display_canvas, f"Coords:{self.address}", (10, max(35, text_base_y - 20)), font, 0.6, text_color_info, font_thickness, cv2.LINE_AA)
                cv2.putText(display_canvas, f"Zoom:{self.size_ratio:.2f}", (10, max(35, text_base_y - 40)), font, 0.6, text_color_info, font_thickness, cv2.LINE_AA)
                
                if self.windows.windows_created and cv2.getWindowProperty(self.config.process_window_name, cv2.WND_PROP_VISIBLE) >=1:
                     cv2.imshow(self.config.process_window_name, display_canvas)
                return display_canvas, self.size_ratio, self.mouse.mouse_point
            except Exception as e:
                print(f"Error in _process_image_for_display for '{name}': {e}\n{traceback.format_exc()}")
                error_img = np.full((self.config.screen_height, self.config.screen_width, 3), 10, dtype=np.uint8)
                cv2.putText(error_img, f"Display Error: {name}", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1)
                if self.windows.windows_created and cv2.getWindowProperty(self.config.process_window_name, cv2.WND_PROP_VISIBLE) >=1:
                    cv2.imshow(self.config.process_window_name, error_img)
                return None
        except Exception as e:
            print(f"Error in _process_image_for_display: {e}")
            self._recover_from_error()
            return None

    def _recover_from_error(self):
        """Reset display state to safe defaults after encountering rendering errors.
        
        This error recovery method restores the ImageViewer display system to a
        known good state when image processing or rendering operations encounter
        errors. It resets zoom, pan, and cached data to prevent cascading failures
        and ensure the viewer remains functional.
        
        The recovery process includes:
        - Resetting zoom ratio to 1.0 (original size)
        - Repositioning view area to default screen bounds
        - Clearing cached scaled image data to force regeneration
        - Preparing the system for fresh rendering attempts
        
        This method is typically called internally when display operations fail,
        ensuring that temporary rendering issues don't permanently disable the
        viewer functionality. It provides a graceful degradation mechanism.
        
        Examples:
            >>> # Internal usage during error handling
            >>> try:
            ...     # Complex image processing that might fail
            ...     complex_rendering_operation()
            ... except Exception:
            ...     self._recover_from_error()  # Reset to safe state
            
        Performance:
            Time Complexity: O(1) - simple parameter reset operations.
            Space Complexity: O(1) - clears cached data, reducing memory usage.
        """
        self.size_ratio = 1.0
        self.show_area = [0, 0, self.config.screen_width, self.config.screen_height]
        self._cached_scaled_image = None

    def _show_text_window(self):
        """Display and update the text logging window with scrollable content.
        
        This method manages the text display window that shows logged messages with
        scrolling functionality. It handles dynamic window sizing, text rendering,
        scroll position management, and graceful error handling for window operations.
        
        The text window system includes:
        - Dynamic text image sizing based on content volume
        - Scrollable viewport with mouse wheel support
        - Automatic scroll position clamping and bounds checking
        - Text rendering with proper line spacing and formatting
        - Window state monitoring and error recovery
        - Memory-efficient text canvas management
        
        Key features:
        - Scroll position parameter: '_text_log_scroll_pos'
        - Dynamic resizing based on log content volume
        - Viewport clipping for performance with large logs
        - Safe window operations with NULL window detection
        - Automatic text canvas generation and display
        
        The method only operates when:
        - Debug/GUI mode is enabled
        - Windows have been successfully created
        - Text window display is enabled in configuration
        
        Handles OpenCV window errors gracefully, including window closure
        detection and NULL window conditions to prevent crashes.
        
        Performance:
            Time Complexity: O(h) where h is the viewport height for text rendering.
            Space Complexity: O(w*h) where w,h are text window dimensions.
        """
        if not self.config.enable_debug or not self.windows.windows_created: return
        if not self._show_text_window_enabled: return
        try:
            # Check if text window exists before trying to access it
            if cv2.getWindowProperty(self.config.text_window_name, cv2.WND_PROP_VISIBLE) < 0:
                return
            
            # Safely get window rectangle with error handling
            try:
                _x, _y, view_w, view_h = cv2.getWindowImageRect(self.config.text_window_name)
            except cv2.error as e:
                # Window was closed or destroyed, skip text window update
                if "NULL window" in str(e):
                    return
                raise  # Re-raise if it's a different error
            view_h = max(1, view_h) 
            text_img_h, text_img_w = self.text_image.shape[:2]
            max_scroll = max(0, text_img_h - view_h)
            scroll_param_name = "_text_log_scroll_pos"
            if scroll_param_name not in self.trackbar.parameters: self.trackbar.parameters[scroll_param_name] = 0 
            current_scroll = self.trackbar.parameters[scroll_param_name]
            current_scroll = max(0, min(current_scroll, max_scroll))
            self.trackbar.parameters[scroll_param_name] = current_scroll
            start_y, end_y = current_scroll, min(text_img_h, current_scroll + view_h)
            if start_y >= end_y or start_y < 0 or end_y > text_img_h :
                 text_roi_content = np.full((view_h, text_img_w, 3), 255, dtype=np.uint8)
            else:
                 text_roi_content = self.text_image[start_y:end_y, :]
            if text_roi_content.size == 0 or text_roi_content.shape[0] == 0:
                text_canvas = np.full((view_h, text_img_w, 3), 250, dtype=np.uint8)
            else:
                text_canvas = np.full((view_h, text_img_w, 3), 255, dtype=text_roi_content.dtype)
                paste_h, paste_w = text_roi_content.shape[:2]
                text_canvas[0:paste_h, 0:paste_w] = text_roi_content
            # Safely display text canvas with error handling
            try:
                cv2.imshow(self.config.text_window_name, text_canvas)
            except cv2.error as e:
                # Text window was closed or destroyed during operation
                if "NULL window" in str(e) or "window doesn't exist" in str(e):
                    return
                raise  # Re-raise if it's a different error
                
        except Exception as e: 
            print(f"CRITICAL: Text window display error: {e}\n{traceback.format_exc()}")


    def _mouse_callback(self, event: int, x: int, y: int, flags: int, userdata: Any):
        """Handle comprehensive mouse interactions for image navigation and ROI management.
        
        This comprehensive callback method processes all mouse interactions within the main
        image display window. It handles coordinate transformations, pixel value reading,
        interactive drawing (rectangles, lines, polygons), zoom/pan operations, and 
        multi-modal interaction states.
        
        Key functionality includes:
        - Coordinate transformation from view space to original image space
        - Real-time pixel value reading and display
        - Interactive ROI rectangle drawing with mouse drag
        - Line profile drawing for analysis
        - Polygon region definition with multi-point clicking
        - Zoom operations with mouse wheel (normal and Ctrl+wheel for fast zoom)
        - Pan operations with middle mouse button drag
        - Mode-specific interaction handling (rectangle/line/polygon modes)
        
        Mouse interaction modes:
        - Rectangle mode (default): Draw rectangular ROIs with left mouse drag
        - Line mode: Draw analysis lines with left mouse click-and-drag
        - Polygon mode: Multi-point polygon definition with left mouse clicks
        
        Mouse controls:
        - Left button: Draw ROIs/lines or add polygon points
        - Right button: Remove last drawn element or finish polygon
        - Right double-click: Clear all drawn elements
        - Middle button: Pan/scroll the image view
        - Mouse wheel: Zoom in/out (Ctrl+wheel for faster zoom)
        
        Coordinate system handling:
        - View coordinates: Mouse position within the display window
        - Scaled coordinates: Position on the scaled/zoomed image
        - Original coordinates: Position on the original full-resolution image
        
        Args:
            event: OpenCV mouse event type (EVENT_LBUTTONDOWN, EVENT_MOUSEMOVE, etc.)
            x: Mouse x-coordinate in view/window space
            y: Mouse y-coordinate in view/window space  
            flags: OpenCV event flags (modifier keys, button states)
            userdata: Additional user data (unused in this implementation)
            
        The method handles complex interaction states and ensures proper coordinate
        transformations, bounds checking, and integration with analysis systems.
        
        Performance:
            Time Complexity: O(1) for most operations, O(n) for polygon operations where n is points.
            Space Complexity: O(1) - updates existing data structures in place.
        """
        if not self.display_images or not self.current_image_dims : return
        orig_img_h, orig_img_w = self.current_image_dims
        if orig_img_h <= 0 or orig_img_w <= 0: return
        try:
            _wx, _wy, view_w, view_h = cv2.getWindowImageRect(self.config.process_window_name)
            if view_w <= 0 or view_h <= 0: return
        except cv2.error: return 
        x_view, y_view = max(0, min(x, view_w - 1)), max(0, min(y, view_h - 1))
        x_on_scaled_img, y_on_scaled_img = self.show_area[0] + x_view, self.show_area[1] + y_view
        current_size_ratio = self.size_ratio if abs(self.size_ratio) > 1e-6 else 1e-6
        ptr_x_orig, ptr_y_orig = int(x_on_scaled_img / current_size_ratio), int(y_on_scaled_img / current_size_ratio)
        ptr_x_orig, ptr_y_orig = max(0, min(ptr_x_orig, orig_img_w - 1)), max(0, min(ptr_y_orig, orig_img_h - 1))
        self.mouse.mouse_point, self.mouse.scale_ptr = (x_view, y_view), (ptr_x_orig, ptr_y_orig)
        self.address = f"({ptr_x_orig},{ptr_y_orig})"
        current_idx = max(0, min(self.trackbar.parameters.get('show', 0), len(self.display_images) - 1))
        if not (0 <= current_idx < len(self.display_images)): return
        image_data, _ = self.display_images[current_idx]
        if image_data is None or not isinstance(image_data, np.ndarray) or image_data.size == 0: return
        try:
            if 0 <= ptr_y_orig < image_data.shape[0] and 0 <= ptr_x_orig < image_data.shape[1]:
                pixel_value = image_data[ptr_y_orig, ptr_x_orig]
                if isinstance(pixel_value, np.ndarray): 
                    if len(pixel_value) >= 3: self.mouse.bright_str = f"BGR:({pixel_value[0]},{pixel_value[1]},{pixel_value[2]})"
                    elif len(pixel_value) == 1: self.mouse.bright_str = f"Gray:{int(pixel_value[0])}"
                    else: self.mouse.bright_str = "Pixel N/A"
                else: self.mouse.bright_str = f"Gray:{int(pixel_value)}"
            else: self.mouse.bright_str = "Out of Bounds"
        except IndexError: self.mouse.bright_str = "Pixel IndexErr"
        except Exception:  self.mouse.bright_str = "Pixel ReadErr"
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse.is_left_button_down = True
            self.mouse.left_button_start = (ptr_x_orig, ptr_y_orig)
            self.mouse.mouse_rect = None
            if self.mouse.is_polygon_mode:
                # If the user clicks near the first point, close the polygon
                if (len(self.mouse.current_polygon) > 2 and
                    np.linalg.norm(np.array(self.mouse.current_polygon[0]) - np.array((ptr_x_orig, ptr_y_orig))) < 10):
                    self.mouse.draw_polygons.append(self.mouse.current_polygon.copy())
                    pass
                    self.mouse.current_polygon.clear()
                    if self.analysis_window:
                        self.analysis_window.update_selectors()
                else:
                    self.mouse.current_polygon.append((ptr_x_orig, ptr_y_orig))
                    pass
            elif self.mouse.is_line_mode:
                self.mouse.line_start = (ptr_x_orig, ptr_y_orig)
        elif event == cv2.EVENT_LBUTTONUP:
            if self.mouse.is_left_button_down and self.mouse.left_button_start and not self.mouse.is_polygon_mode:
                if self.mouse.is_line_mode:
                    if self.mouse.line_start:
                        line_coords = (*self.mouse.line_start, ptr_x_orig, ptr_y_orig)
                        line_length = np.sqrt((ptr_x_orig - self.mouse.line_start[0])**2 + \
                                            (ptr_y_orig - self.mouse.line_start[1])**2)
                        if line_length > 5:
                            self.mouse.draw_lines.append(line_coords)
                            pass
                            if self.analysis_window:
                                self.analysis_window.update_selectors()
                else:
                    rect_x = min(self.mouse.left_button_start[0], ptr_x_orig)
                    rect_y = min(self.mouse.left_button_start[1], ptr_y_orig)
                    rect_w = abs(self.mouse.left_button_start[0] - ptr_x_orig)
                    rect_h = abs(self.mouse.left_button_start[1] - ptr_y_orig)
                    if rect_w > 0 and rect_h > 0:
                        self.mouse.draw_rects.append((rect_x, rect_y, rect_w, rect_h))
                        pass
                        if self.analysis_window:
                            self.analysis_window.update_selectors()
            self.mouse.is_left_button_down = False
            self.mouse.left_button_start = None
            self.mouse.mouse_rect = None
            self.mouse.line_start = None
            self.mouse.current_line = None
        elif event == cv2.EVENT_RBUTTONDOWN:
            if self.mouse.is_polygon_mode:
                if len(self.mouse.current_polygon) > 2:
                    self.mouse.draw_polygons.append(self.mouse.current_polygon.copy())
                    pass
                    self.mouse.current_polygon.clear()
                    if self.analysis_window:
                        self.analysis_window.update_selectors()
            elif self.mouse.is_line_mode:
                if self.mouse.draw_lines: 
                    removed_line = self.mouse.draw_lines.pop()
                    pass
                    if self.analysis_window:
                        self.analysis_window.update_selectors()
                self.mouse.current_line = None
            else:
                if self.mouse.draw_rects: 
                    removed_rect = self.mouse.draw_rects.pop()
                    pass
                    if self.analysis_window:
                        self.analysis_window.update_selectors()
        elif event == cv2.EVENT_RBUTTONDBLCLK:
            if self.mouse.is_polygon_mode:
                self.mouse.draw_polygons.clear()
                self.mouse.current_polygon.clear()
                pass
                if self.analysis_window:
                    self.analysis_window.update_selectors()
            elif self.mouse.is_line_mode:
                if self.mouse.draw_lines: 
                    self.mouse.draw_lines.clear()
                    pass
                    if self.analysis_window:
                        self.analysis_window.update_selectors()
                self.mouse.current_line = None
            else:
                if self.mouse.draw_rects: 
                    self.mouse.draw_rects.clear()
                    pass
                    if self.analysis_window:
                        self.analysis_window.update_selectors()
        elif event == cv2.EVENT_MBUTTONDOWN:
            self.mouse.is_middle_button_down = True
            self.mouse.middle_button_start = (x_view, y_view)
            self.mouse.middle_button_area_start = (self.show_area[0], self.show_area[1])
        elif event == cv2.EVENT_MBUTTONUP:
            self.mouse.is_middle_button_down = False
        elif event == cv2.EVENT_MOUSEWHEEL:
            delta = flags 
            ctrl_key = (flags & cv2.EVENT_FLAG_CTRLKEY) != 0
            zoom_factor = 1.15 if not ctrl_key else 1.40
            if delta > 0: self.size_ratio *= zoom_factor
            else: self.size_ratio /= zoom_factor
            self.size_ratio = max(self.config.min_size_ratio, min(self.size_ratio, self.config.max_size_ratio))
            self.show_area[0] = int(ptr_x_orig * self.size_ratio - x_view)
            self.show_area[1] = int(ptr_y_orig * self.size_ratio - y_view)
        if self.mouse.is_left_button_down and self.mouse.left_button_start:
            if self.mouse.is_line_mode and self.mouse.line_start:
                self.mouse.current_line = (*self.mouse.line_start, ptr_x_orig, ptr_y_orig)
            else:
                rect_x = min(self.mouse.left_button_start[0], ptr_x_orig)
                rect_y = min(self.mouse.left_button_start[1], ptr_y_orig)
                rect_w = abs(self.mouse.left_button_start[0] - ptr_x_orig)
                rect_h = abs(self.mouse.left_button_start[1] - ptr_y_orig)
                self.mouse.mouse_rect = (rect_x, rect_y, rect_w, rect_h)
        elif self.mouse.is_middle_button_down and self.mouse.middle_button_start and self.mouse.middle_button_area_start:
            dx = x_view - self.mouse.middle_button_start[0]
            dy = y_view - self.mouse.middle_button_start[1]
            self.show_area[0] = self.mouse.middle_button_area_start[0] - dx
            self.show_area[1] = self.mouse.middle_button_area_start[1] - dy

    def _text_mouse_callback(self, event: int, x: int, y: int, flags: int, userdata: Any):
        """Handle mouse interactions within the text logging window for scrolling control.
        
        This callback method specifically handles mouse interactions within the text
        display window, primarily focusing on mouse wheel scrolling functionality.
        It manages the scroll position parameter and provides smooth scrolling
        through logged messages.
        
        The scrolling system:
        - Uses internal parameter '_text_log_scroll_pos' to track scroll position
        - Responds to mouse wheel events for vertical scrolling
        - Applies bounds checking to prevent scrolling beyond content limits
        - Uses configurable scroll speed based on text line height
        - Maintains scroll position persistence across window updates
        
        Mouse wheel behavior:
        - Wheel up (positive delta): Scroll up/backward through log history
        - Wheel down (negative delta): Scroll down/forward through log history
        - Scroll amount: 3 text lines per wheel step for smooth navigation
        - Automatic clamping to valid scroll range [0, max_content_height]
        
        Args:
            event: OpenCV mouse event type (primarily EVENT_MOUSEWHEEL)
            x: Mouse x-coordinate in text window space (unused for scrolling)
            y: Mouse y-coordinate in text window space (unused for scrolling)
            flags: OpenCV event flags containing wheel delta information
            userdata: Additional user data (unused in this implementation)
            
        The scroll position is automatically used by _show_text_window() to
        determine which portion of the log content to display in the viewport.
        
        Performance:
            Time Complexity: O(1) - simple parameter updates and bounds checking.
            Space Complexity: O(1) - no additional memory allocation.
        """
        scroll_param_name = "_text_log_scroll_pos"
        if scroll_param_name not in self.trackbar.parameters: self.trackbar.parameters[scroll_param_name] = 0
        if event == cv2.EVENT_MOUSEWHEEL:
            delta = flags 
            scroll_amount = self.config.text_line_height * 3 
            current_scroll = self.trackbar.parameters.get(scroll_param_name, 0)
            if delta > 0: self.trackbar.parameters[scroll_param_name] = max(0, current_scroll - scroll_amount)
            else: self.trackbar.parameters[scroll_param_name] = current_scroll + scroll_amount

    def _process_tk_events(self):
        """Process Tkinter events safely in single-threaded architecture.
        
        This internal method handles Tkinter event processing for the analysis control
        window when it's available and active. It ensures that Tkinter GUI components
        remain responsive without blocking the main OpenCV event loop.
        
        The method operates in a fail-safe manner, silently handling any exceptions
        that might occur during Tkinter event processing to prevent crashes in the
        main application. This is particularly important when integrating different
        GUI frameworks (OpenCV and Tkinter) in a single-threaded application.
        
        The processing includes:
        - Updating idle tasks for the analysis window
        - Processing pending Tkinter events
        - Maintaining responsiveness of analysis controls
        
        This method only operates when:
        - Tkinter is available on the system
        - The analysis window exists and is active
        - The Tkinter root window is properly initialized
        
        Performance:
            Time Complexity: O(e) where e is the number of pending Tkinter events.
            Space Complexity: O(1) - no additional memory allocation.
        """
        try:
            if TKINTER_AVAILABLE and hasattr(self, 'analysis_window') and self.analysis_window and self.analysis_window.root:
                # Process tkinter events without blocking
                self.analysis_window.root.update_idletasks()
                self.analysis_window.root.update()
        except Exception:
            # Don't crash if tkinter events fail - just continue silently
            pass
            # Don't re-raise the exception to avoid crashing the application
    
    def get_drawn_rois(self) -> List[Tuple[int, int, int, int]]:
        """Get a copy of all user-drawn rectangular regions of interest (ROIs).
        
        Returns a list of all rectangular ROIs that have been drawn by the user
        through mouse interaction. Each ROI is represented as a tuple containing
        the rectangle coordinates in (x, y, width, height) format.
        
        Returns:
            List[Tuple[int, int, int, int]]: List of ROI rectangles where each tuple
                contains (x, y, width, height) coordinates in original image space.
                
        Examples:
            >>> viewer = ImageViewer.create_simple()
            >>> # User draws rectangles on the image
            >>> rois = viewer.get_drawn_rois()
            >>> for i, (x, y, w, h) in enumerate(rois):
            ...     print(f"ROI {i}: ({x}, {y}) size {w}x{h}")
        """
        return self.mouse.draw_rects.copy()
    
    def get_drawn_lines(self) -> List[Tuple[int, int, int, int]]:
        """Get a copy of all user-drawn lines for profile analysis.
        
        Returns a list of all lines that have been drawn by the user through
        mouse interaction. Each line is represented as a tuple containing the
        start and end coordinates in (x1, y1, x2, y2) format.
        
        Returns:
            List[Tuple[int, int, int, int]]: List of lines where each tuple contains
                (x1, y1, x2, y2) coordinates in original image space.
                
        Examples:
            >>> viewer = ImageViewer.create_simple()
            >>> # User draws lines on the image
            >>> lines = viewer.get_drawn_lines()
            >>> for i, (x1, y1, x2, y2) in enumerate(lines):
            ...     length = ((x2-x1)**2 + (y2-y1)**2)**0.5
            ...     print(f"Line {i}: ({x1}, {y1}) to ({x2}, {y2}), length: {length:.1f}")
        """
        return self.mouse.draw_lines.copy()

    def get_drawn_polygons(self) -> List[List[Tuple[int, int]]]:
        """Get a copy of all user-drawn polygonal regions for advanced analysis.
        
        Returns a list of all polygons that have been drawn by the user through
        mouse interaction. Each polygon is represented as a list of coordinate
        points defining the polygon boundary.
        
        Returns:
            List[List[Tuple[int, int]]]: List of polygons where each polygon is a
                list of (x, y) coordinate tuples in original image space.
                
        Examples:
            >>> viewer = ImageViewer.create_simple()
            >>> # User draws polygons on the image
            >>> polygons = viewer.get_drawn_polygons()
            >>> for i, polygon in enumerate(polygons):
            ...     print(f"Polygon {i}: {len(polygon)} vertices")
            ...     for j, (x, y) in enumerate(polygon):
            ...         print(f"  Vertex {j}: ({x}, {y})")
        """
        return self.mouse.draw_polygons.copy()

    def cleanup_viewer(self):
        """Perform comprehensive cleanup of all ImageViewer resources and subsystems.
        
        This method properly releases all resources associated with the ImageViewer,
        including OpenCV windows, analysis tools, image data, logging systems, and
        UI components. It ensures that all subsystems are properly shut down and
        resources are freed to prevent memory leaks and resource conflicts.
        
        The cleanup process includes:
        - Destroying all OpenCV windows and UI components
        - Shutting down analysis tools and plotting systems
        - Clearing image data and cached resources
        - Resetting logging systems and message deduplication
        - Stopping all background threads and processes
        - Setting termination flags to stop processing loops
        
        This method should always be called when finished with the ImageViewer,
        preferably in a try-finally block or using the context manager interface.
        
        Examples:
            >>> viewer = ImageViewer.create_simple()
            >>> try:
            ...     # Use viewer for processing
            ...     while viewer.should_loop_continue():
            ...         # Process images...
            ...         pass
            ... finally:
            ...     viewer.cleanup_viewer()
            
            >>> # Preferred: using context manager
            >>> with ImageViewer.create_simple() as viewer:
            ...     # Automatic cleanup on exit
            ...     pass
            
        Performance:
            Time Complexity: O(n) where n is the number of windows and resources to clean up.
            Space Complexity: O(1) - releases memory rather than allocating.
        """
        self.windows.destroy_all_windows()
        if self.analysis_window:
            self.analysis_window.destroy_window()
        # Use cleanup method instead of just close_all_plots to properly stop threading
        if hasattr(self.analyzer, 'cleanup'):
            self.analyzer.cleanup()
        else:
            self.analyzer.close_all_plots()  # Fallback for older analyzer versions
        self._internal_images.clear()
        self._cached_scaled_image = None
        self.text_image = None
        self.log_texts.clear()
        self.logged_messages.clear()  # Clear deduplication set on cleanup
        self._should_continue_loop = False

    def signal_params_changed(self):
        """Signal that trackbar parameters have changed and processing should be triggered.
        
        This method sets an internal flag indicating that trackbar parameter values
        have been modified and the image processing function should be re-executed
        with the new parameter values. This is typically called by trackbar callback
        functions to trigger reprocessing when users adjust trackbar values.
        
        The flag is used by the internal processing loops to determine when to
        call the user-provided image processor function with updated parameters,
        ensuring efficient processing that only occurs when parameters actually change.
        
        Examples:
            >>> # This is typically called internally by trackbar callbacks
            >>> def trackbar_callback(val):
            ...     viewer.signal_params_changed()  # Triggers reprocessing
            
            >>> # Can also be called manually to force reprocessing
            >>> viewer.signal_params_changed()
            >>> viewer.update_display()  # Will use new parameters
            
        Performance:
            Time Complexity: O(1) - simple flag assignment.
            Space Complexity: O(1) - no additional memory allocation.
        """
        self._params_changed = True

    def run_with_internal_loop(self, 
                       images_or_processor: Union[List[Tuple[np.ndarray, str]], Callable[[Dict[str, Any]], List[Tuple[np.ndarray, str]]]], 
                       title: str = ""):
        """Run a complete interactive loop with automatic window management and cleanup.
        
        This method provides a high-level interface for running the ImageViewer with
        either static images or a dynamic processing function. It handles complete
        setup, interactive loop execution, and automatic cleanup, making it ideal
        for standalone applications or quick prototyping.
        
        The method temporarily enables GUI mode regardless of the original configuration,
        creates all necessary windows and UI components, runs the interactive loop until
        the user quits, and then performs complete cleanup and restores the original
        debug state.
        
        Args:
            images_or_processor: Either a list of image tuples for static display,
                a callable function for dynamic processing, or a single numpy array.
                If callable, it should accept (params_dict) and return a list of
                (image, name) tuples.
            title: Optional title for single image display. Only used when
                images_or_processor is a single numpy array.
                
        Examples:
            >>> # Static image display
            >>> images = [(cv2.imread('image1.jpg'), "Image 1"), 
            ...           (cv2.imread('image2.jpg'), "Image 2")]
            >>> viewer.run_with_internal_loop(images)
            
            >>> # Dynamic processing with trackbars
            >>> def process_images(params):
            ...     threshold = params.get('threshold', 127)
            ...     # Apply processing...
            ...     return [(processed_image, f"Thresh: {threshold}")]
            >>> viewer.run_with_internal_loop(process_images)
            
            >>> # Single image with title
            >>> image = cv2.imread('test.jpg')
            >>> viewer.run_with_internal_loop(image, "Test Image")
            
        Performance:
            Time Complexity: O(f * p) where f is frames processed and p is processing time.
            Space Complexity: O(n) where n is the size of images in memory.
        """
        original_debug_state = self.config.enable_debug
        self.config.enable_debug = True

        self.clear_log()
        pass
        self._should_continue_loop = True 
        self._initialize_parameters()

        if callable(images_or_processor):
            self.image_processing_func_internal = images_or_processor
            self._params_changed = True 
        elif isinstance(images_or_processor, list):
            self._internal_images = [(img.copy(), name) for img, name in images_or_processor if isinstance(img, np.ndarray)]
        elif isinstance(images_or_processor, np.ndarray):
             self._internal_images = [(images_or_processor.copy(), title or "Image")]
        else:
            print(f"Error: `images_or_processor` type invalid for internal loop. Got {type(images_or_processor)}")
            self._internal_images = [(np.zeros((100,100,1), dtype=np.uint8), "Input Error")]

        if not self.windows.windows_created:
            self.windows.create_windows(self._mouse_callback, self._text_mouse_callback, self._show_text_window_enabled)
            if not self.windows.windows_created:
                print("FATAL: Failed to create OpenCV windows for internal loop.")
                self.config.enable_debug = original_debug_state
                return
        
        if self.image_processing_func_internal and self._params_changed:
            try:
                self._internal_images = self.image_processing_func_internal(dict(self.trackbar.parameters))
                self._params_changed = False
            except Exception as e:
                print(f"ERROR during initial image processing (internal loop): {e}\n{traceback.format_exc()}")
                self._internal_images = [(np.zeros((100,100,3), dtype=np.uint8), "Processing Error")]

        if self.config.trackbar:
            for trackbar_config_item in self.config.trackbar:
                self.trackbar.create_trackbar(trackbar_config_item, self)
        
        while self._should_continue_loop:
            if self.image_processing_func_internal and self._params_changed:
                try:
                    self._internal_images = self.image_processing_func_internal(dict(self.trackbar.parameters))
                    self._params_changed = False
                except Exception as e:
                    print(f"ERROR image re-processing (internal loop): {e}\n{traceback.format_exc()}")
                    self._params_changed = False
            self._process_frame_and_check_quit()
            if not self.windows.windows_created : self._should_continue_loop = False 
        
        self.cleanup_viewer()
        self.config.enable_debug = original_debug_state
        pass

    def register_event_handler(self, event_name: str, handler: Callable):
        """Register a custom event handler for ImageViewer events.
        
        This method allows registration of custom callback functions that will be
        triggered when specific events occur within the ImageViewer. This enables
        extensibility and custom behavior integration without modifying the core
        ImageViewer code.
        
        Args:
            event_name: String identifier for the event type. Common events might
                include 'parameter_changed', 'image_updated', 'roi_drawn', etc.
            handler: Callable function that will be invoked when the event occurs.
                The handler should accept variable arguments (*args, **kwargs) as
                different events may pass different parameters.
                
        Examples:
            >>> def on_parameter_change(param_name, old_value, new_value):
            ...     print(f"Parameter {param_name} changed from {old_value} to {new_value}")
            >>> 
            >>> viewer = ImageViewer.create_simple()
            >>> viewer.register_event_handler('parameter_changed', on_parameter_change)
            
            >>> def on_roi_drawn(roi_coords):
            ...     x, y, w, h = roi_coords
            ...     print(f"ROI drawn at ({x}, {y}) with size {w}x{h}")
            >>> viewer.register_event_handler('roi_drawn', on_roi_drawn)
            
        Performance:
            Time Complexity: O(1) - simple list append operation.
            Space Complexity: O(h) where h is the number of handlers for the event.
        """
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)
        
    def _trigger_event(self, event_name: str, *args, **kwargs):
        """Trigger all registered handlers for a specific event type.
        
        This internal method invokes all callback functions registered for a given
        event name, passing through any provided arguments and keyword arguments.
        It handles exceptions gracefully to prevent event handler errors from
        crashing the main application.
        
        Args:
            event_name: String identifier for the event type to trigger.
            *args: Variable positional arguments to pass to event handlers.
            **kwargs: Variable keyword arguments to pass to event handlers.
            
        Performance:
            Time Complexity: O(n) where n is the number of registered handlers.
            Space Complexity: O(1) - no additional memory allocation.
        """
        for handler in self._event_handlers.get(event_name, []):
            try:
                handler(*args, **kwargs)
            except Exception as e:
                print(f"Error in event handler: {e}")

    def get_current_state(self) -> Dict[str, Any]:
        """Get a snapshot of the current ImageViewer state for saving or restoration.
        
        This method captures the current viewing state including zoom level, pan position,
        mouse coordinates, and all parameter values. The returned state dictionary can
        be used to restore the exact viewing conditions later or to save user preferences.
        
        Returns:
            Dict[str, Any]: Dictionary containing current state information:
                - 'size_ratio': Current zoom/scale ratio
                - 'show_area': Current pan position as [x, y] offset
                - 'mouse_point': Last recorded mouse position
                - 'parameters': Copy of all current parameter values
                
        Examples:
            >>> viewer = ImageViewer.create_with_trackbars([
            ...     {"name": "Threshold", "param_name": "thresh", "max_value": 255}
            ... ])
            >>> # User adjusts view and parameters
            >>> state = viewer.get_current_state()
            >>> print(f"Zoom: {state['size_ratio']}")
            >>> print(f"Parameters: {state['parameters']}")
            >>> 
            >>> # Save state to file
            >>> import json
            >>> with open('viewer_state.json', 'w') as f:
            ...     json.dump(state, f)
            
        Performance:
            Time Complexity: O(n) where n is the number of parameters to copy.
            Space Complexity: O(n) for the state dictionary and parameter copies.
        """
        return {
            'size_ratio': self.size_ratio,
            'show_area': self.show_area.copy(),
            'mouse_point': self.mouse.mouse_point,
            'parameters': dict(self.trackbar.parameters)
        }
        
    def set_state(self, state: Dict[str, Any]):
        """Restore the ImageViewer to a previously saved state.
        
        This method restores viewing conditions and parameter values from a state
        dictionary created by get_current_state(). It updates zoom level, pan position,
        mouse coordinates, and all parameter values to match the saved state.
        
        Args:
            state: Dictionary containing state information with keys:
                - 'size_ratio': Zoom/scale ratio to restore
                - 'show_area': Pan position as [x, y] offset
                - 'mouse_point': Mouse position to restore
                - 'parameters': Parameter values to apply
                
        Examples:
            >>> # Restore from previously saved state
            >>> viewer = ImageViewer.create_with_trackbars([
            ...     {"name": "Threshold", "param_name": "thresh", "max_value": 255}
            ... ])
            >>> 
            >>> # Load and apply saved state
            >>> import json
            >>> with open('viewer_state.json', 'r') as f:
            ...     saved_state = json.load(f)
            >>> viewer.set_state(saved_state)
            >>> print(f"Restored zoom: {viewer.size_ratio}")
            
        Performance:
            Time Complexity: O(n) where n is the number of parameters to update.
            Space Complexity: O(1) - updates existing data structures in place.
        """
        self.size_ratio = state['size_ratio']
        self.show_area = state['show_area'].copy()
        self.mouse.mouse_point = state['mouse_point']
        self.trackbar.parameters.update(state['parameters'])

    def __enter__(self):
        """Enter the runtime context for the ImageViewer context manager.
        
        This method implements the context manager protocol, allowing the ImageViewer
        to be used with Python's 'with' statement. It returns the viewer instance
        for use within the context block.
        
        Returns:
            ImageViewer: The current ImageViewer instance for use in the context block.
            
        Examples:
            >>> with ImageViewer.create_simple() as viewer:
            ...     viewer.display_images = [(image, "Test")]
            ...     while viewer.should_loop_continue():
            ...         pass
            ...     # Automatic cleanup when exiting the 'with' block
        """
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context and perform cleanup.
        
        This method implements the context manager protocol exit handler,
        ensuring that all ImageViewer resources are properly cleaned up
        when exiting the 'with' statement block, regardless of whether
        an exception occurred.
        
        Args:
            exc_type: Exception type if an exception was raised, None otherwise.
            exc_val: Exception value if an exception was raised, None otherwise.
            exc_tb: Traceback object if an exception was raised, None otherwise.
            
        Returns:
            None: Does not suppress exceptions by returning None/False.
        """
        self.cleanup_viewer()

    @classmethod
    def create_simple(cls, enable_ui: bool = True, window_size: Tuple[int, int] = (800, 600)) -> 'ImageViewer':
        """Create a simple ImageViewer instance with minimal configuration.
        
        This factory method provides a convenient way to create an ImageViewer
        with basic settings suitable for simple image viewing scenarios. It
        creates a default configuration and instantiates the viewer without
        any trackbars or advanced features.
        
        Args:
            enable_ui: Whether to enable interactive GUI mode (True) or headless mode (False).
                GUI mode provides full interactive capabilities including windows and controls.
            window_size: Tuple specifying the main window dimensions as (width, height)
                in pixels. Must contain two positive integers.
                
        Returns:
            ImageViewer: A new ImageViewer instance configured for simple usage
                with default settings and no trackbars.
                
        Examples:
            >>> # Basic interactive viewer
            >>> viewer = ImageViewer.create_simple()
            >>> viewer.display_images = [(image, "My Image")]
            >>> while viewer.should_loop_continue():
            ...     pass
            >>> viewer.cleanup_viewer()
            
            >>> # Headless viewer for automation
            >>> viewer = ImageViewer.create_simple(enable_ui=False, window_size=(640, 480))
            
        Performance:
            Time Complexity: O(1) - constant time instantiation.
            Space Complexity: O(1) - fixed memory allocation for viewer instance.
        """
        config = ViewerConfig.create_simple(enable_ui, window_size)
        return cls(config)

    @classmethod
    def create_with_trackbars(cls, trackbars: List[Dict[str, Any]], enable_ui: bool = True) -> 'ImageViewer':
        """Create an ImageViewer instance with pre-configured trackbars for parameter control.
        
        This factory method creates an ImageViewer with trackbars already defined,
        making it ideal for interactive parameter tuning applications. The trackbars
        enable real-time adjustment of processing parameters with immediate visual
        feedback.
        
        Args:
            trackbars: List of trackbar configuration dictionaries. Each dictionary
                should contain the trackbar definition with keys:
                - 'name': Display name for the trackbar
                - 'param_name': Parameter name used in code
                - 'max_value': Maximum value for the trackbar
                - 'initial_value': Starting value (optional)
                - 'callback': Callback function name (optional)
            enable_ui: Whether to enable interactive GUI mode (True) or headless mode (False).
                GUI mode is recommended when using trackbars for interactive control.
                
        Returns:
            ImageViewer: A new ImageViewer instance with trackbars configured and ready
                for interactive parameter adjustment.
                
        Examples:
            >>> # Create viewer with parameter controls
            >>> trackbars = [
            ...     {"name": "Threshold", "param_name": "thresh", "max_value": 255, "initial_value": 127},
            ...     {"name": "Kernel Size", "param_name": "kernel", "max_value": 31, "initial_value": 5},
            ...     {"name": "Iterations", "param_name": "iterations", "max_value": 10, "initial_value": 1}
            ... ]
            >>> viewer = ImageViewer.create_with_trackbars(trackbars, enable_ui=True)
            >>> 
            >>> # Use with image processor function
            >>> def process_images(params, log_func):
            ...     thresh = params['thresh']
            ...     kernel = params['kernel']
            ...     iterations = params['iterations']
            ...     # Apply processing with current parameters
            ...     return [(processed_image, f"T={thresh}, K={kernel}")]
            >>> 
            >>> viewer.setup_viewer(image_processor_func=process_images)
            
        Performance:
            Time Complexity: O(n) where n is the number of trackbar configurations.
            Space Complexity: O(n) for storing trackbar definitions.
        """
        config = ViewerConfig.create_with_trackbars(trackbars, enable_ui)
        return cls(config)

    def add_trackbar_config(self, trackbar_config: Dict[str, Any]) -> 'ImageViewer':
        """Add a single trackbar configuration to the existing trackbar list.
        
        This method appends a new trackbar configuration to the current list of
        trackbars, enabling dynamic addition of parameter controls after viewer
        initialization. The trackbar will be created when setup_viewer() is called
        or during the next viewer initialization.
        
        Args:
            trackbar_config: Dictionary containing trackbar definition with keys:
                - 'name': Display name for the trackbar
                - 'param_name': Parameter name used in code
                - 'max_value': Maximum value for the trackbar
                - 'initial_value': Starting value (optional)
                - 'callback': Callback function name (optional)
                
        Returns:
            ImageViewer: Returns self for method chaining.
            
        Examples:
            >>> viewer = ImageViewer.create_simple()
            >>> viewer.add_trackbar_config({
            ...     "name": "Brightness", 
            ...     "param_name": "brightness", 
            ...     "max_value": 255,
            ...     "initial_value": 128
            ... })
            >>> viewer.add_trackbar_config({
            ...     "name": "Contrast", 
            ...     "param_name": "contrast", 
            ...     "max_value": 100
            ... })
            >>> viewer.setup_viewer()  # Creates both trackbars
            
        Performance:
            Time Complexity: O(1) - simple list append operation.
            Space Complexity: O(1) - single dictionary reference added.
        """
        self.config.trackbar.append(trackbar_config)
        return self

    def get_param(self, name: str, default: Any = None) -> Any:
        """Get the current value of a specific parameter.
        
        Retrieves the current value of a trackbar parameter by name. If the
        parameter doesn't exist, returns the specified default value.
        
        Args:
            name: The parameter name to retrieve (should match 'param_name' in trackbar config).
            default: Value to return if the parameter doesn't exist. Defaults to None.
            
        Returns:
            Any: The current parameter value, or the default value if not found.
            
        Examples:
            >>> viewer = ImageViewer.create_with_trackbars([
            ...     {"name": "Threshold", "param_name": "thresh", "max_value": 255}
            ... ])
            >>> threshold = viewer.get_param('thresh', 127)
            >>> print(f"Current threshold: {threshold}")
        """
        return self.trackbar.parameters.get(name, default)

    def set_param(self, name: str, value: Any) -> 'ImageViewer':
        """Set the value of a specific parameter with fluent interface support.
        
        Updates the value of a trackbar parameter and synchronizes it with the
        persistent values storage. This change will be reflected in the UI if
        the parameter has a corresponding trackbar.
        
        Args:
            name: The parameter name to set (should match 'param_name' in trackbar config).
            value: The new value to assign to the parameter.
            
        Returns:
            ImageViewer: Returns self for method chaining.
            
        Examples:
            >>> viewer = ImageViewer.create_with_trackbars([
            ...     {"name": "Threshold", "param_name": "thresh", "max_value": 255}
            ... ])
            >>> viewer.set_param('thresh', 150).set_param('kernel', 7)
        """
        self.trackbar.parameters[name] = value
        if name in self.trackbar.persistent_values:
            self.trackbar.persistent_values[name] = value
        return self

    def get_all_params(self) -> Dict[str, Any]:
        """Get a dictionary containing all current parameter values.
        
        Returns a copy of all current parameter values as a dictionary.
        This is useful for passing parameters to image processing functions
        or for saving/restoring parameter states.
        
        Returns:
            Dict[str, Any]: Dictionary mapping parameter names to their current values.
            
        Examples:
            >>> viewer = ImageViewer.create_with_trackbars([
            ...     {"name": "Threshold", "param_name": "thresh", "max_value": 255},
            ...     {"name": "Kernel", "param_name": "kernel", "max_value": 31}
            ... ])
            >>> params = viewer.get_all_params()
            >>> print(f"Current parameters: {params}")
            >>> # Use with image processor
            >>> processed = my_processor(params, viewer.log)
        """
        return dict(self.trackbar.parameters)

    def quick_setup(self, trackbars: List[Dict[str, Any]] = None, enable_ui: bool = True) -> 'ImageViewer':
        """Perform quick setup of the ImageViewer with optional trackbar configuration.
        
        This convenience method provides a streamlined way to configure and initialize
        the ImageViewer in a single call. It optionally sets trackbar configurations,
        configures the UI mode, and immediately calls setup_viewer() to prepare the
        viewer for use.
        
        Args:
            trackbars: Optional list of trackbar configuration dictionaries.
                If provided, replaces any existing trackbar configurations.
                Each dictionary should contain trackbar definition fields.
            enable_ui: Whether to enable interactive GUI mode (True) or headless mode (False).
                
        Returns:
            ImageViewer: Returns self for method chaining.
            
        Examples:
            >>> # Quick setup with trackbars
            >>> trackbars = [
            ...     {"name": "Threshold", "param_name": "thresh", "max_value": 255},
            ...     {"name": "Blur", "param_name": "blur", "max_value": 31}
            ... ]
            >>> viewer = ImageViewer().quick_setup(trackbars, enable_ui=True)
            >>> # Ready to use immediately
            
            >>> # Quick setup without trackbars
            >>> viewer = ImageViewer().quick_setup(enable_ui=True)
            
        Performance:
            Time Complexity: O(n + s) where n is trackbar count and s is setup time.
            Space Complexity: O(n) for trackbar storage.
        """
        if trackbars:
            self.config.trackbar = trackbars
        self.config.enable_debug = enable_ui
        self.setup_viewer()
        return self

    def run_simple_loop(self, image_processor: Optional[ImageProcessor] = None) -> Dict[str, Any]:
        """Run a simple processing loop until termination, returning final parameter values.
        
        This method provides a lightweight alternative to run_with_internal_loop() for
        scenarios where you want to run a processing loop without automatic window
        creation and cleanup. It uses the existing viewer configuration and windows,
        making it suitable for cases where setup has already been performed separately.
        
        The loop continues until the user closes windows (in GUI mode) or the maximum
        iterations are reached (in headless mode). It handles keyboard interrupts
        gracefully and always returns the final parameter values.
        
        Args:
            image_processor: Optional ImageProcessor function to use for generating
                images based on current parameters. If provided, it replaces any
                existing processor function for this loop.
                
        Returns:
            Dict[str, Any]: Dictionary containing final parameter values when the
                loop terminates, useful for saving user preferences or configurations.
                
        Examples:
            >>> # Simple loop with existing setup
            >>> viewer = ImageViewer.create_with_trackbars(trackbars)
            >>> viewer.setup_viewer()
            >>> final_params = viewer.run_simple_loop()
            >>> print(f"Final parameters: {final_params}")
            
            >>> # Loop with new processor
            >>> def my_processor(params, log_func):
            ...     # Process with current parameters
            ...     return [(result_image, "Processed")]
            >>> final_params = viewer.run_simple_loop(my_processor)
            
            >>> # Use returned parameters for batch processing
            >>> batch_process_images(final_params)
            
        Performance:
            Time Complexity: O(f * p) where f is frames processed and p is processing time.
            Space Complexity: O(1) additional space beyond existing allocations.
        """
        if image_processor:
            self.user_image_processor = image_processor

        try:
            while self.should_loop_continue():
                if self.user_image_processor:
                    self.update_display()
                elif self.config.enable_debug:
                    self._process_frame_and_check_quit()
                    
                if not self.config.enable_debug:
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            return self.get_all_params()
