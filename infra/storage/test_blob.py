from infra.storage.blob_client import upload_bytes

upload_bytes(
    blob_path="healthcheck/test.txt",
    data=b"blob storage working",
    content_type="text/plain"
)

print("Upload successful")