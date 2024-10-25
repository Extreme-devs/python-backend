import os
from supabase import create_client
from core.config import settings

supabaseClient = create_client(
    settings.SUPABASE_PROJECT_URL, settings.SUPABASE_ANON_KEY
)


def upload_file(file_path: str, bucket_name: str = "files", replace: bool = True):
    uploaded_files = supabaseClient.storage.from_(bucket_name).list()
    file_name = os.path.basename(file_path)
    for file in uploaded_files:
        if file["name"] == file_name:
            print(f"File {file_name} already exists in bucket {bucket_name}")
            if replace:
                print(f"Replacing {file_name} in bucket {bucket_name}")
                with open(file_path, "rb") as file:
                    supabaseClient.storage.from_(bucket_name).update(file_name, file)
            else:
                print("Skipping upload")
            return
    print(f"Uploading {file_name} to bucket {bucket_name}")
    with open(file_path, "rb") as file:
        supabaseClient.storage.from_(bucket_name).upload(file_name, file)
