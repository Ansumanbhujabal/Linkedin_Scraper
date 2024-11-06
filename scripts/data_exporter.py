import os
import json
import pymongo
from pymongo import MongoClient
import logging
from dotenv import load_dotenv


load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "output" 
COLLECTION_NAME = "output" 
PROCESSED_FILES_COLLECTION = "processed_files"  


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  
OUTPUT_FOLDER = os.path.join(SCRIPT_DIR, "../output")  


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
processed_files_collection = db[PROCESSED_FILES_COLLECTION]

def process_new_file(file_path):
    """Process the new JSON file and insert data into MongoDB."""
    try:
        filename = os.path.basename(file_path)
        if processed_files_collection.find_one({"filename": filename}):
            logging.info(f"File {filename} already processed. Skipping.")
            return
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    collection.insert_one(item)
                    logging.info(f"Inserted item into MongoDB from file {file_path}")
                else:
                    logging.warning(f"Skipping invalid item in file {file_path}: Not a dictionary.")
        elif isinstance(data, dict):
            collection.insert_one(data)
            logging.info(f"Inserted document into MongoDB from file {file_path}")
        else:
            logging.warning(f"Skipping invalid data in file {file_path}: Not a dictionary or list.")
        processed_files_collection.insert_one({"filename": filename})
        logging.info(f"Marked file {filename} as processed.")

    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")


def push_json_files_to_mongo():
    """Push all JSON files in the OUTPUT_FOLDER to MongoDB."""
    if not os.path.isdir(OUTPUT_FOLDER):
        logging.error(f"Output folder '{OUTPUT_FOLDER}' not found.")
        return
    for filename in os.listdir(OUTPUT_FOLDER):
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if file_path.endswith(".json") and os.path.isfile(file_path):
            logging.info(f"Processing file: {file_path}")
            process_new_file(file_path)

if __name__ == "__main__":
    push_json_files_to_mongo()










# import os
# import json
# import pymongo
# from pymongo import MongoClient
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# import time
# import logging
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # MongoDB configuration
# MONGO_URI = os.getenv("MONGO_URI")

# DB_NAME = "output"  # Name of the database
# COLLECTION_NAME = "output"  # Name of the collection within the database

# # Directory to watch for new JSON files
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
# OUTPUT_FOLDER = os.path.join(SCRIPT_DIR, "../output")  # Construct the absolute path

# # # Directory to monitor for new JSON files
# # OUTPUT_FOLDER = "output"

# # Logging configuration
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# # MongoDB client setup
# client = MongoClient(MONGO_URI)
# db = client[DB_NAME]
# collection = db[COLLECTION_NAME]

# class NewFileHandler(FileSystemEventHandler):
#     def on_created(self, event):
#         # Check if a new JSON file was added
#         if event.is_directory:
#             return
#         if event.src_path.endswith(".json"):
#             logging.info(f"New file detected: {event.src_path}")
#             self.process_new_file(event.src_path)

#     def process_new_file(self, file_path):
#         # Load JSON data and insert into MongoDB
#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 data = json.load(f)
#             collection.insert_one(data)
#             logging.info(f"Data from {file_path} inserted into MongoDB collection '{COLLECTION_NAME}'")
#         except Exception as e:
#             logging.error(f"Error processing file {file_path}: {e}")

# def monitor_folder(folder_path):
#     # Set up the folder observer
#     event_handler = NewFileHandler()
#     observer = Observer()
#     observer.schedule(event_handler, folder_path, recursive=False)
#     observer.start()
#     logging.info(f"Monitoring folder '{folder_path}' for new JSON files...")

#     try:
#         while True:
#             time.sleep(1)  # Keep the script running
#     except KeyboardInterrupt:
#         observer.stop()
#     observer.join()

# if __name__ == "__main__":
#     monitor_folder(OUTPUT_FOLDER)
