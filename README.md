# DriftPaint – Art Made From Laptop Motion

## Overview
DriftPaint is a Python desktop application that turns your laptop’s built‑in accelerometer into a creative drawing tool. By tilting the device you control the brush direction, shaking changes the brush, and a tap gesture clears the canvas. The app works fully offline and requires no camera or microphone.

## Features
- **Sensor‑driven drawing** – tilt the laptop to move the brush on a canvas.
- **Shake detection** – change brush colour or style with a quick shake.
- **Tap gesture** – clear the canvas instantly.
- **Mock mode** – when no accelerometer is present you can use the arrow keys to simulate tilt.
- **Adjustable sensitivity** – slider to control how far the brush moves per degree of tilt.
- **Brush size & colour palette** – choose brush size and colour from a vibrant palette.
- **Export artwork** – save your creation as a PNG file.

## Technical Stack
- **Python 3.11+**
- **Tkinter** for the UI and canvas rendering.
- **winrt** (or `winrt-runtime` + `winrt-Windows.Devices.Sensors`) for accessing the Windows accelerometer.
- **Pillow** for image export.

## Installation
```bash
# Clone the repository (if you haven’t already)
git clone https://github.com/abhi3114-glitch/DriftPaint.git
cd DriftPaint

# Create a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # on Windows

# Install dependencies
pip install -r requirements.txt
```

## Running the Application
```bash
python src/main.py
```
- If a hardware accelerometer is detected the status bar will show **"Mode: Hardware Sensor"** and you can draw by moving the laptop.
- If no sensor is found the app falls back to **Mock (Arrow Keys)** mode – use the arrow keys to control the brush.
- Press **Space** to clear the canvas.
- Shake the device (or press **S** in mock mode) to cycle colours.
- Use the sliders on the left panel to adjust brush size and sensitivity.
- Click **Export PNG** to save your artwork.

## Development
- The code is organized under `src/`:
  - `main.py` – UI and drawing logic.
  - `sensor_service.py` – abstraction over the accelerometer and mock mode.
- Adjust the smoothing factor in `sensor_service.py` if you need a different feel for the brush movement.
- Contributions are welcome – feel free to open issues or submit pull requests.

## License
This project is released under the MIT License. See the `LICENSE` file for details.
