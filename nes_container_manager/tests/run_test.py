import psycopg2


try:
    conn = psycopg2.connect(
        host=pg_info["host"],
        port=pg_info["port"],
        dbname=pg_info["database"],
        user=pg_info["user"],
        password=pg_info["password"]
    )

    cur = conn.cursor()

    # ✅ Step 1: Create table
    cur.execute("CREATE TABLE IF NOT EXISTS test_data (id SERIAL PRIMARY KEY, name TEXT);")

    # ✅ Step 2: Insert test data
    cur.execute("INSERT INTO test_data (name) VALUES ('Ghassen');")

    conn.commit()

    # ✅ Step 3: Query data
    cur.execute("SELECT * FROM test_data;")
    rows = cur.fetchall()
    print("✅ DB Rows:", rows)

    cur.close()
    conn.close()

except Exception as e:
    print("❌ Error:", e)


import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("✅ Connected to MQTT Broker")

def on_message(client, userdata, msg):
    print(f"📩 Received: {msg.topic} => {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_info["host"], int(mqtt_info["port"]), 60)

client.loop_start()

# ✅ Step 1: Subscribe to topic
client.subscribe("test/topic")

# ✅ Step 2: Publish a message
client.publish("test/topic", "Hello from test!")

# ✅ Step 3: Wait briefly to receive
import time
time.sleep(2)

client.loop_stop()
client.disconnect()





