import requests
import json
import logging
import os
from bs4 import BeautifulSoup
import boto3
from PIL import Image
from io import BytesIO
from config import (
    SOURCE_IMAGE_REPO_NAME,
    SOURCE_IMAGE_REPO_PATH,
    IMAGE_LOCAL_SAVE_PATH,
    S3_BUCKET,
    S3_IMAGE_PREFIX,
    IMAGE_FILES_NUM,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def collect_github_images(
    repo_name, repo_path, local_save_path, s3_bucket, s3_prefix, n
):
    """Scrape GitHub folder, download up to `n` .png files locally, extract metadata, and upload to S3 in batch."""
    base_url = f"https://github.com/{repo_name}/tree/master/{repo_path}"
    raw_base = f"https://raw.githubusercontent.com/{repo_name}/master/{repo_path}/"

    response = requests.get(base_url)
    if response.status_code != 200:
        logging.info(f"Failed to fetch directory listing: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    script_tag = soup.find("script", {"data-target": "react-app.embeddedData"})

    if not script_tag:
        logging.info("Failed to find embedded JSON data")
        return

    json_data = json.loads(script_tag.string)

    file_entries = json_data.get("payload", {}).get("tree", {}).get("items", [])
    metadata_list = []

    # Ensure local save path exists
    os.makedirs(local_save_path, exist_ok=True)

    files_to_upload = {}
    for file_entry in file_entries:
        if len(files_to_upload) >= n:
            break
        if file_entry["name"].endswith(".png"):  # Only download .png files
            file_url = raw_base + file_entry["name"]
            local_file_path = os.path.join(local_save_path, file_entry["name"])
            metadata = {
                "filename": file_entry["name"],
                "url": file_url,
            }

            metadata_list.append(metadata)

            # Skip downloading if file already exists
            if os.path.exists(local_file_path):
                logging.info(f"File already exists, skipping download: {file_entry['name']}")
                files_to_upload[file_entry["name"]] = local_file_path
                continue

            try:
                file_data = requests.get(file_url).content

                # Save image locally
                with open(local_file_path, "wb") as file:
                    file.write(file_data)
                logging.info(f"Downloaded: {file_entry['name']} to {local_file_path}")

                files_to_upload[file_entry["name"]] = local_file_path

            except Exception as e:
                logging.error(f"Failed to download {file_entry['name']}: {str(e)}")
                
    metadata_path = os.path.join(local_save_path, "image_metadata.json")
    try:
        with open(metadata_path, "w") as json_file:
            json.dump(metadata_list, json_file, indent=4)
        logging.info(f"Metadata saved locally at {metadata_path}")
    except Exception as e:
        logging.error(f"Failed to save metadata locally: {str(e)}")

    # Upload images to S3
    s3_client = boto3.client("s3")
    for file_name, local_file_path in files_to_upload.items():
        s3_path = f"{s3_prefix}/{file_name}"

        # Check if the file was successfully downloaded before uploading
        if not os.path.exists(local_file_path):
            logging.warning(f"Skipping upload: {file_name} was not downloaded successfully.")
            continue

        try:
            with open(local_file_path, "rb") as file:
                s3_client.put_object(Bucket=s3_bucket, Key=s3_path, Body=file)
            logging.info(f"Uploaded: {file_name} to s3://{s3_bucket}/{s3_path}")
        except boto3.exceptions.S3UploadFailedError as e:
            logging.error(f"Failed to upload {file_name} to S3: {str(e)}")
            continue  # Skip failed uploads

    # Upload metadata to S3
    try:
        metadata_json = json.dumps(metadata_list, indent=4)
        metadata_s3_path = f"{s3_prefix}/image_metadata.json"
        s3_client.put_object(Bucket=s3_bucket, Key=metadata_s3_path, Body=metadata_json)
        logging.info(f"Uploaded metadata to s3://{s3_bucket}/{metadata_s3_path}")
    except Exception as e:
        logging.error(f"Failed to upload metadata to S3: {str(e)}")


if __name__ == "__main__":
    collect_github_images(
        repo_name=SOURCE_IMAGE_REPO_NAME,
        repo_path=SOURCE_IMAGE_REPO_PATH,
        local_save_path=IMAGE_LOCAL_SAVE_PATH,
        s3_bucket=S3_BUCKET,
        s3_prefix=S3_IMAGE_PREFIX,
        n=IMAGE_FILES_NUM,
    )
