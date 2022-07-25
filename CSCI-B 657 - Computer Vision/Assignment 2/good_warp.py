# code obtained from : https://github.com/varunjain3/PanoramaStitching/blob/master/mywarp.py 
import os
import cv2
import numpy as np
import sys
from ransac_calculation import ransac
from feature_match import matchfeatures

def warp(src, homography, imgout, y_offset, x_offset):
    H, W, C = imgout.shape
    src_h, src_w, src_c = src.shape
    if homography is not None:
        t = homography
        homography = np.eye(3)
        for i in range(len(t)):
            homography = np.matmul(t[i],homography)

        pts = np.array([[0, 0, 1], [src_w, src_h, 1],
                        [src_w, 0, 1], [0, src_h, 1]]).T
        borders = (np.matmul(homography,pts.reshape(3, -1))).reshape(pts.shape)
        borders /= borders[-1]
        borders = (
            borders+np.array([x_offset, y_offset, 0])[:, np.newaxis]).astype(int)
        h_min, h_max = np.min(borders[1]), np.max(borders[1])
        w_min, w_max = np.min(borders[0]), np.max(borders[0])
        h_inv = np.linalg.inv(homography)
        for i in range(h_min, h_max+1):
            for j in range(w_min, w_max+1):
                if (0 <= i < H and 0 <= j < W):
                    u, v = i-y_offset, j-x_offset
                    src_j, src_i, scale = np.matmul(h_inv,np.array([v, u, 1]))
                    src_i, src_j = int(src_i/scale), int(src_j/scale)
                    if(0 <= src_i < src_h and 0 <= src_j < src_w):
                        imgout[i, j] = src[src_i, src_j]
    else:
        imgout[y_offset:y_offset+src_h, x_offset:x_offset+src_w] = src
    mask = np.sum(imgout, axis=2).astype(bool)
    return imgout, mask


def blend(images, masks, n=5):
    assert(images[0].shape[0] % pow(2, n) ==
           0 and images[0].shape[1] % pow(2, n) == 0)
    g_pyramids = {}
    l_pyramids = {}
    H, W, C = images[0].shape
    for i in range(len(images)):
        G = images[i].copy()
        g_pyramids[i] = [G]
        for _ in range(n):
            G = cv2.pyrDown(G)
            g_pyramids[i].append(G)
        l_pyramids[i] = [G]
        for j in range(len(g_pyramids[i])-2, -1, -1):
            G_up = cv2.pyrUp(G)
            G = g_pyramids[i][j]
            L = cv2.subtract(G, G_up)
            l_pyramids[i].append(L)
    common_mask = masks[0].copy()
    common_image = images[0].copy()
    common_pyramids = [l_pyramids[0][i].copy()
                       for i in range(len(l_pyramids[0]))]
    ls_ = None
    for i in range(1, len(images)):
        y1, x1 = np.where(common_mask == 1)
        y2, x2 = np.where(masks[i] == 1)
        if np.max(x1) > np.max(x2):
            left_py = l_pyramids[i]
            right_py = common_pyramids
        else:
            left_py = common_pyramids
            right_py = l_pyramids[i]
        mask_intersection = np.bitwise_and(common_mask, masks[i])
        if True in mask_intersection:
            y, x = np.where(mask_intersection == 1)
            x_min, x_max = np.min(x), np.max(x)
            split = ((x_max-x_min)/2 + x_min)/W
            LS = []
            for la, lb in zip(left_py, right_py):
                rows, cols, dpt = la.shape
                ls = np.hstack(
                    (la[:, 0:int(split*cols)], lb[:, int(split*cols):]))
                LS.append(ls)
        else:
            LS = []
            for la, lb in zip(left_py, right_py):
                rows, cols, dpt = la.shape
                ls = la + lb
                LS.append(ls)
        ls_ = LS[0]
        for j in range(1, n+1):
            ls_ = cv2.pyrUp(ls_)
            ls_ = cv2.add(ls_, LS[j])
        common_image = ls_
        common_mask = np.sum(common_image.astype(bool), axis=2).astype(bool)
        common_pyramids = LS

    return ls_


if __name__ == '__main__':

    img1_filename = sys.argv[1]
    img2_filename = sys.argv[2]
    output_filename = sys.argv[3]
    img1 = cv2.imread(img1_filename)
    img2 = cv2.imread(img2_filename)
    img1 = cv2.resize(img1,(640,480))
    img2 = cv2.resize(img2,(640,480))

    Images = [img1,img2]

    H, W, C = np.array(img1.shape)*[3, 2, 1] 

    blank_img = np.zeros((H, W, C))
    img_outputs = []
    masks = []
    img, mask = warp(Images[1], None, blank_img.copy(), H//2, W//2)
    img_outputs.append(img)
    masks.append(mask)
    side = []
    poc = matchfeatures(Images[0], Images[1])
    side.append(ransac(poc))
    img, mask = warp(Images[0], side[::-1],blank_img.copy(), H//2, W//2)
    img_outputs.append(img)
    masks.append(mask)
    uncropped = blend(img_outputs, masks)
    mask = np.sum(uncropped, axis=2).astype(bool)
    yy, xx = np.where(mask == 1)
    x_min, x_max = np.min(xx), np.max(xx)
    y_min, y_max = np.min(yy), np.max(yy)
    final = uncropped[y_min:y_max, x_min:x_max]
    cv2.imwrite(output_filename, final)
