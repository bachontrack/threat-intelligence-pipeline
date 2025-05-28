import os

SOURCE_IMAGE_REPO_NAME = os.environ.get("REPO_NAME", "di-dimitrov/mmf")
SOURCE_IMAGE_REPO_PATH = os.environ.get("REPO_PATH", "data/datasets/memes/defaults/images")
SOURCE_TEXT_REPO_NAME = os.environ.get("REPO_NAME", "Vicomtech/hate-speech-dataset")
SOURCE_TEXT_REPO_PATH = os.environ.get("REPO_PATH", "sampled_train")
IMAGE_LOCAL_SAVE_PATH = os.environ.get("LOCAL_SAVE_PATH", "./data/raw/images")
TEXT_LOCAL_SAVE_PATH = os.environ.get("LOCAL_SAVE_PATH", "./data/raw/text")
S3_BUCKET = os.environ.get("S3_BUCKET", "default-bucket")
S3_IMAGE_PREFIX = os.environ.get("S3_PREFIX", "raw/images")
S3_TEXT_PREFIX = os.environ.get("S3_PREFIX", "raw/text")
TEXT_FILES_NUM = int(os.environ.get("NUM_FILES", 5))
IMAGE_FILES_NUM = int(os.environ.get("NUM_FILES", 5))