import openpyxl
import subprocess

def copy_with_azcopy(source_path, destination_path):
    # AzCopy command to copy files
    azcopy_command = f"azcopy copy '{source_path}{SAStoken}' '{destination_path}' --recursive"

    # Execute the AzCopy command
    subprocess.call(azcopy_command, shell=True)

def read_names_from_excel(file_path):
    # Load the Excel file
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active

    # Get the column with the names (assuming it's column A)
    names_column = sheet['A']

    # Extract the names from the column
    names = [cell.value for cell in names_column if cell.value is not None]

    return names

# Path to the Excel file
excel_file_path = '/Users/ihsan/Desktop/all-names-dvc-apps2.xlsx'

# Path to the source and destination directories or containers
SAStoken='yoursastoken'
source_path = 'source_blob_url_path'
destination_path = 'destination_blob_url_path'

# Read names from Excel file
names = read_names_from_excel(excel_file_path)

# Copy files using AzCopy for each name
for name in names:
    source_file = f'{source_path}/{name}'  # Modify this based on your source file structure
    destination_file = f'{destination_path}'  # Modify this based on your destination file structure

    copy_with_azcopy(source_file, destination_file)

print("File copy completed.")

