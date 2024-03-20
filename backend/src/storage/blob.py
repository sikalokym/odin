import io
import os
import configparser
from azure.storage.blob import BlobServiceClient
import pandas as pd

# Load configurations
config = configparser.ConfigParser()
config.read('config/azure_blob.cfg')

# Initialize BlobServiceClient
connection_string = os.environ.get('STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

def add_visa_file(file, spec_markt):
    """
    Uploads a visa file to the specified container in Azure Blob Storage.
    If a file with the same name already exists, it will be overwritten.

    Args:
        file: The file to be uploaded.

    Returns:
        None
    """
    container_name = config.get('CONTAINERS', 'VISA_CONTAINER')
    blob_name = f"{spec_markt}/{file.filename}"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    try:
        blob_client.delete_blob()
    except:
        pass

    blob_client.upload_blob(file)

def load_visa_files(spec_markt):
    """
    Loads Visa files from a specified container and returns a concatenated DataFrame.

    Returns:
        pandas.DataFrame: A DataFrame containing the data from the Visa files.
    """
    container_name = config.get('CONTAINERS', 'VISA_CONTAINER')
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs(name_starts_with=spec_markt)
    df_list = []
    for blob in blob_list:
        blob_client = container_client.get_blob_client(blob)

        # Check if the blob is an Excel file
        if os.path.splitext(blob.name)[1] == '.xlsx':
            # Download the blob to a memory stream
            blob_data = blob_client.download_blob()
            data = io.BytesIO(blob_data.readall())

            # Use pandas to read the Excel file
            try:
                df = pd.read_excel(data, usecols='A:AD', dtype=str)
                df = df.where(pd.notnull(df), None)
                df_list.append(df)
            except Exception as e:
                print(f"Failed to read blob {blob.name}: {e}")
                print(f"Data: {data.getvalue()[:10]}")
                raise e

    return pd.concat(df_list, ignore_index=True)

def load_visa_file(bolb_name):
    """
    Loads a VISA file from Azure Blob Storage and returns the data as a pandas DataFrame.

    Parameters:
    - bolb_name (str): The name of the blob file to load.

    Returns:
    - df (pandas.DataFrame): The loaded data as a pandas DataFrame.
    """

    container_name = config.get('CONTAINERS', 'VISA_CONTAINER')
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(bolb_name)
    blob_data = blob_client.download_blob()
    data = io.BytesIO(blob_data.readall())

    # Use pandas to read the Excel file
    df = pd.read_excel(data, usecols='A:AD', dtype=str)
    df = df.where(pd.notnull(df), None)
    return df
