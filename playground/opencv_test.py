import numpy as np
import cv2

filename = 'C:/Users/Daniel Singer/Documents/Git/masterthesis/images/film.mp4'


# Reading and writing a video file - SUCCESS!
cap = cv2.VideoCapture(filename)
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
out = cv2.VideoWriter('images/output.avi',fourcc, 20.0, (1920,1080))

while(cap.isOpened()):
    ret, frame = cap.read()

    if ret == True:
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

        cv2.imshow('frame', hsv)
        out.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print"Video is stopped."
            break
    else:
        print "ret was false."
        break

print "The show is over."
cap.release()
cv2.destroyAllWindows()