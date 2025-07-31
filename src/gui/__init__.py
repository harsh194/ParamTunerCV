"""
GUI module initialization for the Parameter image viewer application.

This module provides the main GUI components and interfaces for the Parameter
project, including window management, analysis controls, thresholding interfaces,
and theme management. It serves as the central entry point for all GUI-related
functionality.

Main Components:
    - WindowManager: OpenCV window management and lifecycle control
    - AnalysisControlWindow: Professional analysis interface with controls
    - ThresholdingManager: Centralized thresholding operation management
    - ThresholdingWindow: Interactive thresholding interface
    - ThemeManager: Comprehensive theme and styling management

Public API:
    The module exports three main classes through __all__:
    - WindowManager: For OpenCV window operations
    - AnalysisControlWindow: For analysis control interfaces
    - ThemeManager: For theme and styling management

Additional Components:
    While not exported in __all__, the module also provides:
    - ThresholdingManager: For advanced thresholding operations
    - ThresholdingWindow: For detailed thresholding interfaces
    - Enhanced widgets and dialogs for specialized functionality

Usage:
    from src.gui import WindowManager, AnalysisControlWindow, ThemeManager
    
    # Or import specific components:
    from src.gui.thresholding_manager import ThresholdingManager
    from src.gui.enhanced_export_dialog import EnhancedExportDialog

Architecture:
    The GUI module follows a modular design with clear separation of concerns:
    - Window management handles OpenCV window lifecycle
    - Analysis controls provide interactive parameter adjustment
    - Thresholding components offer specialized image segmentation tools
    - Theme management ensures consistent styling across all interfaces
    - Enhanced widgets provide improved user experience
"""

from .window_manager import WindowManager
from .analysis_control_window import AnalysisControlWindow
from .thresholding_manager import ThresholdingManager
from .thresholding_window import ThresholdingWindow
from .theme_manager import ThemeManager

__all__ = ['WindowManager', 'AnalysisControlWindow', 'ThemeManager']
