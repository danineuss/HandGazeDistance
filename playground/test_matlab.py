import scipy.io as sio
import numpy as np
import cv2

for enum in xrange(5):
    number = str(enum * 50)
    while len(number) < 3:
        number = '0' + number
    raw = cv2.imread('C:/Users/dsinger/Documents/Git/Masterthesis/files/test/images/imageHands0000' + number + '.png')
    gray = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)

    gray_m = sio.loadmat('C:/Users/dsinger/Documents/Git/Masterthesis/playground/np_vector.mat')

    g = gray_m[gray_m.keys()[0]]

    conv = np.dstack((g, gray))

    sio.savemat('np_vector.mat', {'gray': conv})

