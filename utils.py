import cv2
from azure.storage.blob import BlobServiceClient

import os
conn_str = os.getenv('BLOB_CONN_STRING')

# blob
class DirectoryClient:
    """
    To write image to blob, delete images from blob
    """
    def __init__(self, container_name):
        self.container_name = container_name
        self.connection_string = conn_str
        self.service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.client = self.service_client.get_container_client(self.container_name)
        
    def write_numpy_array_as_image_to_blob(self, numpy_array, image_name):
        success, encoded_image = cv2.imencode('.jpg', numpy_array)
        if not success:
            print("Error encoding image")
            return "Error encoding image"
        self.client.upload_blob(image_name, encoded_image.tobytes(), overwrite=True)
        print("Successfully uploaded numpy array as image to blob!")
        return "Successfully uploaded numpy array as image to blob!"
    
    def delete_images_from_blob(self, folder_name):
        blobs = self.client.list_blobs(name_starts_with=folder_name)
        # Loop through the blobs and delete each one
        for blob in blobs:
            print(f"Deleting blob: {blob.name}")
            self.client.delete_blob(blob.name)

