import requests
import random
import os
from itertools import cycle
import glob

API_URL = os.environ.get('API_URL', 'http://127.0.0.1:8000/api/auction/vehicles/')
TOKEN = os.environ.get('API_TOKEN', 'c6aa9fd8be7e54eb44eb0219907cf38eae5bf0d2')  # Set your token here or via env

# Dummy vehicle data
VEHICLES = [
    {
        "make": "Toyota",
        "model": "Camry",
        "year": 2020,
        "condition": "New",
        "max_price": 20000.00,
        "available": True
    },
    {
        "make": "Honda",
        "model": "Civic",
        "year": 2021,
        "condition": "Used",
        "max_price": 15000.00,
        "available": True
    },
    {
        "make": "Ford",
        "model": "Mustang",
        "year": 2019,
        "condition": "Used",
        "max_price": 25000.00,
        "available": True
    },
    {
        "make": "BMW",
        "model": "328i",
        "year": 2018,
        "condition": "New",
        "max_price": 35000.00,
        "available": True
    },
    {
        "make": "Tesla",
        "model": "Model 3",
        "year": 2022,
        "condition": "New",
        "max_price": 40000.00,
        "available": True
    }
]

# Dynamically find available images in media/vehicle_images and static/images
MEDIA_IMAGE_PATHS = glob.glob(os.path.join("media", "vehicle_images", "*.jpg"))
STATIC_IMAGE_PATHS = glob.glob(os.path.join("static", "images", "*.jpg")) + glob.glob(os.path.join("static", "images", "*.png"))
IMAGE_PATHS = MEDIA_IMAGE_PATHS + STATIC_IMAGE_PATHS

if not IMAGE_PATHS:
    raise RuntimeError("No vehicle images found in media/vehicle_images or static/images. Please add images to those folders.")

image_cycle = cycle(IMAGE_PATHS)

# Optionally, add image upload if your endpoint requires it
# For now, this script only sends vehicle data (no images)
def create_vehicle(vehicle):
    headers = {"Authorization": f"Token {TOKEN}"} if TOKEN else {}
    image_path = next(image_cycle)
    with open(image_path, "rb") as img_file:
        files = {"images": img_file}
        response = requests.post(API_URL, data=vehicle, headers=headers, files=files)
    if response.status_code == 201:
        print(f"Created: {vehicle['make']} {vehicle['model']} ({vehicle['year']}) with image {image_path}")
    else:
        print(f"Failed to create {vehicle['make']} {vehicle['model']} ({vehicle['year']}): {response.status_code} {response.text}")

if __name__ == "__main__":
    for v in VEHICLES:
        create_vehicle(v)
