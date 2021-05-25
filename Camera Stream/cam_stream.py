# USAGE
# python camera_stream.py

# import the necessary packages
import datetime
import time

# OpenCV library
import cv2

# Numpy Numeric processing library
import numpy as np

from flask import Flask, render_template, Response

#--------------------------------------------------------
# Image resize - helper function

def resize(image, width = None, height = None, inter = cv2.INTER_AREA):
	# initialize the dimensions of the image to be resized and
	# grab the image size
	dim = None
	(h, w) = image.shape[:2]

	# if both the width and height are None, then return the
	# original image
	if width is None and height is None:
		return image

	# check to see if the width is None
	if width is None:
		# calculate the ratio of the height and construct the
		# dimensions
		r = height / float(h)
		dim = (int(w * r), height)

	# otherwise, the height is None
	else:
		# calculate the ratio of the width and construct the
		# dimensions
		r = width / float(w)
		dim = (width, int(h * r))

	# resize the image
	resized = cv2.resize(image, dim, interpolation = inter)

	# return the resized image
	return resized

#--------------------------------------------------------

# Define a Camera class to contain the video stream handler
class MyCamera():
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        time.sleep(0.25)
        self.w = 640
        self.h = 480
        
    def __del__(self):
        self.camera.release()
                 
    def capture_frame(self):
        (grabbed, frame) = self.camera.read()
        if grabbed:
            return frame
        else:
            return np.zeros((self.h, self.w, 3),dtype="uint8")

#--------------------------------------------------
# Define a data generator for the web app
def gen(cam):
    '''Video streaming generator'''
    while True:
        time.sleep(0.15)
        frame = cam.capture_frame()
        if frame.sum()==0:
            print('Camera Problem. Unable to grab frame.')
            
        # resize the frame, convert it to grayscale, and blur it
        frame = resize(frame, height=480, width=640)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (15, 15), 0)
        edged = cv2.Canny(blurred, 50, 150)
        #binary = cv2.threshold(blurred, 25, 255, cv2.THRESH_BINARY)[1]

        h=cam.h
        w=cam.w
        output = np.zeros((h*2, w*2, 3) , dtype="uint8")
        output [0:h, 0:w] = frame
        output [0:h, w:w*2] = np.expand_dims(gray, axis=2)
        output [h:h*2, w:w*2] = np.expand_dims(edged, axis=2)
        output [h:h*2, 0:w] = np.expand_dims(blurred, axis=2)

        cv2.imwrite('/output/out-image.jpg', output)
        img = open('/output/out-image.jpg', 'rb').read()
        
        yield (b'--frame\r\n' + b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')

#----------------------------------------------------------------

# Create a Flask app
app = Flask(__name__)

# What to render at the apps web address?
@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

# Video will be streamed here
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(MyCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

#------------------------------------------------------
#----------------Main Program--------------------
#------------------------------------------------------

if __name__ == '__main__':

    print('\n Now running the web server.........')
    # Default port is 5000 
    app.run(host='0.0.0.0', debug=True, threaded=True)

