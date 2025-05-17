import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import math

image = cv.imread('TEM/DF-17500x-220-20obj-cGaN-01.tif')
#print(f'dtype:{image.dtype}')

image_filt = cv.GaussianBlur(image,(19,19),5)

plt.subplot(121),plt.imshow(image),plt.title('Original')
plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(image_filt),plt.title('Blurred')
plt.xticks([]), plt.yticks([])
plt.show()

# Uncomment to play with canny thresholds:
# def callback(input):
#     pass

# winname = 'canny'
# cv.namedWindow(winname)
# cv.createTrackbar('minThres',winname,0,255,callback)
# cv.createTrackbar('maxThres',winname,0,255,callback)

# while True:
#     if cv.waitKey(1) == ord('q'):
#         break

#     minThres = cv.getTrackbarPos('minThres',winname)
#     maxThres = cv.getTrackbarPos('maxThres',winname)
#     cannyedge = cv.Canny(image_filt,minThres, maxThres)
#     cv.imshow(winname,cannyedge)

edges = cv.Canny(image_filt, 25, 32)

plt.imshow(edges)
plt.xticks([]), plt.yticks([])
plt.show()

lines = cv.HoughLines(edges, 1, np.pi / 180, 150, None, 0, 0)

# print(lines)

cdst_right = cv.cvtColor(edges, cv.COLOR_GRAY2BGR)
cdst_left = cdst_right.copy()

right_angles = []
left_angles = []
    
if lines is not None:
    for i in range(0, len(lines)):
        rho = lines[i][0][0]
        theta = lines[i][0][1]

        angle_deg = np.degrees(theta)

        a = math.cos(theta)
        b = math.sin(theta)
        x0 = a * rho
        y0 = b * rho
        pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
        pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))

        if 2.2 < theta < 3:
            cv.line(cdst_right, pt1, pt2, (0,0,255), 3, cv.LINE_AA)
            right_angles.append(angle_deg)

        elif 0.5 < theta < 1.2:
            cv.line(cdst_left, pt1, pt2, (0,255,0), 3, cv.LINE_AA)
            left_angles.append(angle_deg)

plt.subplot(121),plt.imshow(cdst_right)
plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(cdst_left)
plt.xticks([]), plt.yticks([])
plt.show()

# print(right_angles)
# print(left_angles)

right_avg_angle = np.mean(right_angles)
right_std_angle = np.std(right_angles)

left_avg_angle = np.mean(left_angles)
left_std_angle = np.std(left_angles)

angle = abs(right_avg_angle - left_avg_angle)
if angle > 90:
    angle = 180 - angle

print(f"Right group lines ({len(right_angles)} lines):")
print(f"  Angles (degrees): {[round(a, 2) for a in right_angles]}")
print(f"  Average angle: {right_avg_angle:.2f}° ± {right_std_angle:.2f}°")
print()
print(f"Left group lines ({len(left_angles)} lines):")
print(f"  Angles (degrees): {[round(a, 2) for a in left_angles]}")
print(f"  Average angle: {left_avg_angle:.2f}° ± {left_std_angle:.2f}°")
print()
print(f"Angle between line groups: {angle:.2f}°")

plt.figure(figsize=(12, 10))

# Plot angle distribution
plt.plot()
bins = np.arange(0, 181, 5)  # Bins from 0 to 180 degrees
plt.hist([right_angles, left_angles], bins=bins, alpha=0.7, 
         label=['Right group', 'Left group'], color=['red', 'green'])
plt.xlabel('Angle (degrees)')
plt.ylabel('Number of lines')
plt.title('Distribution of Line Angles')
plt.axvline(right_avg_angle, color='darkred', linestyle='dashed', 
            linewidth=2, label=f'Right avg: {right_avg_angle:.2f}°')
plt.axvline(left_avg_angle, color='darkgreen', linestyle='dashed', 
            linewidth=2, label=f'Left avg: {left_avg_angle:.2f}°')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.show()