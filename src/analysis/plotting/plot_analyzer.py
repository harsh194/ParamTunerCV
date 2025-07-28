import cv2
import numpy as np
import os
import json
import io
from typing import List, Tuple, Optional, Dict, Any

def _test_matplotlib_backend(backend_name):
    """Test if a matplotlib backend actually works by creating a test figure."""
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

def _detect_opencv_context():
    """Detect if we're running in an OpenCV application context."""
    try:
        import cv2
        # Check if OpenCV is imported (strong indicator we're in OpenCV app)
        return True
    except ImportError:
        return False

def _check_pyqt5_conflict():
    """Check if PyQt5 is installed and warn about OpenCV conflicts."""
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
        print("🚨 CRITICAL: PyQt5 + OpenCV detected!")
        print("   This combination causes fatal GIL threading errors.")
        print("   Please uninstall PyQt5: pip uninstall PyQt5")
        print("   OpenCV applications will use Agg backend with cv2.imshow display.")
        print("")
    
    if opencv_detected:
        # In OpenCV applications, ALL interactive backends conflict with cv2.waitKey()!
        # Even TkAgg creates Tkinter event loops that cause GIL threading errors
        # Solution: Use Agg backend + display plots via OpenCV windows
        backends_to_try = [
            ('Agg', 'Agg (OpenCV-compatible - plots displayed via cv2.imshow)')
        ]
        print("🔍 OpenCV detected - using non-interactive matplotlib backend")
        print("📊 Plots will be displayed in OpenCV windows to avoid GUI conflicts")
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
    
    # Print which backend was successfully configured
    print(f"Matplotlib backend: {backend_tried}")
    
    # Show info and warnings for different backends
    if working_backend in ['Qt5Agg', 'Qt4Agg']:
        if opencv_detected:
            print("⚠️  WARNING: Qt backend with OpenCV detected - this may cause GIL threading errors!")
            print("   → Consider using TkAgg backend for OpenCV applications")
        else:
            print("✓ Qt backend detected - plots will run in main thread for optimal stability")
    elif working_backend == 'TkAgg':
        if opencv_detected:
            print("⚠️  WARNING: TkAgg backend with OpenCV may still cause GIL conflicts!")
            print("   → Agg backend is recommended for OpenCV applications")
        else:
            print("Warning: Using TkAgg backend. Qt backends are recommended for better stability.")
            print("  → Install PyQt5 for better performance: pip install PyQt5>=5.15.0")
    elif working_backend == 'Agg':
        if opencv_detected:
            print("✅ Agg backend selected - plots will display via OpenCV windows")
            print("   → This completely avoids GUI event loop conflicts")
        else:
            print("Warning: Using non-interactive matplotlib backend. Plots may not display properly.")
    
    MATPLOTLIB_AVAILABLE = True
    
except ImportError as e:
    MATPLOTLIB_AVAILABLE = False
    print(f"Warning: matplotlib not available ({e}). Pixel profile and histogram features will be disabled.")

