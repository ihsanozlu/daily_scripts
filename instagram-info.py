import requests
import json

def getInstagramData(username):
    url = "https://www.instagram.com/api/v1/users/web_profile_info/?username=" + username
    headers = {
        'authority': 'www.instagram.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,tr;q=0.8',
        'cookie': 'mid=ZBh7jQAEAAE664tE7eyB47yngonH; ig_did=F45C0C88-2637-4347-A7DC-D39E2DCB73CC; ig_nrcb=1; datr=i3sYZCnnbPxGKI2x-E1A-dnP; csrftoken=p6Mn1LcS4qqeSWcvfc6VnERn8h24Q0ZC',
        'dpr': '2',
        'referer': 'https://www.instagram.com/' + username + "/",
        'sec-ch-prefers-color-scheme': 'dark',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-full-version-list': '"Google Chrome";v="117.0.5938.62", "Not;A=Brand";v="8.0.0.0", "Chromium";v="117.0.5938.62"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-model': '"Nexus 5"',
        'sec-ch-ua-platform': '"Android"',
        'sec-ch-ua-platform-version': '"6.0"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36',
        'viewport-width': '466',
        'x-asbd-id': '129477',
        'x-csrftoken': 'p6Mn1LcS4qqeSWcvfc6VnERn8h24Q0ZC',
        'x-ig-app-id': '1217981644879628',
        'x-ig-www-claim': '0',
        'x-requested-with': 'XMLHttpRequest',
    }

    response = requests.get(url, headers=headers)
    print(response.text)
    if response.status_code == 200:
        body = json.loads(response.text)
        print("username: ", body["data"]["user"]["username"])
        print("fullname: ", body["data"]["user"]["full_name"])
        print("biografi: ", body["data"]["user"]["biography"])
        print("external url: ", body["data"]["user"]["external_url"])
        print("follower count: ", body["data"]["user"]["edge_followed_by"]["count"])
        print("follow count: ", body["data"]["user"]["edge_follow"]["count"])
        print("profile photo: ", body["data"]["user"]["profile_pic_url_hd"])
        print("private:", body["data"]["user"]["is_private"])
        print("total media count: ", body["data"]["user"]["edge_owner_to_timeline_media"]["count"])
    else:
        print(f"The request has been failed. Status code: {response.status_code}")


getInstagramData("instagram_username")

