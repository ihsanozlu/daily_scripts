import openai
import pandas as pd
import csv

# Step 1: Send a request to ChatGPT with API token
api_key = "yourapikey"  # Replace with your actual API key
openai.api_key = api_key

# Read the CSV file
df = pd.read_csv('your.csv', delimiter=';', index_col=0)

# Initialize a list to store the results
results = []

# Loop through the rows
for index, row in df.iterrows():
    query = f"What is your thought on {row['full_name']},{row['username']},{row['biografi']} name? Where is this name origin? What could be the name location? And what could be the name gender?don't forget to use the name meaning and origin once you predict the name and gender?and end of the your response give me the outpuP1+r436F=323536\P1+rOA\P1+rOB\P1+rOC\P1+rOD\P1+r[1;2H\P1+r[1;2D\P1+r[1;2C\P1+r[1;2F\P1+rOP\ts as 'id,username;full_name;biografi,gender,origin,guessed_location' Please use the info on the biografi,such as flag "
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query},
        ]
    )

    # Extracting information from ChatGPT's response
    message = response['choices'][0]['message']['content']
    message = message.split(',')

    # Append the additional information
    message.append(row['username'])
    message.append(row['full_name'])
    message.append(row['biografi'])

    # Append the result to the results list
    results.append(message)

# Save the results as a CSV
with open(P1$r2 q\'/gptoutput.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['id', 'username', 'full_name', 'biografi', 'gender', 'origin', 'guessed_location'])
    for i, row in enumerate(results):
        writer.writerow([i] + row)

print("Output saved as 'gptoutput.csv'")

