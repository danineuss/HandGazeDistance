import cv2
import numpy as np

filename = 'P:/Forschung/2012_Eye_Tracking/30_Studiarbeiten/MA_DanielSinger_ET_Datenauswertung/3 - Dateien/4 - First Train Data/2016_06_17_Train_Data_Hands.avi'

# Now I want to play around with color spaces and see in which space my video is saved.
vidcap = cv2.VideoCapture(filename)
success, image = vidcap.read()
images = []
n = 100
i = 0
while success and i <= n:
    success, image = vidcap.read()
    images.append(image)
    i += 1
print len(images)

colorModes = {'BGR2GRAY':cv2.COLOR_BGR2GRAY, 'BGR2HSV':cv2.COLOR_BGR2HSV}

normalImg = images[n]

## This section displays the different color transformations. I chose BGR2HSV.
#for key in colorModes.keys():
#    converted_img = cv2.cvtColor(normal_img, colorModes.get(key))
#    cv2.imshow('Normal', normal_img)
#    cv2.imshow(key, converted_img)
    
#k = cv2.waitKey(0) & 0xFF
#if k == ord('q'):
#    print "That was enough."
#    cv2.destroyAllWindows()

# This section is useful when you want to understand the different channels in the HSV color space.
convertedImg = cv2.cvtColor(normalImg, cv2.COLOR_BGR2HSV)
h, s, v = cv2.split(convertedImg)
colors = {'h':h, 's':s, 'v':v}
cv2.imshow('normal', normalImg)
cv2.imshow('hsv', convertedImg)
cv2.imshow('h', h)
cv2.imshow('s', s)
cv2.imshow('v', v)
cv2.imshow('h+v', h-v)
k = cv2.waitKey(0) & 0xFF
if k == ord('q'):
    print "That was enough."
    cv2.destroyAllWindows()

## This section shows nicely how the images are split using the BGR code.
#pokemon = cv2.imread('C:/Users/dsinger/Documents/Visual Studio 2015/Projects/Masterthesis/files/pokemon_blue.jpg', )
#cv2.imshow('pokemon', pokemon)
#k = cv2.waitKey(0) & 0xFF
#if k == ord('q'):
#    print "That was enough."
#    cv2.destroyAllWindows()

#b, g, r = cv2.split(pokemon)
#colors = {'b':b, 'g':g, 'r':r}
#for key in colors.keys():
#    cv2.imshow(key, colors.get(key))
#k = cv2.waitKey(0) & 0xFF
#if k == ord('q'):
#    print "That was enough."
#    cv2.destroyAllWindows()