class PlotAnalyzer:
    """Handles image analysis plotting features like pixel profiles and histograms."""
    
    CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".parameter_plot_settings.json")
    
    def __init__(self):
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
        
    def _figure_to_opencv_image(self, fig):
        """Convert matplotlib figure to high-quality OpenCV image for display."""
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
        """Load plot settings from config file."""
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
            
    def update_plot_settings(self, plot_type: str, settings: Dict[str, Any]):
        """Update plot settings for the specified plot type."""
        self.plot_settings[f"{plot_type}_settings"] = settings
        
        # Save settings to file
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.plot_settings, f, indent=2)
        except Exception as e:
            print(f"Error saving plot settings: {e}")
    
    def _plot_worker(self):
        """Worker thread for handling matplotlib operations safely."""
        print("Plot worker thread started")
        while self._plotting_active:
            try:
                try:
                    print("Waiting for plot request...")
                    plot_request = self._plot_queue.get(timeout=0.5)
                    if plot_request is None:  # Shutdown signal
                        print("Received shutdown signal")
                        break
                    
                    print(f"Processing plot request: {plot_request['type']}")
                    plot_type = plot_request['type']
                    if plot_type == 'histogram':
                        self._create_histogram_plot_internal(**plot_request['args'])
                    elif plot_type == 'profile':
                        self._create_pixel_profile_plot_internal(**plot_request['args'])
                    
                    self._plot_queue.task_done()
                    print("Plot request completed")
                except:
                    # Queue was empty or timeout occurred, continue checking
                    threading.Event().wait(0.1)  # Small delay when queue is empty
                    
            except Exception as e:
                print(f"Plot worker error: {e}")
                # Continue running even if there's an error
                threading.Event().wait(0.1)
        print("Plot worker thread ended")
    
    def _start_plot_thread(self):
        """Start the plotting thread if not already running."""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        with self._thread_lock:
            if not self._plotting_active:
                self._plotting_active = True
                self._plot_thread = threading.Thread(target=self._plot_worker, daemon=True)
                self._plot_thread.start()
    
    def _stop_plot_thread(self):
        """Stop the plotting thread."""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        with self._thread_lock:
            if self._plotting_active:
                self._plotting_active = False
                if self._plot_queue:
                    self._plot_queue.put(None)  # Shutdown signal
                if self._plot_thread and self._plot_thread.is_alive():
                    self._plot_thread.join(timeout=2)
    
    def create_pixel_profile_plot(self, image: np.ndarray, line_coords: Tuple[int, int, int, int], title: str = "Pixel Profile"):
        """Create a pixel intensity profile plot along a line."""
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for pixel profile plotting")
            return
        
        # For OpenCV + Agg backend, run directly in main thread (no GUI conflicts)
        if self._opencv_detected and self._is_agg_backend:
            print("Using Agg backend with OpenCV - direct main thread execution")
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
    
    def _create_pixel_profile_plot_internal(self, image: np.ndarray, line_coords: Tuple[int, int, int, int], title: str = "Pixel Profile"):
        """Internal method for creating pixel profile plots (runs in separate thread)."""
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
                print("Converting profile plot to OpenCV image...")
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
                    print(f"High-quality profile displayed in OpenCV window: {window_name}")
                    print(f"Plot resolution: {width}x{height} pixels")
                    
                    # Store window name for cleanup tracking
                    if not hasattr(self, '_opencv_windows'):
                        self._opencv_windows = set()
                    self._opencv_windows.add(window_name)
                    
                    # Store OpenCV image for direct saving (since we're using OpenCV display)
                    self._last_profile_opencv_image = opencv_img.copy()
                    self._last_profile_window_name = window_name
                    
                else:
                    print("Failed to convert profile plot to OpenCV image")
                    
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

    def create_histogram_plot(self, image: np.ndarray, roi: Optional[Tuple[int, int, int, int]] = None, polygon: Optional[List[Tuple[int, int]]] = None, title: str = "Histogram"):
        """Create a histogram plot for the image, ROI, or polygon."""
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for histogram plotting")
            return
        
        print(f"Creating histogram plot with backend: {self._current_backend}")
        print(f"OpenCV detected: {self._opencv_detected}")
        print(f"Image shape: {image.shape if image is not None else 'None'}")
        
        # For OpenCV + Agg backend, run directly in main thread (no GUI conflicts)
        if self._opencv_detected and self._is_agg_backend:
            print("Using Agg backend with OpenCV - direct main thread execution")
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
            print("Starting plot thread...")
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
                print("Queuing histogram plot request...")
                self._plot_queue.put(plot_request, timeout=5)
                print("Histogram plot request queued successfully")
            except Exception as e:
                print(f"Failed to queue histogram plot: {e}")
        else:
            # Non-OpenCV Qt backends can run in main thread
            print("Using main thread for Qt backend")
            self._create_histogram_plot_internal(
                image.copy(), 
                roi, 
                polygon.copy() if polygon else None, 
                title
            )
    
    def _create_histogram_plot_internal(self, image: np.ndarray, roi: Optional[Tuple[int, int, int, int]] = None, polygon: Optional[List[Tuple[int, int]]] = None, title: str = "Histogram"):
        """Internal method for creating histogram plots (runs in separate thread)."""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        print("Starting histogram plot creation...")
        print(f"Thread: {threading.current_thread().name}")
        print(f"Is main thread: {threading.current_thread() is threading.main_thread()}")
        
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
                print("Converting matplotlib plot to OpenCV image...")
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
                    print(f"High-quality histogram displayed in OpenCV window: {window_name}")
                    print(f"Plot resolution: {width}x{height} pixels")
                    
                    # Store window name for cleanup tracking
                    if not hasattr(self, '_opencv_windows'):
                        self._opencv_windows = set()
                    self._opencv_windows.add(window_name)
                    
                    # Store OpenCV image for direct saving (since we're using OpenCV display)
                    self._last_histogram_opencv_image = opencv_img.copy()
                    self._last_histogram_window_name = window_name
                    
                else:
                    print("Failed to convert matplotlib figure to OpenCV image")
                    
                # Close the matplotlib figure to save memory
                plt.close(fig)
                
            else:
                # Interactive backends (non-OpenCV applications)
                current_thread_is_main = threading.current_thread() is threading.main_thread()
                print(f"Displaying histogram plot - main thread: {current_thread_is_main}")
                
                if current_thread_is_main:
                    # Running in main thread - safe for all backends
                    print("Showing plot in main thread")
                    plt.show(block=False)
                    try:
                        fig.canvas.draw()
                        fig.canvas.flush_events()
                        print("Plot displayed successfully")
                    except Exception as e:
                        print(f"Warning: Display issue: {e}")
                else:
                    # Running in worker thread - only safe for TkAgg
                    if self._is_tkinter_backend:
                        try:
                            print("Showing TkAgg plot in worker thread")
                            plt.show(block=False)
                            threading.Event().wait(0.2)  # Give more time to initialize
                            fig.canvas.draw()
                            print("TkAgg plot displayed successfully")
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
                
                print(f"Histogram plot stored with ID: {plot_id}")
                print(f"Total plots: {len(self.plot_windows)}")
                
        except Exception as e:
            print(f"Error creating histogram plot: {e}")

    def _get_line_points(self, x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        """Get all points along a line using Bresenham's algorithm."""
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
        """Calculate histogram data for the image, ROI, or polygon."""
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
        """Calculate pixel intensity profile along a line."""
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
    
    def close_all_plots(self):
        """Close all open plot windows (thread-safe)."""
        if not MATPLOTLIB_AVAILABLE:
            print("   → Matplotlib not available, skipping plot cleanup")
            return
            
        print("   → Starting close_all_plots()")
        print(f"   → Found {len(self.plot_windows)} matplotlib plot windows")
        
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
                print(f"   → Found {len(self._opencv_windows)} OpenCV plot windows: {list(self._opencv_windows)}")
                for window_name in list(self._opencv_windows):
                    try:
                        print(f"   → Closing OpenCV window: {window_name}")
                        cv2.destroyWindow(window_name)
                        print(f"   → Successfully closed: {window_name}")
                    except Exception as e:
                        print(f"   → Error closing window {window_name}: {e}")
                self._opencv_windows.clear()
                print("   → All OpenCV windows cleared from tracking set")
            else:
                print("   → No OpenCV windows found (_opencv_windows attribute missing)")
                
        except Exception as e:
            print(f"Error closing plots: {e}")
    
    def save_last_histogram_plot(self, filename: str, dpi: int = 200) -> bool:
        """Save the last created histogram plot as an image."""
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for plot saving")
            return False
            
        try:
            print(f"💾 Saving histogram plot to: {filename}")
            
            # For Agg backend with OpenCV display, save the stored OpenCV image directly
            if self._is_agg_backend and self._opencv_detected:
                print("   → Using OpenCV display - saving stored image directly")
                if hasattr(self, '_last_histogram_opencv_image') and self._last_histogram_opencv_image is not None:
                    # Save the OpenCV image directly as PNG
                    success = cv2.imwrite(filename, self._last_histogram_opencv_image)
                    if success:
                        print(f"   → Successfully saved OpenCV histogram image to {filename}")
                        return True
                    else:
                        print(f"   → Error: Failed to write image to {filename}")
                        return False
                else:
                    print("   → Error: No OpenCV histogram image available for saving")
                    return False
            else:
                # For interactive backends, save the last created figure
                if self.plot_windows:
                    last_fig = list(self.plot_windows.values())[-1]
                    last_fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                                   facecolor='white', edgecolor='none')
                    print(f"   → Successfully saved plot to {filename}")
                    return True
                else:
                    print("   → Error: No plots available for saving")
                    return False
                    
        except Exception as e:
            print(f"Error saving histogram plot: {e}")
            return False
    
    def save_last_profile_plot(self, filename: str, dpi: int = 200) -> bool:
        """Save the last created profile plot as an image."""
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for plot saving")
            return False
            
        try:
            print(f"💾 Saving profile plot to: {filename}")
            
            # For Agg backend with OpenCV display, save the stored OpenCV image directly
            if self._is_agg_backend and self._opencv_detected:
                print("   → Using OpenCV display - saving stored image directly")
                if hasattr(self, '_last_profile_opencv_image') and self._last_profile_opencv_image is not None:
                    # Save the OpenCV image directly as PNG
                    success = cv2.imwrite(filename, self._last_profile_opencv_image)
                    if success:
                        print(f"   → Successfully saved OpenCV profile image to {filename}")
                        return True
                    else:
                        print(f"   → Error: Failed to write image to {filename}")
                        return False
                else:
                    print("   → Error: No OpenCV profile image available for saving")
                    return False
            else:
                # For interactive backends, save the last created figure
                if self.plot_windows:
                    last_fig = list(self.plot_windows.values())[-1]
                    last_fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                                   facecolor='white', edgecolor='none')
                    print(f"   → Successfully saved plot to {filename}")
                    return True
                else:
                    print("   → Error: No plots available for saving")
                    return False
                    
        except Exception as e:
            print(f"Error saving profile plot: {e}")
            return False
    
    def cleanup(self):
        """Clean up the plot analyzer and stop threading."""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        try:
            # Close all plots first
            self.close_all_plots()
            
            # Stop the plotting thread
            self._stop_plot_thread()
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure proper cleanup."""
        try:
            self.cleanup()
        except:
            pass  # Ignore errors during destruction
