#!/bin/bash

# Output file path
output_file="vm_memory_info.json"

# Start with an empty array
echo "[" > "$output_file"

# Fetch the list of VMs and process each VM
az vm list --query "[].{VMName:name, Location:location, VmSize:hardwareProfile.vmSize}" -o tsv | while read vm_name location vm_size; do
  memory_size=$(az vm list-sizes --location "$location" --query "[?name=='$vm_size'].memoryInMB" -o tsv)
  # Add each JSON object to the output file, appending comma if it's not the first object
  echo "{\"VMName\":\"$vm_name\", \"Memory\":$memory_size}," >> "$output_file"
done

# Remove the last comma and close the array
sed -i '' -e '$ s/,$//' "$output_file"
echo "]" >> "$output_file"
