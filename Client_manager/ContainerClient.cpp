#include "ContainerClient.h"
#include <curl/curl.h>
#include <libpq-fe.h>
#include <mqtt/async_client.h>
#include <iostream>
#include <thread>
#include <chrono>

using json = nlohmann::json;

ContainerClient::ContainerClient(const std::string& url)
    : server_url(url), start_endpoint(url + "/start"), stop_endpoint(url + "/stop") {}

size_t ContainerClient::WriteCallback(void* contents, size_t size, size_t nmemb, std::string* userp) {
    size_t totalSize = size * nmemb;
    userp->append((char*)contents, totalSize);
    return totalSize;
}

std::string ContainerClient::send_post_and_return_response(const std::string& url, const std::string& json_payload) {
    CURL* curl = curl_easy_init();
    std::string response_string;
    if (curl) {
        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_payload.c_str());
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_string);

        CURLcode res = curl_easy_perform(curl);
        if (res != CURLE_OK) {
            std::cerr << "Request to " << url << " failed: " << curl_easy_strerror(res) << std::endl;
        }
        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
    }
    return response_string;
}

void ContainerClient::send_post(const std::string& url, const std::string& json_payload) {
    CURL* curl = curl_easy_init();
    if (curl) {
        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_payload.c_str());
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_perform(curl);
        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
    }
}

json ContainerClient::start_services(const std::vector<std::string>& services) {
    json req;
    req["services"] = services;
    std::string resp = send_post_and_return_response(start_endpoint, req.dump());
    try {
        json jresp = json::parse(resp);
        std::cout << "Response from /start:\n" << jresp.dump(4) << std::endl;
        // Optionally sleep a little if containers need time
        std::this_thread::sleep_for(std::chrono::seconds(2));
        return jresp;
    } catch (std::exception& e) {
        std::cerr << "JSON parse error: " << e.what() << "\nResponse was: " << resp << std::endl;
        return {};
    }
}

void ContainerClient::stop_services() {
    send_post(stop_endpoint, R"({"status":"stopped"})");
}

bool ContainerClient::test_postgres(const json& pginfo) {
    std::string conninfo =
        "host=" + pginfo["host"].get<std::string>() +
        " port=" + std::to_string(pginfo["port"].get<int>()) +
        " user=" + pginfo["user"].get<std::string>() +
        " password=" + pginfo["password"].get<std::string>() +
        " dbname=" + pginfo["database"].get<std::string>();

    PGconn* conn = PQconnectdb(conninfo.c_str());
    if (PQstatus(conn) != CONNECTION_OK) {
        std::cerr << "Connection to Postgres failed: " << PQerrorMessage(conn) << std::endl;
        PQfinish(conn);
        return false;
    }
    PQexec(conn, "CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, txt VARCHAR(100));");
    PGresult* res = PQexec(conn, "INSERT INTO test_table(txt) VALUES('Hello from C++ client!') RETURNING id;");
    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        std::cerr << "Postgres insert failed: " << PQerrorMessage(conn) << std::endl;
        PQclear(res);
        PQfinish(conn);
        return false;
    }
    std::cout << "Inserted row into Postgres, id: " << PQgetvalue(res, 0, 0) << std::endl;
    PQclear(res);
    PQfinish(conn);
    return true;
}

bool ContainerClient::test_mqtt(const json& mqttinfo) {
    std::string address = "tcp://" + mqttinfo["host"].get<std::string>() + ":" + std::to_string(mqttinfo["port"].get<int>());
    std::string client_id = "cpp-client";
    mqtt::async_client client(address, client_id);

    mqtt::connect_options connOpts;
    if (mqttinfo.contains("username") && mqttinfo.contains("password")) {
        connOpts.set_user_name(mqttinfo["username"].get<std::string>());
        connOpts.set_password(mqttinfo["password"].get<std::string>());
    }

    try {
        auto tok = client.connect(connOpts);
        tok->wait();
        std::string topic = "test/topic";
        std::string payload = "Hello from C++ client!";
        client.publish(topic, payload.c_str(), payload.size(), 1, false)->wait();
        std::cout << "Published test MQTT message." << std::endl;
        client.disconnect()->wait();
        return true;
    }
    catch (const mqtt::exception& exc) {
        std::cerr << "MQTT error: " << exc.what() << std::endl;
        return false;
    }
}
