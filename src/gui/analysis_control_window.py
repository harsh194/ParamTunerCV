import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
from .thresholding_manager import ThresholdingManager
from .theme_manager import ThemeManager
from .enhanced_widgets import ComboboxWithIndicator
try:
    from .enhanced_export_dialog import EnhancedExportDialog
    ENHANCED_EXPORT_AVAILABLE = True
    print("✅ EnhancedExportDialog imported successfully")
except ImportError as e:
    ENHANCED_EXPORT_AVAILABLE = False
    print(f"❌ Failed to import EnhancedExportDialog: {e}")
    
    # Create a fallback simple export dialog
    class SimpleExportDialog:
        def __init__(self, parent, theme_manager):
            self.parent = parent
            
        def show(self, filename_prefix="", on_export=None, on_cancel=None):
            # Simple fallback - just call the export with default values
            if on_export:
                on_export("histogram", "json", f"{filename_prefix}_export.json")
    
    EnhancedExportDialog = SimpleExportDialog

TKINTER_AVAILABLE = True
try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    TKINTER_AVAILABLE = False

class Tooltip:
    """
    Create a tooltip for a given widget.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

class AnalysisControlWindow:
    """Professional tkinter-based analysis control window with buttons and selectors."""
    
    def __init__(self, viewer: 'ImageViewer'):
        self.viewer = viewer
        self.window_created = False
        self.roi_selection = 0
        self.line_selection = 0
        self.polygon_selection = 0
        self.root = None
        self.theme_manager = ThemeManager(use_dark_mode=True)
        self.thresholding_manager = ThresholdingManager(viewer)
        
        self.active_buttons = {
            'line_mode': False,
            'polygon_mode': False,
            'thresholding': False
        }
        self.quick_access_buttons = {}
        self.action_buttons = {}  # Store references to action buttons for feedback
        
        # Track active states for persistent green highlighting
        self.active_states = {
            'analysis': None,  # Currently active analysis button
            'drawing_management': None,  # Currently active drawing management button
            'export_plots': None  # Currently active export/plots button
        }
        
    def create_window(self):
        """Create the analysis control window with enhanced UI."""
        if self.window_created or not self.viewer.config.enable_debug or not TKINTER_AVAILABLE:
            return

        try:
            if not hasattr(tk, '_default_root') or tk._default_root is None:
                root = tk.Tk()
                root.withdraw()

            self.root = tk.Toplevel()
            self.root.title("Analysis Controls")
            self.root.geometry("420x650")
            self.root.minsize(380, 550)
            
            # Ensure window stays visible and maintains its title
            self.root.wm_attributes("-topmost", False)  # Don't force always on top
            self.root.resizable(True, True)  # Allow resizing but with constraints

            self.theme_manager.configure_theme(self.root)
            
            # Create a container frame
            container = ttk.Frame(self.root)
            container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
            
            # Create canvas with scrollbar - store as instance attributes
            self.canvas = tk.Canvas(container, highlightthickness=0, bd=0)
            self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
            
            # Create a main frame inside the canvas - store as instance attribute
            self.main_frame = ttk.Frame(self.canvas, style=self.theme_manager.get_frame_style())
            
            # Configure the canvas
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            # Position at origin to fill width
            self.canvas_frame = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
            
            # Pack the canvas and scrollbar
            self.canvas.pack(side="left", fill="both", expand=True)
            self.scrollbar.pack(side="right", fill="y")
            
            # Ensure scrollbar is visible
            self.scrollbar.lift()
            
            # Bind events for proper scrolling behavior
            self.main_frame.bind("<Configure>", self._on_frame_configure)
            self.canvas.bind("<Configure>", self._on_canvas_configure)
            
            # Add mouse wheel scrolling support
            self._bind_mousewheel()
            
            # No padding frame needed - content fills full width

            self._create_quick_access_section(self.main_frame)
            self._create_selection_section(self.main_frame)
            self._create_analysis_section(self.main_frame)
            self._create_drawing_section(self.main_frame)
            self._create_export_section(self.main_frame)
            
            # Add minimal bottom padding to prevent text cutoff
            bottom_padding = ttk.Frame(self.main_frame, style=self.theme_manager.get_frame_style())
            bottom_padding.pack(fill='x', pady=(5, 15), padx=0)

            self.update_selectors()
            self._update_quick_access_buttons()
            self.window_created = True
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            # Make window focus and bring to front
            self.root.lift()
            self.root.focus_force()

        except Exception as e:
            print(f"Failed to create analysis control window: {e}")
            self.window_created = False

    def _on_frame_configure(self, event):
        """Update scroll region when the main frame size changes."""
        try:
            # Get the actual bounding box of all content
            bbox = self.canvas.bbox("all")
            if bbox:
                x1, y1, x2, y2 = bbox
                # Use actual content size for scroll region
                content_width = x2 - x1
                content_height = y2 - y1
                
                # Set scroll region to actual content size (this enables proper scrolling)
                self.canvas.configure(scrollregion=(0, 0, content_width, content_height))
            else:
                # If no content bounding box, use minimal scroll region
                self.canvas.configure(scrollregion=(0, 0, 1, 1))
        except Exception as e:
            if self.viewer:
                print(f"Error updating scroll region: {e}")
    
    def _on_canvas_configure(self, event):
        """Update the scrollable frame width when the canvas is resized."""
        try:
            # Update the width of the scrollable frame to match the canvas width
            canvas_width = event.width
            if canvas_width > 0 and hasattr(self, 'canvas_frame') and self.canvas_frame:
                self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
        except Exception as e:
            if self.viewer:
                print(f"Error configuring canvas: {e}")
    
    def _bind_mousewheel(self):
        """Bind mouse wheel scrolling to the canvas."""
        def _on_mousewheel(event):
            try:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        # Bind mouse wheel events when entering/leaving the window
        self.root.bind('<Enter>', _bind_to_mousewheel)
        self.root.bind('<Leave>', _unbind_from_mousewheel)
        
        # Also bind to canvas for better UX
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)

    def _create_section_frame(self, parent, title):
        section_frame = ttk.Frame(parent, style=self.theme_manager.get_frame_style())
        section_frame.pack(fill='x', pady=(5, 10), padx=2)
        
        inner_frame = ttk.Frame(section_frame, style=self.theme_manager.get_frame_style())
        inner_frame.pack(fill='x', padx=5, pady=12)
        
        header = ttk.Label(inner_frame, text=title, style="Header.TLabel")
        header.pack(fill='x', pady=(0, 8), padx=2)
        
        separator = ttk.Separator(inner_frame, orient='horizontal')
        separator.pack(fill='x', pady=(0, 12), padx=2)
        
        return inner_frame

    def _create_selection_section(self, parent_frame):
        selection_frame = self._create_section_frame(parent_frame, "Selection")

        # ROI Selection
        roi_frame = ttk.Frame(selection_frame, style=self.theme_manager.get_frame_style())
        roi_frame.pack(fill='x', pady=3, padx=8)
        roi_frame.columnconfigure(1, weight=1)
        
        roi_label = ttk.Label(roi_frame, text="ROI:", width=10, anchor='w')
        roi_label.grid(row=0, column=0, sticky='w', padx=(5, 12))
        Tooltip(roi_label, "Select a region of interest for analysis")
        
        self.roi_var = tk.StringVar(value="Full Image")
        self.roi_combo = ComboboxWithIndicator(
            roi_frame, 
            theme_manager=self.theme_manager,
            textvariable=self.roi_var, 
            state="readonly",
            max_dropdown_items=10
        )
        self.roi_combo.grid(row=0, column=1, sticky='ew')
        self.roi_combo.bind('<<ComboboxSelected>>', self._on_roi_select)
        Tooltip(self.roi_combo, "Choose a specific region of interest or use the full image")

        # Line Selection
        line_frame = ttk.Frame(selection_frame, style=self.theme_manager.get_frame_style())
        line_frame.pack(fill='x', pady=3, padx=8)
        line_frame.columnconfigure(1, weight=1)
        
        line_label = ttk.Label(line_frame, text="Line:", width=10, anchor='w')
        line_label.grid(row=0, column=0, sticky='w', padx=(5, 12))
        Tooltip(line_label, "Select a line for pixel profile analysis")
        
        self.line_var = tk.StringVar(value="All Lines")
        self.line_combo = ComboboxWithIndicator(
            line_frame, 
            theme_manager=self.theme_manager,
            textvariable=self.line_var, 
            state="readonly",
            max_dropdown_items=10
        )
        self.line_combo.grid(row=0, column=1, sticky='ew')
        self.line_combo.bind('<<ComboboxSelected>>', self._on_line_select)
        Tooltip(self.line_combo, "Choose a specific line or analyze all lines")

        # Polygon Selection
        poly_frame = ttk.Frame(selection_frame, style=self.theme_manager.get_frame_style())
        poly_frame.pack(fill='x', pady=3, padx=8)
        poly_frame.columnconfigure(1, weight=1)
        
        poly_label = ttk.Label(poly_frame, text="Polygon:", width=10, anchor='w')
        poly_label.grid(row=0, column=0, sticky='w', padx=(5, 12))
        Tooltip(poly_label, "Select a polygon for area analysis")
        
        self.polygon_var = tk.StringVar(value="All Polygons")
        self.polygon_combo = ComboboxWithIndicator(
            poly_frame, 
            theme_manager=self.theme_manager,
            textvariable=self.polygon_var, 
            state="readonly",
            max_dropdown_items=10
        )
        self.polygon_combo.grid(row=0, column=1, sticky='ew')
        self.polygon_combo.bind('<<ComboboxSelected>>', self._on_polygon_select)
        Tooltip(self.polygon_combo, "Choose a specific polygon or analyze all polygons")

    def _create_analysis_section(self, parent_frame):
        analysis_frame = self._create_section_frame(parent_frame, "Analysis")
        
        btn_style = self.theme_manager.get_button_style("primary")
        
        # Create a grid layout for better organization
        analysis_grid = ttk.Frame(analysis_frame, style=self.theme_manager.get_frame_style())
        analysis_grid.pack(fill='x', pady=5)
        analysis_grid.columnconfigure(0, weight=1, minsize=100)
        analysis_grid.columnconfigure(1, weight=1, minsize=100)
        
        hist_btn = ttk.Button(analysis_grid, text="📊 Show Histogram", command=self._show_histogram, style=btn_style)
        hist_btn.grid(row=0, column=0, padx=3, pady=3, sticky="ew")
        Tooltip(hist_btn, "Display histogram of the selected ROI or polygon (H key)")
        self.action_buttons['histogram'] = hist_btn

        prof_btn = ttk.Button(analysis_grid, text="📈 Show Profiles", command=self._show_profiles, style=btn_style)
        prof_btn.grid(row=0, column=1, padx=3, pady=3, sticky="ew")
        Tooltip(prof_btn, "Display pixel profiles of the selected lines (Shift+P)")
        self.action_buttons['profiles'] = prof_btn

        thresh_btn = ttk.Button(analysis_frame, text="🌡️ Thresholding", command=self._open_thresholding_window, style=btn_style)
        thresh_btn.pack(fill='x', pady=2)
        Tooltip(thresh_btn, "Open the thresholding window for image segmentation")
        self.action_buttons['thresholding'] = thresh_btn
        

    def _create_drawing_section(self, parent_frame):
        drawing_frame = self._create_section_frame(parent_frame, "Drawing Management")

        btn_style = self.theme_manager.get_button_style()
        warning_style = self.theme_manager.get_button_style()  # Use default for destructive actions
        
        # Edit tools
        edit_label = ttk.Label(drawing_frame, text="Edit Tools:", font=('TkDefaultFont', 9, 'bold'))
        edit_label.pack(anchor='w', pady=(0, 5))
        
        undo_btn = ttk.Button(drawing_frame, text="↶ Undo Last Point", command=self._undo_last_point, style=btn_style)
        undo_btn.pack(fill='x', pady=2)
        Tooltip(undo_btn, "Undo the last point of the current polygon (Ctrl+Z)")
        self.action_buttons['undo'] = undo_btn
        
        # Clear tools with warning styling
        clear_label = ttk.Label(drawing_frame, text="Clear Tools:", font=('TkDefaultFont', 9, 'bold'))
        clear_label.pack(anchor='w', pady=(10, 5))

        # Create a grid for clear buttons
        clear_grid = ttk.Frame(drawing_frame, style=self.theme_manager.get_frame_style())
        clear_grid.pack(fill='x', pady=2)
        clear_grid.columnconfigure(0, weight=1, minsize=100)
        clear_grid.columnconfigure(1, weight=1, minsize=100)

        clear_rect_btn = ttk.Button(clear_grid, text="🗑️ Clear Last Rectangle", command=self._clear_last_rectangle, style=warning_style)
        clear_rect_btn.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        Tooltip(clear_rect_btn, "Clear the last drawn rectangle/ROI")
        self.action_buttons['clear_rect'] = clear_rect_btn

        clear_line_btn = ttk.Button(clear_grid, text="🗑️ Clear Last Line", command=self._clear_last_line, style=warning_style)
        clear_line_btn.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        Tooltip(clear_line_btn, "Clear the last drawn line")
        self.action_buttons['clear_line'] = clear_line_btn

        clear_last_btn = ttk.Button(clear_grid, text="🗑️ Clear Last Polygon", command=self._clear_last_polygon, style=warning_style)
        clear_last_btn.grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        Tooltip(clear_last_btn, "Clear the last drawn polygon (Delete key)")
        self.action_buttons['clear_polygon'] = clear_last_btn

        clear_all_btn = ttk.Button(clear_grid, text="🗑️ Clear All Objects", command=self._clear_all, style=warning_style)
        clear_all_btn.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        Tooltip(clear_all_btn, "Clear all ROIs, lines, and polygons (Ctrl+Delete)")
        self.action_buttons['clear_all'] = clear_all_btn

    def _create_export_section(self, parent_frame):
        export_frame = self._create_section_frame(parent_frame, "Export & Plots")
        
        btn_style = self.theme_manager.get_button_style()
        
        # Export tools
        export_label = ttk.Label(export_frame, text="Export Data:", font=('TkDefaultFont', 9, 'bold'))
        export_label.pack(anchor='w', pady=(0, 5))
        
        export_data_btn = tk.Button(
            export_frame,
            text="📊 Export Analysis Data", 
            command=self._export_analysis_data,
            width=20,
            height=1,
            relief="raised",
            bd=2,
            font=('TkDefaultFont', 10, 'bold'),
            bg='#007bff',
            fg='white',
            activebackground='#0056b3',
            activeforeground='white'
        )
        export_data_btn.pack(fill='x', pady=3)
        Tooltip(export_data_btn, "Export histogram, profile, or polygon data to CSV/JSON/PNG (Ctrl+E)")
        self.action_buttons['export_data'] = export_data_btn
        
        # Plot management
        plots_label = ttk.Label(export_frame, text="Plot Management:", font=('TkDefaultFont', 9, 'bold'))
        plots_label.pack(anchor='w', pady=(10, 5))

        close_plots_btn = ttk.Button(export_frame, text="❌ Close All Plots", command=self._close_plots, style=btn_style)
        close_plots_btn.pack(fill='x', pady=3)
        Tooltip(close_plots_btn, "Close all open matplotlib windows (Ctrl+W)")
        self.action_buttons['close_plots'] = close_plots_btn
    
    def update_selectors(self):
        if not self.window_created: return
        try:
            # Update ROI selector
            try:
                roi_options = ["Full Image"] + [f"ROI {i+1}" for i in range(len(self.viewer.mouse.draw_rects))]
                self.roi_combo['values'] = roi_options  # Use direct assignment instead of set_values
                if self.roi_selection >= len(roi_options): self.roi_selection = 0
                self.roi_var.set(roi_options[self.roi_selection])
            except Exception as e:
                print(f"Error updating ROI selector: {e}")
            
            # Update Line selector
            try:
                line_options = ["All Lines"] + [f"Line {i+1}" for i in range(len(self.viewer.mouse.draw_lines))]
                self.line_combo['values'] = line_options  # Use direct assignment instead of set_values
                if self.line_selection >= len(line_options): self.line_selection = 0
                self.line_var.set(line_options[self.line_selection])
            except Exception as e:
                print(f"Error updating Line selector: {e}")

            # Update Polygon selector
            try:
                poly_options = ["All Polygons"] + [f"Polygon {i+1}" for i in range(len(self.viewer.mouse.draw_polygons))]
                self.polygon_combo['values'] = poly_options  # Use direct assignment instead of set_values
                if self.polygon_selection >= len(poly_options): self.polygon_selection = 0
                self.polygon_var.set(poly_options[self.polygon_selection])
            except Exception as e:
                print(f"Error updating Polygon selector: {e}")
                
        except Exception as e:
            print(f"Error updating selectors: {e}")
            pass
    
    def _on_roi_select(self, event):
        selection = self.roi_var.get()
        self.roi_selection = 0 if selection == "Full Image" else int(selection.split()[-1])
        
        prev_selection = self.viewer.mouse.selected_roi
        self.viewer.mouse.selected_roi = self.roi_selection - 1 if self.roi_selection > 0 else None
        
        changes = self.viewer.mouse.validate_selections()
        
        if changes['roi_changed']:
            if self.viewer.mouse.selected_roi is None:
                if prev_selection is not None:
                    pass
                elif self.roi_selection > 0:
                    pass
            else:
                pass
        
        self.viewer.update_display()

    def _on_line_select(self, event):
        selection = self.line_var.get()
        self.line_selection = 0 if selection == "All Lines" else int(selection.split()[-1])
        
        prev_selection = self.viewer.mouse.selected_line
        self.viewer.mouse.selected_line = self.line_selection - 1 if self.line_selection > 0 else None
        
        changes = self.viewer.mouse.validate_selections()
        
        if changes['line_changed']:
            if self.viewer.mouse.selected_line is None:
                if prev_selection is not None:
                    pass
                elif self.line_selection > 0:
                    pass
            else:
                pass
        
        self.viewer.update_display()

    def _on_polygon_select(self, event):
        selection = self.polygon_var.get()
        self.polygon_selection = 0 if selection == "All Polygons" else int(selection.split()[-1])
        
        prev_selection = self.viewer.mouse.selected_polygon
        self.viewer.mouse.selected_polygon = self.polygon_selection - 1 if self.polygon_selection > 0 else None
        
        changes = self.viewer.mouse.validate_selections()
        
        if changes['polygon_changed']:
            if self.viewer.mouse.selected_polygon is None:
                if prev_selection is not None:
                    pass
                elif self.polygon_selection > 0:
                    pass
            else:
                pass
        
        self.viewer.update_display()

    def _show_histogram(self):
        # Set as active button in analysis section
        self._set_active_button('analysis', 'histogram')
        
        if not self.viewer._internal_images: return
        current_idx = self.viewer.trackbar.parameters.get('show', 0)
        image, title = self.viewer._internal_images[current_idx]
        
        # Store current window focus and geometry to restore later
        current_focus = self.root.focus_get()
        current_geometry = self.root.geometry()
        current_title = self.root.title()
        
        try:
            if self.polygon_selection > 0:
                poly_index = self.polygon_selection - 1
                if poly_index < len(self.viewer.mouse.draw_polygons):
                    polygon = self.viewer.mouse.draw_polygons[poly_index]
                    self.viewer.analyzer.create_histogram_plot(image, polygon=polygon, title=f"{title} - Polygon {self.polygon_selection}")
            elif self.roi_selection > 0:
                roi_index = self.roi_selection - 1
                if roi_index < len(self.viewer.mouse.draw_rects):
                    roi = self.viewer.mouse.draw_rects[roi_index]
                    self.viewer.analyzer.create_histogram_plot(image, roi=roi, title=f"{title} - ROI {self.roi_selection}")
            else:
                self.viewer.analyzer.create_histogram_plot(image, title=f"{title} - Full Image")
        finally:
            # Restore window focus, geometry and title after matplotlib plot creation
            # Reduced delay since we're now using proper threading
            self.root.after(50, lambda: self._restore_window_state(current_focus, current_geometry, current_title))

    def _restore_window_state(self, focus_widget, geometry, title):
        """Restore window state after matplotlib plot creation."""
        try:
            # Restore window title (most important for user visibility)
            if self.root and self.root.winfo_exists():
                self.root.title(title or "Analysis Controls")
                
                # Restore window geometry without forcing minimum size
                if geometry:
                    self.root.geometry(geometry)
                
                # Restore focus if possible
                if focus_widget and hasattr(focus_widget, 'focus_set'):
                    try:
                        focus_widget.focus_set()
                    except:
                        self.root.focus_set()
                else:
                    self.root.focus_set()
                    
                # Ensure window is visible and properly drawn
                self.root.lift()
                self.root.update_idletasks()
                
                # Also refresh OpenCV window titles to ensure they remain visible
                if hasattr(self.viewer, 'windows') and self.viewer.windows:
                    self.viewer.windows.refresh_window_titles()
                    
        except Exception as e:
            print(f"Error restoring window state: {e}")

    def _show_profiles(self):
        # Set as active button in analysis section
        self._set_active_button('analysis', 'profiles')
        
        if not self.viewer._internal_images or not self.viewer.mouse.draw_lines: return
        current_idx = self.viewer.trackbar.parameters.get('show', 0)
        image, title = self.viewer._internal_images[current_idx]
        
        # Store current window state to restore later
        current_focus = self.root.focus_get()
        current_geometry = self.root.geometry()
        current_title = self.root.title()
        
        try:
            if self.line_selection == 0:
                for i, line in enumerate(self.viewer.mouse.draw_lines):
                    self.viewer.analyzer.create_pixel_profile_plot(image, line, f"{title} - Line {i+1}")
            else:
                line_index = self.line_selection - 1
                if line_index < len(self.viewer.mouse.draw_lines):
                    line = self.viewer.mouse.draw_lines[line_index]
                    self.viewer.analyzer.create_pixel_profile_plot(image, line, f"{title} - Line {self.line_selection}")
        finally:
            # Restore window state after matplotlib plot creation
            # Reduced delay since we're now using proper threading
            self.root.after(50, lambda: self._restore_window_state(current_focus, current_geometry, current_title))

    def _toggle_line_mode(self):
        self.viewer.mouse.is_line_mode = not self.viewer.mouse.is_line_mode
        self.viewer.mouse.is_polygon_mode = False
        self._update_quick_access_buttons()

    def _toggle_polygon_mode(self):
        self.viewer.mouse.is_polygon_mode = not self.viewer.mouse.is_polygon_mode
        self.viewer.mouse.is_line_mode = False
        self._update_quick_access_buttons()

    def _toggle_rectangle_mode(self):
        self.viewer.mouse.is_line_mode = False
        self.viewer.mouse.is_polygon_mode = False
        self._update_quick_access_buttons()

    def _undo_last_point(self):
        # Set as active button in drawing management section
        self._set_active_button('drawing_management', 'undo')
        
        if self.viewer.mouse.is_polygon_mode and self.viewer.mouse.current_polygon:
            self.viewer.mouse.undo_last_point()

    def _clear_last_rectangle(self):
        # Set as active button in drawing management section
        self._set_active_button('drawing_management', 'clear_rect')
        
        if self.viewer.mouse.draw_rects:
            if self.viewer.mouse.selected_roi == len(self.viewer.mouse.draw_rects) - 1:
                self.viewer.mouse.selected_roi = None
            
            self.viewer.mouse.draw_rects.pop()
            self.update_selectors()
            self.viewer.update_display()

    def _clear_last_line(self):
        # Set as active button in drawing management section
        self._set_active_button('drawing_management', 'clear_line')
        
        if self.viewer.mouse.draw_lines:
            if self.viewer.mouse.selected_line == len(self.viewer.mouse.draw_lines) - 1:
                self.viewer.mouse.selected_line = None
            
            self.viewer.mouse.draw_lines.pop()
            self.update_selectors()
            self.viewer.update_display()
        self.viewer.mouse.current_line = None

    def _clear_last_polygon(self):
        # Set as active button in drawing management section
        self._set_active_button('drawing_management', 'clear_polygon')
        
        if self.viewer.mouse.draw_polygons:
            if self.viewer.mouse.selected_polygon == len(self.viewer.mouse.draw_polygons) - 1:
                self.viewer.mouse.selected_polygon = None
            
            self.viewer.mouse.draw_polygons.pop()
            self.update_selectors()
            self.viewer.update_display()

    def _clear_all(self):
        # Set as active button in drawing management section
        self._set_active_button('drawing_management', 'clear_all')
        
        self.viewer.mouse.draw_rects.clear()
        self.viewer.mouse.draw_lines.clear()
        self.viewer.mouse.draw_polygons.clear()
        self.viewer.mouse.current_polygon.clear()
        self.viewer.mouse.current_line = None
        self.viewer.mouse.clear_selections()
        self.update_selectors()
        self.viewer.update_display()

    def _close_plots(self):
        # Set as active button in export_plots section
        self._set_active_button('export_plots', 'close_plots')
        
        print("📋 Close All Plots button clicked")
        if hasattr(self.viewer, 'analyzer') and self.viewer.analyzer:
            print("   → Calling analyzer.close_all_plots()")
            self.viewer.analyzer.close_all_plots()
            print("   → close_all_plots() completed")
        else:
            print("   → Error: No analyzer found on viewer")

        
    def _export_analysis_data(self):
        # Set as active button in export_plots section
        self._set_active_button('export_plots', 'export_data')
        
        print("📊 Export Analysis Data button clicked")
        
        if not self.viewer._internal_images:
            print("   → Error: No images available for analysis")
            messagebox.showinfo("Export Analysis", "No image available for analysis.")
            return
        
        print(f"   → Found {len(self.viewer._internal_images)} images available for export")
            
        current_idx = self.viewer.trackbar.parameters.get('show', 0)
        image, title = self.viewer._internal_images[current_idx]
        
        print(f"   → Current image: {title}, Index: {current_idx}")
        print(f"   → Image shape: {image.shape if image is not None else 'None'}")
        
        try:
            print("   → Creating enhanced export dialog...")
            export_dialog = EnhancedExportDialog(self.root, self.theme_manager)
            
            print("   → Showing export dialog...")
            export_dialog.show(
                filename_prefix=title.replace(' ', '_'),
                on_export=lambda export_type, export_format, full_path: self._handle_export(
                    export_type, export_format, full_path, image
                )
            )
            print("   → Export dialog displayed successfully")
        except Exception as e:
            print(f"   → Error creating/showing export dialog: {e}")
            messagebox.showerror("Export Error", f"Failed to open export dialog: {str(e)}")
        
    def _handle_export(self, export_type, export_format, full_path, image):
        print(f"📁 _handle_export called:")
        print(f"   → Export type: {export_type}")
        print(f"   → Export format: {export_format}")
        print(f"   → Full path: {full_path}")
        print(f"   → Image shape: {image.shape if image is not None else 'None'}")
        
        # Handle image export
        if export_format == "image":
            print("   → Processing image export...")
            if export_type == "histogram":
                success = self.viewer.analyzer.save_last_histogram_plot(full_path)
                if success:
                    messagebox.showinfo("Export Complete", f"Histogram plot image saved to {full_path}")
                else:
                    messagebox.showerror("Export Failed", "Failed to save histogram plot image")
            elif export_type == "profile":
                success = self.viewer.analyzer.save_last_profile_plot(full_path)
                if success:
                    messagebox.showinfo("Export Complete", f"Profile plot image saved to {full_path}")
                else:
                    messagebox.showerror("Export Failed", "Failed to save profile plot image")
            else:
                messagebox.showerror("Export Error", f"Image export not supported for {export_type}")
            return
        
        try:
            if export_type == "histogram":
                print("   → Processing histogram export...")
                if self.polygon_selection > 0:
                    print(f"   → Using polygon selection: {self.polygon_selection}")
                    poly_index = self.polygon_selection - 1
                    if poly_index < len(self.viewer.mouse.draw_polygons):
                        polygon = self.viewer.mouse.draw_polygons[poly_index]
                        print(f"   → Calculating histogram for polygon {poly_index}")
                        histogram_data = self.viewer.analyzer.calculate_histogram(image, polygon=polygon)
                        print(f"   → Histogram data keys: {list(histogram_data.keys()) if histogram_data else 'None'}")
                        print(f"   → Calling export_analysis_data...")
                        success = self.viewer.analyzer.export_analysis_data('histogram', histogram_data, export_format, full_path)
                        print(f"   → Export success: {success}")
                        if success:
                            messagebox.showinfo("Export Complete", f"Histogram data exported to {full_path}")
                        else:
                            messagebox.showerror("Export Failed", "Failed to export histogram data")
                    else:
                        print(f"   → Error: Invalid polygon index {poly_index}")
                        messagebox.showerror("Export Error", "Selected polygon is no longer valid")
                elif self.roi_selection > 0:
                    print(f"   → Using ROI selection: {self.roi_selection}")
                    roi_index = self.roi_selection - 1
                    if roi_index < len(self.viewer.mouse.draw_rects):
                        roi = self.viewer.mouse.draw_rects[roi_index]
                        print(f"   → Calculating histogram for ROI {roi_index}: {roi}")
                        histogram_data = self.viewer.analyzer.calculate_histogram(image, roi=roi)
                        print(f"   → Histogram data keys: {list(histogram_data.keys()) if histogram_data else 'None'}")
                        print(f"   → Calling export_analysis_data...")
                        success = self.viewer.analyzer.export_analysis_data('histogram', histogram_data, export_format, full_path)
                        print(f"   → Export success: {success}")
                        if success:
                            messagebox.showinfo("Export Complete", f"Histogram data exported to {full_path}")
                        else:
                            messagebox.showerror("Export Failed", "Failed to export histogram data")
                    else:
                        print(f"   → Error: Invalid ROI index {roi_index}")
                        messagebox.showerror("Export Error", "Selected ROI is no longer valid")
                else:
                    print("   → Using full image for histogram")
                    histogram_data = self.viewer.analyzer.calculate_histogram(image)
                    print(f"   → Histogram data keys: {list(histogram_data.keys()) if histogram_data else 'None'}")
                    print(f"   → Calling export_analysis_data...")
                    success = self.viewer.analyzer.export_analysis_data('histogram', histogram_data, export_format, full_path)
                    print(f"   → Export success: {success}")
                    if success:
                        messagebox.showinfo("Export Complete", f"Histogram data exported to {full_path}")
                    else:
                        messagebox.showerror("Export Failed", "Failed to export histogram data")
            
            elif export_type == "profile":
                print("   → Processing profile export...")
                if not self.viewer.mouse.draw_lines:
                    print("   → Error: No line profiles available")
                    messagebox.showinfo("Export Analysis", "No line profiles available to export.")
                    return
                
                print(f"   → Found {len(self.viewer.mouse.draw_lines)} line profiles")
                    
                if self.line_selection == 0:
                    print("   → Exporting all line profiles...")
                    base_path = os.path.splitext(full_path)[0]
                    exported_count = 0
                    
                    for i, line in enumerate(self.viewer.mouse.draw_lines):
                        line_path = f"{base_path}_line{i+1}.{export_format}"
                        print(f"   → Processing line {i+1}: {line}")
                        profile_data = self.viewer.analyzer.calculate_pixel_profile(image, line)
                        print(f"   → Profile data keys: {list(profile_data.keys()) if profile_data else 'None'}")
                        success = self.viewer.analyzer.export_analysis_data('profile', profile_data, export_format, line_path)
                        print(f"   → Export success for line {i+1}: {success}")
                        if success:
                            exported_count += 1
                            
                    if exported_count > 0:
                        messagebox.showinfo("Export Complete", f"Exported {exported_count} line profiles.")
                    else:
                        messagebox.showerror("Export Failed", "Failed to export any line profiles")
                else:
                    print(f"   → Exporting single line profile: {self.line_selection}")
                    line_index = self.line_selection - 1
                    if line_index < len(self.viewer.mouse.draw_lines):
                        line = self.viewer.mouse.draw_lines[line_index]
                        print(f"   → Processing line {line_index}: {line}")
                        profile_data = self.viewer.analyzer.calculate_pixel_profile(image, line)
                        print(f"   → Profile data keys: {list(profile_data.keys()) if profile_data else 'None'}")
                        success = self.viewer.analyzer.export_analysis_data('profile', profile_data, export_format, full_path)
                        print(f"   → Export success: {success}")
                        if success:
                            messagebox.showinfo("Export Complete", f"Profile data exported to {full_path}")
                        else:
                            messagebox.showerror("Export Failed", "Failed to export profile data")
                    else:
                        print(f"   → Error: Invalid line index {line_index}")
                        messagebox.showerror("Export Error", "Selected line is no longer valid")
                            
            elif export_type == "polygon":
                print("   → Processing polygon export...")
                if not self.viewer.mouse.draw_polygons:
                    print("   → Error: No polygons available")
                    messagebox.showinfo("Export Analysis", "No polygons available to export.")
                    return
                
                print(f"   → Found {len(self.viewer.mouse.draw_polygons)} polygons")
                
                if self.polygon_selection > 0:
                    print(f"   → Exporting single polygon: {self.polygon_selection}")
                    poly_index = self.polygon_selection - 1
                    if poly_index < len(self.viewer.mouse.draw_polygons):
                        polygon = [self.viewer.mouse.draw_polygons[poly_index]]
                        print(f"   → Processing polygon {poly_index}: {len(polygon[0])} points")
                        success = self.viewer.analyzer.export_analysis_data('polygon', polygon, export_format, full_path)
                        print(f"   → Export success: {success}")
                        if success:
                            messagebox.showinfo("Export Complete", f"Polygon data exported to {full_path}")
                        else:
                            messagebox.showerror("Export Failed", "Failed to export polygon data")
                    else:
                        print(f"   → Error: Invalid polygon index {poly_index}")
                        messagebox.showerror("Export Error", "Selected polygon is no longer valid")
                else:
                    print("   → Exporting all polygons...")
                    success = self.viewer.analyzer.export_analysis_data('polygon', self.viewer.mouse.draw_polygons, export_format, full_path)
                    print(f"   → Export success: {success}")
                    if success:
                        messagebox.showinfo("Export Complete", f"All polygon data exported to {full_path}")
                    else:
                        messagebox.showerror("Export Failed", "Failed to export polygon data")
                        
        except Exception as e:
            messagebox.showerror("Export Error", f"Error during export: {str(e)}")
            print(f"Export error: {str(e)}")

    def _open_thresholding_window(self):
        # Set as active button in analysis section
        self._set_active_button('analysis', 'thresholding')
        
        self.thresholding_manager.open_colorspace_selection_window()
        

    def _on_closing(self):
        self.thresholding_manager.cleanup_windows()
        self.destroy_window()
    
    def destroy_window(self):
        if self.window_created and self.root:
            try: 
                # Clean up mouse wheel bindings
                if hasattr(self, 'canvas'):
                    self.canvas.unbind_all("<MouseWheel>")
                self.root.destroy()
            except: 
                pass
            self.window_created = False
            self.root = None
            self.canvas = None
            self.main_frame = None
            self.scrollbar = None
            self.canvas_frame = None
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for quick access."""
        def on_key_press(event):
            try:
                key = event.keysym.lower()
                if key == 'r':
                    self._toggle_rectangle_mode()
                elif key == 'l':
                    self._toggle_line_mode()
                elif key == 'p' and not (event.state & 0x1):  # P without shift
                    self._toggle_polygon_mode()
                elif key == 'h':
                    self._show_histogram()
                elif key == 'p' and (event.state & 0x1):  # Shift+P
                    self._show_profiles()
                elif key == 'escape':
                    # Clear current drawing mode
                    if self.viewer.mouse.is_line_mode or self.viewer.mouse.is_polygon_mode:
                        self.viewer.mouse.is_line_mode = False
                        self.viewer.mouse.is_polygon_mode = False
                        self._update_quick_access_buttons()
            except Exception as e:
                if self.viewer:
                    print(f"Keyboard shortcut error: {e}")
        
        # Bind to the root window
        self.root.bind('<KeyPress>', on_key_press)
        self.root.focus_set()  # Make sure the window can receive key events

    def _create_quick_access_section(self, parent_frame):
        quick_frame = self._create_section_frame(parent_frame, "Drawing Tools")
        
        drawing_frame = ttk.Frame(quick_frame, style=self.theme_manager.get_frame_style())
        drawing_frame.pack(fill='x', pady=(0, 10))
        drawing_frame.columnconfigure(0, weight=1, minsize=100)
        drawing_frame.columnconfigure(1, weight=1, minsize=100)
        drawing_frame.columnconfigure(2, weight=1, minsize=100)
        
        rectangle_btn = ttk.Button(
            drawing_frame, 
            text="⬛ Rectangle Mode", 
            command=self._toggle_rectangle_mode,
            style=self.theme_manager.get_button_style()
        )
        rectangle_btn.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        Tooltip(rectangle_btn, "Toggle rectangle drawing mode (R key)")
        self.quick_access_buttons['rectangle_mode'] = rectangle_btn
        
        line_btn = ttk.Button(
            drawing_frame, 
            text="📏 Line Mode", 
            command=self._toggle_line_mode,
            style=self.theme_manager.get_button_style()
        )
        line_btn.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        Tooltip(line_btn, "Toggle line drawing mode (L key)")
        self.quick_access_buttons['line_mode'] = line_btn
        
        polygon_btn = ttk.Button(
            drawing_frame, 
            text="🔺 Polygon Mode", 
            command=self._toggle_polygon_mode,
            style=self.theme_manager.get_button_style()
        )
        polygon_btn.grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        Tooltip(polygon_btn, "Toggle polygon drawing mode (P key)")
        self.quick_access_buttons['polygon_mode'] = polygon_btn
        
        # Add keyboard bindings
        self._setup_keyboard_shortcuts()

    def _update_quick_access_buttons(self):
        """Update the state of quick access buttons based on active modes."""
        if not self.window_created or not self.quick_access_buttons:
            return
            
        try:
            # Rectangle mode is active when neither line nor polygon mode is active
            is_rectangle_mode = not self.viewer.mouse.is_line_mode and not self.viewer.mouse.is_polygon_mode
            
            # Update rectangle mode button
            if self.quick_access_buttons.get('rectangle_mode'):
                style = self.theme_manager.get_button_style("active") if is_rectangle_mode else self.theme_manager.get_button_style()
                self.quick_access_buttons['rectangle_mode'].config(style=style)
                
            # Update line mode button
            if self.quick_access_buttons.get('line_mode'):
                style = self.theme_manager.get_button_style("active") if self.viewer.mouse.is_line_mode else self.theme_manager.get_button_style()
                self.quick_access_buttons['line_mode'].config(style=style)
                
            # Update polygon mode button
            if self.quick_access_buttons.get('polygon_mode'):
                style = self.theme_manager.get_button_style("active") if self.viewer.mouse.is_polygon_mode else self.theme_manager.get_button_style()
                self.quick_access_buttons['polygon_mode'].config(style=style)
        except Exception as e:
            print(f"Error updating quick access buttons: {e}")

    def _set_active_button(self, section, button_key):
        """Set a button as active and update visual states for the section."""
        if not self.action_buttons or not self.window_created:
            return
            
        try:
            # Clear previous active button in this section
            if self.active_states.get(section):
                prev_button = self.action_buttons.get(self.active_states[section])
                if prev_button and prev_button.winfo_exists():
                    # Check if it's a tk.Button or ttk.Button
                    if isinstance(prev_button, tk.Button):
                        # Handle tk.Button styling - restore original colors
                        if self.active_states[section] == 'export_data':
                            prev_button.config(
                                bg='#007bff',
                                fg='white',
                                relief="raised",
                                bd=2,
                                activebackground='#0056b3'
                            )
                    else:
                        # Handle ttk.Button styling
                        prev_button.config(style=self.theme_manager.get_button_style())
            
            # Set new active button
            self.active_states[section] = button_key
            current_button = self.action_buttons.get(button_key)
            if current_button and current_button.winfo_exists():
                # Check if it's a tk.Button or ttk.Button
                if isinstance(current_button, tk.Button):
                    # Handle tk.Button styling - apply active green style
                    current_button.config(
                        bg='#28a745',
                        fg='white',
                        relief="solid",
                        bd=2,
                        activebackground='#1e7e34'
                    )
                else:
                    # Handle ttk.Button styling
                    current_button.config(style=self.theme_manager.get_button_style("active"))
                    
        except Exception as e:
            if self.viewer:
                print(f"Button state error: {e}")
                
    def _rebind_canvas_events(self):
        """Re-bind canvas events after button state changes."""
        # This method is no longer needed since we're not unbinding events
        pass

    def _provide_button_feedback(self, button):
        """Provide visual feedback when action buttons are clicked."""
        if not button:
            return
            
        try:
            # Store original style
            original_style = button.cget('style')
            
            # Change to active style temporarily
            button.config(style=self.theme_manager.get_button_style("active"))
            
            # Schedule return to original style after 200ms
            self.root.after(200, lambda: button.config(style=original_style))
        except Exception as e:
            if self.viewer:
                print(f"Button feedback error: {e}")
