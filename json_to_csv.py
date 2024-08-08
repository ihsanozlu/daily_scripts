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

# Replace 'input.json' with the path to your JSON file
# Replace 'output.csv' with the path where you want to save the CSV file
json_to_csv('/Users/ihsan/Downloads/input.json', '/Users/ihsan/Downloads/output.csv')

