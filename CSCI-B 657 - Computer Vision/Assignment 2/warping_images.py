# code obtained from : https://github.com/varunjain3/PanoramaStitching/blob/master/mywarp.py 
import cv2
import numpy as np

def warping(src, homography, imgout, y_offset, x_offset):

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
        for i in tqdm(range(h_min, h_max+1)):
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
