import cv2
import numpy as np
from typing import List
from sklearn.cluster import SpectralClustering
# import sys
import os


def generate_orb_features(filename: str, n_features: int = 1000) -> cv2.ORB:
    """
    Given the filename of an image will import and generate the orb
    object that will be used for comparisons in count_matching_features
    """
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    orb = cv2.ORB_create(nfeatures = n_features)
    (keypoints, descriptors) = orb.detectAndCompute(img, None)
    return descriptors



def count_matching_features(descriptors1: np.array, descriptors2:  np.array,matcher: cv2.BFMatcher, tau:float = .75) -> int:
    """
    Given two descriptors of an ORB two images
    and the criteria for the matching
    will compute the similarity between the
    two as the number of matching features.
    """

    sim_score = 0
    # create a distance matrix between all the descriptors
    # https://docs.opencv.org/4.x/dc/dc3/tutorial_py_matcher.html
    matches = matcher.knnMatch(descriptors1, descriptors2, k=2)
    for m,n in matches:
        sim_score += m.distance < tau*n.distance
    return sim_score/len(descriptors1)


def spectral_clustering(sim_matrix: np.array, n_clusters: int) -> List[str]:
    """
    Given a similarity matrix and the number of clusters will perform spectral 
    clustering into the provided number of groups
    """
    sc = SpectralClustering(n_clusters=n_clusters,affinity='precomputed')
    sc.fit(sim_matrix)
    labels = sc.labels_
    return labels

def write_out_clusters(clusters: List[int],filenames: List[str], outputFile: str,n_clusters: int) -> None:
    """
    Given the clusters will output the filenames on each individual
    line to the designated outputfile
    """
    if 'part1-images/' in filenames[0]:
        filenames = [i.replace('part1-images/',"") for i in filenames]
    properLine = [ [] for _ in range(n_clusters) ]
    for i in range(len(clusters)):
        assinged_class = clusters[i]
        filename = filenames[i]
        properLine[assinged_class].append(filename)
    with open(outputFile,'w') as endFile:
        for line in properLine:
            txt = " ".join(line) + "\n"
            endFile.write(txt)
    return

def compute_pairwise_accuracy(estimated_clusters: List[int],filenames: List[str],n_clusters:int):
    """
    Computers the pairwise accuracy by
    """
    if 'part1-images/' in filenames[0]:
        filenames = [i.replace('part1-images/',"") for i in filenames]
    n = len(filenames)
    prevGroup = ""
    curGroup = -1
    trueClusters = []
    for file in filenames:
        group = file.split("_")[0]
        if group != prevGroup:
            curGroup += 1
            prevGroup = group
        trueClusters.append(curGroup)
    tp = 0
    tn = 0
    for i in range(n):
        for j in range(n):
            if trueClusters[i] == trueClusters[j]:
                tp += estimated_clusters[i] == estimated_clusters[j]
            else:
                tn += estimated_clusters[i] != estimated_clusters[j]
    return (tp+tn)/(n*(n-1))


def p1(args):
    # get the list of input files and number of clusters and output file
    inputFiles = args[3:-1]
    n_clusters = int(args[2])
    outputFile = args[-1]
    #inputFiles = [f"part1-images/{i}" for i in os.listdir('./part1-images')]
    
    n_imgs = len(inputFiles)
    n_features = 1000
    im_orbs = [generate_orb_features(fn,n_features=n_features) for fn in inputFiles]
    
    # create the similarity matrix
    sim_matrix = np.zeros( (n_imgs,n_imgs) )

    #determine the matching criteria
    tau = .85
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    for i in range(n_imgs):
        for j in range(n_imgs):
            orb1,orb2 = im_orbs[i],im_orbs[j]
            sim_score = count_matching_features(orb1,orb2,bf,tau)
            sim_matrix[i,j] = sim_score
            sim_matrix[j,i] = sim_score

    clusters = spectral_clustering(sim_matrix,n_clusters)
    #write the output
    acc =compute_pairwise_accuracy(clusters,inputFiles,n_clusters)
    print(acc)
    write_out_clusters(clusters,inputFiles,outputFile,n_clusters)