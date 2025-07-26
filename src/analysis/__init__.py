from .plotting.plot_analyzer import PlotAnalyzer
from .export.export_manager import ExportManager

# For backward compatibility
class ImageAnalyzer:
    """Compatibility class that delegates to PlotAnalyzer and ExportManager."""
    
    def __init__(self):
        self._plot_analyzer = PlotAnalyzer()
        self._export_manager = ExportManager()
    
    def create_pixel_profile_plot(self, *args, **kwargs):
        return self._plot_analyzer.create_pixel_profile_plot(*args, **kwargs)
    
    def create_histogram_plot(self, *args, **kwargs):
        return self._plot_analyzer.create_histogram_plot(*args, **kwargs)
    
    def export_analysis_data(self, *args, **kwargs):
        return self._export_manager.export_analysis_data(*args, **kwargs)
    
    def calculate_histogram(self, *args, **kwargs):
        return self._plot_analyzer.calculate_histogram(*args, **kwargs)
    
    def calculate_pixel_profile(self, *args, **kwargs):
        return self._plot_analyzer.calculate_pixel_profile(*args, **kwargs)
    
    def close_all_plots(self):
        return self._plot_analyzer.close_all_plots()

__all__ = ["ImageAnalyzer", "PlotAnalyzer", "ExportManager"]