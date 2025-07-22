import tkinter as tk
from tkinter import ttk
import json
import os
from typing import Dict, Any, List, Optional, Callable

class PlotCustomizationDialog:
    """
    Dialog for customizing plot appearance and saving/loading plot presets.
    """
    
    CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".parameter_plot_settings.json")
    
    def __init__(self, parent, theme_manager, plot_type="histogram"):
        """
        Initialize the plot customization dialog.
        
        Args:
            parent: Parent window
            theme_manager: ThemeManager instance for styling
            plot_type: Type of plot to customize ('histogram' or 'profile')
        """
        self.parent = parent
        self.theme_manager = theme_manager
        self.plot_type = plot_type
        self.dialog = None
        self.settings = self._load_settings()
        
        # Default values based on plot type
        if plot_type == "histogram":
            self.default_settings = {
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
            }
        else:  # profile
            self.default_settings = {
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
            }
        
        self.current_settings = self.settings.get(f"{plot_type}_settings", self.default_settings.copy())
        
        self.figure_width = tk.IntVar(value=self.current_settings["figure_size"][0])
        self.figure_height = tk.IntVar(value=self.current_settings["figure_size"][1])
        self.dpi = tk.IntVar(value=self.current_settings["dpi"])
        self.grid = tk.BooleanVar(value=self.current_settings["grid"])
        self.grid_alpha = tk.DoubleVar(value=self.current_settings["grid_alpha"])
        self.title_fontsize = tk.IntVar(value=self.current_settings["title_fontsize"])
        self.axis_fontsize = tk.IntVar(value=self.current_settings["axis_fontsize"])
        self.line_width = tk.DoubleVar(value=self.current_settings["line_width"])
        self.line_alpha = tk.DoubleVar(value=self.current_settings["line_alpha"])
        self.show_legend = tk.BooleanVar(value=self.current_settings["show_legend"])
        
        self.colors = {}
        for color_name, color_value in self.current_settings["colors"].items():
            self.colors[color_name] = tk.StringVar(value=color_value)
        
        self.preset_name = tk.StringVar(value="")
        
        self.on_apply_callback = None
        self.on_cancel_callback = None
        
    def _load_settings(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            return {
                "histogram_settings": {},
                "profile_settings": {},
                "presets": {}
            }
        except Exception:
            return {
                "histogram_settings": {},
                "profile_settings": {},
                "presets": {}
            }
            
    def _save_settings(self):
        try:
            self.settings[f"{self.plot_type}_settings"] = self._get_current_settings()
            
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving plot settings: {e}")
            
    def _get_current_settings(self) -> Dict[str, Any]:
        settings = {
            "figure_size": (self.figure_width.get(), self.figure_height.get()),
            "dpi": self.dpi.get(),
            "grid": self.grid.get(),
            "grid_alpha": self.grid_alpha.get(),
            "title_fontsize": self.title_fontsize.get(),
            "axis_fontsize": self.axis_fontsize.get(),
            "line_width": self.line_width.get(),
            "line_alpha": self.line_alpha.get(),
            "show_legend": self.show_legend.get(),
            "colors": {}
        }
        
        for color_name, color_var in self.colors.items():
            settings["colors"][color_name] = color_var.get()
            
        return settings
            
    def show(self, on_apply=None, on_cancel=None):
        self.on_apply_callback = on_apply
        self.on_cancel_callback = on_cancel
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Customize {self.plot_type.capitalize()} Plot")
        self.dialog.geometry("500x600")
        self.dialog.minsize(450, 550)
        self.dialog.resizable(True, True)
        
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.theme_manager.configure_theme(self.dialog)
        
        self._center_on_parent()
        
        self._create_dialog_content()
        
        self.parent.wait_window(self.dialog)
        
    def _center_on_parent(self):
        if not self.dialog or not self.parent:
            return
            
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f" +{x}+{y}")
        
    def _create_dialog_content(self):
        main_frame = ttk.Frame(self.dialog, style=self.theme_manager.get_frame_style())
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        title_label = ttk.Label(
            main_frame, 
            text=f"Customize {self.plot_type.capitalize()} Plot", 
            style=self.theme_manager.get_label_style("header")
        )
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        general_tab = ttk.Frame(notebook, style=self.theme_manager.get_frame_style())
        colors_tab = ttk.Frame(notebook, style=self.theme_manager.get_frame_style())
        presets_tab = ttk.Frame(notebook, style=self.theme_manager.get_frame_style())
        
        notebook.add(general_tab, text="General")
        notebook.add(colors_tab, text="Colors")
        notebook.add(presets_tab, text="Presets")
        
        self._create_general_tab(general_tab)
        self._create_colors_tab(colors_tab)
        self._create_presets_tab(presets_tab)
        
        self._create_button_section(main_frame)
        
    def _create_general_tab(self, parent):
        parent.pack(padx=10, pady=10, fill='both', expand=True)
        size_frame = ttk.LabelFrame(
            parent, 
            text="Figure Size", 
            style=self.theme_manager.get_frame_style()
        )
        size_frame.pack(fill=tk.X, pady=5, padx=10)
        
        width_frame = ttk.Frame(size_frame, style=self.theme_manager.get_frame_style())
        width_frame.pack(fill=tk.X, pady=2)
        
        width_label = ttk.Label(width_frame, text="Width:")
        width_label.pack(side=tk.LEFT, padx=(0, 5))
        
        width_spinbox = ttk.Spinbox(
            width_frame, 
            from_=4, 
            to=20, 
            increment=1, 
            textvariable=self.figure_width,
            width=5
        )
        width_spinbox.pack(side=tk.LEFT)
        
        height_frame = ttk.Frame(size_frame, style=self.theme_manager.get_frame_style())
        height_frame.pack(fill=tk.X, pady=2)
        
        height_label = ttk.Label(height_frame, text="Height:")
        height_label.pack(side=tk.LEFT, padx=(0, 5))
        
        height_spinbox = ttk.Spinbox(
            height_frame, 
            from_=3, 
            to=15, 
            increment=1, 
            textvariable=self.figure_height,
            width=5
        )
        height_spinbox.pack(side=tk.LEFT)
        
        dpi_frame = ttk.Frame(size_frame, style=self.theme_manager.get_frame_style())
        dpi_frame.pack(fill=tk.X, pady=2)
        
        dpi_label = ttk.Label(dpi_frame, text="DPI:")
        dpi_label.pack(side=tk.LEFT, padx=(0, 5))
        
        dpi_spinbox = ttk.Spinbox(
            dpi_frame, 
            from_=72, 
            to=300, 
            increment=1, 
            textvariable=self.dpi,
            width=5
        )
        dpi_spinbox.pack(side=tk.LEFT)
        
        grid_frame = ttk.LabelFrame(
            parent, 
            text="Grid", 
            style=self.theme_manager.get_frame_style()
        )
        grid_frame.pack(fill=tk.X, pady=5, padx=10)
        
        grid_check = ttk.Checkbutton(
            grid_frame, 
            text="Show Grid", 
            variable=self.grid
        )
        grid_check.pack(anchor=tk.W, pady=2)
        
        grid_alpha_frame = ttk.Frame(grid_frame, style=self.theme_manager.get_frame_style())
        grid_alpha_frame.pack(fill=tk.X, pady=2)
        
        grid_alpha_label = ttk.Label(grid_alpha_frame, text="Grid Opacity:")
        grid_alpha_label.pack(side=tk.LEFT, padx=(0, 5))
        
        grid_alpha_scale = ttk.Scale(
            grid_alpha_frame, 
            from_=0.1, 
            to=1.0, 
            orient=tk.HORIZONTAL, 
            variable=self.grid_alpha
        )
        grid_alpha_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        font_frame = ttk.LabelFrame(
            parent, 
            text="Font Sizes", 
            style=self.theme_manager.get_frame_style()
        )
        font_frame.pack(fill=tk.X, pady=5, padx=10)
        
        title_font_frame = ttk.Frame(font_frame, style=self.theme_manager.get_frame_style())
        title_font_frame.pack(fill=tk.X, pady=2)
        
        title_font_label = ttk.Label(title_font_frame, text="Title:")
        title_font_label.pack(side=tk.LEFT, padx=(0, 5))
        
        title_font_spinbox = ttk.Spinbox(
            title_font_frame, 
            from_=8, 
            to=24, 
            increment=1, 
            textvariable=self.title_fontsize,
            width=5
        )
        title_font_spinbox.pack(side=tk.LEFT)
        
        axis_font_frame = ttk.Frame(font_frame, style=self.theme_manager.get_frame_style())
        axis_font_frame.pack(fill=tk.X, pady=2)
        
        axis_font_label = ttk.Label(axis_font_frame, text="Axes:")
        axis_font_label.pack(side=tk.LEFT, padx=(0, 5))
        
        axis_font_spinbox = ttk.Spinbox(
            axis_font_frame, 
            from_=8, 
            to=20, 
            increment=1, 
            textvariable=self.axis_fontsize,
            width=5
        )
        axis_font_spinbox.pack(side=tk.LEFT)
        
        line_frame = ttk.LabelFrame(
            parent, 
            text="Line Properties", 
            style=self.theme_manager.get_frame_style()
        )
        line_frame.pack(fill=tk.X, pady=5, padx=10)
        
        line_width_frame = ttk.Frame(line_frame, style=self.theme_manager.get_frame_style())
        line_width_frame.pack(fill=tk.X, pady=2)
        
        line_width_label = ttk.Label(line_width_frame, text="Width:")
        line_width_label.pack(side=tk.LEFT, padx=(0, 5))
        
        line_width_spinbox = ttk.Spinbox(
            line_width_frame, 
            from_=0.5, 
            to=5.0, 
            increment=0.5, 
            textvariable=self.line_width,
            width=5
        )
        line_width_spinbox.pack(side=tk.LEFT)
        
        line_alpha_frame = ttk.Frame(line_frame, style=self.theme_manager.get_frame_style())
        line_alpha_frame.pack(fill=tk.X, pady=2)
        
        line_alpha_label = ttk.Label(line_alpha_frame, text="Opacity:")
        line_alpha_label.pack(side=tk.LEFT, padx=(0, 5))
        
        line_alpha_scale = ttk.Scale(
            line_alpha_frame, 
            from_=0.1, 
            to=1.0, 
            orient=tk.HORIZONTAL, 
            variable=self.line_alpha
        )
        line_alpha_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        legend_check = ttk.Checkbutton(
            line_frame, 
            text="Show Legend", 
            variable=self.show_legend
        )
        legend_check.pack(anchor=tk.W, pady=2)
        
    def _create_colors_tab(self, parent):
        parent.pack(padx=10, pady=10, fill='both', expand=True)
        color_frame = ttk.LabelFrame(
            parent, 
            text="Channel Colors", 
            style=self.theme_manager.get_frame_style()
        )
        color_frame.pack(fill=tk.X, pady=5, padx=10)
        
        for color_name in self.colors.keys():
            color_var = self.colors[color_name]
            
            channel_frame = ttk.Frame(color_frame, style=self.theme_manager.get_frame_style())
            channel_frame.pack(fill=tk.X, pady=2)
            
            channel_label = ttk.Label(channel_frame, text=f"{color_name.capitalize()}:")
            channel_label.pack(side=tk.LEFT, padx=(0, 5))
            
            color_entry = ttk.Entry(
                channel_frame, 
                textvariable=color_var,
                width=10
            )
            color_entry.pack(side=tk.LEFT)
            
            preview_frame = tk.Frame(channel_frame, width=20, height=20)
            preview_frame.pack(side=tk.LEFT, padx=5)
            
            def update_preview(var_name, index, mode, frame=preview_frame, color_var=color_var):
                try:
                    color = color_var.get()
                    frame.configure(background=color)
                except:
                    frame.configure(background="gray")
            
            color_var.trace_add("write", update_preview)
            update_preview(None, None, None)
            
            def show_color_picker(color_var=color_var):
                colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#000000"]
                
                popup = tk.Toplevel(self.dialog)
                popup.title("Select Color")
                popup.geometry("200x150")
                popup.transient(self.dialog)
                popup.grab_set()
                
                self.theme_manager.configure_theme(popup)
                
                for i, color in enumerate(colors):
                    btn = ttk.Button(
                        popup, 
                        text="", 
                        width=3,
                        command=lambda c=color: [color_var.set(c), popup.destroy()]
                    )
                    btn.grid(row=i//4, column=i%4, padx=5, pady=5)
                    
                    lbl = tk.Label(popup, text="   ", background=color)
                    lbl.grid(row=i//4, column=i%4+1, padx=5, pady=5)
            
            color_btn = ttk.Button(
                channel_frame, 
                text="...", 
                width=3,
                command=lambda cv=color_var: show_color_picker(cv)
            )
            color_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = ttk.Button(
            color_frame, 
            text="Reset to Default Colors", 
            command=self._reset_colors,
            style=self.theme_manager.get_button_style()
        )
        reset_btn.pack(pady=10)
        
    def _reset_colors(self):
        for color_name, color_value in self.default_settings["colors"].items():
            if color_name in self.colors:
                self.colors[color_name].set(color_value)
        
    def _create_presets_tab(self, parent):
        parent.pack(padx=10, pady=10, fill='both', expand=True)
        presets_frame = ttk.LabelFrame(
            parent, 
            text="Saved Presets", 
            style=self.theme_manager.get_frame_style()
        )
        presets_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        plot_presets = self.settings.get("presets", {}).get(self.plot_type, {})
        
        if not plot_presets:
            no_presets_label = ttk.Label(
                presets_frame, 
                text="No saved presets found.\nCreate a new preset below."
            )
            no_presets_label.pack(pady=20)
        else:
            preset_list_frame = ttk.Frame(presets_frame, style=self.theme_manager.get_frame_style())
            preset_list_frame.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(preset_list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            preset_listbox = tk.Listbox(
                preset_list_frame,
                height=5,
                selectmode=tk.SINGLE,
                yscrollcommand=scrollbar.set
            )
            preset_listbox.pack(fill=tk.BOTH, expand=True)
            scrollbar.config(command=preset_listbox.yview)
            
            for preset_name in plot_presets.keys():
                preset_listbox.insert(tk.END, preset_name)
            
            preset_buttons_frame = ttk.Frame(presets_frame, style=self.theme_manager.get_frame_style())
            preset_buttons_frame.pack(fill=tk.X, pady=5)
            
            load_btn = ttk.Button(
                preset_buttons_frame, 
                text="Load", 
                command=lambda: self._load_preset(preset_listbox),
                style=self.theme_manager.get_button_style("primary")
            )
            load_btn.pack(side=tk.LEFT, padx=5)
            
            delete_btn = ttk.Button(
                preset_buttons_frame, 
                text="Delete", 
                command=lambda: self._delete_preset(preset_listbox),
                style=self.theme_manager.get_button_style()
            )
            delete_btn.pack(side=tk.LEFT)
        
        save_preset_frame = ttk.LabelFrame(
            parent, 
            text="Save New Preset", 
            style=self.theme_manager.get_frame_style()
        )
        save_preset_frame.pack(fill=tk.X, pady=5, padx=10)
        
        name_frame = ttk.Frame(save_preset_frame, style=self.theme_manager.get_frame_style())
        name_frame.pack(fill=tk.X, pady=2)
        
        name_label = ttk.Label(name_frame, text="Name:")
        name_label.pack(side=tk.LEFT, padx=(0, 5))
        
        name_entry = ttk.Entry(
            name_frame, 
            textvariable=self.preset_name
        )
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        save_btn = ttk.Button(
            save_preset_frame, 
            text="Save Current Settings as Preset", 
            command=self._save_preset,
            style=self.theme_manager.get_button_style("primary")
        )
        save_btn.pack(fill=tk.X, pady=5)
        
    def _load_preset(self, listbox):
        selection = listbox.curselection()
        if not selection:
            return
            
        preset_name = listbox.get(selection[0])
        preset_data = self.settings.get("presets", {}).get(self.plot_type, {}).get(preset_name)
        
        if not preset_data:
            return
            
        if "figure_size" in preset_data:
            self.figure_width.set(preset_data["figure_size"][0])
            self.figure_height.set(preset_data["figure_size"][1])
        
        if "dpi" in preset_data:
            self.dpi.set(preset_data["dpi"])
            
        if "grid" in preset_data:
            self.grid.set(preset_data["grid"])
            
        if "grid_alpha" in preset_data:
            self.grid_alpha.set(preset_data["grid_alpha"])
            
        if "title_fontsize" in preset_data:
            self.title_fontsize.set(preset_data["title_fontsize"])
            
        if "axis_fontsize" in preset_data:
            self.axis_fontsize.set(preset_data["axis_fontsize"])
            
        if "line_width" in preset_data:
            self.line_width.set(preset_data["line_width"])
            
        if "line_alpha" in preset_data:
            self.line_alpha.set(preset_data["line_alpha"])
            
        if "show_legend" in preset_data:
            self.show_legend.set(preset_data["show_legend"])
            
        if "colors" in preset_data:
            for color_name, color_value in preset_data["colors"].items():
                if color_name in self.colors:
                    self.colors[color_name].set(color_value)
        
    def _delete_preset(self, listbox):
        selection = listbox.curselection()
        if not selection:
            return
            
        preset_name = listbox.get(selection[0])
        
        if self.plot_type in self.settings.get("presets", {}):
            if preset_name in self.settings["presets"][self.plot_type]:
                del self.settings["presets"][self.plot_type][preset_name]
                
                self._save_settings()
                
                listbox.delete(selection[0])
        
    def _save_preset(self):
        preset_name = self.preset_name.get().strip()
        if not preset_name:
            return
            
        preset_data = self._get_current_settings()
        
        if "presets" not in self.settings:
            self.settings["presets"] = {}
            
        if self.plot_type not in self.settings["presets"]:
            self.settings["presets"][self.plot_type] = {}
            
        self.settings["presets"][self.plot_type][preset_name] = preset_data
        
        self._save_settings()
        
        self.preset_name.set("")
        
        self.dialog.destroy()
        self.show(self.on_apply_callback, self.on_cancel_callback)
        
    def _create_button_section(self, parent):
        button_frame = ttk.Frame(parent, style=self.theme_manager.get_frame_style())
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        reset_btn = ttk.Button(
            button_frame, 
            text="Reset All", 
            command=self._reset_all,
            style=self.theme_manager.get_button_style()
        )
        reset_btn.pack(side=tk.LEFT)
        
        cancel_btn = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self._on_cancel,
            style=self.theme_manager.get_button_style()
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        apply_btn = ttk.Button(
            button_frame, 
            text="Apply", 
            command=self._on_apply,
            style=self.theme_manager.get_button_style("primary")
        )
        apply_btn.pack(side=tk.RIGHT)
        
    def _reset_all(self):
        self.figure_width.set(self.default_settings["figure_size"][0])
        self.figure_height.set(self.default_settings["figure_size"][1])
        
        self.dpi.set(self.default_settings["dpi"])
        
        self.grid.set(self.default_settings["grid"])
        self.grid_alpha.set(self.default_settings["grid_alpha"])
        
        self.title_fontsize.set(self.default_settings["title_fontsize"])
        self.axis_fontsize.set(self.default_settings["axis_fontsize"])
        
        self.line_width.set(self.default_settings["line_width"])
        self.line_alpha.set(self.default_settings["line_alpha"])
        self.show_legend.set(self.default_settings["show_legend"])
        
        self._reset_colors()
        
    def _on_apply(self):
        self._save_settings()
        
        settings = self._get_current_settings()
        
        self.dialog.destroy()
        
        if self.on_apply_callback:
            self.on_apply_callback(settings)
            
    def _on_cancel(self):
        self.dialog.destroy()
        
        if self.on_cancel_callback:
            self.on_cancel_callback()
