"""Plotting and analysis visualization functionality for the Parameter project.

This module provides comprehensive plotting capabilities for image analysis including
pixel profiles and histograms. It handles matplotlib backend detection and compatibility
with OpenCV applications, providing both interactive and non-interactive plotting modes.

The module automatically detects the runtime environment and selects appropriate
matplotlib backends to prevent conflicts between OpenCV and matplotlib GUI systems.
It supports both standard matplotlib display and OpenCV window display for plots.

Main Classes:
    PlotAnalyzer: Handles creation and management of analysis plots

Main Functions:
    _test_matplotlib_backend: Tests matplotlib backend compatibility
    _detect_opencv_context: Detects OpenCV application environment
    _check_pyqt5_conflict: Checks for PyQt5 installation conflicts

Usage:
    analyzer = PlotAnalyzer()
    analyzer.create_histogram_plot(image, title="Image Histogram")
    analyzer.create_pixel_profile_plot(image, (x1, y1, x2, y2), "Pixel Profile")
"""

import cv2
import numpy as np
import os
import json
import io
from typing import List, Tuple, Optional, Dict, Any

def _test_matplotlib_backend(backend_name: str) -> bool:
    """Test if a matplotlib backend actually works by creating a test figure.
    
    This function attempts to initialize a matplotlib backend and create a test
    figure to verify that the backend is functional. This is necessary because
    some backends may be installed but not properly configured.
    
    Args:
        backend_name: Name of the matplotlib backend to test (e.g., 'Qt5Agg', 'TkAgg', 'Agg').
        
    Returns:
        bool: True if the backend works correctly, False otherwise.
        
    Examples:
        >>> if _test_matplotlib_backend('Qt5Agg'):
        ...     print("Qt5Agg backend is available")
        
    Performance:
        Time Complexity: O(1) - constant time backend test.
        Space Complexity: O(1) - minimal memory for test figure.
    """
    try:
        import matplotlib
        matplotlib.use(backend_name, force=True)
        import matplotlib.pyplot as plt
        
        # Actually test if we can create a figure with this backend
        fig = plt.figure(figsize=(1, 1))
        fig.canvas.draw()
        plt.close(fig)
        return True
    except Exception:
        return False

def _detect_opencv_context() -> bool:
    """Detect if we're running in an OpenCV application context.
    
    This function checks whether OpenCV is available and imported, which
    indicates that we're likely running within an OpenCV-based application.
    This detection helps choose appropriate matplotlib backends that won't
    conflict with OpenCV's event handling.
    
    Returns:
        bool: True if OpenCV context is detected, False otherwise.
        
    Examples:
        >>> if _detect_opencv_context():
        ...     print("Running in OpenCV application")
        
    Performance:
        Time Complexity: O(1) - simple import check.
        Space Complexity: O(1) - no additional memory usage.
    """
    try:
        import cv2
        # Check if OpenCV is imported (strong indicator we're in OpenCV app)
        return True
    except ImportError:
        return False

def _check_pyqt5_conflict() -> bool:
    """Check if PyQt5 is installed and warn about potential OpenCV conflicts.
    
    This function detects the presence of PyQt5, which can cause threading
    conflicts when used together with OpenCV applications. The combination
    of PyQt5 and OpenCV can lead to GIL (Global Interpreter Lock) threading
    errors in matplotlib plotting.
    
    Returns:
        bool: True if PyQt5 is installed, False otherwise.
        
    Examples:
        >>> if _check_pyqt5_conflict():
        ...     print("PyQt5 detected - potential OpenCV conflicts")
        
    Performance:
        Time Complexity: O(1) - simple import check.
        Space Complexity: O(1) - no additional memory usage.
    """
    try:
        import PyQt5
        return True
    except ImportError:
        return False

try:
    import matplotlib
    import matplotlib.pyplot as plt
    import threading
    from queue import Queue
    
    # Check if we're in an OpenCV application context
    opencv_detected = _detect_opencv_context()
    pyqt5_installed = _check_pyqt5_conflict()
    
    # Check for dangerous PyQt5 + OpenCV combination
    if opencv_detected and pyqt5_installed:
        # PyQt5 + OpenCV causes fatal GIL threading errors
        # Use Agg backend with cv2.imshow display instead
        pass
    
    if opencv_detected:
        # In OpenCV applications, ALL interactive backends conflict with cv2.waitKey()!
        # Even TkAgg creates Tkinter event loops that cause GIL threading errors
        # Solution: Use Agg backend + display plots via OpenCV windows
        backends_to_try = [
            ('Agg', 'Agg (OpenCV-compatible - plots displayed via cv2.imshow)')
        ]
    else:
        # In non-OpenCV applications, prefer Qt backends
        backends_to_try = [
            ('Qt5Agg', 'Qt5Agg (recommended)'),
            ('Qt4Agg', 'Qt4Agg'),
            ('TkAgg', 'TkAgg (with threading protection)'),
            ('Agg', 'Agg (non-interactive)')
        ]
    
    backend_tried = None
    working_backend = None
    
    for backend_name, description in backends_to_try:
        if _test_matplotlib_backend(backend_name):
            working_backend = backend_name
            backend_tried = description
            break
    
    if working_backend is None:
        raise ImportError("No working matplotlib backend found")
    
    # Set the working backend
    matplotlib.use(working_backend, force=True)
    
    # Set the working backend (removed debug print)
    
    # Backend info and warnings (removed debug output)
    # Different backends have different compatibility with OpenCV
    # but we suppress the startup messages to reduce console noise
    
    MATPLOTLIB_AVAILABLE = True
    
except ImportError as e:
    MATPLOTLIB_AVAILABLE = False
    print(f"Warning: matplotlib not available ({e}). Pixel profile and histogram features will be disabled.")

