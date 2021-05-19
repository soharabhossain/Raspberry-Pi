import cv2

cap = cv2.VideoCapture(0)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))
n_frames = 200
while n_frames > 0:
    ret, frame = cap.read()
    if ret == True:
        # write the flipped frame
        out.write(frame)
        n_frames -= 1
    else:
        break
    print('frames to capture: {}'.format(n_frames))

# Release everything when done
cap.release()
out.release()
