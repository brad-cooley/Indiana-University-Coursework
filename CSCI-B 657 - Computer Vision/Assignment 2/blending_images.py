import os
import cv2
import numpy as np

def blend(images, masks, n=5):

    assert(images[0].shape[0] % pow(2, n) == 0 and images[0].shape[1] % pow(2, n) == 0)

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

