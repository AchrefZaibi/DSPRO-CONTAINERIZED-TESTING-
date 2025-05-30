from testcontainers.core.container import DockerContainer

def start_mqtt():
    container = (
        DockerContainer("eclipse-mosquitto:2.0")
        .with_exposed_ports(1883)
        .with_command("/usr/sbin/mosquitto -c /mosquitto-no-auth.conf")
    )
    container.start()
    return container