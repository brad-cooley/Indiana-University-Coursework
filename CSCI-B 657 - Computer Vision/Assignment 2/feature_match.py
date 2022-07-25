# code obtained from : https://github.com/varunjain3/PanoramaStitching/blob/master/mywarp.py 
import os
import cv2
import numpy as np


def matchfeatures(img1, img2, number_of_features=1000):

    orb = cv2.ORB_create(nfeatures=number_of_features)
    keypoint1, descriptor1 = orb.detectAndCompute(img1, None)
    keypoint2, descriptor2 = orb.detectAndCompute(img2, None)

    brute_force = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matched_points = brute_force.match(descriptor1, descriptor2)

    sorted_points = sorted(matched_points, key=lambda x: x.distance)

    matched_points = []
    for match in sorted_points:
        im1 = keypoint1[match.queryIdx].pt
        im2 = keypoint2[match.trainIdx].pt
        feature = list(map(int, list(im1) + list(im2)))
        matched_points.append(feature)

    return np.array(matched_points)
