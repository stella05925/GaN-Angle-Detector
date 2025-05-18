import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from PIL import Image
from skimage.draw import line

image = Image.open('TEM/DF-17500x-220-20obj-cGaN-01.tif')

image = np.array(image)

fftshift = np.fft.fftshift(np.fft.fft2(image))
magnitude = np.log(np.abs(fftshift))

plt.plot()
plt.imshow(magnitude, cmap='gray')
plt.show()

print(magnitude.shape)

center = (magnitude.shape[0]//2, magnitude.shape[1]//2)

# print(center) (1024,1024)

# center to right-middle --> 0 deg
# print(np.sum(image[1023][1023:2048]))

# center to top-middle --> 90 deg
# print(np.sum(image[0:1023][1023]))

#Store coordinates of border points:

row_coords = np.arange(magnitude.shape[1]//2)
col_coords = np.zeros_like(row_coords)
border_pts_left = np.column_stack((row_coords,col_coords))

# print(border_pts_left.shape)
# print(border_pts_left[0:5])

border_pts_right = np.column_stack((row_coords, col_coords + 2047))

# print(border_pts_right.shape)
# print(border_pts_right[0:5])

row_coords = np.arange(magnitude.shape[1])
col_coords = np.zeros_like(row_coords)

border_pts_top = np.column_stack((col_coords,row_coords))

# print(border_pts_top.shape)
# print(border_pts_top[0:5])

# use scikit-image line function which generates pixel coordinates of a line
# going in a continuous counter-clockwise path around top half of image: starting from the middle-right, going up to the top-right corner, then left across the top border, and down the left border

brightness = []

for point in reversed(border_pts_right):
    # line from (1024,1024) to point along right border of image
    rr, cc = line(center[0], center[1], point[0], point[1])
    brightness.append(np.mean(magnitude[rr, cc]))

for point in reversed(border_pts_top):
    rr, cc = line(center[0], center[1], point[0], point[1])
    brightness.append(np.mean(magnitude[rr, cc]))

for point in border_pts_left:
    rr, cc = line(center[0], center[1], point[0], point[1])
    brightness.append(np.mean(magnitude[rr, cc]))

y = np.array(brightness)

# plots x axis of num border pixels
plt.plot(np.arange(len(y)), y)
plt.show()