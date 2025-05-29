from testcontainers.core.container import DockerContainer

def start_mqtt():
    container = DockerContainer("eclipse-mosquitto:2.0")
    container.with_exposed_ports(1883)
    container.start()
    return container