from nes_container_manager.manager.manager import ContainerManager
import psycopg2
import paho.mqtt.client as mqtt
import time

# 👇 Everything goes inside this block!
with ContainerManager(services=["mqtt", "postgres"]) as manager:
    pg_info = manager.get_connection_info("postgres")
    mqtt_info = manager.get_connection_info("mqtt")

    # === PostgreSQL Logic ===
    try:
        conn = psycopg2.connect(
            host=pg_info["host"],
            port=pg_info["port"],
            dbname=pg_info["database"],
            user=pg_info["user"],
            password=pg_info["password"]
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


    # === MQTT Logic ===
    def on_connect(client, userdata, flags, rc):
        print("✅ Connected to MQTT Broker")

    def on_message(client, userdata, msg):
        print(f"📩 Received: {msg.topic} => {msg.payload.decode()}")

    client = mqtt.Client(protocol=mqtt.MQTTv311)
    # or mqtt.MQTTv5
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        # This connects to the broker using connection info from mqtt_info, 60 is keep alive interval in seconds
        client.connect(mqtt_info["host"], int(mqtt_info["port"]), 60)
        client.loop_start()
        client.subscribe("test/topic")
        #If a message is published to a topic you're subscribed to — you receive it.
        client.publish("test/topic", "Hello from ContainerManager!")
        time.sleep(2)
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        print("❌ MQTT Error:", e)






