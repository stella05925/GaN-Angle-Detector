# dot product between image and filter of bright line of ray 

import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from PIL import Image
from scipy.stats import cauchy
from scipy.optimize import curve_fit

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

def beam_weight(angle, X, Y, thickness):
    angle = np.radians(angle)
    mask = np.exp(-(X * np.cos(angle) + Y * np.sin(angle))**2/thickness**2)
    return mask / np.sum(mask)
    

# plt.imshow(angle_weight(45), cmap='viridis')
# plt.imshow(beam_weight(58, X, Y, 1), cmap='viridis')
# plt.colorbar()
# plt.title("Heatmap from Function")
# plt.show()

brightness_arr = []

# takes way too long:
sample_range = np.arange(123, 126, 0.025)
for i in sample_range:
    brightness = beam_weight(i, X, Y, 1) * magnitude
    brightness_arr.append(np.sum(brightness))
    print(i)

# plt.plot(sample_range, brightness_arr)
# plt.xlabel("Angle (degrees)")
# plt.ylabel("Sum of filtered magnitude")
# plt.show()

# To Do: curve fit this with cauchy, possibly find ways to speed it up
#        write documentation brightness-along-ray and beamfilter --> README

brightness_arr = np.array(brightness_arr)
angle = np.array(sample_range)

def cauchy_function(x, loc, scale):
    pdf_values = cauchy.pdf(x, loc=loc, scale=scale)
    brightness_min = brightness_arr.min()
    brightness_max = brightness_arr.max()
    return pdf_values * (brightness_max - brightness_min) / pdf_values.max() + brightness_min

#initial guesses of parameters
loc_guess_right = angle[np.argmax(brightness_arr)]  
scale_guess_right = (angle.max() - angle.min()) / 10

# loc_guess_left = peak_left_angles[np.argmax(peak_left_brightness)]  
# scale_guess_left = (peak_left_angles.max() - peak_left_angles.min()) / 10

initial_guess_right = [loc_guess_right, scale_guess_right]

# initial_guess_left = [loc_guess_left, scale_guess_left]


# [loc, scale] of cauchy fit (# loc: location of peak, scale: width of curve)
fit_right, _ = curve_fit(cauchy_function, angle, brightness_arr, p0=initial_guess_right)
# fit_left, _ = curve_fit(cauchy_function_left, peak_left_angles, peak_left_brightness, p0=initial_guess_left)

# Generate fitted curve using the angles and fitted parameters
fitted_curve_right = cauchy_function(angle, *fit_right)
# fitted_curve_left = cauchy_function_left(peak_left_angles, *fit_left)

# print(f"[location, scale]\nparameters for right curve:{fit_right}\nparameters for left curve:{fit_left}")
print(f"[location, scale]\nparameters for right curve:{fit_right}")

# Plot comparison
#plt.subplot(1,2,1)
plt.plot(angle, brightness_arr, 'o', label='Original data')
plt.plot(angle, fitted_curve_right, '-', label='Cauchy fit')
#plt.subplot(1,2,2)
# plt.plot(peak_left_angles, peak_left_brightness, 'o', label='Original data')
# plt.plot(peak_left_angles, fitted_curve_left, '-', label='Cauchy fit')
plt.legend()
plt.show()