class PlotAnalyzer:
    """Handles image analysis plotting features including pixel profiles and histograms.
    
    This class provides comprehensive plotting capabilities for image analysis tasks.
    It automatically handles matplotlib backend compatibility with OpenCV applications,
    manages thread-safe plotting operations, and provides both interactive and
    non-interactive plotting modes.
    
    The class supports:
    - Histogram plotting for color and grayscale images
    - Pixel intensity profile plotting along lines
    - ROI (Region of Interest) and polygon-based analysis
    - Automatic backend selection for OpenCV compatibility
    - Plot export functionality with high-quality rendering
    - Thread-safe plotting operations to prevent GUI conflicts
    
    Attributes:
        CONFIG_FILE (str): Path to the plot settings configuration file
        plot_windows (Dict): Dictionary tracking open matplotlib plot windows
        plot_settings (Dict): Current plot styling and configuration settings
        _plot_thread (Thread): Background thread for safe plotting operations
        _plot_queue (Queue): Queue for thread-safe plot requests
        _thread_lock (Lock): Threading lock for synchronization
        _plotting_active (bool): Flag indicating if plotting thread is active
        _current_backend (str): Currently active matplotlib backend
        _is_tkinter_backend (bool): Whether using TkAgg backend
        _is_agg_backend (bool): Whether using Agg (non-interactive) backend
        _opencv_detected (bool): Whether OpenCV context was detected
    
    Examples:
        >>> analyzer = PlotAnalyzer()
        >>> histogram_data = analyzer.calculate_histogram(image)
        >>> analyzer.create_histogram_plot(image, title="Image Analysis")
        >>> profile_data = analyzer.calculate_pixel_profile(image, (x1, y1, x2, y2))
        >>> analyzer.create_pixel_profile_plot(image, (x1, y1, x2, y2), "Line Profile")
    """
    
    CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".parameter_plot_settings.json")
    
    def __init__(self):
        """Initialize the PlotAnalyzer with backend detection and configuration.
        
        Sets up the plotting system by detecting the runtime environment,
        configuring appropriate matplotlib backends, initializing threading
        components for safe plotting, and loading user plot settings.
        
        The initialization process:
        1. Detects matplotlib availability and OpenCV context
        2. Sets up thread-safe plotting infrastructure
        3. Determines optimal backend configuration
        4. Loads user plot styling preferences
        
        Raises:
            ImportError: If matplotlib is not available and plotting is attempted.
            
        Examples:
            >>> analyzer = PlotAnalyzer()
            >>> print(f"Using backend: {analyzer._current_backend}")
            >>> print(f"OpenCV detected: {analyzer._opencv_detected}")
        """
        self.plot_windows = {}  # Track open matplotlib windows
        self.plot_settings = self._load_plot_settings()
        self._plot_thread = None
        self._plot_queue = Queue() if MATPLOTLIB_AVAILABLE else None
        self._thread_lock = threading.Lock() if MATPLOTLIB_AVAILABLE else None
        self._plotting_active = False
        
        # Store which backend we're using for special handling
        self._current_backend = matplotlib.get_backend() if MATPLOTLIB_AVAILABLE else None
        self._is_tkinter_backend = self._current_backend == 'TkAgg' if MATPLOTLIB_AVAILABLE else False
        self._is_agg_backend = self._current_backend == 'Agg' if MATPLOTLIB_AVAILABLE else False
        self._opencv_detected = _detect_opencv_context() if MATPLOTLIB_AVAILABLE else False
        
    def _figure_to_opencv_image(self, fig) -> Optional[np.ndarray]:
        """Convert matplotlib figure to high-quality OpenCV image for display.
        
        This method converts a matplotlib figure to an OpenCV-compatible image format
        for display in OpenCV windows. It uses high-quality rendering settings to
        ensure sharp text and lines, applies anti-aliasing, and returns the image
        in BGR format suitable for cv2.imshow().
        
        Args:
            fig: Matplotlib figure object to convert.
            
        Returns:
            Optional[np.ndarray]: OpenCV image in BGR format, or None if conversion fails.
                The image is optimized for display with high DPI and anti-aliasing.
                
        Examples:
            >>> fig, ax = plt.subplots()
            >>> ax.plot([1, 2, 3], [1, 4, 2])
            >>> opencv_img = analyzer._figure_to_opencv_image(fig)
            >>> if opencv_img is not None:
            ...     cv2.imshow("Plot", opencv_img)
            
        Performance:
            Time Complexity: O(n) where n is the number of pixels in the figure.
            Space Complexity: O(n) for the image buffer and decoded image.
        """
        try:
            # Save figure to memory buffer with high quality settings
            buf = io.BytesIO()
            fig.savefig(
                buf, 
                format='png', 
                dpi=200,  # Increased DPI for much sharper text and lines
                bbox_inches='tight',
                facecolor='white',  # Ensure white background
                edgecolor='none',
                pad_inches=0.1,  # Small padding for better appearance
                pil_kwargs={'compress_level': 1}  # Minimal compression for best quality
            )
            buf.seek(0)
            
            # Read as numpy array
            img_array = np.frombuffer(buf.getvalue(), dtype=np.uint8)
            
            # Decode as OpenCV image (this gives us BGR format)
            opencv_image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            # Optional: Apply slight anti-aliasing for smoother text and lines
            if opencv_image is not None and opencv_image.size > 0:
                # Apply mild Gaussian blur to reduce any aliasing artifacts
                # This makes text and lines appear smoother
                opencv_image = cv2.GaussianBlur(opencv_image, (0, 0), 0.3)
            
            buf.close()
            return opencv_image
            
        except Exception as e:
            print(f"Error converting matplotlib figure to OpenCV image: {e}")
            return None
        
    def _load_plot_settings(self) -> Dict[str, Any]:
        """Load plot settings from configuration file with fallback defaults.
        
        This method loads user-customized plot settings from a JSON configuration file
        stored in the user's home directory. If the file doesn't exist or contains
        errors, it returns comprehensive default settings for both histogram and
        profile plots including styling, colors, and layout preferences.
        
        Returns:
            Dict[str, Any]: Dictionary containing plot settings with keys:
                - 'histogram_settings': Settings for histogram plots
                - 'profile_settings': Settings for profile plots  
                - 'presets': User-defined plot presets
                Each settings dict contains figure_size, dpi, colors, fonts, etc.
                
        Examples:
            >>> analyzer = PlotAnalyzer()
            >>> settings = analyzer._load_plot_settings()
            >>> print(f"Figure size: {settings['histogram_settings']['figure_size']}")
            >>> print(f"Line width: {settings['profile_settings']['line_width']}")
            
        Performance:
            Time Complexity: O(1) - simple file read and JSON parse.
            Space Complexity: O(1) - fixed-size configuration dictionary.
        """
        default_settings = {
            "histogram_settings": {
                "figure_size": (12, 7),  # Larger figure for better quality
                "dpi": 150,  # Higher DPI for matplotlib rendering
                "grid": True,
                "grid_alpha": 0.3,
                "title_fontsize": 16,  # Larger fonts for better readability
                "axis_fontsize": 14,
                "line_width": 2.5,  # Slightly thicker lines
                "line_alpha": 0.9,  # Less transparency for cleaner appearance
                "show_legend": True,
                "colors": {
                    "blue": "#051B7C",    # Professional blue
                    "green": "#2ca02c",   # Professional green  
                    "red": "#d62728",     # Professional red
                    "gray": "#2c2c2c"     # Dark gray instead of black
                }
            },
            "profile_settings": {
                "figure_size": (12, 7),  # Larger figure for better quality
                "dpi": 150,  # Higher DPI for matplotlib rendering
                "grid": True,
                "grid_alpha": 0.3,
                "title_fontsize": 16,  # Larger fonts for better readability
                "axis_fontsize": 14,
                "line_width": 2.5,  # Slightly thicker lines
                "line_alpha": 0.9,  # Less transparency for cleaner appearance
                "show_legend": True,
                "colors": {
                    "blue": "#051B7C",    # Professional blue
                    "green": "#2ca02c",   # Professional green
                    "red": "#d62728",     # Professional red
                    "gray": "#2c2c2c"     # Dark gray instead of black
                }
            },
            "presets": {}
        }
        
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    settings = json.load(f)
                    
                # Ensure all required settings exist by merging with defaults
                if "histogram_settings" not in settings:
                    settings["histogram_settings"] = default_settings["histogram_settings"]
                if "profile_settings" not in settings:
                    settings["profile_settings"] = default_settings["profile_settings"]
                if "presets" not in settings:
                    settings["presets"] = {}
                    
                return settings
            return default_settings
        except Exception:
            # If there's any error loading settings, return defaults
            return default_settings
            
    def update_plot_settings(self, plot_type: str, settings: Dict[str, Any]) -> None:
        """Update plot settings for the specified plot type and save to configuration.
        
        This method updates the plot settings for either histogram or profile plots
        and automatically saves the updated configuration to the user's settings file.
        The settings are immediately available for subsequent plot operations.
        
        Args:
            plot_type: Type of plot to update settings for. Should be either
                'histogram' or 'profile'.
            settings: Dictionary containing the new settings to apply. Should include
                keys like 'figure_size', 'dpi', 'colors', 'line_width', etc.
                
        Examples:
            >>> new_settings = {
            ...     'figure_size': (10, 6),
            ...     'dpi': 120,
            ...     'line_width': 3.0,
            ...     'colors': {'red': '#FF0000', 'blue': '#0000FF'}
            ... }
            >>> analyzer.update_plot_settings('histogram', new_settings)
            
        Performance:
            Time Complexity: O(1) - dictionary update and file write.
            Space Complexity: O(1) - settings dictionary storage.
        """
        self.plot_settings[f"{plot_type}_settings"] = settings
        
        # Save settings to file
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.plot_settings, f, indent=2)
        except Exception as e:
            print(f"Error saving plot settings: {e}")
    
    def _plot_worker(self) -> None:
        """Worker thread for handling matplotlib operations safely in background.
        
        This method runs in a separate thread to handle matplotlib plotting operations
        that might conflict with OpenCV's event handling. It processes plot requests
        from a queue and executes them safely, preventing GUI threading conflicts
        that can occur when matplotlib and OpenCV run in the same application.
        
        The worker thread:
        1. Continuously monitors the plot request queue
        2. Processes histogram and profile plot requests
        3. Handles thread-safe matplotlib operations
        4. Provides proper cleanup and error handling
        
        Note:
            This method is intended for internal use only and runs automatically
            when the plotting thread is started.
            
        Examples:
            >>> # This method runs automatically when plot thread starts
            >>> analyzer._start_plot_thread()  # Starts worker thread
            
        Performance:
            Time Complexity: O(∞) - runs continuously until stopped.
            Space Complexity: O(1) - minimal memory for queue processing.
        """
        # Plot worker thread started
        while self._plotting_active:
            try:
                try:
                    # Waiting for plot request...
                    plot_request = self._plot_queue.get(timeout=0.5)
                    if plot_request is None:  # Shutdown signal
                        # Received shutdown signal
                        break
                    
                    # Processing plot request
                    plot_type = plot_request['type']
                    if plot_type == 'histogram':
                        self._create_histogram_plot_internal(**plot_request['args'])
                    elif plot_type == 'profile':
                        self._create_pixel_profile_plot_internal(**plot_request['args'])
                    
                    self._plot_queue.task_done()
                    # Plot request completed
                except:
                    # Queue was empty or timeout occurred, continue checking
                    threading.Event().wait(0.1)  # Small delay when queue is empty
                    
            except Exception as e:
                print(f"Plot worker error: {e}")
                # Continue running even if there's an error
                threading.Event().wait(0.1)
        # Plot worker thread ended
    
    def _start_plot_thread(self) -> None:
        """Start the plotting thread if not already running.
        
        This method initializes and starts a background worker thread for handling
        matplotlib plotting operations safely. The thread is only started if matplotlib
        is available and no plotting thread is currently active. This prevents
        threading conflicts between matplotlib and OpenCV GUI operations.
        
        The method uses thread-safe locking to ensure only one plotting thread
        runs at a time and properly initializes the worker thread as a daemon
        thread that will automatically terminate when the main application exits.
        
        Examples:
            >>> analyzer = PlotAnalyzer()
            >>> analyzer._start_plot_thread()  # Start background plotting
            >>> # Now safe to queue plot operations
            
        Performance:
            Time Complexity: O(1) - simple thread initialization.
            Space Complexity: O(1) - minimal thread overhead.
        """
        if not MATPLOTLIB_AVAILABLE:
            return
            
        with self._thread_lock:
            if not self._plotting_active:
                self._plotting_active = True
                self._plot_thread = threading.Thread(target=self._plot_worker, daemon=True)
                self._plot_thread.start()
    
    def _stop_plot_thread(self) -> None:
        """Stop the plotting thread and clean up resources.
        
        This method safely stops the background plotting thread by setting the
        termination flag, sending a shutdown signal through the queue, and waiting
        for the thread to complete. It includes proper cleanup with timeout handling
        to prevent hanging if the thread doesn't respond promptly.
        
        The method:
        1. Sets the plotting_active flag to False
        2. Sends None as a shutdown signal to the queue
        3. Waits up to 2 seconds for thread termination
        4. Uses thread-safe locking for coordination
        
        Examples:
            >>> analyzer = PlotAnalyzer()
            >>> analyzer._start_plot_thread()
            >>> # ... do some plotting work ...
            >>> analyzer._stop_plot_thread()  # Clean shutdown
            
        Performance:
            Time Complexity: O(1) - bounded by 2-second timeout.
            Space Complexity: O(1) - no additional memory usage.
        """
        if not MATPLOTLIB_AVAILABLE:
            return
            
        with self._thread_lock:
            if self._plotting_active:
                self._plotting_active = False
                if self._plot_queue:
                    self._plot_queue.put(None)  # Shutdown signal
                if self._plot_thread and self._plot_thread.is_alive():
                    self._plot_thread.join(timeout=2)
    
    def create_pixel_profile_plot(self, image: np.ndarray, line_coords: Tuple[int, int, int, int], title: str = "Pixel Profile") -> None:
        """Create a pixel intensity profile plot along a line.
        
        This method generates a plot showing pixel intensity values along a specified
        line in the image. For color images, it plots separate curves for each channel
        (red, green, blue). For grayscale images, it plots a single intensity curve.
        The plot shows distance along the line on the x-axis and pixel intensity values
        on the y-axis.
        
        The method automatically handles backend compatibility with OpenCV applications
        by using appropriate threading or direct execution based on the detected
        environment and matplotlib backend.
        
        Args:
            image: Input image as numpy array (either color or grayscale).
            line_coords: Tuple of (x1, y1, x2, y2) defining the line endpoints
                in pixel coordinates.
            title: Title for the plot. Defaults to "Pixel Profile".
            
        Examples:
            >>> analyzer = PlotAnalyzer()
            >>> # Create profile from top-left to bottom-right
            >>> analyzer.create_pixel_profile_plot(image, (0, 0, 100, 100), "Diagonal Profile")
            >>> # Create horizontal profile across image center
            >>> h, w = image.shape[:2]
            >>> analyzer.create_pixel_profile_plot(image, (0, h//2, w-1, h//2), "Horizontal Profile")
            
        Performance:
            Time Complexity: O(n) where n is the length of the line in pixels.
            Space Complexity: O(n) for storing pixel values along the line.
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for pixel profile plotting")
            return
        
        # For OpenCV + Agg backend, run directly in main thread (no GUI conflicts)
        if self._opencv_detected and self._is_agg_backend:
            # Using Agg backend with OpenCV - direct main thread execution
            self._create_pixel_profile_plot_internal(image.copy(), line_coords, title)
            return
        
        # For other combinations, use threading
        if self._opencv_detected or self._current_backend in ['TkAgg']:
            # Use threading for problematic combinations
            self._start_plot_thread()
            
            plot_request = {
                'type': 'profile',
                'args': {
                    'image': image.copy(),
                    'line_coords': line_coords,
                    'title': title
                }
            }
            
            try:
                self._plot_queue.put(plot_request, timeout=5)
            except Exception as e:
                print(f"Failed to queue profile plot: {e}")
        else:
            # Non-OpenCV Qt backends can run in main thread
            self._create_pixel_profile_plot_internal(image.copy(), line_coords, title)
    
    def _create_pixel_profile_plot_internal(self, image: np.ndarray, line_coords: Tuple[int, int, int, int], title: str = "Pixel Profile") -> None:
        """Internal method for creating pixel profile plots with thread-safe execution.
        
        This internal method handles the actual matplotlib plotting operations for pixel
        intensity profiles. It runs in either the main thread or a worker thread depending
        on the backend configuration and OpenCV compatibility requirements. The method
        creates high-quality plots with customizable styling and handles both interactive
        and non-interactive display modes.
        
        The method performs the following operations:
        1. Extracts pixel values along the specified line using Bresenham's algorithm
        2. Calculates distances from the line start point
        3. Creates matplotlib figure with user-configured styling
        4. Plots separate curves for each color channel (or single curve for grayscale)
        5. Handles display based on backend type (matplotlib vs OpenCV windows)
        6. Stores plot references for later access and cleanup
        
        Args:
            image: Input image as numpy array (color or grayscale).
            line_coords: Tuple of (x1, y1, x2, y2) defining line endpoints in pixel coordinates.
            title: Title for the plot display. Defaults to "Pixel Profile".
            
        Note:
            This method is for internal use only and should not be called directly.
            Use create_pixel_profile_plot() instead for public API access.
            
        Examples:
            >>> # Internal usage (not recommended for direct calls)
            >>> analyzer._create_pixel_profile_plot_internal(image, (0, 0, 100, 100), "Internal Profile")
            
        Performance:
            Time Complexity: O(n + m) where n is line length and m is plot rendering.
            Space Complexity: O(n) for pixel values and plot data structures.
        """
        if not MATPLOTLIB_AVAILABLE:
            return
        
        try:
            x1, y1, x2, y2 = line_coords
            
            points = self._get_line_points(x1, y1, x2, y2)
            
            if image is None or image.size == 0:
                print("Invalid image for profile plotting")
                return
            
            valid_points = [(x, y) for x, y in points if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]]
            
            if len(valid_points) < 2:
                print("Not enough valid points for profile")
                return
            
            distances = [np.sqrt((p[0] - x1)**2 + (p[1] - y1)**2) for p in valid_points]
            
            # Get plot settings
            settings = self.plot_settings.get("profile_settings", {})
            figure_size = settings.get("figure_size", (10, 6))
            dpi = settings.get("dpi", 100)
            grid = settings.get("grid", True)
            grid_alpha = settings.get("grid_alpha", 0.3)
            title_fontsize = settings.get("title_fontsize", 14)
            axis_fontsize = settings.get("axis_fontsize", 12)
            line_width = settings.get("line_width", 2)
            line_alpha = settings.get("line_alpha", 0.8)
            show_legend = settings.get("show_legend", True)
            colors = settings.get("colors", {
                "blue": "#0000FF",
                "green": "#00FF00",
                "red": "#FF0000",
                "gray": "#000000"
            })
            
            # Create figure with custom size and DPI
            fig, ax = plt.subplots(figsize=figure_size, dpi=dpi)
            
            if len(image.shape) == 3:  # Color image
                blue_values = [image[p[1], p[0], 0] for p in valid_points]
                green_values = [image[p[1], p[0], 1] for p in valid_points]
                red_values = [image[p[1], p[0], 2] for p in valid_points]
                
                ax.plot(distances, blue_values, color=colors.get("blue", "#0000FF"), 
                       label='Blue', linewidth=line_width, alpha=line_alpha)
                ax.plot(distances, green_values, color=colors.get("green", "#00FF00"), 
                       label='Green', linewidth=line_width, alpha=line_alpha)
                ax.plot(distances, red_values, color=colors.get("red", "#FF0000"), 
                       label='Red', linewidth=line_width, alpha=line_alpha)
                
                if show_legend:
                    ax.legend()
                
            else:  # Grayscale image
                gray_values = [image[p[1], p[0]] for p in valid_points]
                ax.plot(distances, gray_values, color=colors.get("gray", "#000000"), 
                       linewidth=line_width, alpha=line_alpha, label='Intensity')
                
                if show_legend:
                    ax.legend()
            
            ax.set_xlabel('Distance (pixels)', fontsize=axis_fontsize)
            ax.set_ylabel('Pixel Intensity', fontsize=axis_fontsize)
            ax.set_title(f'{title}\nLine: ({x1},{y1}) → ({x2},{y2})', fontsize=title_fontsize)
            ax.grid(grid, alpha=grid_alpha)
            ax.set_ylim(0, 255)
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            plt.tight_layout()
            
            # Handle display based on backend type
            if self._is_agg_backend and self._opencv_detected:
                # Agg backend in OpenCV app - convert to OpenCV image and display
                # Converting profile plot to OpenCV image...
                opencv_img = self._figure_to_opencv_image(fig)
                
                if opencv_img is not None:
                    # Display using OpenCV with optimized window settings
                    window_name = f"Profile - {title}"
                    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
                    
                    # Set initial window size for better quality display
                    height, width = opencv_img.shape[:2]
                    # Scale to reasonable size while maintaining aspect ratio
                    max_width, max_height = 1200, 800
                    if width > max_width or height > max_height:
                        scale = min(max_width/width, max_height/height)
                        new_width = int(width * scale)
                        new_height = int(height * scale)
                        cv2.resizeWindow(window_name, new_width, new_height)
                    
                    cv2.imshow(window_name, opencv_img)
                    # High-quality profile displayed in OpenCV window
                    
                    # Store window name for cleanup tracking
                    if not hasattr(self, '_opencv_windows'):
                        self._opencv_windows = set()
                    self._opencv_windows.add(window_name)
                    
                    # Store OpenCV image for direct saving (since we're using OpenCV display)
                    self._last_profile_opencv_image = opencv_img.copy()
                    self._last_profile_window_name = window_name
                    
                else:
                    # Failed to convert profile plot to OpenCV image
                    pass
                    
                # Close the matplotlib figure to save memory
                plt.close(fig)
                
            else:
                # Interactive backends (non-OpenCV applications)
                current_thread_is_main = threading.current_thread() is threading.main_thread()
                
                if current_thread_is_main:
                    # Running in main thread - safe for all backends
                    plt.show(block=False)
                    try:
                        fig.canvas.draw()
                        fig.canvas.flush_events()
                    except Exception as e:
                        print(f"Warning: Display issue: {e}")
                else:
                    # Running in worker thread - only safe for TkAgg
                    if self._is_tkinter_backend:
                        try:
                            plt.show(block=False)
                            threading.Event().wait(0.1)  # Give time to initialize
                            fig.canvas.draw()
                            # Don't call flush_events with TkAgg in thread
                        except Exception as e:
                            print(f"Warning: Display issue with TkAgg backend: {e}")
                    else:
                        print("Error: Non-TkAgg backend should not run in worker thread")
                        return
                
                # Store figure for interactive backends only
                plot_id = f"profile_{len(self.plot_windows)}"
                if self._thread_lock:
                    with self._thread_lock:
                        self.plot_windows[plot_id] = fig
                else:
                    self.plot_windows[plot_id] = fig
                
        except Exception as e:
            print(f"Error creating profile plot: {e}")

    def create_histogram_plot(self, image: np.ndarray, roi: Optional[Tuple[int, int, int, int]] = None, polygon: Optional[List[Tuple[int, int]]] = None, title: str = "Histogram") -> None:
        """Create a histogram plot for the image with optional ROI or polygon masking.
        
        This method generates a histogram plot showing the distribution of pixel intensities
        in the image. For color images, it displays separate histograms for each channel
        (blue, green, red). For grayscale images, it shows a single intensity histogram.
        The method supports region-of-interest (ROI) analysis and polygon masking for
        selective area analysis.
        
        The method automatically handles matplotlib backend compatibility with OpenCV
        applications by choosing appropriate threading strategies or direct execution
        based on the detected environment configuration.
        
        Args:
            image: Input image as numpy array (color or grayscale).
            roi: Optional ROI as (x, y, width, height) tuple for rectangular region analysis.
                If provided, only pixels within this rectangle are included in the histogram.
            polygon: Optional list of (x, y) coordinate tuples defining a polygon mask.
                If provided, only pixels within the polygon are included in the histogram.
            title: Title for the histogram plot. Defaults to "Histogram".
            
        Examples:
            >>> analyzer = PlotAnalyzer()
            >>> # Full image histogram
            >>> analyzer.create_histogram_plot(image, title="Full Image Histogram")
            >>> # ROI-based histogram
            >>> analyzer.create_histogram_plot(image, roi=(100, 100, 200, 150), title="ROI Histogram")
            >>> # Polygon-masked histogram
            >>> polygon_coords = [(50, 50), (150, 50), (100, 150)]
            >>> analyzer.create_histogram_plot(image, polygon=polygon_coords, title="Polygon Histogram")
            
        Performance:
            Time Complexity: O(n) where n is the number of pixels in the analysis region.
            Space Complexity: O(1) for histogram bins (fixed 256 bins per channel).
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for histogram plotting")
            return
        
        # Creating histogram plot with current backend
        
        # For OpenCV + Agg backend, run directly in main thread (no GUI conflicts)
        if self._opencv_detected and self._is_agg_backend:
            # Using Agg backend with OpenCV - direct main thread execution
            self._create_histogram_plot_internal(
                image.copy(),
                roi,
                polygon.copy() if polygon else None,
                title
            )
            return
        
        # For other backends, use previous threading logic
        if self._opencv_detected or self._current_backend in ['TkAgg']:
            # Use threading for problematic combinations
            # Starting plot thread...
            self._start_plot_thread()
            
            plot_request = {
                'type': 'histogram',
                'args': {
                    'image': image.copy(),
                    'roi': roi,
                    'polygon': polygon.copy() if polygon else None,
                    'title': title
                }
            }
            
            try:
                # Queuing histogram plot request...
                self._plot_queue.put(plot_request, timeout=5)
                # Histogram plot request queued successfully
            except Exception as e:
                print(f"Failed to queue histogram plot: {e}")
        else:
            # Non-OpenCV Qt backends can run in main thread
            # Using main thread for Qt backend
            self._create_histogram_plot_internal(
                image.copy(), 
                roi, 
                polygon.copy() if polygon else None, 
                title
            )
    
    def _create_histogram_plot_internal(self, image: np.ndarray, roi: Optional[Tuple[int, int, int, int]] = None, polygon: Optional[List[Tuple[int, int]]] = None, title: str = "Histogram") -> None:
        """Internal method for creating histogram plots with thread-safe execution.
        
        This internal method handles the actual matplotlib plotting operations for histogram
        visualization. It runs in either the main thread or a worker thread depending on
        backend compatibility requirements. The method processes ROI and polygon masks,
        calculates histogram data using OpenCV, and creates high-quality matplotlib plots
        with user-configurable styling.
        
        The method performs comprehensive histogram analysis:
        1. Validates input image and parameters
        2. Creates polygon masks using OpenCV fillPoly if specified
        3. Extracts ROI regions while maintaining proper bounds checking
        4. Calculates histograms for each color channel using cv2.calcHist
        5. Creates matplotlib figure with customizable styling and colors
        6. Handles display based on backend type (interactive vs OpenCV windows)
        7. Stores plot references for cleanup and export functionality
        
        Args:
            image: Input image as numpy array (color or grayscale).
            roi: Optional ROI as (x, y, width, height) tuple for analysis region.
            polygon: Optional list of (x, y) coordinate tuples for polygon masking.
            title: Title for the histogram display. Defaults to "Histogram".
            
        Note:
            This method is for internal use only and should not be called directly.
            Use create_histogram_plot() instead for public API access.
            
        Examples:
            >>> # Internal usage (not recommended for direct calls)
            >>> analyzer._create_histogram_plot_internal(image, roi=(0,0,100,100), title="Internal Histogram")
            
        Performance:
            Time Complexity: O(n + m) where n is pixels in analysis region and m is plot rendering.
            Space Complexity: O(c) where c is number of channels (1 for grayscale, 3 for color).
        """
        if not MATPLOTLIB_AVAILABLE:
            return
        
        # Starting histogram plot creation...
        
        try:
            if image is None or image.size == 0:
                print("Invalid image for histogram plotting")
                return
            
            mask = None
            if polygon:
                mask = np.zeros(image.shape[:2], dtype=np.uint8)
                poly_points = np.array(polygon, dtype=np.int32)
                cv2.fillPoly(mask, [poly_points], 255)
                title += " (Polygon)"
            
            roi_image = image
            if roi:
                x, y, w, h = roi
                x = max(0, min(x, image.shape[1] - 1))
                y = max(0, min(y, image.shape[0] - 1))
                w = min(w, image.shape[1] - x)
                h = min(h, image.shape[0] - y)
                
                if w <= 0 or h <= 0:
                    print("Invalid ROI dimensions")
                    return
                
                roi_image = image[y:y+h, x:x+w]
                if mask is not None:
                    mask = mask[y:y+h, x:x+w]
                title += f" (ROI: {x},{y} {w}x{h})"

            if roi_image.size == 0:
                print("ROI image is empty")
                return
            
            # Get plot settings
            settings = self.plot_settings.get("histogram_settings", {})
            figure_size = settings.get("figure_size", (10, 6))
            dpi = settings.get("dpi", 100)
            grid = settings.get("grid", True)
            grid_alpha = settings.get("grid_alpha", 0.3)
            title_fontsize = settings.get("title_fontsize", 14)
            axis_fontsize = settings.get("axis_fontsize", 12)
            line_width = settings.get("line_width", 2)
            line_alpha = settings.get("line_alpha", 0.8)
            show_legend = settings.get("show_legend", True)
            colors = settings.get("colors", {
                "blue": "#0000FF",
                "green": "#00FF00",
                "red": "#FF0000",
                "gray": "#000000"
            })
            
            # Create figure with custom size and DPI
            fig, ax = plt.subplots(figsize=figure_size, dpi=dpi)
            
            if len(roi_image.shape) == 3:  # Color image
                color_names = ['blue', 'green', 'red']
                labels = ['Blue', 'Green', 'Red']
                
                for i, (color_name, label) in enumerate(zip(color_names, labels)):
                    hist = cv2.calcHist([roi_image], [i], mask, [256], [0, 256])
                    hist = hist.flatten()
                    ax.plot(range(256), hist, color=colors.get(color_name, color_name), 
                           label=label, linewidth=line_width, alpha=line_alpha)
                    
            else:  # Grayscale image
                hist = cv2.calcHist([roi_image], [0], mask, [256], [0, 256])
                hist = hist.flatten()
                ax.plot(range(256), hist, color=colors.get("gray", "#000000"), 
                       linewidth=line_width, alpha=line_alpha, label='Intensity')
            
            ax.set_xlabel('Pixel Intensity', fontsize=axis_fontsize)
            ax.set_ylabel('Frequency', fontsize=axis_fontsize)
            ax.set_title(title, fontsize=title_fontsize)
            ax.grid(grid, alpha=grid_alpha)
            ax.set_xlim(0, 255)
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            if show_legend and (len(roi_image.shape) == 3 or len(roi_image.shape) == 2):
                ax.legend()
            
            plt.tight_layout()
            
            # Handle display based on backend type
            if self._is_agg_backend and self._opencv_detected:
                # Agg backend in OpenCV app - convert to OpenCV image and display
                # Converting matplotlib plot to OpenCV image...
                opencv_img = self._figure_to_opencv_image(fig)
                
                if opencv_img is not None:
                    # Display using OpenCV with optimized window settings
                    window_name = f"Histogram - {title}"
                    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
                    
                    # Set initial window size for better quality display
                    height, width = opencv_img.shape[:2]
                    # Scale to reasonable size while maintaining aspect ratio
                    max_width, max_height = 1200, 800
                    if width > max_width or height > max_height:
                        scale = min(max_width/width, max_height/height)
                        new_width = int(width * scale)
                        new_height = int(height * scale)
                        cv2.resizeWindow(window_name, new_width, new_height)
                    
                    cv2.imshow(window_name, opencv_img)
                    # High-quality histogram displayed in OpenCV window
                    
                    # Store window name for cleanup tracking
                    if not hasattr(self, '_opencv_windows'):
                        self._opencv_windows = set()
                    self._opencv_windows.add(window_name)
                    
                    # Store OpenCV image for direct saving (since we're using OpenCV display)
                    self._last_histogram_opencv_image = opencv_img.copy()
                    self._last_histogram_window_name = window_name
                    
                else:
                    # Failed to convert matplotlib figure to OpenCV image
                    pass
                    
                # Close the matplotlib figure to save memory
                plt.close(fig)
                
            else:
                # Interactive backends (non-OpenCV applications)
                current_thread_is_main = threading.current_thread() is threading.main_thread()
                # Displaying histogram plot
                
                if current_thread_is_main:
                    # Running in main thread - safe for all backends
                    # Showing plot in main thread
                    plt.show(block=False)
                    try:
                        fig.canvas.draw()
                        fig.canvas.flush_events()
                        # Plot displayed successfully
                        pass
                    except Exception as e:
                        print(f"Warning: Display issue: {e}")
                else:
                    # Running in worker thread - only safe for TkAgg
                    if self._is_tkinter_backend:
                        try:
                            # Showing TkAgg plot in worker thread
                            plt.show(block=False)
                            threading.Event().wait(0.2)  # Give more time to initialize
                            fig.canvas.draw()
                            # TkAgg plot displayed successfully
                            pass
                            # Don't call flush_events with TkAgg in thread
                        except Exception as e:
                            print(f"Warning: Display issue with TkAgg backend: {e}")
                    else:
                        print("Error: Non-TkAgg backend should not run in worker thread")
                        return
                
                # Store figure for interactive backends only
                plot_id = f"histogram_{len(self.plot_windows)}"
                if self._thread_lock:
                    with self._thread_lock:
                        self.plot_windows[plot_id] = fig
                else:
                    self.plot_windows[plot_id] = fig
                
                # Histogram plot stored with ID
                
        except Exception as e:
            print(f"Error creating histogram plot: {e}")

    def _get_line_points(self, x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        """Get all points along a line using Bresenham's line drawing algorithm.
        
        This method implements Bresenham's algorithm to generate all integer pixel
        coordinates that lie along the line between two specified endpoints. The
        algorithm ensures that the line is drawn with minimal aliasing and includes
        all pixels that the line passes through, making it ideal for pixel-perfect
        line analysis in image processing applications.
        
        Bresenham's algorithm is efficient and produces visually smooth lines by
        determining which pixels should be illuminated to form a close approximation
        to a straight line between two endpoints.
        
        Args:
            x1: X-coordinate of the line start point.
            y1: Y-coordinate of the line start point.
            x2: X-coordinate of the line end point.
            y2: Y-coordinate of the line end point.
            
        Returns:
            List[Tuple[int, int]]: List of (x, y) coordinate tuples representing
                all pixels along the line from (x1, y1) to (x2, y2) inclusive.
                
        Examples:
            >>> analyzer = PlotAnalyzer()
            >>> points = analyzer._get_line_points(0, 0, 3, 3)
            >>> print(points)  # [(0,0), (1,1), (2,2), (3,3)]
            >>> # Horizontal line
            >>> h_points = analyzer._get_line_points(0, 5, 5, 5)
            >>> print(h_points)  # [(0,5), (1,5), (2,5), (3,5), (4,5), (5,5)]
            
        Performance:
            Time Complexity: O(max(|x2-x1|, |y2-y1|)) - linear in line length.
            Space Complexity: O(max(|x2-x1|, |y2-y1|)) - for storing all line points.
        """
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        
        while True:
            points.append((x, y))
            
            if x == x2 and y == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return points
    
    def calculate_histogram(self, image: np.ndarray, roi: Optional[Tuple[int, int, int, int]] = None, polygon: Optional[List[Tuple[int, int]]] = None) -> Dict[str, np.ndarray]:
        """Calculate histogram data for the image with optional ROI or polygon masking.
        
        This method computes histogram data without creating visualizations, making it
        suitable for data analysis and export operations. It calculates intensity
        distributions for all color channels in the specified image region using
        OpenCV's optimized histogram calculation functions.
        
        The method supports flexible region analysis through ROI rectangles or
        arbitrary polygon shapes, enabling focused analysis of specific image areas.
        For color images, it calculates separate histograms for blue, green, and red
        channels. For grayscale images, it calculates a single intensity histogram.
        
        Args:
            image: Input image as numpy array (color or grayscale).
            roi: Optional ROI as (x, y, width, height) tuple for rectangular region analysis.
                If provided, only pixels within this rectangle are included.
            polygon: Optional list of (x, y) coordinate tuples defining a polygon mask.
                If provided, only pixels within the polygon are included.
                
        Returns:
            Dict[str, np.ndarray]: Dictionary containing histogram data with keys:
                - 'bins': Array of intensity bin values (0-255)
                - 'roi': Copy of the ROI parameter for reference
                - 'polygon': Copy of the polygon parameter for reference
                - For color images: 'blue', 'green', 'red' keys with histogram arrays
                - For grayscale images: 'gray' key with histogram array
                Returns empty dict if image is invalid or region has no pixels.
                
        Examples:
            >>> analyzer = PlotAnalyzer()
            >>> # Full image histogram data
            >>> hist_data = analyzer.calculate_histogram(image)
            >>> print(f"Red channel max: {max(hist_data['red'])}")
            >>> # ROI-based histogram data
            >>> roi_hist = analyzer.calculate_histogram(image, roi=(100, 100, 200, 150))
            >>> print(f"ROI blue channel: {len(roi_hist['blue'])} bins")
            >>> # Access bin centers
            >>> bins = hist_data['bins']  # [0, 1, 2, ..., 255]
            
        Performance:
            Time Complexity: O(n) where n is the number of pixels in the analysis region.
            Space Complexity: O(c) where c is the number of channels (256 bins per channel).
        """
        if image is None or image.size == 0:
            return {}
        
        mask = None
        if polygon:
            mask = np.zeros(image.shape[:2], dtype=np.uint8)
            poly_points = np.array(polygon, dtype=np.int32)
            cv2.fillPoly(mask, [poly_points], 255)
        
        roi_image = image
        if roi:
            x, y, w, h = roi
            x = max(0, min(x, image.shape[1] - 1))
            y = max(0, min(y, image.shape[0] - 1))
            w = min(w, image.shape[1] - x)
            h = min(h, image.shape[0] - y)
            
            if w <= 0 or h <= 0:
                return {}
            
            roi_image = image[y:y+h, x:x+w]
            if mask is not None:
                mask = mask[y:y+h, x:x+w]

        if roi_image.size == 0:
            return {}
        
        result = {
            'bins': np.arange(256),
            'roi': roi,
            'polygon': polygon
        }
        
        if len(roi_image.shape) == 3:  # Color image
            for i, channel in enumerate(['blue', 'green', 'red']):
                hist = cv2.calcHist([roi_image], [i], mask, [256], [0, 256])
                result[channel] = hist.flatten()
        else:  # Grayscale image
            hist = cv2.calcHist([roi_image], [0], mask, [256], [0, 256])
            result['gray'] = hist.flatten()
        
        return result
    
    def calculate_pixel_profile(self, image: np.ndarray, line_coords: Tuple[int, int, int, int]) -> Dict[str, np.ndarray]:
        """Calculate pixel intensity profile data along a specified line.
        
        This method computes pixel intensity values along a line without creating
        visualizations, making it suitable for data analysis and export operations.
        It uses Bresenham's algorithm to determine all pixels along the line and
        extracts their intensity values for each color channel.
        
        The method calculates distances from the line start point and collects
        corresponding pixel intensities, providing comprehensive data for profile
        analysis. For color images, it extracts separate profiles for blue, green,
        and red channels. For grayscale images, it extracts a single intensity profile.
        
        Args:
            line_coords: Tuple of (x1, y1, x2, y2) defining the line endpoints
                in pixel coordinates within the image bounds.
                
        Returns:
            Dict[str, np.ndarray]: Dictionary containing profile data with keys:
                - 'distances': Array of distance values from line start point
                - 'line_coords': Copy of input line coordinates for reference
                - 'points': List of (x, y) pixel coordinates along the line
                - For color images: 'blue', 'green', 'red' keys with intensity arrays
                - For grayscale images: 'gray' key with intensity array
                Returns empty dict if image is invalid or line has insufficient points.
                
        Examples:
            >>> analyzer = PlotAnalyzer()
            >>> # Diagonal profile across image
            >>> profile_data = analyzer.calculate_pixel_profile(image, (0, 0, 100, 100))
            >>> distances = profile_data['distances']
            >>> red_intensities = profile_data['red']
            >>> print(f"Profile length: {len(distances)} pixels")
            >>> print(f"Max red intensity: {max(red_intensities)}")
            >>> # Horizontal profile
            >>> h_profile = analyzer.calculate_pixel_profile(image, (0, 50, 200, 50))
            >>> print(f"Horizontal profile points: {len(h_profile['points'])}")
            
        Performance:
            Time Complexity: O(n) where n is the length of the line in pixels.
            Space Complexity: O(n*c) where c is the number of channels.
        """
        if image is None or image.size == 0:
            return {}
        
        x1, y1, x2, y2 = line_coords
        points = self._get_line_points(x1, y1, x2, y2)
        
        valid_points = [(x, y) for x, y in points if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]]
        
        if len(valid_points) < 2:
            return {}
        
        distances = np.array([np.sqrt((p[0] - x1)**2 + (p[1] - y1)**2) for p in valid_points])
        
        result = {
            'distances': distances,
            'line_coords': line_coords,
            'points': valid_points
        }
        
        if len(image.shape) == 3:  # Color image
            blue_values = np.array([image[p[1], p[0], 0] for p in valid_points])
            green_values = np.array([image[p[1], p[0], 1] for p in valid_points])
            red_values = np.array([image[p[1], p[0], 2] for p in valid_points])
            
            result['blue'] = blue_values
            result['green'] = green_values
            result['red'] = red_values
        else:  # Grayscale image
            gray_values = np.array([image[p[1], p[0]] for p in valid_points])
            result['gray'] = gray_values
        
        return result
    
    def close_all_plots(self) -> None:
        """Close all open plot windows with thread-safe cleanup operations.
        
        This method performs comprehensive cleanup of all plotting resources including
        matplotlib figures and OpenCV windows. It handles both interactive matplotlib
        backends and Agg backend with OpenCV display, ensuring proper resource cleanup
        to prevent memory leaks and window artifacts.
        
        The cleanup process includes:
        1. Thread-safe closure of all matplotlib figure windows
        2. Clearing the plot windows tracking dictionary
        3. Closing OpenCV windows created for Agg backend display
        4. Clearing OpenCV window tracking sets
        5. Proper error handling to ensure cleanup continues even if individual operations fail
        
        This method is automatically called during analyzer cleanup but can also be
        called manually when immediate plot closure is needed.
        
        Examples:
            >>> analyzer = PlotAnalyzer()
            >>> analyzer.create_histogram_plot(image)
            >>> analyzer.create_pixel_profile_plot(image, (0, 0, 100, 100))
            >>> # Close all created plots
            >>> analyzer.close_all_plots()
            >>> print(f"Remaining plots: {len(analyzer.plot_windows)}")  # Should be 0
            
        Performance:
            Time Complexity: O(n) where n is the number of open plot windows.
            Space Complexity: O(1) - releases memory used by plot tracking.
        """
        if not MATPLOTLIB_AVAILABLE:
            # Matplotlib not available, skipping plot cleanup
            return
            
        # Starting close_all_plots()
        # Found matplotlib plot windows
        
        try:
            # Close matplotlib figures
            if self._thread_lock:
                with self._thread_lock:
                    for fig in self.plot_windows.values():
                        try:
                            plt.close(fig)
                        except:
                            pass  # Ignore errors when closing figures
                    self.plot_windows.clear()
            else:
                for fig in self.plot_windows.values():
                    try:
                        plt.close(fig)
                    except:
                        pass
                self.plot_windows.clear()
            
            # Close OpenCV windows created by Agg backend
            if hasattr(self, '_opencv_windows'):
                # Found OpenCV plot windows
                for window_name in list(self._opencv_windows):
                    try:
                        # Closing OpenCV window
                        cv2.destroyWindow(window_name)
                        # Successfully closed window
                    except Exception as e:
                        print(f"   → Error closing window {window_name}: {e}")
                self._opencv_windows.clear()
                # All OpenCV windows cleared from tracking set
            else:
                # No OpenCV windows found (_opencv_windows attribute missing)
                pass
                
        except Exception as e:
            print(f"Error closing plots: {e}")
    
    def save_last_histogram_plot(self, filename: str, dpi: int = 200) -> bool:
        """Save the last created histogram plot as a high-quality image file.
        
        This method exports the most recently created histogram plot to an image file
        with configurable quality settings. It handles both interactive matplotlib
        backends and Agg backend with OpenCV display, automatically choosing the
        appropriate save method based on the current backend configuration.
        
        For Agg backend with OpenCV display, it saves the stored high-resolution
        OpenCV image directly. For interactive backends, it uses matplotlib's
        savefig functionality with optimized settings for publication-quality output.
        
        Args:
            filename: Output filename with extension (e.g., 'histogram.png', 'plot.jpg').
                The file format is determined by the extension.
            dpi: Dots per inch for image quality. Higher values produce sharper images
                but larger files. Defaults to 200 for high-quality output.
                
        Returns:
            bool: True if the plot was successfully saved, False otherwise.
            
        Examples:
            >>> analyzer = PlotAnalyzer()
            >>> analyzer.create_histogram_plot(image, title="RGB Histogram")
            >>> # Save with default high quality
            >>> success = analyzer.save_last_histogram_plot("rgb_histogram.png")
            >>> if success:
            ...     print("Histogram saved successfully")
            >>> # Save with custom DPI
            >>> analyzer.save_last_histogram_plot("high_res_histogram.png", dpi=300)
            
        Performance:
            Time Complexity: O(n) where n is the number of pixels in the plot image.
            Space Complexity: O(n) for temporary image buffer during save operation.
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for plot saving")
            return False
            
        try:
            # Saving histogram plot to file
            
            # For Agg backend with OpenCV display, save the stored OpenCV image directly
            if self._is_agg_backend and self._opencv_detected:
                # Using OpenCV display - saving stored image directly
                if hasattr(self, '_last_histogram_opencv_image') and self._last_histogram_opencv_image is not None:
                    # Save the OpenCV image directly as PNG
                    success = cv2.imwrite(filename, self._last_histogram_opencv_image)
                    if success:
                        # Successfully saved OpenCV histogram image
                        return True
                    else:
                        # Error: Failed to write image to file
                        return False
                else:
                    # Error: No OpenCV histogram image available for saving
                    return False
            else:
                # For interactive backends, save the last created figure
                if self.plot_windows:
                    last_fig = list(self.plot_windows.values())[-1]
                    last_fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                                   facecolor='white', edgecolor='none')
                    # Successfully saved plot to file
                    return True
                else:
                    # Error: No plots available for saving
                    return False
                    
        except Exception as e:
            print(f"Error saving histogram plot: {e}")
            return False
    
    def save_last_profile_plot(self, filename: str, dpi: int = 200) -> bool:
        """Save the last created pixel profile plot as a high-quality image file.
        
        This method exports the most recently created pixel profile plot to an image
        file with configurable quality settings. It handles both interactive matplotlib
        backends and Agg backend with OpenCV display, automatically choosing the
        appropriate save method based on the current backend configuration.
        
        For Agg backend with OpenCV display, it saves the stored high-resolution
        OpenCV image directly. For interactive backends, it uses matplotlib's
        savefig functionality with optimized settings for publication-quality output.
        
        Args:
            filename: Output filename with extension (e.g., 'profile.png', 'line_plot.jpg').
                The file format is determined by the extension.
            dpi: Dots per inch for image quality. Higher values produce sharper images
                but larger files. Defaults to 200 for high-quality output.
                
        Returns:
            bool: True if the plot was successfully saved, False otherwise.
            
        Examples:
            >>> analyzer = PlotAnalyzer()
            >>> analyzer.create_pixel_profile_plot(image, (0, 0, 100, 100), "Diagonal Profile")
            >>> # Save with default high quality
            >>> success = analyzer.save_last_profile_plot("diagonal_profile.png")
            >>> if success:
            ...     print("Profile plot saved successfully")
            >>> # Save with custom DPI for publication
            >>> analyzer.save_last_profile_plot("publication_profile.png", dpi=300)
            
        Performance:
            Time Complexity: O(n) where n is the number of pixels in the plot image.
            Space Complexity: O(n) for temporary image buffer during save operation.
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for plot saving")
            return False
            
        try:
            # Saving profile plot to file
            
            # For Agg backend with OpenCV display, save the stored OpenCV image directly
            if self._is_agg_backend and self._opencv_detected:
                # Using OpenCV display - saving stored image directly
                if hasattr(self, '_last_profile_opencv_image') and self._last_profile_opencv_image is not None:
                    # Save the OpenCV image directly as PNG
                    success = cv2.imwrite(filename, self._last_profile_opencv_image)
                    if success:
                        # Successfully saved OpenCV profile image
                        return True
                    else:
                        # Error: Failed to write image to file
                        return False
                else:
                    # Error: No OpenCV profile image available for saving
                    return False
            else:
                # For interactive backends, save the last created figure
                if self.plot_windows:
                    last_fig = list(self.plot_windows.values())[-1]
                    last_fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                                   facecolor='white', edgecolor='none')
                    # Successfully saved plot to file
                    return True
                else:
                    # Error: No plots available for saving
                    return False
                    
        except Exception as e:
            print(f"Error saving profile plot: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up the plot analyzer and stop all threading operations.
        
        This method performs comprehensive cleanup of the PlotAnalyzer instance,
        ensuring proper resource deallocation and thread termination. It should be
        called when the analyzer is no longer needed to prevent memory leaks and
        ensure clean application shutdown.
        
        The cleanup process includes:
        1. Closing all open plot windows (matplotlib and OpenCV)
        2. Stopping the background plotting thread
        3. Clearing all plot tracking data structures
        4. Releasing threading resources (locks, queues)
        
        This method is automatically called by the destructor (__del__) but can
        also be called manually for explicit cleanup control.
        
        Examples:
            >>> analyzer = PlotAnalyzer()
            >>> analyzer.create_histogram_plot(image)
            >>> analyzer.create_pixel_profile_plot(image, (0, 0, 100, 100))
            >>> # Explicitly clean up when done
            >>> analyzer.cleanup()
            >>> # Analyzer should not be used after cleanup
            
        Performance:
            Time Complexity: O(n) where n is the number of open plots and threads.
            Space Complexity: O(1) - releases all tracked resources.
        """
        if not MATPLOTLIB_AVAILABLE:
            return
            
        try:
            # Close all plots first
            self.close_all_plots()
            
            # Stop the plotting thread
            self._stop_plot_thread()
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def __del__(self) -> None:
        """Destructor to ensure proper cleanup when the object is garbage collected.
        
        This special method is automatically called by Python's garbage collector
        when the PlotAnalyzer instance is being destroyed. It ensures that all
        resources are properly cleaned up even if the user forgets to call cleanup()
        explicitly, preventing resource leaks and orphaned threads.
        
        The destructor calls the cleanup() method within a try-except block to
        handle any potential errors during the destruction process without raising
        exceptions that could interfere with garbage collection.
        
        Note:
            While this provides automatic cleanup, it's recommended to call cleanup()
            explicitly for deterministic resource management, as the timing of
            destructor execution depends on Python's garbage collection behavior.
            
        Examples:
            >>> analyzer = PlotAnalyzer()
            >>> analyzer.create_histogram_plot(image)
            >>> # When analyzer goes out of scope, __del__ is called automatically
            >>> del analyzer  # Explicit deletion triggers __del__
            
        Performance:
            Time Complexity: Same as cleanup() - O(n) where n is number of resources.
            Space Complexity: O(1) - releases all resources without allocation.
        """
        try:
            self.cleanup()
        except:
            pass  # Ignore errors during destruction
