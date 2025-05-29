from testcontainers.postgres import PostgresContainer

def start_postgres():
    container = PostgresContainer("postgres:15")
    container.with_env("POSTGRES_DB", "testdb")
    container.with_env("POSTGRES_USER", "user")
    container.with_env("POSTGRES_PASSWORD", "pass")
    container.with_exposed_ports(5432)
    container.start()
    return container
