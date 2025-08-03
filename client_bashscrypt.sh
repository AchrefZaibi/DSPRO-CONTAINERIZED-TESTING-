#!/bin/bash

echo "Compiling client..."
g++ -o client client_manager/main.cpp client_manager/ContainerClient.cpp -lcurl -lpq -lpaho-mqttpp3 -lpaho-mqtt3as -std=c++11 -I/usr/include/postgresql

echo "Running client..."
./client

