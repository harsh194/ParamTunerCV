import json
import csv
import os
from typing import Any, Dict, List, Tuple, Optional

class ExportManager:
    """Handles exporting analysis data to various formats."""
    
    def __init__(self):
        pass
    
    def export_analysis_data(self, analysis_type: str, data: Any, format: str = 'json', filename: str = 'analysis_export'):
        """
        Export analysis data to a file.
        
        Args:
            analysis_type: Type of analysis data ('histogram', 'profile', 'polygon')
            data: The data to export
            format: Export format ('json' or 'csv')
            filename: Base filename without extension
            
        Returns:
            bool: True if export was successful
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
        """
        Export histogram data to a file.
        
        Args:
            histogram_data: Dictionary with channel names as keys and intensity counts as values
            format: Export format ('json' or 'csv')
            filename: Base filename without extension
            
        Returns:
            bool: True if export was successful
        """
        try:
            if format == 'json':
                export_filename = f"{filename}.json"
                with open(export_filename, 'w') as f:
                    json.dump(histogram_data, f, indent=4)
                print(f"Exported histogram data to {export_filename}")
                return True
            elif format == 'csv':
                export_filename = f"{filename}.csv"
                with open(export_filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    # Write header
                    channels = list(histogram_data.keys())
                    writer.writerow(['intensity'] + channels)
                    
                    # Write data
                    for i in range(256):  # Assuming 8-bit image with 256 intensity levels
                        row = [i]
                        for channel in channels:
                            if i < len(histogram_data[channel]):
                                row.append(histogram_data[channel][i])
                            else:
                                row.append(0)
                        writer.writerow(row)
                print(f"Exported histogram data to {export_filename}")
                return True
            else:
                print(f"Unsupported export format: {format}")
                return False
        except Exception as e:
            print(f"Error exporting histogram data: {e}")
            return False
    
    def export_profile_data(self, profile_data: Dict[str, List[float]], format: str = 'json', filename: str = 'profile_export') -> bool:
        """
        Export pixel profile data to a file.
        
        Args:
            profile_data: Dictionary with 'distances' and channel names as keys
            format: Export format ('json' or 'csv')
            filename: Base filename without extension
            
        Returns:
            bool: True if export was successful
        """
        try:
            if format == 'json':
                export_filename = f"{filename}.json"
                with open(export_filename, 'w') as f:
                    json.dump(profile_data, f, indent=4)
                print(f"Exported profile data to {export_filename}")
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
                        row = [distances[i]]
                        for channel in channels:
                            if i < len(profile_data[channel]):
                                row.append(profile_data[channel][i])
                            else:
                                row.append(0)
                        writer.writerow(row)
                print(f"Exported profile data to {export_filename}")
                return True
            else:
                print(f"Unsupported export format: {format}")
                return False
        except Exception as e:
            print(f"Error exporting profile data: {e}")
            return False
    
    def export_polygon_data(self, polygon_data: List[List[Tuple[int, int]]], format: str = 'json', filename: str = 'polygon_export') -> bool:
        """
        Export polygon data to a file.
        
        Args:
            polygon_data: List of polygons, where each polygon is a list of (x,y) points
            format: Export format ('json' or 'csv')
            filename: Base filename without extension
            
        Returns:
            bool: True if export was successful
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
                print(f"Unsupported export format: {format}")
                return False
        except Exception as e:
            print(f"Error exporting polygon data: {e}")
            return False
