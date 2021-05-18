# camera.py

import cv2
from eyetracker import EyeTracker
import imutils

from picamera import PiCamera
from picamera.array import PiRGBArray

# Live video feed will be streamed
class MyPiCamera():
    def __init__(self):

    def capture_frame(self):
        self.frames = []
        self.cam.capture('./image.jpg')
        self.frames.append(open('./image.jpg', 'rb').read())
        return self.frames[0]

# -----------------------------------------------------------------------------------
class PiVideoCamera(object):
    def __init__(self):

        self.et = EyeTracker("haarcascade_frontalface_default.xml", "haarcascade_eye.xml")
        self.cam = MyPiCamera() 
       
        # Capture video frame with the Camera of Raspberry-pi
        self.video = self.cam.capture_frame()
        
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
    
    def __del__(self):
        del self.cam
    
    def get_frame(self):
        image = self.cam.capture_frame()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the video stream.
        img = self.process_video_frames(image)
        #img=self.track_face_eyes(image)
        ret, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tobytes()
# -----------------------------------------------------------------------------
    def process_video_frames(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
     	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	edged = cv2.Canny(blurred, 50, 150)
	# binary = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        return edged

# -----------------------------------------------------------------------------
    def track_face_eyes(self, frame):
          
	# resize the frame and convert it to grayscale
	frame = imutils.resize(frame, width = 300)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# detect faces and eyes in the image
	rects = self.et.track(gray)

	# loop over the face bounding boxes and draw them
	for rect in rects:
		cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)
        return frame
    
