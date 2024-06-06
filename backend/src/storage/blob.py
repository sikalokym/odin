import io
import os
import configparser
from azure.storage.blob import BlobServiceClient
import pandas as pd

from src.database.db_operations import DBOperations

# Load configurations
config = configparser.ConfigParser()
config.read('config/azure_blob.cfg')

# Initialize BlobServiceClient
connection_string = os.environ.get('STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

def add_visa_file(file, country_code):
    """
    Uploads a visa file to the specified container in Azure Blob Storage.
    If a file with the same name already exists, it will be overwritten.

    Args:
        file: The file to be uploaded.

    Returns:
        None
    """
    container_name = config.get('CONTAINERS', 'VISA_CONTAINER')
    blob_name = f"{country_code}/{file.filename}"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    try:
        file.seek(0)
        blob_client.upload_blob(file, overwrite=True)
    except Exception as e:
        print(f"Failed to upload blob {blob_name}: {e}")
        raise e

def load_available_visa_files(country_code):
    """
    Loads the list of available Visa files from the specified container.

    Args:
        country_code (str): The country code to filter the blob names.

    Returns:
        list: A list of blob names without the file extensions.
    """

    container_name = config.get('CONTAINERS', 'VISA_CONTAINER')
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs(name_starts_with=country_code)

    # Remove country code prefix and file extension from each blob name
    blob_names = [blob.name for blob in blob_list]
    visa_names = [os.path.splitext(blob_name[len(country_code) + 1:])[0] for blob_name in blob_names]

    visa_files = {visa_name: blob_name for visa_name, blob_name in zip(visa_names, blob_names)}
    return visa_files

def get_available_visa_files(country_code, model_year):
    """
    Loads the list of available Visa files from the specified container.

    Args:
        country_code (str): The country code to filter the blob names.

    Returns:
        list: A list of blob names without the file extensions.
    """
    raw_visa_files = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'RAW_VISA'), columns=['VisaFile', '[Car Type] as CarType'], conditions=[f"CountryCode = '{country_code}'", f"[Model Year] = '{model_year}'"])

    return raw_visa_files
    
def load_visa_files(country_code):
    """
    Loads Visa files from a specified container and returns a concatenated DataFrame.

    Returns:
        pandas.DataFrame: A DataFrame containing the data from the Visa files.
    """
    container_name = config.get('CONTAINERS', 'VISA_CONTAINER')
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs(name_starts_with=country_code)
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
                df['VisaFile'] = blob.name[len(country_code)+1:]
                df['CountryCode'] = country_code
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
