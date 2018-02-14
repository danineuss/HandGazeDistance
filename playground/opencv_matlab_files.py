import cv2
import numpy as np
import scipy.io as sio

path = 'C:/Users/dsinger/Documents/Git/AITDistributedRandomForest/data/rf_data/'
filename = 'perturbated_7_gestures_test_decimated_factor_1_64_64_pythonFileType.mat'

matFile = sio.loadmat(path + filename)
print matFile