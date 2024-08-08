import os
import re
import requests
from requests.auth import HTTPBasicAuth

source_workspace = "sourceworkspace"
destination_workspace = "destinationworkspace"
s_username = "sourceusername"
s_password = "sourcetoken"

d_username = "destinationusername"
d_password = "destinationtoken"

s_auth = HTTPBasicAuth(s_username, s_password)
d_auth = HTTPBasicAuth(d_username, d_password)

def get_repositories():
    repos = []
    url = f"https://api.bitbucket.org/2.0/repositories/{source_workspace}"
    
    while url:
        response = requests.get(url, auth=s_auth)
        if response.status_code != 200:
            print(f"Error fetching repositories: {response.status_code} - {response.text}")
            break
        data = response.json()
        repos.extend(data['values'])
        url = data.get('next')

    return repos

# Function to get the list of projects from the source workspace
def get_projects():
    projects = []
    url = f"https://api.bitbucket.org/2.0/workspaces/{source_workspace}/projects"

    while url:
        response = requests.get(url, auth=s_auth)
        if response.status_code != 200:
            print(f"Error fetching projects: {response.status_code} - {response.text}")
            break
        data = response.json()
        projects.extend(data['values'])
        url = data.get('next')

    return projects

# Function to format repository name
def format_repo_name(name):
    return re.sub(r'[^a-z0-9._-]', '', name.lower())

# Function to create a project in the destination workspace
def create_project(project):
    project_key = project['key']
    project_name = project['name']
    project_description = project.get('description', '')

    response = requests.post(
        f"https://api.bitbucket.org/2.0/workspaces/{destination_workspace}/projects",
        auth=d_auth,
        json={
            "key": project_key,
            "name": project_name,
            "description": project_description
        }
    )
    if response.status_code != 201:
        print(f"Error creating project {project_key}: {response.status_code} - {response.text}")
    return response.status_code

# Function to create a repository in the destination workspace within a project
def create_repository(repo, project_key):
    repo_name = format_repo_name(repo['name'])
    response = requests.post(
        f"https://api.bitbucket.org/2.0/repositories/{destination_workspace}/{repo_name}",
        auth=d_auth,
        json={
            "scm": "git",
            "is_private": True,
            "project": {"key": project_key}
        }
    )
    if response.status_code != 201:
        print(f"Error creating repository {repo_name}: {response.status_code} - {response.text}")
    return response.status_code

# Get the list of projects and repositories from the source workspace
projects = get_projects()
repos = get_repositories()

# Create projects in the destination workspace
for project in projects:
    create_project(project)

# Migrate repositories
for repo in repos:
    repo_name = format_repo_name(repo["name"])
    clone_url = repo["links"]["clone"][0]["href"]
    project_key = repo["project"]["key"]

    try:
        # Clone the repository
        os.system(f"git clone {clone_url}")

        try:
            # Change directory to the cloned repository
            os.chdir(repo_name)
        except FileNotFoundError as e:
            print(f"Error: {e} - Skipping repository {repo_name}")
            continue

        try:
            # Create the repository in the destination workspace within the project
            create_repository(repo, project_key)

            # Push the repository to the new workspace
            os.system(f"git remote set-url origin https://{d_username}:{d_password}@bitbucket.org/{destination_workspace}/{repo_name}.git")
            os.system("git push -u origin --all")
            os.system("git push -u origin --tags")
        except Exception as e:
            print(f"Error during repository operations: {e} - Skipping repository {repo_name}")

        finally:
            # Change back to the parent directory
            os.chdir("..")
            # Remove the cloned repository
            os.system(f"rm -rf {repo_name}")

    except Exception as e:
        print(f"Unexpected error with repository {repo_name}: {e}")

print("Repositories and projects migration completed!")

