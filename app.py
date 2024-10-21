"""
Script Name: app.py
Description: FastAPI to connect to Twilio server to be able to receive and send Virtual Try-On images to User on whatsapp
Author: Mandar Avhad
Date: 2024-10-20
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union, Any, Optional
from fastapi import FastAPI, Form

import os
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import requests
from starlette.requests import Request

from PIL import Image

from utils import DirectoryClient
import numpy as np

from io import BytesIO


# Defining a model to handle input data
class InputData(BaseModel):
    input_string: Union[str, Any] #str


# Reading all key values from env variables
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_my_whatsapp = os.getenv('MY_WHATSAPP')
twilio_number = os.getenv('TWILIO_NUMBER')
huggingface_tk = os.getenv('HUGGINGFACE_TK')

container_1 = os.getenv('CONTAINER_1')
container_2 = os.getenv('CONTAINER_2')
container_3 = os.getenv('CONTAINER_3')

base_url = os.getenv('AZURE_BASE_URL')


# Initialize FastAPI app
app = FastAPI()

# Initialize Twilio instance
client = Client(account_sid, auth_token)


def send_message(body_text):
    client.messages.create(
        from_=twilio_number, body=body_text, to=twilio_my_whatsapp
    )

def send_media_message(url, body_text):
    from twilio.rest import Client
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
    media_url=[url],
    body=body_text,
    from_=twilio_number,
    to=twilio_my_whatsapp,
    )
    
    # delete the images from blob after result (temp)
    # container_name = "demo" # read it from env var/secret
    blob_class = DirectoryClient(container_1)
    
    blob_class.delete_images_from_blob(folder_name="test/input/")
    blob_class.delete_images_from_blob(folder_name="test/")


# Placeholder API, testing
@app.post("/echo")
async def echo_string(Body: str = Form()):
    """
    Placeholder API, for testing

    """
    print(Body, "=====Body data====")
    return send_message("Hello, welcome to Virtual Try-On")


################
# read the image and apply tryon on it
@app.post("/tryon")
async def try_on(
    request: Request,
    Body: str = Form(None),
    NumMedia: str = Form(...),
    MessageSid: str = Form(...),
    MediaUrl0: str = Form(None)
):
    """
    Tryon api to read the input image (person, garment) or result to perform
    the Try-On operations using gradio huggingface space and send the response
    via Twilio to the user on whatsapp
    """

    print("========Try ON API========")
    print(Body, "=====Body====")
    print(MediaUrl0, "=======MediaUrl0=====")

    # (Quick way around) Purposly doing the Twilio CLient and Gradio CLient imports here multiple times
    # as it will create a clash because of same Class Name 

    from twilio.rest import Client
    client = Client(account_sid, auth_token)

    # to ask user to upload image if not uploaded
    if Body.lower() != "result":
        if NumMedia == '0':
            return send_message("Please upload an image of a person or a garment with a text Person/Garment")
    
    if Body.lower() == "person":
        img_name = "person.jpg"
    elif Body.lower() == "garment":
        img_name = "garment.jpg"
    else:
        img_name = "result.jpg"

    # upload incoming input image to blob, and then use that url
    if img_name != "result.jpg":
        # Get the image from the URL
        response = requests.get(MediaUrl0)

        # open as Pil img
        input_img = Image.open(BytesIO(response.content))
        # Convert the image to a NumPy array
        input_img_np = np.array(input_img)
        # color scheme rgb
        input_img_np = input_img_np[:, :, ::-1]
        
        # writing the numpy array image to blob
        blob_class = DirectoryClient(container_2)

        blob_class.write_numpy_array_as_image_to_blob(input_img_np, img_name)

        input_url = f"{base_url}/{container_2}/{img_name}"
        print(input_url, "=======input_url blob=========")

    print(img_name, "====img_name======")
    if img_name == "result.jpg":
        try:
            person_img = f"{base_url}/{container_2}/person.jpg"
            garment_img = f"{base_url}/{container_2}/garment.jpg"
            
            # Try-ON gradio logic
            from gradio_client import Client, file
            from gradio_client import handle_file

            print("====starting try on==========")
            client = Client("Nymbo/Virtual-Try-On", hf_token = huggingface_tk)

            result = client.predict(
                    dict={"background":handle_file(person_img),"layers":[],"composite":None},
                    garm_img=handle_file(garment_img),
                    garment_des="Hello!!",
                    is_checked=True,
                    is_checked_crop=False,
                    denoise_steps=30,
                    seed=42,
                    api_name="/tryon",

            )
            print(result[0], "----gradio result url----------")

            res_image = Image.open(result[0])
            res_image_np = np.array(res_image)
            res_image_np = res_image_np[:, :, ::-1]

            # writing the numpy array image to blob
            blob_class = DirectoryClient(container_3)

            # unique filename received from gradio client api, test
            res_filename = "".join([result[0].split("/")[-2], ".jpg"])
            blob_class.write_numpy_array_as_image_to_blob(res_image_np, res_filename)
            res_url = f"{base_url}/{container_3}/{res_filename}"

            # blob_class.write_numpy_array_as_image_to_blob(res_image_np, img_name)
            # res_url = f"{base_url}/{container_3}/{img_name}"

            print(res_url, "=======result url blob=========")

            body_text = "Here is your Virtual Try-On image"

            return send_media_message(res_url, body_text)

        except Exception as e:
            print(e, "=====ERROR in Try-On Gradio API==========")
            return send_message("Error in creating virtual try on image. Please try again by uploading the Person and Garment images again.")
    
    elif img_name == "person.jpg":
        msg = "Thank you for uploading Person image. Now please upload Garment image"
        return send_message(msg)

    elif img_name == "garment.jpg":
        msg = "Thank you for uploading Garment image. Now Please Upload the Person image if you haven't uploaded.\
        If you have already uploaded Both, then please type Result to get the Try-On result image."
        return send_message(msg)
    else:
        return send_message("Please try uploading an image with Person/Garment tag. Thank you")





