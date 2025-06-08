import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from PIL import Image
from skimage.draw import line
from scipy.stats import cauchy
from scipy.optimize import curve_fit
from fitter import Fitter, get_common_distributions, get_distributions

image = Image.open('TEM/DF-17500x-220-20obj-cGaN-01.tif')

image = np.array(image)

fftshift = np.fft.fftshift(np.fft.fft2(image))
magnitude = np.log(np.abs(fftshift))

# plt.plot()
# plt.imshow(magnitude, cmap='gray')
# plt.show()

#print(magnitude.shape)

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
angle = []

for point in reversed(border_pts_right):
    # line from (1024,1024) to point along right border of image
    rr, cc = line(center[0], center[1], point[0], point[1])
    brightness.append(np.mean(magnitude[rr, cc]))
    angle.append(float(np.arctan2(point[0] - center[0], point[1] - center[1])))

for point in reversed(border_pts_top):
    rr, cc = line(center[0], center[1], point[0], point[1])
    brightness.append(np.mean(magnitude[rr, cc]))
    angle.append(float(np.arctan2(point[0] - center[0], point[1] - center[1])))

for point in border_pts_left:
    rr, cc = line(center[0], center[1], point[0], point[1])
    brightness.append(np.mean(magnitude[rr, cc]))
    angle.append(float(np.arctan2(point[0] - center[0], point[1] - center[1])))

y = np.array(brightness)

# plots x axis of num border pixels
#plt.plot(np.arange(len(y)), y)
# plt.plot(angle, y)
# plt.show()

# line_aa with intensity to weight before taking the mean --> not good

# curve fit --> cauchy --> find parameters

# full width half maximum

# fitter library

brightness = np.array(brightness)
angle = np.array(angle)

# peak right: -2.6, -2.45
# peak left: -0.8, -0.5

# extract the parts of the plot that we are interested in:
# boolean array:
condition_right = (angle <= -2.5) & (angle >= -2.58)
condition_left = (angle <= -0.58) & (angle >= -0.68)

peak_right_angles = angle[condition_right]
peak_right_brightness = brightness[condition_right]

peak_left_angles = angle[condition_left]
peak_left_brightness = brightness[condition_left]

# plt.subplot(1, 2, 1)
# plt.plot(peak_right_angles, peak_right_brightness)
# plt.subplot(1,2,2)
# plt.plot(peak_left_angles, peak_left_brightness)
# plt.show()

# fit cauchy using scipy
# 2 new methods used: scipy.stats.cauchy, scipy.optimize.curve_fit

def cauchy_function_right(x, loc, scale):
    pdf_values = cauchy.pdf(x, loc=loc, scale=scale)
    brightness_min = peak_right_brightness.min()
    brightness_max = peak_right_brightness.max()
    return pdf_values * (brightness_max - brightness_min) / pdf_values.max() + brightness_min

def cauchy_function_left(x, loc, scale):
    pdf_values = cauchy.pdf(x, loc=loc, scale=scale)
    brightness_min = peak_left_brightness.min()
    brightness_max = peak_left_brightness.max()
    return pdf_values * (brightness_max - brightness_min) / pdf_values.max() + brightness_min

#initial guesses of parameters
loc_guess_right = peak_right_angles[np.argmax(peak_right_brightness)]  
scale_guess_right = (peak_right_angles.max() - peak_right_angles.min()) / 10

loc_guess_left = peak_left_angles[np.argmax(peak_left_brightness)]  
scale_guess_left = (peak_left_angles.max() - peak_left_angles.min()) / 10

initial_guess_right = [loc_guess_right, scale_guess_right]

initial_guess_left = [loc_guess_left, scale_guess_left]


# [loc, scale] of cauchy fit (# loc: location of peak, scale: width of curve)
fit_right, _ = curve_fit(cauchy_function_right, peak_right_angles, peak_right_brightness, p0=initial_guess_right)
fit_left, _ = curve_fit(cauchy_function_left, peak_left_angles, peak_left_brightness, p0=initial_guess_left)

# Generate fitted curve using the angles and fitted parameters
fitted_curve_right = cauchy_function_right(peak_right_angles, *fit_right)
fitted_curve_left = cauchy_function_left(peak_left_angles, *fit_left)

print(f"[location, scale]\nparameters for right curve:{fit_right}\nparameters for left curve:{fit_left}")

# Plot comparison
plt.subplot(1,2,1)
plt.plot(peak_right_angles, peak_right_brightness, 'o', label='Original data')
plt.plot(peak_right_angles, fitted_curve_right, '-', label='Cauchy fit')
plt.subplot(1,2,2)
plt.plot(peak_left_angles, peak_left_brightness, 'o', label='Original data')
plt.plot(peak_left_angles, fitted_curve_left, '-', label='Cauchy fit')
plt.legend()
plt.show()

# def fitter_method(data):
#     f = Fitter(data,
#            distributions=get_common_distributions())
#     f.fit()
#     f.summary()

# fitter_method(peak_right_brightness)