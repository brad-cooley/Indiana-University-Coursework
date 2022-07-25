import sys
import numpy as np
import cv2
from ransac_calculation import ransac
from feature_match import matchfeatures
def linear_transformation(img,transformation):
    blank_image = np.zeros((len(img),len(img[0])), np.uint8)
    for i in range(len(img)):
        for j in range(len(img[0])):
            m = np.array([j,i,1])
            m1 = np.matmul(transformation,m)
            m1[0]=int(m1[0]/m1[2])
            m1[1]=int(m1[1]/m1[2])
            if m1[0]>=0 and m1[1]>=0 and m1[0]<len(img[0]) and m1[1]<len(img):
                blank_image[int(m1[1]),int(m1[0])]=img[i,j]
    return blank_image

def mix(img1,img2,h_tr):
    return linear_transformation(img1,h_tr)


def p3(args):
    img1_filename = args[2]
    img2_filename = args[3]
    output_filename = args[4]
    img1 = cv2.imread(img1_filename, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_filename, cv2.IMREAD_GRAYSCALE)
    h1 = ransac(matchfeatures(img1,img2))
    final = mix(img2,img1,h1)
    a = matchfeatures(img1,final)
    if a[0][1]<a[0][3]:
        temp = final
        final =img1
        img1=temp

    h,w=img1.shape
    h1,w1=final.shape
    h2=max(h,h1)
    w2=w+w1
    blank = np.zeros((h2,w2),np.uint8)
    blank[0:h,w1:w2]=img1
    for i in range(h1):
        for j in range(w1):
            if final[i,j]>=20 and i<1329:
                blank[i,j+525]=max(blank[i,j+525],final[i,j])
    h5 = ransac(a)
    offset = abs(w1-int(h5[0,-1]))
    print(offset)
    for i in range(h1):
        for j in range(w1):
            if final[i,j]>=20 and i<h:
                blank[i,j+offset]=max(blank[i,j+offset],final[i,j])
    blank_image1=blank
    for i in range(len(final)):
        for j in range(len(final[0])):
            m = np.array([j,i,1])
            m1 = np.matmul(h5,m)
            m1[0]=int(m1[0]/m1[2])
            m1[1]=int(m1[1]/m1[2])+2000
            if m1[0]>=0 and m1[1]>=0 and m1[1]<h and m1[0]<w2:
                blank_image1[int(m1[1])][int(m1[0])]=final[i][j]

    cv2.imwrite(output_filename, blank_image1)
