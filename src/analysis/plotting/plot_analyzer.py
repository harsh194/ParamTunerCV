import cv2
import numpy as np
import os
import json
from typing import List, Tuple, Optional, Dict, Any

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('TkAgg')  # Use TkAgg backend for better compatibility
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Pixel profile and histogram features will be disabled.")

class PlotAnalyzer:
    """Handles image analysis plotting features like pixel profiles and histograms."""
    
    CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".parameter_plot_settings.json")
    
    def __init__(self):
        self.plot_windows = {}  # Track open matplotlib windows
        self.plot_settings = self._load_plot_settings()
        
    def _load_plot_settings(self) -> Dict[str, Any]:
        """Load plot settings from config file."""
        default_settings = {
            "histogram_settings": {
                "figure_size": (10, 6),
                "dpi": 100,
                "grid": True,
                "grid_alpha": 0.3,
                "title_fontsize": 14,
                "axis_fontsize": 12,
                "line_width": 2,
                "line_alpha": 0.8,
                "show_legend": True,
                "colors": {
                    "blue": "#0000FF",
                    "green": "#00FF00",
                    "red": "#FF0000",
                    "gray": "#000000"
                }
            },
            "profile_settings": {
                "figure_size": (10, 6),
                "dpi": 100,
                "grid": True,
                "grid_alpha": 0.3,
                "title_fontsize": 14,
                "axis_fontsize": 12,
                "line_width": 2,
                "line_alpha": 0.8,
                "show_legend": True,
                "colors": {
                    "blue": "#0000FF",
                    "green": "#00FF00",
                    "red": "#FF0000",
                    "gray": "#000000"
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
    
    def create_pixel_profile_plot(self, image: np.ndarray, line_coords: Tuple[int, int, int, int], title: str = "Pixel Profile"):
        """Create a pixel intensity profile plot along a line."""
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for pixel profile plotting")
            return
        
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
        plt.show(block=False)
        
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        plot_id = f"profile_{len(self.plot_windows)}"
        self.plot_windows[plot_id] = fig

    def create_histogram_plot(self, image: np.ndarray, roi: Optional[Tuple[int, int, int, int]] = None, polygon: Optional[List[Tuple[int, int]]] = None, title: str = "Histogram"):
        """Create a histogram plot for the image, ROI, or polygon."""
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for histogram plotting")
            return
        
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
        plt.show(block=False)
        
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        plot_id = f"histogram_{len(self.plot_windows)}"
        self.plot_windows[plot_id] = fig

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
        """Close all open plot windows."""
        for fig in self.plot_windows.values():
            plt.close(fig)
        self.plot_windows.clear()
