import cv2
import traceback
from typing import Callable
from ..config.viewer_config import ViewerConfig

class WindowManager:
    """Manages OpenCV windows."""
    def __init__(self, config: ViewerConfig):
        self.config = config
        self.windows_created = False

    def create_windows(self, mouse_callback: Callable, text_mouse_callback: Callable, create_text_window: bool = True):
        if self.windows_created: return
        if not self.config.enable_debug: # Don't create windows if debug is off
            # print("WindowManager: Debug mode is off, not creating windows.") # Optional log
            return

        try:
            cv2.namedWindow(self.config.process_window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
            cv2.resizeWindow(self.config.process_window_name, self.config.screen_width, self.config.screen_height)
            cv2.setMouseCallback(self.config.process_window_name, mouse_callback)

            if create_text_window:
                cv2.namedWindow(self.config.text_window_name, cv2.WINDOW_AUTOSIZE)
                cv2.resizeWindow(self.config.text_window_name, self.config.text_window_width, self.config.text_window_height)
                cv2.setMouseCallback(self.config.text_window_name, text_mouse_callback)

            if self.config.trackbar: # Only create trackbar window if trackbar defs exist
                cv2.namedWindow(self.config.trackbar_window_name, cv2.WINDOW_AUTOSIZE)
                cv2.resizeWindow(self.config.trackbar_window_name, self.config.trackbar_window_width, self.config.trackbar_window_height)
            
            self.windows_created = True
            # print("WindowManager: Windows created successfully.") # Optional log
        except Exception as e:
            print(f"CRITICAL: Error creating OpenCV windows: {e}\n{traceback.format_exc()}")
            self.windows_created = False

    def destroy_all_windows(self):
        if self.windows_created:
            cv2.destroyAllWindows()
            self.windows_created = False
            # print("WindowManager: Windows destroyed.") # Optional log

    def resize_process_window(self, width: int, height: int):
        if not self.windows_created: return # No window to resize
        try:
            if cv2.getWindowProperty(self.config.process_window_name, cv2.WND_PROP_VISIBLE) < 1:
                return
            min_w, min_h = self.config.min_window_size
            max_w, max_h = self.config.screen_width * 2, self.config.screen_height * 2
            if self.config.desktop_resolution:
                max_w, max_h = self.config.desktop_resolution
            width = max(min_w, min(width, max_w))
            height = max(min_h, min(height, max_h))
            cv2.resizeWindow(self.config.process_window_name, width, height)
        except cv2.error: pass 
        except Exception: pass

    def refresh_window_titles(self):
        """Refresh window titles to ensure they remain visible after matplotlib operations."""
        if not self.windows_created:
            return
        
        try:
            # Force refresh of OpenCV windows to restore titles
            if cv2.getWindowProperty(self.config.process_window_name, cv2.WND_PROP_VISIBLE) >= 1:
                cv2.setWindowTitle(self.config.process_window_name, self.config.process_window_name)
                
            if cv2.getWindowProperty(self.config.text_window_name, cv2.WND_PROP_VISIBLE) >= 1:
                cv2.setWindowTitle(self.config.text_window_name, self.config.text_window_name)
                
            if hasattr(self.config, 'trackbar_window_name') and cv2.getWindowProperty(self.config.trackbar_window_name, cv2.WND_PROP_VISIBLE) >= 1:
                cv2.setWindowTitle(self.config.trackbar_window_name, self.config.trackbar_window_name)
                
        except (cv2.error, Exception):
            # Silently handle any errors - window title refresh is not critical
            pass
