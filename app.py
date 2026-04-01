from datetime import datetime, timezone
import random

from flask import Flask, jsonify, request


app = Flask(__name__)

# Global mode state for sensor simulation.
current_mode = "normal"

# Supported ranges for each mode.
MODE_RANGES = {
    "normal": {"spo2": (95, 100), "heart_rate": (70, 90)},
    "warning": {"spo2": (85, 92), "heart_rate": (100, 120)},
    "critical": {"spo2": (75, 85), "heart_rate": (120, 140)},
}


def generate_data():
    """
    Generate one sensor reading based on the current global mode.
    """
    ranges = MODE_RANGES[current_mode]
    spo2 = random.randint(*ranges["spo2"])
    heart_rate = random.randint(*ranges["heart_rate"])

    return {
        "spo2": spo2,
        "heart_rate": heart_rate,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/")
def health():
    """
    Basic endpoint to confirm the server is running.
    """
    return "Sensor Server Running"


@app.get("/data")
def get_data():
    """
    Return simulated real-time patient sensor data.
    Each request produces a new value within the active mode range.
    """
    return jsonify(generate_data())


@app.post("/set_mode")
def set_mode():
    """
    Set the global simulation mode using JSON body:
    { "mode": "normal" | "warning" | "critical" }
    """
    global current_mode

    payload = request.get_json(silent=True) or {}
    mode = payload.get("mode")

    if mode not in MODE_RANGES:
        return jsonify(
            {
                "error": "Invalid mode",
                "allowed_modes": list(MODE_RANGES.keys()),
            }
        ), 400

    current_mode = mode
    return jsonify({"message": "Mode updated", "mode": current_mode})


if __name__ == "__main__":
    # Expose server externally for local network testing.
    app.run(host="0.0.0.0", port=5000)