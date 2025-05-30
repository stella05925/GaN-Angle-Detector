# dot product between image and filter of bright line of ray 

import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from PIL import Image

image = Image.open('TEM/DF-17500x-220-20obj-cGaN-01.tif')

image = np.array(image)

fftshift = np.fft.fftshift(np.fft.fft2(image))
magnitude = np.log(np.abs(fftshift))

# plt.plot()
# plt.imshow(magnitude, cmap='gray')
# plt.show()

# set up filter dimensions

h, w = image.shape

x = np.arange(w) - (w//2)  
y = np.arange(h) - (h//2)
X, Y = np.meshgrid(x, y)

# print(X[0,0], Y[0,0])

# print(X[h//2, w//2], Y[h//2, w//2])

angles = np.arctan2(Y, X) # cartesian coordinates --> map of angles

sigma = np.deg2rad(5)

def angle_weight(angle):
    target_angle = np.deg2rad(-angle) # loop with target_angle range from 0 to -180

    raw_diff = angles - target_angle # distance of angles in filter to the target angle

    diff = (raw_diff + np.pi) % (2 * np.pi) - np.pi # wrap distance to [-pi,pi]

    gaussian_angle = np.exp(-0.5 * (diff / sigma)**2) # Gaussian weight on angle

    gaussian_angle /= gaussian_angle.max() # normalize

    return gaussian_angle

# plt.imshow(gaussian_angle, cmap='viridis')
# plt.colorbar()
# plt.title("Heatmap from Function")
# plt.show()

brightness_arr = []

# takes way too long:
for i in range(181):
    brightness = angle_weight(i) * magnitude
    brightness_arr.append(np.sum(brightness))

x = np.arange(181)
plt.plot(x, brightness_arr)
plt.xlabel("Angle (degrees)")
plt.ylabel("Sum of filtered magnitude")
plt.show()