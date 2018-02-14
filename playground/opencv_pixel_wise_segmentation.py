import cv2
import numpy as np

filename = 'C:/Users/dsinger/Documents/Visual Studio 2015/Projects/Masterthesis/files/pokemon_blue.jpg'

# This section shows nicely how the images are split using the BGR code.
pokemon = cv2.imread(filename)
convertedImg = cv2.cvtColor(pokemon, cv2.COLOR_BGR2HSV)

h, s, v = cv2.split(convertedImg)
colorsHSV = {'h':h, 's':s, 'v':v}

b, g, r = cv2.split(pokemon)
colorsBGR = {'b':b, 'g':g, 'r':r}

## Here all the color channels are displayed using the BGR color space.
#for key in colorsBGR.keys():
#    cv2.imshow(key, colorsBGR.get(key))
#cv2.imshow('pokemon', pokemon)
#cv2.imshow('bToZero?', bToZero)
#k = cv2.waitKey(0) & 0xFF
#if k == ord('q'):
#    print "That was enough."
#    cv2.destroyAllWindows()


## This section tries to threshold the Pokemon Blue edition.
#threshold = 90
#width = np.size(pokemon, 1)
#height = np.size(pokemon, 0)

#bThreshold = np.zeros_like(b)

#for i in range(width):
#    for j in range(height):
#        if b[j][i] > threshold:
#            bThreshold[j][i] = b[j][i]
#        else:
#            pass

#cv2.imshow('normal', pokemon)
#cv2.imshow('b before threshold', b)
#cv2.imshow('b after threshold', bThreshold)
#k = cv2.waitKey(0) & 0xFF
#if k == ord('q'):
#    print "That was enough."
#    cv2.destroyAllWindows()


# Now we try to segment a hand in the HSV color space.
filename2 = 'P:/Forschung/2012_Eye_Tracking/30_Studiarbeiten/MA_DanielSinger_ET_Datenauswertung/3 - Dateien/4 - First Train Data/2016_06_17_Train_Data_Hands.avi'

# Now I want to play around with color spaces and see in which space my video is saved.
vidcap = cv2.VideoCapture(filename2)
success, image = vidcap.read()
images = []
n = 100
i = 0
while success and i <= n:
    success, image = vidcap.read()
    images.append(image)
    i += 1
print len(images)
image = images[n]

convertedImg2 = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

h2, s2, v2 = cv2.split(convertedImg2)
colorsHSV2 = {'h':h2, 's':s2, 'v':v2}

threshold2 = 150
width2 = np.size(image, 1)
height2 = np.size(image, 0)

segmented = np.zeros_like(image)

for i in range(width2):
    for j in range(height2):
        if v2[j][i] > threshold2:
            segmented[j][i] = v2[j][i]
        else:
            pass

cv2.imshow('normal', image)
cv2.imshow('v before threshold', v2)
cv2.imshow('v after threshold', segmented)
k = cv2.waitKey(0) & 0xFF
if k == ord('q'):
    print "That was enough."
    cv2.destroyAllWindows()
