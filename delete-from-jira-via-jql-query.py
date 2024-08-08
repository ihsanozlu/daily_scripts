import requests
from requests.auth import HTTPBasicAuth

# Set your Jira server URL and email
JIRA_URL = 'https://yourserver.atlassian.net'
EMAIL = 'your@email.net'
API_TOKEN = 'yourapitoken'
# Construct the JQL query to select the issues you want to delete
JQL_QUERY = 'project = "VAA" AND issueKey >= VAA-4755 AND issueKey <= VAA-4798 AND issueType = Epic'

# Perform authentication using HTTP BasicAuth
auth = HTTPBasicAuth(EMAIL, API_TOKEN)

# Perform a JQL search to retrieve the issues to delete
search_response = requests.get(
    f'{JIRA_URL}/rest/api/2/search',
    auth=auth,
    params={'jql': JQL_QUERY, 'maxResults': 1000}  # Adjust maxResults as needed
)
if search_response.status_code != 200:
    print("Failed to execute JQL search.")
    exit()

issues_to_delete = search_response.json()['issues']

# Delete each issue individually
for issue in issues_to_delete:
    issue_key = issue['key']
    delete_response = requests.delete(
        f'{JIRA_URL}/rest/api/2/issue/{issue_key}',
        auth=auth
    )
    if delete_response.status_code == 204:
        print(f"Issue {issue_key} deleted successfully.")
    else:
        print(f"Failed to delete issue {issue_key}. Error: {delete_response.text}")

