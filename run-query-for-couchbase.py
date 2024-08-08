from couchbase.cluster import Cluster, ClusterOptions
from couchbase.auth import PasswordAuthenticator
from datetime import timedelta
import json
import csv

def json_to_csv(json_file, csv_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header using keys from the first dictionary in the JSON
        writer.writerow(data[0].keys())

        # Write data
        for row in data:
            writer.writerow(row.values())

# Couchbase Server connection settings
cluster = Cluster('couchbase://yourhost', ClusterOptions(
    authenticator=PasswordAuthenticator('username', 'password'),
    scan_wait=timedelta(seconds=120)
))

# Replace 'bucket_name' with the name of your bucket
bucket = cluster.bucket('hybrid_data_lake')
collection = bucket.default_collection()

# Couchbase N1QL query
query = '''
    --put the N1QL query here
'''

# Execute the query
result = cluster.query(query,scan_wait=timedelta(seconds=120))

# Fetch results as JSON objects
json_results = [row for row in result]

# Convert JSON to CSV
json_file_path = '/Users/ihsan/Downloads/result_of_query.json'  # Temporarily store JSON data
csv_file_path = '/Users/ihsan/Downloads/result_of_query.csv'  # Replace with your desired CSV file path

with open(json_file_path, 'w') as jsonfile:
    json.dump(json_results, jsonfile)

# Convert JSON to CSV
json_to_csv(json_file_path, csv_file_path)

print("Result written to", csv_file_path)

