# server.py
from flask import Flask, request, jsonify
from nes_container_manager.manager.manager import ContainerManager
import threading

app = Flask(__name__)

# Global manager instance (for reuse)
container_manager = None

@app.route("/start", methods=["POST"])
def start_services():
    global container_manager

    services = request.json.get("services", ["postgres", "mqtt"])

    try:
        container_manager = ContainerManager(services=services)
        container_manager.__enter__()  # Manually enter context manager

        info = {
            name: container_manager.get_connection_info(name)
            for name in services
        }
        return jsonify({"status": "started", "info": info})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/stop", methods=["POST"])
def stop_services():
    global container_manager

    if container_manager:
        container_manager.__exit__(None, None, None)
        container_manager = None
        return jsonify({"status": "stopped"})
    else:
        return jsonify({"status": "no active services"}), 400

@app.route("/")
def index():
    return "✅ Container Manager API is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
