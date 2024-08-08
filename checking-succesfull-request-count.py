import requests
from requests.auth import HTTPBasicAuth

USERNAME = "username"
PASSWORD = "password"


def send_request(device_id):
    url = f"https://yourendpoint/api/v1/{device_id}"
    response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if response.status_code == 200:
        return True
    else:
        return False

def main(device_ids):
    successful_requests = 0
    unsuccessful_devices = []
    for device in device_ids:
        device_id = device['deviceId']
        if send_request(device_id):
            successful_requests += 1
            print(f"Successfull request count:  {successful_requests}")
        else:
            unsuccessful_devices.append(device_id)
    print(f"Total successful requests: {successful_requests}")
    if unsuccessful_devices:
        print("Unsuccessful requests:")
        for device_id in unsuccessful_devices:
            print(device_id)

if __name__ == "__main__":
    # Example device IDs, replace with your own list or read from CSV
    device_ids = []
    main(device_ids)

