from flask import Flask, render_template, Response

# Raspberry Pi camera module (requires picamera package)
from picamera import PiCamera

from time import sleep


# ---------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Live video feed will be streamed
class MyPiCamera():
    def __init__(self):
        self.cam = PiCamera()
        self.cam.resolution = (320, 256)
        self.cam.framerate = 16
                 
    def capture_frame(self):
        self.frames = []
        self.cam.capture('./image.jpg')
        self.frames.append(open('./image.jpg', 'rb').read())
        return self.frames[0]

# -----------------------------------------------------------------------------

def pigen(picamera):
    """Video streaming generator function."""
    while True:
       frame = picamera.capture_frame()

       yield (b'--frame\r\n' + b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# -----------------------------------------------------------------------------

app = Flask(__name__)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(pigen(MyPiCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)

   
