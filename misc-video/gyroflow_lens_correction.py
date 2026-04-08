import cv2
import numpy as np

# Paramètres Gyroflow (Runcam Thumb2 wide, 3840x2160)
K = np.array([
    [1818.428733127828, 0, 1919.392429274946],
    [0, 1818.800090510473, 1144.922449884292],
    [0, 0, 1]
])

D = np.array([
    [0.1349079411166253],
    [-0.2008114276310018],
    [0.1734474039997024],
    [-0.06331740532773920]
])

img = cv2.imread('frame_3m02.png')
h, w = img.shape[:2]

# balance=1.0 → garde tous les pixels (comme ton padding)
new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
    K, D, (w, h), np.eye(3), balance=1.0
)

map1, map2 = cv2.fisheye.initUndistortRectifyMap(
    K, D, np.eye(3), new_K, (w, h), cv2.CV_16SC2
)

undistorted = cv2.remap(img, map1, map2, cv2.INTER_LANCZOS4)
cv2.imwrite('frame_3m02_gyroflow.png', undistorted)
