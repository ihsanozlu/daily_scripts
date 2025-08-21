import requests

ZABBIX_URL = "http://your_zabbix_host/api_jsonrpc.php"
headers = {
    "Content-Type": "application/json"
}

service_map = {
    "rds": ["REDIS-SERVER1.SERVICE STATUS", "REDIS-SERVER2.SERVICE STATUS", "REDIS-SERVER3.SERVICE STATUS"],
    "vrn": ["VARNISH.SERVICE STATUS"],
    "kfk": ["KAFKA-SERVER.SERVICE STATUS"],
    "mq": ["RABBITMQ-SERVER.SERVICE STATUS"],
    "elsc": ["KIBANA.SERVICE STATUS", "ELASTICSEARCH.SERVICE STATUS"],
    "k8smc": ["RKE2-SERVER.SERVICE STATUS"],
    "k8swc": ["RKE2-AGENT.SERVICE STATUS"]
}

login_resp = requests.post(ZABBIX_URL, headers=headers, json={
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {"username": "user", "password": "pass"},
    "id": 1
}).json()

if "result" not in login_resp:
    raise SystemExit(f"Login failed: {login_resp}")

API_TOKEN = login_resp["result"]
print("Got API token:", API_TOKEN)

headers["Authorization"] = f"Bearer {API_TOKEN}"

hosts_resp = requests.post(ZABBIX_URL, headers=headers, json={
    "jsonrpc": "2.0",
    "method": "host.get",
    "params": {"output": ["hostid", "name"]},
    "id": 2
}).json()

if "result" not in hosts_resp:
    raise SystemExit(f"Host fetch failed: {hosts_resp}")

for host in hosts_resp["result"]:
    hostid = host["hostid"]
    hostname = host["name"].lower()

    for key, items in service_map.items():
        if key in hostname:
            print(f"Host {hostname} -> enable items: {items}")

            items_resp = requests.post(ZABBIX_URL, headers=headers, json={
                "jsonrpc": "2.0",
                "method": "item.get",
                "params": {"hostids": hostid, "output": ["itemid", "name", "status"]},
                "id": 3
            }).json()

            if "result" not in items_resp:
                print(f"  Failed to get items for {hostname}: {items_resp}")
                continue

            for item in items_resp["result"]:
                if item["name"] in items and item["status"] == "1":  # 1 = disabled
                    print(f" -> Enabling {item['name']}")
                    requests.post(ZABBIX_URL, headers=headers, json={
                        "jsonrpc": "2.0",
                        "method": "item.update",
                        "params": {"itemid": item["itemid"], "status": 0},
                        "id": 4
                    })
