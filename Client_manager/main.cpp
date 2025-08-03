#include "ContainerClient.h"
#include <iostream>

int main() {
    ContainerClient client("http://127.0.0.1:5050");
    auto info = client.start_services({"postgres","mqtt"});
    if (info.contains("postgres")) client.test_postgres(info["postgres"]);
    if (info.contains("mqtt")) client.test_mqtt(info["mqtt"]);
    client.stop_services();
    return 0;
}
