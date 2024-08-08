import requests
import json
from ast import literal_eval
import csv
import base64

# Authorization
headers = {
  'Authorization': 'Bearer dapitokendatabricks',
}


def rec_req(instance="https://your-databaricks-server-url.azuredatabricks.net", loc="/", target_table="your_table"):
    data_path = '{{"path": "{0}"}}'.format(loc)
    url = '{}/api/2.0/workspace/list'.format(instance)
    response = requests.get(url, headers=headers, data=data_path)
    response.raise_for_status()
    jsonResponse = response.json()

    results = []

    for i, result in jsonResponse.items():
        for value in result:
            dump = json.dumps(value)
            data = literal_eval(dump)
            if data['object_type'] == 'DIRECTORY':
                results += rec_req(instance, data['path'], target_table)
            elif data['object_type'] == 'NOTEBOOK':
                notebook_path = data['path']
                notebook_url = f'{instance}/api/2.0/workspace/export'
                notebook_response = requests.get(notebook_url, headers=headers, params={'format': 'SOURCE', 'path': notebook_path})
                notebook_response.raise_for_status()
                notebook_content_encoded = notebook_response.json()['content']
                notebook_content = base64.b64decode(notebook_content_encoded).decode('utf-8')
                if target_table in notebook_content:
                    results.append((f'Table {target_table} found in notebook: {notebook_path}',))

    return results


# Call the function and get the results
results = rec_req()

print(results)  # Add this line to verify the contents of results

# Save the results to a CSV file
with open('/target_table_used_notebooks_search_result_local.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(results)



