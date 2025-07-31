#include <iostream>
#include <string>
#include <curl/curl.h>
#include <thread>
#include <chrono>

const std::string SERVER_URL = "http://172.21.80.102:5050";
const std::string START_ENDPOINT = SERVER_URL + "/start";
const std::string STOP_ENDPOINT = SERVER_URL + "/stop";
const std::string MESSAGE_ENDPOINT = SERVER_URL + "/message";

// Function to send a POST request with JSON
void send_post(const std::string& url, const std::string& json_payload) {
    CURL* curl = curl_easy_init();
    if (curl) {
        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_payload.c_str());
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        CURLcode res = curl_easy_perform(curl);
        if (res != CURLE_OK)
            std::cerr << " Request to " << url << " failed: " << curl_easy_strerror(res) << std::endl;

        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
    }
}

int main() {
    std::cout << "▶Starting services..." << std::endl;
    send_post(START_ENDPOINT, R"({"services": ["postgres", "mqtt"]})");

    std::this_thread::sleep_for(std::chrono::seconds(2));  // wait a bit for containers to start

    std::cout << "Sending message to server..." << std::endl;
    send_post(MESSAGE_ENDPOINT, R"({"message": "Hello from C++ client!"})");

    std::this_thread::sleep_for(std::chrono::seconds(1));

    std::cout << " Stopping services..." << std::endl;
    send_post(STOP_ENDPOINT, "");

    return 0;
}
