
import cv2
import numpy as np

#--------------------------------------------------------------------------
def translate(image, x, y):
	# Define the translation matrix and perform the translation
	M = np.float32([[1, 0, x], [0, 1, y]])
	shifted = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))

	# Return the translated image
	return shifted

def rotate(image, angle, center = None, scale = 1.0):
	# Grab the dimensions of the image
	(h, w) = image.shape[:2]

	# If the center is None, initialize it as the center of
	# the image
	if center is None:
		center = (w / 2, h / 2)

	# Perform the rotation
	M = cv2.getRotationMatrix2D(center, angle, scale)
	rotated = cv2.warpAffine(image, M, (w, h))

	# Return the rotated image
	return rotated

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

#------------------------------------------------------------------------

class EyeTracker:
	def __init__(self, faceCascadePath, eyeCascadePath):
		# load the face and eye detector
		self.faceCascade = cv2.CascadeClassifier(faceCascadePath)
		self.eyeCascade = cv2.CascadeClassifier(eyeCascadePath)

	def track(self, image):
		# detect faces in the image and initialize the list of
		# rectangles containing the faces and eyes
		faceRects = self.faceCascade.detectMultiScale(image,
			scaleFactor = 1.1, minNeighbors = 5, minSize = (30, 30),
			flags = cv2.CASCADE_SCALE_IMAGE)
		rects = []

		# loop over the face bounding boxes
		for (fX, fY, fW, fH) in faceRects:
			# extract the face ROI and update the list of
			# bounding boxes
			faceROI = image[fY:fY + fH, fX:fX + fW]
			rects.append((fX, fY, fX + fW, fY + fH))
			
			# detect eyes in the face ROI
			eyeRects = self.eyeCascade.detectMultiScale(faceROI,
				scaleFactor = 1.1, minNeighbors = 10, minSize = (20, 20),
				flags = cv2.CASCADE_SCALE_IMAGE)

			# loop over the eye bounding boxes
			for (eX, eY, eW, eH) in eyeRects:
				# update the list of boounding boxes
				rects.append(
					(fX + eX, fY + eY, fX + eX + eW, fY + eY + eH))

		# return the rectangles representing bounding
		# boxes around the faces and eyes
		return rects
#-------------------------------------------------------------------

class FaceDetector:
	def __init__(self, faceCascadePath):
		# load the face detector
		self.faceCascade = cv2.CascadeClassifier(faceCascadePath)

	def detect(self, image, scaleFactor = 1.1, minNeighbors = 5, minSize = (20, 20)):
		# detect faces in the image
		rects = self.faceCascade.detectMultiScale(image, scaleFactor = scaleFactor, minNeighbors = minNeighbors, minSize = minSize, flags = cv2.CASCADE_SCALE_IMAGE)

		# return the rectangles representing bounding
		# boxes around the faces
		return rects

#-----------------------------------------------------------------------

class VideoCamera(object):
    def __init__(self):

        self.et = EyeTracker("https://github.com/soharabhossain/Raspberry-Pi/blob/main/Haar-Cascades/haarcascade_frontalface_default.xml", "https://github.com/soharabhossain/Raspberry-Pi/blob/main/Haar-Cascades/haarcascade_eye.xml")
        
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file instead.
        self.video = cv2.VideoCapture(0)
        
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()

        #img = self.process_video_frames(image)

        # Track face and eyes in the frames
        img=self.track_face_eyes(image)
        
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the video stream.
        ret, jpeg = cv2.imencode('.jpg', img)

        return jpeg.tobytes()
# -----------------------------------------------------------------------------
    def process_video_frames(self, image):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
     	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	edged = cv2.Canny(blurred, 50, 150)
	#binary = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        return edged

# -----------------------------------------------------------------------------
    def track_face_eyes(self, frame):
          
	# resize the frame and convert it to grayscale
	frame = resize(frame, width = 300)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# detect faces and eyes in the image
	rects = self.et.track(gray)

	# loop over the face bounding boxes and draw them
	for rect in rects:
		cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)

        return frame
#------------------------------------------------------------------------------
#---------------Main Program-----------------------------
    
from flask import Flask, render_template, Response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n' +  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) # localhost:5000
    #app.run(host='169.254.232.101', debug=True) # ip of the local machine

    
