# this is from : https://web.stanford.edu/class/cs231m/lectures/lecture-5-stitching-blending.pdf and partly https://github.com/varunjain3/PanoramaStitching/blob/master/mywarp.py
import os
import cv2
import random
import numpy as np


def transformation_matrix(correspond):

    A = []
    for x1, y1, x2, y2 in correspond:
        A.append([x1, y1, 1, 0, 0, 0, -x1*x2, -y1*x2,-x2])
        A.append([0, 0, 0, x1, y1, 1, -x1*y2, -y1*y2,-y2])
    A = np.asarray(A)
    U, S, Vh = np.linalg.svd(A)
    h = Vh[-1, :] / Vh[-1, -1]
    h1 = h.reshape(3, 3)
    return h1

# The method shown in clides was not followed. . it gave scaling issues due to
# h[3,3] not being calculated.
