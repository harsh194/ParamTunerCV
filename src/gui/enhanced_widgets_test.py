import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.theme_manager import ThemeManager
from gui.plot_customization_dialog import PlotCustomizationDialog

def main():
    """Test the plot customization dialog."""
    root = tk.Tk()
    root.title("Plot Customization Test")
    root.geometry("400x300")
    
    # Create theme manager
    theme_manager = ThemeManager(use_dark_mode=True)
    theme_manager.configure_theme(root)
    
    # Create main frame
    main_frame = ttk.Frame(root, style=theme_manager.get_frame_style())
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    # Create buttons to open plot customization dialogs
    histogram_btn = ttk.Button(
        main_frame, 
        text="Customize Histogram Plot", 
        command=lambda: open_customization_dialog(root, theme_manager, "histogram"),
        style=theme_manager.get_button_style("primary")
    )
    histogram_btn.pack(fill=tk.X, pady=10)
    
    profile_btn = ttk.Button(
        main_frame, 
        text="Customize Profile Plot", 
        command=lambda: open_customization_dialog(root, theme_manager, "profile"),
        style=theme_manager.get_button_style("primary")
    )
    profile_btn.pack(fill=tk.X, pady=10)
    
    # Create exit button
    exit_btn = ttk.Button(
        main_frame, 
        text="Exit", 
        command=root.destroy,
        style=theme_manager.get_button_style()
    )
    exit_btn.pack(fill=tk.X, pady=10)
    
    # Start main loop
    root.mainloop()

def open_customization_dialog(root, theme_manager, plot_type):
    """Open the plot customization dialog."""
    dialog = PlotCustomizationDialog(root, theme_manager, plot_type=plot_type)
    dialog.show(
        on_apply=lambda settings: print(f"Applied {plot_type} settings: {settings}")
    )

if __name__ == "__main__":
    main()