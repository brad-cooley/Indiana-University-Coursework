from turtle import home
import numpy as np
import cv2 as cv
# import sys
import os
from typing import List
import math

def apply_transformation(im: np.array, transformation: np.array) -> np.array:
    """
    Given an image as a numpy array and a transformation matrix
    create a new image that is the applied transformation of the
    original using homogenous coordinates and bilinear interpolation
    """
    nrows, ncols, channels = im.shape
    new_img = np.zeros((nrows, ncols, channels), dtype=np.uint8)
    inv_transform = np.linalg.inv(transformation)
    homo_to_2d = lambda x: (x[0] / x[2], x[1] / x[2])
    # assume the first dimmension is the column and the second is the rows
    for y in range(nrows):
        for x in range(ncols):
            new_img_coords = np.array([x, y, 1])
            # perform inverse warping
            og_img_coords = np.dot(inv_transform, new_img_coords)
            og_x, og_y = homo_to_2d(og_img_coords)
            # for now just use NN interpolation
            og_x, og_y = int(og_x), int(og_y)
            if (0 <= og_y < nrows) and (0 <= og_x < ncols):
                new_pixels = im[og_y, og_x]
                new_img[y, x] = new_pixels
    return new_img


def calculate_transformation_matrix(points1: List[tuple], points2: List[tuple]):
    """
    Given two lists of coordinates (in respective order of eachother)
    Solves linear system of equations to find the transformation matrix
    that will match the two images.
    """
    n = len(points1)
    if n == 1:
        # This is a simple translation so we only need to find two parameters
        # looking for value that changes x -> xprime
        x, y = points1[0]
        xprime, yprime = points2[0]
        x_change = xprime - x
        y_change = yprime - y
        return np.array([[1, 0, x_change], [0, 1, y_change], [0, 0, 1]])
    elif n == 2:

        src = points2
        dest = points1

        euc_src = math.dist(src[0], src[1])
        euc_dest = math.dist(dest[0], dest[1])

        src_delta_x = src[1][0] - src[0][0]
        src_delta_y = src[1][1] - src[0][1]

        dest_delta_x = dest[1][0] - dest[0][0]
        dest_delta_y = dest[1][1] - dest[0][1]

        src_vec = np.array([src_delta_x, src_delta_y])
        dest_vec = np.array([dest_delta_x, dest_delta_y])

        theta_src = math.atan(src_vec[1] / src_vec[0])
        theta_dest = math.atan(dest_vec[1] / dest_vec[0])

        rotation_matrix = np.array([
                [math.cos(theta_src - theta_dest), -math.sin(theta_src - theta_dest),0],
                [math.sin(theta_src - theta_dest), math.cos(theta_src - theta_dest), 0],
                [0, 0, 1]
        ])

        dest_p1_rotated = np.matmul(
            np.array([dest[0][0], dest[0][1], 1]), rotation_matrix
        )
        dest_p2_rotated = np.matmul(
            np.array([dest[1][0], dest[1][1], 1]), rotation_matrix
        )

        x_change = src[0][0] - dest[0][0]
        y_change = src[0][1] - dest[0][1]

        translation_matrix = np.array([[1, 0, x_change], [0, 1, y_change], [0, 0, 1]])

        return np.matmul(translation_matrix, rotation_matrix)

    elif n == 3:
        # affine transformation
        src = points2
        dest = points1

        # fill out lhs of equation
        lhs = np.zeros((6, 6))
        indx = 0

        for p1, p2 in zip(dest, src):
            x, y = p1
            xprime, yprime = p2
            vals1 = [x, y, 1, 0, 0, 0]
            vals2 = [0, 0, 0, x, y, 1]
            lhs[indx, :] = np.array(vals1)
            lhs[indx + 1, :] = np.array(vals2)
            indx += 2
        rhs = np.zeros(6)
        indx = 0

        for xprime, yprime in src:
            rhs[indx] = xprime
            rhs[indx + 1] = yprime
            indx += 2

        # transformation matrix is just solution of linear equation
        solution = np.linalg.solve(lhs, rhs)
        solution = np.append(solution, np.array([0, 0, 1]))
        return solution.reshape((3, 3))

    elif n == 4:
        # projective transformation
        src = points2
        dest = points1
        # fill out lhs of equation
        lhs = np.zeros((8, 8))
        indx = 0
        for p1, p2 in zip(dest, src):
            x, y = p1
            xprime, yprime = p2
            vals1 = [x, y, 1, 0, 0, 0, -x * xprime, -y * xprime]
            vals2 = [0, 0, 0, x, y, 1, -x * yprime, -y * yprime]
            lhs[indx, :] = np.array(vals1)
            lhs[indx + 1, :] = np.array(vals2)
            indx += 2
        rhs = np.zeros(8)
        indx = 0
        for xprime, yprime in src:
            rhs[indx] = xprime
            rhs[indx + 1] = yprime
            indx += 2
        # transformation matrix is just solution of linear equation
        solution = np.linalg.solve(lhs, rhs)
        solution = np.append(solution, 1)
        return solution.reshape((3, 3))


def p2(args):
    n_transformations = int(args[2])
    img2_filename = args[3]
    img1_filename = args[4]
    output_filename = args[5]
    points = args[6:]

    img1_coordinates = list()
    img2_coordinates = list()

    # split args up
    for coords in range(0, len(points), 2):
        img1_coordinates.append(points[coords])

    for coords in range(1, len(points), 2):
        img2_coordinates.append(points[coords])

    for i in range(n_transformations):
        img1_coordinates[i] = tuple(int(j) for j in img1_coordinates[i].split(","))
        img2_coordinates[i] = tuple(int(j) for j in img2_coordinates[i].split(","))

    img2_coordinates = img2_coordinates[:n_transformations]
    img1_coordinates = img1_coordinates[:n_transformations]

    img1 = cv.imread(img1_filename)
    for y, x in img2_coordinates:
        img1[x - 5 : x + 5, y - 5 : y + 5, :] = 0
        img1[x - 5 : x + 5, y - 5 : y + 5, 2] = 255
    cv.imwrite("img2_keypoints.jpg", img1)
    img2 = cv.imread(img2_filename)
    for y, x in img1_coordinates:
        img2[x - 5 : x + 5, y - 5 : y + 5, :] = 0
        img2[x - 5 : x + 5, y - 5 : y + 5, 2] = 255
    cv.imwrite("img1_keypoints.jpg", img2)
    # Do transformations
    # transformation_matrix = np.array([
    #     [.907,.258,-182],
    #     [-.153,1.44,58],
    #     [-.000306,.000731,1]
    # ])
    # compute and display transformation matrix
    transformation_matrix = calculate_transformation_matrix(
        img2_coordinates, img1_coordinates
    )
    print(transformation_matrix)
    # apply transformation to img1.png
    input_im = cv.imread(img1_filename)
    new_im = apply_transformation(input_im, transformation_matrix)
    # save new transformation to img_output.png
    cv.imwrite(output_filename, new_im)