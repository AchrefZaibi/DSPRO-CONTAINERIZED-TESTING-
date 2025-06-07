from nes_container_manager.manager.manager import ContainerManager
import pytest

def test_containers_run():
    with ContainerManager(services=["mqtt", "postgres"]) as manager:
        mqtt_info = manager.get_connection_info("mqtt")
        pg_info = manager.get_connection_info("postgres")

        print("MQTT running on:", mqtt_info)
        print("Postgres running on:", pg_info)
def test_start_and_get_connection_info():
    with ContainerManager(services=["mqtt", "postgres"]) as manager:
        # Ensure containers are stored
        assert "mqtt" in manager.containers
        assert "postgres" in manager.containers

        # Test MQTT connection info
        mqtt_info = manager.get_connection_info("mqtt")
        assert "host" in mqtt_info
        assert "port" in mqtt_info

        # Test Postgres connection info
        pg_info = manager.get_connection_info("postgres")
        assert pg_info["host"]
        assert pg_info["port"]
        assert pg_info["database"] == "testdb"
        assert pg_info["user"] == "user"
        assert pg_info["password"] == "password"

def test_get_connection_info_before_start():
    manager = ContainerManager(services=["mqtt"])
    # Not using context manager, no containers started
    assert manager.get_connection_info("mqtt") is None

def test_cleanup_services_stops_all(monkeypatch):
    class DummyContainer:
        def __init__(self):
            self.stopped = False
        def stop(self):
            self.stopped = True

    dummy = DummyContainer()
    manager = ContainerManager(services=[])
    manager.containers = {
        "mqtt": dummy,
        "postgres": dummy,
    }
    manager.cleanup_services()
    assert dummy.stopped is True

def test_invalid_service_raises():
    manager = ContainerManager(services=[])
    with pytest.raises(ValueError):
        manager.start_service("invalid_service_name")
