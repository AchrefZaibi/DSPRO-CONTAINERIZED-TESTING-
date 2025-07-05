from testcontainers.postgres import PostgresContainer


def start_postgres():
    container = PostgresContainer(
        image="postgres:15",
        username="user",
        password="password",
        dbname="testdb"
    )
    container.with_exposed_ports(5432)
    container.start()
    return container
