
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

sensor_data = {
    "in_count": 0,
    "out_count": 0,
    "total": 0,
    "temperature": None,
    "humidity": None,
    "last_update": None
}

@app.route("/")
def home():
    return render_template("index.html")

# ESP32 sends readings to this endpoint

@app.route("/api/update", methods=["POST"])
def update_data():
    incoming = request.get_json(silent=True)

    if not incoming:
        print("ESP32 ERROR: No JSON data received", flush=True)
        return jsonify({"error": "No JSON data received"}), 400

    # Display received sensor data in Render Application Logs
    print("ESP32 DATA RECEIVED:", incoming, flush=True)

    try:
        for key in ("in_count", "out_count", "total"):
            if key in incoming:
                sensor_data[key] = int(incoming[key])

        for key in ("temperature", "humidity"):
            if key in incoming:
                value = incoming[key]
                sensor_data[key] = (
                    float(value) if value is not None else None
                )

        sensor_data["last_update"] = datetime.now().isoformat()

        print("SENSOR DATA SAVED:", sensor_data, flush=True)

        return jsonify({"status": "success"})

    except (ValueError, TypeError) as error:
        print("SENSOR DATA ERROR:", str(error), flush=True)
        return jsonify({"error": "Invalid sensor data"}), 400

# Website reads the latest values from this endpoint
@app.route("/api/data")
def get_data():
    return jsonify(sensor_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
