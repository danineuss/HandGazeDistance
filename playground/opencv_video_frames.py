import cv2
import numpy as np

filename = 'C:/Users/dsinger/Documents/Git/Masterthesis/files/movies/2016_06_17_Train_Data_Hands.avi'

## This code writes each single still into a .jpg file - SUCCESS!
#vidcap = cv2.VideoCapture(filename)
#success,image = vidcap.read()
#count = 0
#success = True
#while success:
#    success,image = vidcap.read()
#    print 'Read a new frame: ', success
#    cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file
#    count += 1

# Now I want to create a single images matrix to store all the still images.
vidcap = cv2.VideoCapture(filename)
success, image = vidcap.read()
images = []
if success:
    while success:
        success, image = vidcap.read()
        images.append(image)
        
    print len(images)

    cv2.imshow('number 10', images[10])
    k = cv2.waitKey(0) & 0xFF
    if k == ord('q'):
        print "That was enough."
        cv2.destroyAllWindows()
else:
    print "This didn't work ..."