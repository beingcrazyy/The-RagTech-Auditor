from azure.storage.blob import BlobServiceClient, ContentSettings
import os
from dotenv import load_dotenv

load_dotenv()

ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
KEY = os.getenv("AZURE_STORAGE_KEY")
CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER")

_blob_service = BlobServiceClient(
    account_url=f"https://{ACCOUNT}.blob.core.windows.net",
    credential=KEY
)

_container = _blob_service.get_container_client(CONTAINER)


def upload_bytes(blob_path: str, data: bytes, content_type: str):
    blob = _container.get_blob_client(blob_path)
    blob.upload_blob(
        data,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type)
    )


def upload_file(blob_path: str, local_path: str, content_type: str):
    with open(local_path, "rb") as f:
        upload_bytes(blob_path, f.read(), content_type)


def download_bytes(blob_path: str) -> bytes:
    blob = _container.get_blob_client(blob_path)
    stream = blob.download_blob()
    return stream.readall()