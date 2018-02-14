import cv2
import numpy as np
import csv

videoPath = 'P:/Forschung/2012_Eye_Tracking/30_Studiarbeiten/MA_DanielSinger_ET_Datenauswertung/3 - Dateien/4 - First Train Data/2016_06_17_Train_Data_Hands.avi'
imagesPath = 'C:/Users/dsinger/Documents/Visual Studio 2015/Projects/Masterthesis/files/images/'
csvName = 'C:/Users/dsinger/Documents/Visual Studio 2015/Projects/Masterthesis/files/csvImages.csv'

# I want to save single images of my movie as seperate files which I need to later train my algorithm.
vidCap = cv2.VideoCapture(videoPath)
success, image = vidCap.read()
if success:
    print 'Loading Video: SUCCESS'
else:
    print 'Loading Video: FAILED'

# Here I define how many images I want to store.
images = []
n = 3
i = 0

#while success and i < n:
#    success, image = vidCap.read()
#    images.append(image)
#    cv2.imwrite(imagesPath + 'image' + str(i) + '.png', image)
#    i += 1

#if len(images) == n:
#    print 'Parsing Video: SUCCESS'
#else:
#    print 'Loading Video: FAILED'

#with open(csvName, 'wb') as csvFile:
#    writer = csv.writer(csvFile, dialect = 'excel')
#    content = [['filepath', 'number']]
#    for i in  range(len(images)):
#        content.append([str(imagesPath) + 'image' + str(i) + '.png', str(i)])
#        print 'Length(content): ' + str(len(content))
#    writer.writerows(content)

# Now I want to combine sparsing the images, saving the images and writing the csv.file.
print success
with open(csvName, 'wb') as csvFile:
    print success
    writer = csv.writer(csvFile, dialect = 'excel')
    content = [['filepath', 'number']]
    
    while success and i < n:
        success, image = vidCap.read()
        images.append(image)
        imageName = imagesPath + 'image' + str(i) + '.png'
        cv2.imwrite(imageName, image)
        content.append([imageName, str(i)])
        i += 1
    
    writer.writerows(content)

print 'Saving and csving: SUCCESS'