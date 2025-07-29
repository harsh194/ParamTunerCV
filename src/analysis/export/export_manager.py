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
        print(f"🏭 ExportManager.export_analysis_data called:")
        print(f"   → Analysis type: {analysis_type}")
        print(f"   → Format: {format}")
        print(f"   → Filename: {filename}")
        print(f"   → Data type: {type(data)}")
        
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
        print(f"📊 export_histogram_data called:")
        print(f"   → Format: {format}")
        print(f"   → Filename: {filename}")
        print(f"   → Data keys: {list(histogram_data.keys()) if histogram_data else 'None'}")
        
        try:
            if format == 'json':
                export_filename = f"{filename}.json"
                print(f"   → Writing to JSON file: {export_filename}")
                
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
                print(f"   → Successfully exported histogram data to {export_filename}")
                return True
            elif format == 'csv':
                export_filename = f"{filename}.csv"
                print(f"   → Writing to CSV file: {export_filename}")
                with open(export_filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    # Filter only channel data (exclude metadata like 'bins', 'roi', 'polygon')
                    valid_channels = []
                    for key, value in histogram_data.items():
                        if key not in ['bins', 'roi', 'polygon']:
                            # Check if it's array-like data (numpy array, list, or tuple)
                            if hasattr(value, '__len__') and len(value) > 0:
                                valid_channels.append(key)
                    
                    print(f"   → Valid CSV channels: {valid_channels}")
                    
                    if not valid_channels:
                        print("   → ERROR: No valid channel data found")
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
                print(f"   → Successfully exported histogram data to {export_filename}")
                return True
            else:
                print(f"Unsupported export format: {format}")
                return False
        except Exception as e:
            print(f"   → ERROR exporting histogram data: {e}")
            import traceback
            traceback.print_exc()
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
