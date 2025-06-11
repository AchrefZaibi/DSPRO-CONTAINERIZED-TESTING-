from setuptools import setup, find_packages

setup(
    name="nes_container_manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "testcontainers",
        "psycopg2-binary",
        "paho-mqtt",
        "pytest"
    ],
)
