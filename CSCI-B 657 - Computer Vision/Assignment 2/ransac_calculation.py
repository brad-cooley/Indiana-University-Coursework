# code obtained from : https://github.com/varunjain3/PanoramaStitching/blob/master/mywarp.py 
import os
import cv2
import random
import numpy as np

from itertools import combinations
from projective_transformation import transformation_matrix
def check_boundary_correspond(c,n):
    if n>len(c):
        return False
    return True

def ransac(correspond, n=30, threshold=2, check_times=4000):
    #correspond = poc
    if check_boundary_correspond(correspond,n)==False:
        print("problem with number of correspondences. probably not the same image?")

    temp = 0
    best_poc = correspond[:n]
    best_inliers = None
    match_pairs = list(combinations(best_poc, 4))
    for matches in match_pairs[:check_times]:
        transformation_mat = transformation_matrix(matches)
        inliers = []
        count = 0
        for feature in best_poc:
            src = np.ones((3, 1))
            tgt = np.ones((3, 1))
            src[:2, 0] = feature[:2]
            tgt[:2, 0] = feature[2:4]
            tgt_hat = np.matmul(transformation_mat,src)
            if tgt_hat[-1, 0] != 0:
                tgt_hat = tgt_hat/tgt_hat[-1, 0]
                if np.linalg.norm(tgt_hat-tgt) < threshold:
                    count += 1
                    inliers.append(feature)
        if count > temp:
            temp = count
            best_inliers = inliers
    best_h = transformation_matrix(best_inliers)
    #print(best_h)
    return best_h
