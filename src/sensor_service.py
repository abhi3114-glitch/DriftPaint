import time
import math
import collections

# Try to import winrt packages for Windows accelerometer
try:
    import winrt.windows.devices.sensors as sensors
    WINRT_AVAILABLE = True
except ImportError:
    sensors = None
    WINRT_AVAILABLE = False


class SensorService:
    """
    Handles accelerometer data from Windows sensors or provides mock data.
    Uses a Low-Pass Filter for smoothing and detects shake gestures.
    """

    def __init__(self, use_mock=False):
        self.running = False
        self.accelerometer = None
        self.smoothing_factor = 0.15  # Lower = smoother, higher = more responsive

        # Data State
        self.raw_x, self.raw_y, self.raw_z = 0.0, 0.0, 0.0
        self.smooth_x, self.smooth_y = 0.0, 0.0

        # Gesture State
        self.last_shake_time = 0
        self.shake_threshold = 1.5  # g-force variance
        self.history = collections.deque(maxlen=20)

        # Mock State
        self.use_mock = use_mock
        self.mock_dx = 0.0
        self.mock_dy = 0.0

        if not self.use_mock and WINRT_AVAILABLE:
            try:
                self.accelerometer = sensors.Accelerometer.get_default()
                if self.accelerometer is None:
                    print("[SensorService] No accelerometer found. Switching to Mock mode.")
                    self.use_mock = True
                else:
                    # Set report interval (in milliseconds) for ~30Hz
                    min_interval = self.accelerometer.minimum_report_interval
                    self.accelerometer.report_interval = max(33, min_interval)
                    print(f"[SensorService] Accelerometer found. Report interval: {self.accelerometer.report_interval}ms")
            except Exception as e:
                print(f"[SensorService] Error initializing accelerometer: {e}. Using Mock mode.")
                self.use_mock = True
        else:
            if not WINRT_AVAILABLE:
                print("[SensorService] winrt not available. Using Mock mode.")
            self.use_mock = True

    def start(self):
        self.running = True
        if self.accelerometer and not self.use_mock:
            try:
                self.accelerometer.add_reading_changed(self._on_reading_changed)
                print("[SensorService] Started with real accelerometer.")
            except Exception as e:
                print(f"[SensorService] Failed to attach reading handler: {e}. Falling back to mock mode.")
                self.use_mock = True
        if self.use_mock:
            print("[SensorService] Started in Mock Mode. Use arrow keys to simulate tilt.")

    def stop(self):
        self.running = False
        if self.accelerometer and not self.use_mock:
            try:
                self.accelerometer.remove_reading_changed(self._on_reading_changed)
            except Exception:
                pass
        print("[SensorService] Stopped.")

    def _on_reading_changed(self, sender, args):
        """Callback for real accelerometer data."""
        reading = args.reading
        if reading:
            self._process_data(reading.acceleration_x, reading.acceleration_y, reading.acceleration_z)

    def update_mock(self, dx, dy):
        """Called by UI to simulate tilt via keys. dx, dy are in range [-1, 1]."""
        self.mock_dx = dx
        self.mock_dy = dy
        # Simulate processing with mock values
        self._process_data(self.mock_dx, self.mock_dy, -1.0)

    def _process_data(self, x, y, z):
        """Process raw accelerometer data: smooth and detect gestures."""
        self.raw_x, self.raw_y, self.raw_z = x, y, z

        # Low Pass Filter (Exponential Moving Average)
        self.smooth_x = (x * self.smoothing_factor) + (self.smooth_x * (1 - self.smoothing_factor))
        self.smooth_y = (y * self.smoothing_factor) + (self.smooth_y * (1 - self.smoothing_factor))

        self._detect_gestures(x, y, z)

    def _detect_gestures(self, x, y, z):
        """Detect shake gesture based on acceleration variance."""
        now = time.time()

        # Calculate magnitude
        magnitude = math.sqrt(x * x + y * y + z * z)
        self.history.append(magnitude)

        # Shake Detection (High energy variance over recent samples)
        if len(self.history) >= 10:
            variance = max(self.history) - min(self.history)
            if variance > self.shake_threshold:
                if now - self.last_shake_time > 1.0:  # 1 second cooldown
                    self.last_shake_time = now
                    print("[Gesture] Shake detected!")

    def get_state(self):
        """Returns current state for UI consumption."""
        return {
            'x': self.smooth_x,
            'y': self.smooth_y,
            'raw_x': self.raw_x,
            'raw_y': self.raw_y,
            'shake_time': self.last_shake_time
        }

    def set_smoothing(self, factor):
        """Set smoothing factor (0.05 to 0.5)."""
        self.smoothing_factor = max(0.05, min(0.5, factor))
