from flask import Flask, request, jsonify
from nes_container_manager.manager.manager import ContainerManager

app = Flask(__name__)

container_manager = None

@app.route("/start", methods=["POST"])
def start_services():
    global container_manager

    services = request.json.get("services", ["postgres", "mqtt"])

    try:
        print(f" ---Starting services: {services}")
        container_manager = ContainerManager(services)
        container_manager.__enter__()  # Start all containers
        print(" ---Containers started")

        # Get host/port/database info
        info = {
            name: container_manager.get_connection_info(name)
            for name in services
        }

        return jsonify({"status": "started", "info": info})

    except Exception as e:
        print(f"--- Error in /start: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/stop", methods=["POST"])
def stop_services():
    global container_manager

    try:
        if container_manager:
            container_manager.__exit__(None, None, None)
            container_manager = None
            print("---Containers stopped")
        return jsonify({"status": "stopped"})

    except Exception as e:
        print(f"---Error in /stop: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/message", methods=["POST"])
def receive_message():
    data = request.json
    print(f"--- Received from client: {data}")
    return jsonify({"status": "received"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
