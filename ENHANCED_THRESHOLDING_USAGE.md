# Enhanced Thresholding Functionality - Usage Guide

## Overview

The enhanced thresholding functionality now provides a **separate process window** with full zoom/pan capabilities and independent trackbars, similar to the main process window. This gives you complete control over thresholding operations with professional image analysis tools.

## Key Features

### 🖼️ Separate Process Window
- **Independent window**: `"Thresholded Process - {ColorSpace}"`
- **Full zoom/pan support**: Just like the main process window
- **Real-time updates**: Changes to parameters instantly update the display
- **Professional image handling**: Proper scaling, caching, and rendering

### 🎛️ Enhanced Mouse Controls
- **Mouse wheel**: Zoom in/out around cursor position
- **Middle-click + drag**: Pan the image 
- **Left-click + drag**: Draw ROI rectangles for analysis
- **Right-click**: Remove last ROI or reset view when no ROIs exist
- **Live feedback**: Current zoom level and ROI count displayed on image

### 📊 Independent Trackbar System
- **Dedicated trackbar window**: `"Thresholding Trackbars - {ColorSpace}"`
- **Method-specific trackbars**: Automatically switches trackbars when changing threshold methods
- **All threshold types supported**: Binary, Binary Inverted, Truncated, To Zero, To Zero Inverted
- **Real-time parameter display**: Current settings shown in control window

## How to Access

1. **Run your application** (e.g., `python check.py`)
2. **Open Analysis Control Window** (should open automatically)
3. **Click "Thresholding" button** in the Analysis Control Window
4. **Select color space** from the popup menu:
   - Grayscale
   - HSV, BGR, HLS, Lab, Luv, YCrCb, XYZ

## Available Threshold Methods

### For Grayscale Images:
- **Simple**: Standard threshold with adjustable threshold value
- **Adaptive**: Local thresholding with block size and C constant
- **Otsu**: Automatic threshold selection using Otsu's method
- **Triangle**: Automatic threshold using triangle method

### For Color Spaces:
- **Range**: Traditional min/max range thresholding per channel
- **Simple**: Per-channel thresholding with selected threshold type
- **Otsu**: Per-channel Otsu thresholding
- **Triangle**: Per-channel triangle thresholding  
- **Adaptive**: Per-channel adaptive thresholding

## Windows Created

When you open thresholding for a color space, you get **only the essential windows**:

1. **Control Window** (Tkinter):
   - Method selection (radio buttons)
   - Threshold type dropdown
   - Parameter status display
   - Preset configurations
   - Save/Load configs
   - Mouse control instructions

2. **Thresholded Process Window** (OpenCV):
   - Real-time thresholded image display
   - Full zoom/pan functionality
   - ROI drawing and management
   - Status overlay (zoom level, ROI count)

3. **Thresholding Trackbars Window** (OpenCV):
   - Method-specific parameter controls
   - Real-time parameter adjustment
   - Automatic trackbar switching

**Note**: The text window and analysis control window are **NOT** created during thresholding to avoid clutter. You already have these from the main viewer.

## Mouse Controls Summary

| Action | Function |
|--------|----------|
| **Mouse Wheel** | Zoom in/out around cursor |
| **Middle + Drag** | Pan the image view |
| **Left + Drag** | Draw ROI rectangle |
| **Right Click** | Remove last ROI or reset view |

## Advanced Features

### 🎯 ROI Analysis
- Draw multiple ROIs on the thresholded image
- ROIs are displayed with colored rectangles and labels
- Selected ROI highlighted with different color
- ROI coordinates preserved during zoom/pan operations

### 💾 Configuration Management  
- **Save Config**: Export current threshold settings to JSON
- **Load Config**: Import previously saved configurations
- **Presets**: Quick access to common threshold configurations
  - Document Scan (Otsu binary)
  - Adaptive Text (Variable lighting)
  - Blue/Red/Green Object Detection (HSV range)
  - And more...

### 🔄 Real-time Updates
- All parameter changes instantly update the display
- Smooth zoom/pan operations with caching
- Responsive UI with proper event handling
- Status display shows current method and key parameters

## Usage Examples

### Example 1: Document Processing
1. Open thresholding → Select "Grayscale"
2. Choose "Otsu" method for automatic threshold
3. Select "BINARY" threshold type
4. Use mouse wheel to zoom in on text areas
5. Draw ROIs around specific text regions

### Example 2: Color Object Detection  
1. Open thresholding → Select "HSV"
2. Choose "Range" method
3. Adjust H, S, V min/max trackbars to isolate color
4. Use zoom/pan to examine detection results
5. Draw ROIs around detected objects

### Example 3: Adaptive Text Processing
1. Open thresholding → Select "Grayscale"  
2. Choose "Adaptive" method
3. Adjust block size and C constant
4. Select "MEAN_C" or "GAUSSIAN_C" method
5. Pan around image to see adaptive behavior

## Tips for Best Results

1. **Start with appropriate color space**:
   - Grayscale for text/documents
   - HSV for color-based detection
   - Lab for perceptual color differences

2. **Use zoom for precision**:
   - Zoom in to see pixel-level threshold effects
   - Zoom out for overall image assessment

3. **Try different methods**:
   - Simple for controlled conditions
   - Adaptive for varying lighting
   - Otsu/Triangle for automatic thresholding

4. **Save successful configurations**:
   - Use Save Config for reproducible results
   - Create custom presets for common tasks

5. **Combine with ROI analysis**:
   - Draw ROIs on areas of interest  
   - Use Analysis Control Window for detailed analysis

## Troubleshooting

- **Window not appearing**: Check that debug mode is enabled
- **Trackbars not updating**: Try switching threshold methods
- **Performance issues**: Close unused analysis windows
- **ROI drawing issues**: Ensure you're in the correct mouse mode

## Technical Details

The enhanced thresholding uses a dedicated `ImageViewer` instance that:
- Reuses all existing zoom/pan/mouse functionality
- Maintains separate parameter state from main viewer
- Provides real-time image processing pipeline
- Handles window lifecycle management automatically

This architecture ensures consistency with the main application while providing specialized thresholding capabilities.