# Parameter

A flexible image viewer with interactive features for image processing and analysis.

## Features

-   Interactive zoom and pan
-   ROI selection (rectangular and line-based)
-   Trackbar controls for real-time parameter tuning
-   Pixel profile and histogram analysis
-   Headless mode for automated processing
-   Extensible and modular design

## Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/your-username/parameter.git
    cd parameter
    ```

2.  Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

See `sample.py` for a detailed example of how to use the `parameter` package.

### Basic Example

```python
import cv2
from parameter.core.image_viewer import ImageViewer
from parameter.utils.factory import create_viewer_with_common_controls

# Create an image viewer with common controls
viewer = create_viewer_with_common_controls()

# Load an image
image = cv2.imread("path/to/your/image.jpg")

# Create a simple image processing function
def process_image(params, log):
    # Get parameters from the trackbars
    threshold = params.get("threshold", 128)
    kernel_size = params.get("kernel_size", 5)

    # Apply some processing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, np.ones((kernel_size, kernel_size)))

    # Return a list of images to display
    return [
        (image, "Original"),
        (gray, "Grayscale"),
        (thresh, "Thresholded"),
        (morphed, "Morphed"),
    ]

# Set up the viewer with the processing function
viewer.setup_viewer(image_processor_func=process_image)

# Run the main loop
viewer.run_simple_loop()
```
