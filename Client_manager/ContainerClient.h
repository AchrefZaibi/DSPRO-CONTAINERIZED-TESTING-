#pragma once
#include <string>
#include <vector>
#include <nlohmann/json.hpp>

class ContainerClient {
public:
    explicit ContainerClient(const std::string& server_url);
    nlohmann::json start_services(const std::vector<std::string>& services);
    void stop_services();
    bool test_postgres(const nlohmann::json& pginfo);
    bool test_mqtt(const nlohmann::json& mqttinfo);

private:
    std::string server_url;
    std::string start_endpoint;
    std::string stop_endpoint;
    static size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* userp);
    std::string send_post_and_return_response(const std::string& url, const std::string& json_payload);
    void send_post(const std::string& url, const std::string& json_payload);
};
