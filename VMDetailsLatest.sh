#!/bin/bash

# Initialize an empty array to hold VM data (this is now for logging purposes)
vm_data=()

# Fetch the list of VMs
vm_list=$(az vm list --query "[].{VMName:name, ResourceGroup:resourceGroup, Location:location, VmSize:hardwareProfile.vmSize}" -o tsv)

# Process each VM in sequence to avoid parallel issues
echo "$vm_list" | while read vm_name resource_group location vm_size; do
  echo "Processing VM: $vm_name"
  echo "Location: $location"  # Print the location to check if it's populated

  # Fetch details for the current VM
  if [ -z "$location" ]; then
    echo "Location is empty for VM: $vm_name"
    continue  # Skip to the next VM if location is empty
  fi

  vcpu_count=$(az vm list-sizes --location "$location" --query "[?name=='$vm_size'].numberOfCores" -o tsv)
  memory_size=$(az vm list-sizes --location "$location" --query "[?name=='$vm_size'].memoryInMB" -o tsv)

  # Ensure each variable is populated
  echo "vCPU: $vcpu_count, Memory: $memory_size"

  private_ip=$(az vm list-ip-addresses --name "$vm_name" --resource-group "$resource_group" --query "[].virtualMachine.network.privateIpAddresses[0]" -o tsv)
  public_ip=$(az vm list-ip-addresses --name "$vm_name" --resource-group "$resource_group" --query "[].virtualMachine.network.publicIpAddresses[0].ipAddress" -o tsv)

  os_type=$(az vm show --name "$vm_name" --resource-group "$resource_group" --query "storageProfile.osDisk.osType" -o tsv)
  os_disk_storage_account=$(az vm show --name "$vm_name" --resource-group "$resource_group" --query "storageProfile.osDisk.managedDisk.storageAccountType" -o tsv)
  os_disk_size=$(az vm show --name "$vm_name" --resource-group "$resource_group" --query "storageProfile.osDisk.diskSizeGb" -o tsv)

  data_disks=$(az vm show --name "$vm_name" --resource-group "$resource_group" --query "storageProfile.dataDisks[].{StorageAccountType:managedDisk.storageAccountType, DiskSize:diskSizeGb}" -o tsv)

  # Collect the data for each VM in a JSON-like format
  vm_data+=(
    "{
      \"VMName\": \"$vm_name\",
      \"ResourceGroup\": \"$resource_group\",
      \"Location\": \"$location\",
      \"VmSize\": \"$vm_size\",
      \"vCPU\": \"$vcpu_count\",
      \"MemorySize\": \"$memory_size\",
      \"PrivateIPs\": \"$private_ip\",
      \"PublicIPs\": \"$public_ip\",
      \"OsType\": \"$os_type\",
      \"OsDiskStorageAccountType\": \"$os_disk_storage_account\",
      \"OsDiskSizeGb\": \"$os_disk_size\",
      \"DataDiskStorageAccountType\": \"$(echo "$data_disks" | awk '{print $1}' | paste -sd ',' -)\",
      \"DataDiskSizeGb\": \"$(echo "$data_disks" | awk '{print $2}' | paste -sd ',' -)\"
    }"
  )
done

# Output the collected data to a file
echo "[${vm_data[@]}]" > vm_data.json
