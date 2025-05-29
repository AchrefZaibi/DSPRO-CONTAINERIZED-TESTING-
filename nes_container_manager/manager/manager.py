from nes_container_manager.services.mqtt import start_mqtt
from nes_container_manager.services.postgres import start_postgres

class ContainerManager:
    def __init__(self, services):
        self.services = services
        self.containers = {}

    def __enter__(self):
        for service in self.services:
            container = self.start_service(service)
            self.containers[service] = container
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_services()

    def start_service(self, service_name):
        if service_name == "mqtt":
            return start_mqtt()
        elif service_name == "postgres":
            return start_postgres()
        else:
            raise ValueError(f"Unknown service: {service_name}")

    def get_connection_info(self, service_name):
        container = self.containers.get(service_name)
        if not container:
            return None
        if service_name == "postgres":
            return {
                "host": container.get_container_host_ip(),
                "port": container.get_exposed_port(5432),
                "database": "testdb",
                "user": "user",
                "password": "pass"
            }
        elif service_name == "mqtt":
            return {
                "host": container.get_container_host_ip(),
                "port": container.get_exposed_port(1883)
            }

    def cleanup_services(self):
        for container in self.containers.values():
            try:
                container.stop()
            except Exception as e:
                print(f"Error stopping container: {e}")
