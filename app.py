from datetime import datetime, timezone
import random
import time
from flask import Flask, jsonify, request

app = Flask(__name__)

current_mode = "normal"
last_spike_time = time.time()

MODE_RANGES = {
    "normal": {
        "spo2": (95, 100),
        "heart_rate": (60, 100),
        "bp_sys": (100, 120),
        "bp_dia": (60, 80),
        "resp_rate": (12, 20),
        "temperature": (36.5, 37.5),
        "glucose": (80, 120),
        "map": (70, 100),
        "cardiac_output": (4.0, 8.0),
        "cardiac_index": (2.5, 4.0),
        "cvp": (2, 8),
    },
    "warning": {
        "spo2": (85, 92),
        "heart_rate": (100, 120),
        "bp_sys": (90, 100),
        "bp_dia": (55, 65),
        "resp_rate": (20, 24),
        "temperature": (37.5, 38.5),
        "glucose": (140, 200),
        "map": (65, 70),
        "cardiac_output": (3.5, 4.0),
        "cardiac_index": (2.2, 2.5),
        "cvp": (8, 12),
    },
    "critical": {
        "spo2": (75, 85),
        "heart_rate": (120, 140),
        "bp_sys": (80, 90),
        "bp_dia": (40, 55),
        "resp_rate": (25, 35),
        "temperature": (39.0, 41.0),
        "glucose": (250, 350),
        "map": (50, 65),
        "cardiac_output": (2.5, 3.5),
        "cardiac_index": (1.5, 2.2),
        "cvp": (12, 18),
    },
}

def generate_data():
    global last_spike_time
    ranges = MODE_RANGES[current_mode]
    data = {}

    for key, (low, high) in ranges.items():
        if key in ["temperature", "cardiac_output", "cardiac_index"]:
            data[key] = round(random.uniform(low, high), 1)
        else:
            data[key] = random.randint(int(low), int(high))

    if time.time() - last_spike_time > 60:
        last_spike_time = time.time()
        param = random.choice(list(data.keys()))

        if param == "spo2":
            data[param] = random.randint(70, 85)
        elif param == "heart_rate":
            data[param] = random.randint(130, 150)
        elif param == "bp_sys":
            data[param] = random.randint(70, 85)
        elif param == "bp_dia":
            data[param] = random.randint(35, 50)
        elif param == "resp_rate":
            data[param] = random.randint(30, 40)
        elif param == "temperature":
            data[param] = round(random.uniform(39.5, 41.5), 1)
        elif param == "glucose":
            data[param] = random.randint(300, 400)
        elif param == "map":
            data[param] = random.randint(50, 60)
        elif param == "cardiac_output":
            data[param] = round(random.uniform(2.0, 3.0), 1)
        elif param == "cardiac_index":
            data[param] = round(random.uniform(1.2, 2.0), 1)
        elif param == "cvp":
            data[param] = random.randint(14, 20)

    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    return data

@app.get("/")
def health():
    return "Sensor Server Running"

@app.get("/data")
def get_data():
    return jsonify(generate_data())

@app.post("/set_mode")
def set_mode():
    global current_mode
    payload = request.get_json(silent=True) or {}
    mode = payload.get("mode")

    if mode not in MODE_RANGES:
        return jsonify({
            "error": "Invalid mode",
            "allowed_modes": list(MODE_RANGES.keys()),
        }), 400

    current_mode = mode
    return jsonify({"message": "Mode updated", "mode": current_mode})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)