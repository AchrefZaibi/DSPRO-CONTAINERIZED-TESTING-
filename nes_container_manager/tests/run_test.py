# server.py

from flask import Flask, request, jsonify
from nes_container_manager.manager.manager import ContainerManager
import psycopg2
import paho.mqtt.client as mqtt
import socket
import time

# 🔧 Initialize Flask app
app = Flask(__name__)

# 🔁 Global variables
container_manager = None
mqtt_client = None
mqtt_messages = []

# 🕒 Wait for port to become available
def wait_for_port(host, port, timeout=30):
    print(f"🔄 Waiting for {host}:{port} ...")
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, int(port)), timeout=20):
                print(f"✅ Port {port} on {host} is open!")
                return True
        except OSError as e:
            print(f"⏳ Still waiting for {host}:{port} ... {str(e)}")
            if time.time() - start_time > timeout:
                print(f"❌ Timeout reached for {host}:{port}")
                return False
            time.sleep(1)

# 🔊 MQTT handlers
def on_connect(client, userdata, flags, rc):
    print("✅ MQTT connected")
    client.subscribe("test/topic")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"📩 MQTT Received: {msg.topic} => {payload}")
    mqtt_messages.append({"topic": msg.topic, "payload": payload})

# 🌐 Root check
@app.route("/")
def index():
    return "✅ Container Manager API is running!"

# 🚀 Start containers
@app.route("/start", methods=["POST"])
def start_services():
    global container_manager, mqtt_client

    services = request.json.get("services", ["postgres", "mqtt"])
    print(f"🚀 Starting services: {services}")

    try:
        # Create and start container manager
        container_manager = ContainerManager(services=services)
        container_manager.__enter__()  # manually enter context
        print("✅ Containers started")

        # Get connection info and wait for ports
        for name in services:
            conn = container_manager.get_connection_info(name)
            if not wait_for_port(conn["host"], conn["port"], timeout=60):
                raise TimeoutError(f"{name} on {conn['host']}:{conn['port']} not ready.")

        # Start MQTT
        if "mqtt" in services:
            mqtt_info = container_manager.get_connection_info("mqtt")
            mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
            mqtt_client.on_connect = on_connect
            mqtt_client.on_message = on_message
            mqtt_client.connect(mqtt_info["host"], int(mqtt_info["port"]), 60)
            mqtt_client.loop_start()

        # Done
        info = {
            name: container_manager.get_connection_info(name)
            for name in services
        }

        return jsonify({"status": "started", "info": info})

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("❌ Error in /start:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

# 🛑 Stop containers
@app.route("/stop", methods=["POST"])
def stop_services():
    global container_manager, mqtt_client

    try:
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            mqtt_client = None

        if container_manager:
            container_manager.__exit__(None, None, None)
            container_manager = None

        print("🛑 Containers stopped")
        return jsonify({"status": "stopped"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 📦 Fetch test data
@app.route("/data", methods=["GET"])
def get_data():
    if not container_manager:
        return jsonify({"status": "error", "message": "No running containers"}), 400

    try:
        # PostgreSQL query
        pg_info = container_manager.get_connection_info("postgres")
        conn = psycopg2.connect(
            host=pg_info["host"],
            port=pg_info["port"],
            dbname=pg_info["database"],
            user=pg_info["user"],
            password=pg_info["password"],
            connect_timeout=3
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM test_data;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify({
            "status": "ok",
            "postgres": rows,
            "mqtt": mqtt_messages
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 📨 C++ client sends message
@app.route("/message", methods=["POST"])
def receive_message():
    data = request.json
    print(f"📨 Received from client: {data}")
    return jsonify({"status": "ok", "message": "Message received!"})

# ▶ Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
