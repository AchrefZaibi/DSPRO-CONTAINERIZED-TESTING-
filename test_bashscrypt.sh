#!/bin/bash

echo "=== Building Docker image: mytest-test6 ==="
docker build -t mytest-test6 .

echo ""
echo "=== Running container and mounting Docker socket ==="
docker run -v /var/run/docker.sock:/var/run/docker.sock -e TESTCONTAINERS_RYUK_DISABLED=true mytest-test6

echo "" 
echo "=== running unit tests for the python library ( every function ) "
pytest nes_container_manager/tests/test_container.py
