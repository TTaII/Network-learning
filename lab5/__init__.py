from skimage.feature import corner_harris, corner_peaks
import cv2
import numpy as np

#cv2.Sobel()
# src = np.array([[1,2,3],[1,2,3],[1,2,3]])
# x = cv2.GaussianBlur(src)
#print(np.arctan2(0,-10)/np.pi)
print(int(-1.9))
for i in range(0,11):
    print(np.arctan2(i,10)/np.pi*4)
for i in range(10,100,10):
    print(np.arctan2(i,-10)/np.pi*4)
for i in range(0,11):
    print(np.arctan2(i,-10)/np.pi*4)
    
for i in range(0,11):
    print(np.arctan2(-10,i)/np.pi*4)
for i in range(-10,0):
    print(np.arctan2(i,10)/np.pi*4)