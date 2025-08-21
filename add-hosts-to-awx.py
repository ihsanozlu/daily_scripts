import requests
import pandas as pd

AWX_URL = "https://your_awx_url:32236/api/v2"
TOKEN = "token"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def get_inventory_id(name):
    url = f"{AWX_URL}/inventories/?name={name}"
    r = requests.get(url, headers=HEADERS, verify=False)
    data = r.json()
    if data['count'] > 0:
        return data['results'][0]['id']
    else:
        payload = {"name": name, "organization": 1} 
        r = requests.post(f"{AWX_URL}/inventories/", headers=HEADERS, json=payload, verify=False)
        return r.json()['id']

def add_host(inventory_id, host_name, ansible_host):
    variables = f"---\nansible_host: '{ansible_host}'"
    payload = {
        "name": host_name,
        "inventory": inventory_id,
        "variables": variables
    }
    r = requests.post(f"{AWX_URL}/hosts/", headers=HEADERS, json=payload, verify=False)
    if r.status_code == 201:
        print(f"✅ Host '{host_name}' added to inventory {inventory_id}")
    else:
        print(f"❌ Failed to add host '{host_name}': {r.text}")

df = pd.read_excel('/Users/user/Documents/add-hosts-to-ansible.xlsx')

for _, row in df.iterrows():
    inv_id = get_inventory_id(row['inventory_name'])
    add_host(inv_id, row['host_name'], row['host_ip'])
