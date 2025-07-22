import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.theme_manager import ThemeManager

def main():
    """Test the theme manager."""
    root = tk.Tk()
    root.title("Theme Manager Test")
    root.geometry("500x400")
    
    # Create theme manager
    theme_manager = ThemeManager(use_dark_mode=False)
    theme_manager.configure_theme(root)
    
    # Create main frame
    main_frame = ttk.Frame(root, style=theme_manager.get_frame_style())
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    # Create a label
    title_label = ttk.Label(
        main_frame, 
        text="Theme Manager Test", 
        style=theme_manager.get_label_style("header")
    )
    title_label.pack(fill=tk.X, pady=(0, 10))
    
    # Create a button
    primary_btn = ttk.Button(
        main_frame, 
        text="Primary Button", 
        style=theme_manager.get_button_style("primary")
    )
    primary_btn.pack(fill=tk.X, pady=5)
    theme_manager.create_tooltip(primary_btn, "This is a primary button")
    
    secondary_btn = ttk.Button(
        main_frame, 
        text="Secondary Button", 
        style=theme_manager.get_button_style("secondary")
    )
    secondary_btn.pack(fill=tk.X, pady=5)
    theme_manager.create_tooltip(secondary_btn, "This is a secondary button")
    
    default_btn = ttk.Button(
        main_frame, 
        text="Default Button", 
        style=theme_manager.get_button_style()
    )
    default_btn.pack(fill=tk.X, pady=5)
    theme_manager.create_tooltip(default_btn, "This is a default button")
    
    # Create a toggle button for theme
    def toggle_theme():
        is_dark = theme_manager.toggle_theme()
        theme_manager.configure_theme(root)
        theme_label.config(text=f"Current Theme: {'Dark' if is_dark else 'Light'}")
    
    theme_btn = ttk.Button(
        main_frame, 
        text="Toggle Theme", 
        command=toggle_theme,
        style=theme_manager.get_button_style()
    )
    theme_btn.pack(fill=tk.X, pady=5)
    
    theme_label = ttk.Label(
        main_frame, 
        text=f"Current Theme: {'Dark' if theme_manager.use_dark_mode else 'Light'}"
    )
    theme_label.pack(pady=5)
    
    # Create a section with a frame
    section_frame = ttk.LabelFrame(
        main_frame, 
        text="Section Frame", 
        style=theme_manager.get_frame_style()
    )
    section_frame.pack(fill=tk.X, pady=10, padx=10)
    
    # Add some content to the section
    section_label = ttk.Label(
        section_frame, 
        text="This is a section frame"
    )
    section_label.pack(pady=5)
    
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

if __name__ == "__main__":
    main()