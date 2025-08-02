from nes_container_manager.manager.manager import ContainerManager
import psycopg2
import paho.mqtt.client as mqtt
import time
import socket

# 🔁 Helper function to wait for service to become available
def wait_for_port(host, port, timeout=30):
    print(f"🔄 Waiting for {host}:{port} ...")
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, int(port)), timeout=2):
                print(f"✅ Port {port} on {host} is open!")
                return True
        except OSError as e:
            print(f"⏳ Still waiting for {host}:{port} ... {str(e)}")
            if time.time() - start_time > timeout:
                print(f"❌ Timeout reached for {host}:{port}")
                return False
            time.sleep(1)

# 👇 Everything goes inside this block!
with ContainerManager(services=["mqtt", "postgres"]) as manager:
    pg_info = manager.get_connection_info("postgres")
    mqtt_info = manager.get_connection_info("mqtt")

    # === PostgreSQL Logic ===
    if wait_for_port(pg_info["host"], pg_info["port"]):
        try:
            conn = psycopg2.connect(
                host=pg_info["host"],
                port=pg_info["port"],
                dbname=pg_info["database"],
                user=pg_info["user"],
                password=pg_info["password"],
                connect_timeout=3
            )


            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS test_data (id SERIAL PRIMARY KEY, name TEXT);")
            cur.execute("INSERT INTO test_data (name) VALUES ('Ghassen');")
            conn.commit()
            cur.execute("SELECT * FROM test_data;")
            rows = cur.fetchall()
            print("✅ DB Rows:", rows)
            cur.close()
            conn.close()

        except Exception as e:
            print("❌ DB Error:", e)
            print("🔍 pg_info:", pg_info)
    else:

        print("❌ PostgreSQL not ready after timeout")

    # === MQTT Logic ===
    def on_connect(client, userdata, flags, rc):
        print("✅ Connected to MQTT Broker")

    def on_message(client, userdata, msg):
        print(f"📩 Received: {msg.topic} => {msg.payload.decode()}")

    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    if wait_for_port(mqtt_info["host"], mqtt_info["port"]):
        try:
            client.connect(mqtt_info["host"], int(mqtt_info["port"]), 60)
            client.loop_start()
            client.subscribe("test/topic")
            client.publish("test/topic", "Hello from ContainerManager!")
            time.sleep(2)
            client.loop_stop()
            client.disconnect()
        except Exception as e:
            print("❌ MQTT Error:", e)
    else:
        print("❌ MQTT not ready after timeout")