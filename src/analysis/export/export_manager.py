"""Export functionality for the Parameter project.

This module provides capabilities for exporting analysis data to various formats
including JSON and CSV. It handles different types of data such as histograms,
pixel profiles, and polygon coordinates with proper serialization and formatting.

Main Classes:
    ExportManager: Manages the export of analysis data to different file formats

Usage:
    export_manager = ExportManager()
    export_manager.export_analysis_data('histogram', histogram_data, 'json', 'my_histogram')
"""

import json
import csv
import os
from typing import Any, Dict, List, Tuple, Optional

class ExportManager:
    """Manages the export of analysis data to various file formats.
    
    This class provides methods to export different types of analysis data
    (histograms, pixel profiles, polygons) to common file formats like JSON and CSV.
    It handles the formatting and serialization of data appropriate to each
    export format, including conversion of numpy arrays to JSON-serializable types.
    
    The class supports three main analysis data types:
    - Histogram data: Channel-based intensity distributions
    - Profile data: Pixel intensity profiles along lines
    - Polygon data: Coordinate lists defining geometric regions
    
    Attributes:
        None
    
    Examples:
        >>> export_manager = ExportManager()
        >>> histogram_data = {'red': [10, 20, 30], 'green': [5, 15, 25]}
        >>> success = export_manager.export_histogram_data(histogram_data, 'json', 'my_histogram')
        >>> if success:
        ...     print("Export completed successfully")
    """
    
    def __init__(self):
        """Initialize the ExportManager.
        
        Creates a new ExportManager instance with no configuration parameters.
        The class is stateless and ready to export data immediately after instantiation.
        
        Examples:
            >>> export_manager = ExportManager()
            >>> # Ready to use for any export operations
        """
        pass
    
    def export_analysis_data(self, analysis_type: str, data: Any, format: str = 'json', filename: str = 'analysis_export') -> bool:
        """Export analysis data to a file based on the specified analysis type.
        
        This method serves as a dispatcher that routes different types of analysis
        data to their appropriate export handlers. It supports histogram data,
        pixel profile data, and polygon coordinate data.
        
        Args:
            analysis_type: Type of analysis data to export. Must be one of:
                'histogram', 'profile', or 'polygon'.
            data: The data to export. Type varies based on analysis_type:
                - For 'histogram': Dict[str, List[int]] with channel data
                - For 'profile': Dict[str, List[float]] with distance and intensity data
                - For 'polygon': List[List[Tuple[int, int]]] with coordinate lists
            format: Export format, either 'json' or 'csv'. Defaults to 'json'.
            filename: Base filename without extension. The appropriate extension
                will be added automatically. Defaults to 'analysis_export'.
                
        Returns:
            bool: True if export was successful, False otherwise.
            
        Raises:
            ValueError: If analysis_type is not one of the supported types.
            IOError: If the file cannot be written to disk.
            
        Examples:
            >>> export_manager = ExportManager()
            >>> histogram_data = {'red': [10, 20, 30], 'green': [5, 15, 25]}
            >>> success = export_manager.export_analysis_data('histogram', histogram_data, 'json')
            >>> print(f"Export successful: {success}")
            
        Performance:
            Time Complexity: O(n) where n is the size of the data to be exported.
            Space Complexity: O(n) for temporary storage during format conversion.
        """
        
        if analysis_type == 'histogram':
            return self.export_histogram_data(data, format, filename)
        elif analysis_type == 'profile':
            return self.export_profile_data(data, format, filename)
        elif analysis_type == 'polygon':
            return self.export_polygon_data(data, format, filename)
        else:
            print(f"Unknown analysis type: {analysis_type}")
            return False
    
    def export_histogram_data(self, histogram_data: Dict[str, List[int]], format: str = 'json', filename: str = 'histogram_export') -> bool:
        """Export histogram data to a file in the specified format.
        
        This method takes histogram data as a dictionary where keys are channel names
        (e.g., 'red', 'green', 'blue', 'gray') and values are lists of intensity counts
        for each histogram bin. It handles both numpy arrays and Python lists,
        converting them to the appropriate format for the target file type.
        
        For JSON export, numpy arrays are converted to lists for serialization.
        For CSV export, data is structured with intensity values as rows and
        channels as columns, filtering out metadata fields like 'bins', 'roi', 'polygon'.

        Args:
            histogram_data: Dictionary with channel names as keys and intensity counts as values.
                Each value should be a list or numpy array of integers representing the
                histogram bins. May also contain metadata keys like 'bins', 'roi', 'polygon'
                which are handled appropriately for each export format.
            format: Export format, either 'json' or 'csv'. Defaults to 'json'.
            filename: Base filename without extension. The extension (.json or .csv)
                will be added automatically. Defaults to 'histogram_export'.
                
        Returns:
            bool: True if export was successful, False otherwise.
            
        Raises:
            IOError: If the file cannot be written to disk.
            ValueError: If the histogram_data contains no valid channel data for CSV export.
            
        Examples:
            >>> export_manager = ExportManager()
            >>> histogram_data = {
            ...     'red': [10, 20, 30, 25, 15],
            ...     'green': [5, 15, 25, 30, 20],
            ...     'blue': [8, 18, 22, 28, 18]
            ... }
            >>> success = export_manager.export_histogram_data(histogram_data, 'json', 'my_histogram')
            >>> print(f"Export successful: {success}")
            
        Performance:
            Time Complexity: O(n*m) where n is the number of channels and m is the number of bins.
            Space Complexity: O(n*m) for temporary storage during format conversion.
        """
        
        try:
            if format == 'json':
                export_filename = f"{filename}.json"
                
                # Convert numpy arrays to lists for JSON serialization
                json_data = {}
                for key, value in histogram_data.items():
                    if hasattr(value, 'tolist'):  # numpy array
                        json_data[key] = value.tolist()
                    elif isinstance(value, (list, tuple)):
                        json_data[key] = list(value)
                    else:
                        json_data[key] = value
                
                with open(export_filename, 'w') as f:
                    json.dump(json_data, f, indent=4)
                return True
            elif format == 'csv':
                export_filename = f"{filename}.csv"
                with open(export_filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    # Filter only channel data (exclude metadata like 'bins', 'roi', 'polygon')
                    valid_channels = []
                    for key, value in histogram_data.items():
                        if key not in ['bins', 'roi', 'polygon']:
                            # Check if it's array-like data (numpy array, list, or tuple)
                            if hasattr(value, '__len__') and len(value) > 0:
                                valid_channels.append(key)
                    
                    if not valid_channels:
                        return False
                    
                    # Write header
                    writer.writerow(['intensity'] + valid_channels)
                    
                    # Write data - determine the actual length of histogram data
                    max_length = 0
                    for channel in valid_channels:
                        max_length = max(max_length, len(histogram_data[channel]))
                    
                    for i in range(max_length):
                        row = [i]
                        for channel in valid_channels:
                            channel_data = histogram_data[channel]
                            if i < len(channel_data):
                                # Handle both numpy arrays and lists
                                if hasattr(channel_data, 'item'):  # numpy array
                                    row.append(float(channel_data[i]))
                                else:
                                    row.append(channel_data[i])
                            else:
                                row.append(0)
                        writer.writerow(row)
                return True
            else:
                return False
        except Exception as e:
            print(f"Error exporting histogram data: {e}")
            return False
    
    def export_profile_data(self, profile_data: Dict[str, List[float]], format: str = 'json', filename: str = 'profile_export') -> bool:
        """Export pixel profile data to a file in the specified format.
        
        This method exports pixel intensity profile data collected along a line.
        The data typically includes distance measurements and corresponding pixel
        intensities for each color channel. It handles both numpy arrays and
        Python lists, ensuring proper serialization for the target format.
        
        For JSON export, numpy arrays are converted to lists. For CSV export,
        data is structured with distances as the first column followed by
        intensity values for each channel.

        Args:
            profile_data: Dictionary containing profile measurements. Expected keys:
                - 'distances': List or array of distance values along the line
                - Channel names (e.g., 'red', 'green', 'blue', 'gray'): Lists or arrays
                  of pixel intensity values corresponding to each distance point
            format: Export format, either 'json' or 'csv'. Defaults to 'json'.
            filename: Base filename without extension. The extension (.json or .csv)
                will be added automatically. Defaults to 'profile_export'.
                
        Returns:
            bool: True if export was successful, False otherwise.
            
        Raises:
            IOError: If the file cannot be written to disk.
            KeyError: If required 'distances' key is missing from profile_data.
            
        Examples:
            >>> export_manager = ExportManager()
            >>> profile_data = {
            ...     'distances': [0.0, 1.0, 2.0, 3.0, 4.0],
            ...     'red': [120, 130, 125, 135, 140],
            ...     'green': [110, 115, 120, 125, 130],
            ...     'blue': [100, 105, 110, 115, 120]
            ... }
            >>> success = export_manager.export_profile_data(profile_data, 'csv', 'line_profile')
            >>> print(f"Profile export successful: {success}")
            
        Performance:
            Time Complexity: O(n*m) where n is the number of distance points and m is the number of channels.
            Space Complexity: O(n*m) for temporary storage during format conversion.
        """
        try:
            if format == 'json':
                export_filename = f"{filename}.json"
                
                # Convert numpy arrays to lists for JSON serialization
                json_data = {}
                for key, value in profile_data.items():
                    if hasattr(value, 'tolist'):  # numpy array
                        json_data[key] = value.tolist()
                    elif isinstance(value, (list, tuple)):
                        json_data[key] = list(value)
                    else:
                        json_data[key] = value
                
                with open(export_filename, 'w') as f:
                    json.dump(json_data, f, indent=4)
                return True
            elif format == 'csv':
                export_filename = f"{filename}.csv"
                with open(export_filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Get all keys except 'distances'
                    channels = [key for key in profile_data.keys() if key != 'distances']
                    
                    # Write header
                    writer.writerow(['distance'] + channels)
                    
                    # Write data
                    distances = profile_data.get('distances', [])
                    for i in range(len(distances)):
                        # Handle numpy arrays for distances
                        if hasattr(distances, 'item'):  # numpy array
                            row = [float(distances[i])]
                        else:
                            row = [distances[i]]
                            
                        for channel in channels:
                            channel_data = profile_data[channel]
                            if i < len(channel_data):
                                # Handle both numpy arrays and lists
                                if hasattr(channel_data, 'item'):  # numpy array
                                    row.append(float(channel_data[i]))
                                else:
                                    row.append(channel_data[i])
                            else:
                                row.append(0)
                        writer.writerow(row)
                return True
            else:
                return False
        except Exception as e:
            print(f"Error exporting profile data: {e}")
            return False
    
    def export_polygon_data(self, polygon_data: List[List[Tuple[int, int]]], format: str = 'json', filename: str = 'polygon_export') -> bool:
        """Export polygon coordinate data to a file in the specified format.
        
        This method exports lists of polygons where each polygon is defined by
        a series of (x, y) coordinate points. The data can be exported in either
        JSON format (preserving the nested structure) or CSV format (flattened
        with polygon and point identifiers).
        
        For JSON export, the nested list structure is preserved directly.
        For CSV export, data is flattened into rows with columns for polygon_id,
        point_id, x, and y coordinates.

        Args:
            polygon_data: List of polygons, where each polygon is a list of (x, y) coordinate
                tuples. Each tuple represents a point in the polygon, and points should be
                ordered to define the polygon boundary.
            format: Export format, either 'json' or 'csv'. Defaults to 'json'.
            filename: Base filename without extension. The extension (.json or .csv)
                will be added automatically. Defaults to 'polygon_export'.
                
        Returns:
            bool: True if export was successful, False otherwise.
            
        Raises:
            IOError: If the file cannot be written to disk.
            ValueError: If polygon_data is empty or contains invalid coordinate data.
            
        Examples:
            >>> export_manager = ExportManager()
            >>> polygon_data = [
            ...     [(10, 10), (20, 10), (20, 20), (10, 20)],  # Rectangle
            ...     [(30, 30), (40, 35), (35, 45)]             # Triangle
            ... ]
            >>> success = export_manager.export_polygon_data(polygon_data, 'json', 'regions')
            >>> print(f"Polygon export successful: {success}")
            
        Performance:
            Time Complexity: O(n*m) where n is the number of polygons and m is the average number of points per polygon.
            Space Complexity: O(1) for JSON export, O(n*m) for CSV export due to flattening.
        """
        try:
            if format == 'json':
                export_filename = f"{filename}.json"
                with open(export_filename, 'w') as f:
                    json.dump(polygon_data, f, indent=4)
                print(f"Exported polygon data to {export_filename}")
                return True
            elif format == 'csv':
                export_filename = f"{filename}.csv"
                with open(export_filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["polygon_id", "point_id", "x", "y"])
                    for poly_id, polygon in enumerate(polygon_data):
                        for point_id, point in enumerate(polygon):
                            writer.writerow([poly_id, point_id, point[0], point[1]])
                print(f"Exported polygon data to {export_filename}")
                return True
            else:
                return False
        except Exception as e:
            print(f"Error exporting polygon data: {e}")
            return False
