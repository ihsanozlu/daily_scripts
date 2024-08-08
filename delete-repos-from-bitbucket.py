import requests
from requests.auth import HTTPBasicAuth

# Replace with your Bitbucket workspace ID and username
workspace = "yourworkspace"
username = "username"
# Your personal access token from Bitbucket
access_token = "yourpersonalaccestoken"

# Bitbucket API endpoint for listing repositories
base_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}"

# Function to delete a repository
def delete_repo(repo_slug):
    delete_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}"
    response = requests.delete(delete_url, auth=HTTPBasicAuth(username, access_token))
    if response.status_code == 204:
        print(f"Successfully deleted {repo_slug}")
    else:
        print(f"Failed to delete {repo_slug}: {response.status_code} - {response.text}")

# Function to get repositories with pagination
def get_repositories_with_pagination(url):
    while url:
        response = requests.get(url, auth=HTTPBasicAuth(username, access_token))
        if response.status_code == 200:
            data = response.json()
            for repo in data["values"]:
                yield repo["slug"]
            url = data.get("next")  # Get the next page URL if it exists
        else:
            print(f"Failed to fetch repositories: {response.status_code} - {response.text}")
            break

# Main function to delete all repositories
def delete_all_repositories():
    for repo_slug in get_repositories_with_pagination(base_url):
        print(f"Deleting repository: {repo_slug}")
        delete_repo(repo_slug)

# Execute the script
if __name__ == "__main__":
    delete_all_repositories()

