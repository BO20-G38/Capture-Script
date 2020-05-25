################################################################################
# Author: Sverre Stafsengen Broen
# Run script: python capture.py
#
# This script is for capturing images on the Raspberry Pi
# It captures an image and stores it
# prep_img prepares it by gray scaling and resizing
# Then it sends the image through post request to API
# It catches the response and prints it
# Error count is to stop the script if too many errors has occured
################################################################################

from time import sleep
from picamera import PiCamera
import requests
import sys
import cv2

# prepares the image by grey scaling, and resizing to 100X100
def prep_img(filepath):
    IMG_SIZE = 100  # 50 in txt-based
    img_grayscale = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)  # read in the image, convert to grayscale
    img_resized = cv2.resize(img_grayscale, (IMG_SIZE, IMG_SIZE))  # resize image to match model's expected sizing
    return img_resized


# Preparing paths
IMG_PATH = './capture_script/img_lib/imgs/'
RESIZE_PATH = './capture_script/img_lib/imgs_resized/'
URL = 'http://localhost:3000'

# Initiating variables
error_count = 0
image_count = 0

# Preparing camera module
camera = PiCamera()
camera.resolution = (1000, 1000)

camera.start_preview()
while error_count < 5:
    sleep(2)

    # Preparing name of captured image
    image_count += 1
    capture_name = 'image' + image_count + '.jpg'

    # Capturing image, prepares it, and stores it in resize path
    camera.capture(IMG_PATH + capture_name)
    image = prep_img(IMG_PATH + capture_name)
    isWritten = cv2.imwrite(RESIZE_PATH + capture_name, image)
    if isWritten:  # If successful write to resize path
        # Fetches resized image from path
        resized_image = open(RESIZE_PATH + capture_name, 'rb')

        # Does request, gets status code and closes connection
        response = requests.post(URL, files=dict(file=resized_image))
        status_code = response.status_code
        response.close()

        print(status_code)
        if str(status_code) != str(200):  # Increase error if status code isn't 200
            error_count += 1
    else:
        error_count += 1


camera.stop_preview()
sys.exit()
