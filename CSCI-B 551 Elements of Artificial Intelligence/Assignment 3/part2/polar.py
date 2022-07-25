#!/usr/local/bin/python3
#
# Authors: McKenzie Quinn <redacted>, Brad Cooley <redacted>, John Holt <redacted>
#
# Ice layer finder
# Based on skeleton code by D. Crandall, November 2021
#

from PIL import Image
from numpy import *
from numpy.random.mtrand import normal
from scipy.ndimage import filters
import sys
import imageio

from collections import Counter
from scipy.stats import *
import warnings
warnings.filterwarnings("ignore")

# calculate "Edge strength map" of an image                                                                                                                                      
def edge_strength(input_image):
    grayscale = array(input_image.convert('L'))
    filtered_y = zeros(grayscale.shape)
    filters.sobel(grayscale,0,filtered_y)
    return sqrt(filtered_y**2)

# draw a "line" on an image (actually just plot the given y-coordinates
#  for each x-coordinate)
# - image is the image to draw on
# - y_coordinates is a list, containing the y-coordinates and length equal to the x dimension size
#   of the image
# - color is a (red, green, blue) color triple (e.g. (255, 0, 0) would be pure red
# - thickness is thickness of line in pixels
#
def draw_boundary(image, y_coordinates, color, thickness):
    for (x, y) in enumerate(y_coordinates):
        for t in range( int(max(y-int(thickness/2), 0)), int(min(y+int(thickness/2), image.size[1]-1 )) ):
            image.putpixel((x, t), color)
    return image

def draw_asterisk(image, pt, color, thickness):
    for (x, y) in [ (pt[0]+dx, pt[1]+dy) for dx in range(-3, 4) for dy in range(-2, 3) if dx == 0 or dy == 0 or abs(dx) == abs(dy) ]:
        if 0 <= x < image.size[0] and 0 <= y < image.size[1]:
            image.putpixel((x, y), color)
    return image


# Save an image that superimposes three lines (simple, hmm, feedback) in three different colors 
# (yellow, blue, red) to the filename
def write_output_image(filename, image, simple, hmm, feedback, feedback_pt):
    new_image = draw_boundary(image, simple, (255, 255, 0), 2)
    new_image = draw_boundary(new_image, hmm, (0, 0, 255), 2)
    new_image = draw_boundary(new_image, feedback, (255, 0, 0), 2)
    new_image = draw_asterisk(new_image, feedback_pt, (255, 0, 0), 2)
    imageio.imwrite(filename, new_image)

# main program
#
if __name__ == "__main__":

    if len(sys.argv) != 6:
        raise Exception("Program needs 5 parameters: input_file airice_row_coord airice_col_coord icerock_row_coord icerock_col_coord")

    input_filename = sys.argv[1]
    gt_airice = [ int(i) for i in sys.argv[2:4] ]
    gt_icerock = [ int(i) for i in sys.argv[4:6] ]

    # load in image 
    input_image = Image.open(input_filename).convert('RGB')
    image_array = array(input_image.convert('L'))

    # print(image_array[0])

    # compute edge strength mask -- in case it's helpful. Feel free to use this.
    edge_strength = edge_strength(input_image)
    imageio.imwrite('edges.png', uint8(255 * edge_strength / (amax(edge_strength))))

    # You'll need to add code here to figure out the results! For now,
    # just create some random lines.
    airice_simple = []
    airice_hmm = []
    icerock_simple = []
    icerock_hmm = []
    edge_strength_T = transpose(edge_strength)
    image_array_T = transpose(image_array)

    i = 0
    for col in edge_strength_T:
        probs = {}
        j = 0

        for entry in col:
            prob = int(entry) / sum(col)
            probs[j] = prob
            j+=1

        c = Counter(probs)
        most_common = c.most_common(10)
        air_mean = 0

        if i != 0:
            air_mean = mean(airice_simple)

        while most_common[0][0] > mean(airice_simple) + 10 or most_common[0][0] < mean(airice_simple) - 10:
            most_common.pop(0)

        airice = most_common[0][0]
        airice_simple.append(airice)
        most_common = c.most_common(20)

        while most_common[0][0] < airice + 10:
            most_common.pop(0)

        if i == 0:
            while most_common[0][0] > mean(icerock_simple) + 10 or most_common[0][0] < mean(icerock_simple) - 10:
                most_common.pop(0)
        else:
            while most_common[0][0] > icerock_simple[i-1] + 75 or most_common[0][0] < icerock_simple[i-1] - 75:
                most_common.pop(0)

        icerock_simple.append(most_common[0][0])
        i += 1

    emissions = []
    for j in range(len(image_array[0])):

        col = []
        darkest = 10000
        lightest = -1
        for i in range(len(image_array)):
            col.append([0,image_array[i][j]])
            if image_array[i][j] < darkest:
                darkest = image_array[i][j]
            elif image_array[i][j] > lightest:
                lightest = image_array[i][j]
        for i in range(len(col)):
            col[i][0]=(lightest-image_array[i][j])/lightest
        emissions.append(col)
        airice = max(col)
        airice_index = col.index(airice)
        icerock = [0,10000]
        for i in range(0,airice_index):
            if image_array[i][j] < icerock[1] and airice_index-i > 10:
                icerock = col[i]
        for i in range(airice_index + 1, len(image_array)):
            if image_array[i][j] < icerock[1] and i-airice_index > 10:
                icerock = col[i]
        icerock_index = col.index(icerock)
        if icerock_index < airice_index:
            airice,icerock = icerock,airice
            airice_index,icerock_index = icerock_index,airice_index
        # airice_simple.append(airice_index)
        # icerock_simple.append(icerock_index)
    prior_air = []
    prior_rock = []
    for i in range(len(emissions[0])):
        prior_air.append([emissions[0][i][0],[i]])

    for i in range(1,len(image_array[0])): #i represents t
        air_current = []
        for j in range(len(emissions[i])): #j cycles through state rows in viterbi
            vmax = 0
            vmax_trail = 0
            for k in range(len(prior_air)): #k cycles through prior jstates for maximization
                max_check = prior_air[k][0]*1/(abs(k-j)+1)
                if max_check > vmax:
                    vmax = max_check
                    vmax_trail = k
            air_current.append([emissions[i][j][0]*vmax,prior_air[vmax_trail][1]+[j]])
        prior_air = air_current
    airice_hmm =  max(prior_air)[1]
    for i in range(len(emissions)):
        for j in range(len(emissions[i])):
            if j-airice_hmm[i] <= 10:
                emissions[i][j][0]=0

    for i in range(len(emissions[0])):
        prior_rock.append([emissions[0][i][0],[i]])

    for i in range(1,len(image_array[0])): #i represents t
        rock_current = []
        for j in range(len(emissions[i])):
            v2max = 0
            v2max_trail = 0
            for k in range(len(prior_rock)):
                max_check2 = prior_rock[k][0]*1/(abs(k-j)//10+1)
                if max_check2 > v2max and abs(k-j)< 20:
                    v2max = max_check2
                    v2max_trail = k
            rock_current.append([emissions[i][j][0]*v2max,prior_rock[v2max_trail][1]+[j]])
        prior_rock = rock_current
    icerock_hmm = max(prior_rock)[1]

    '''
    Homemade version of viterbi. Not great, obviously.
    '''

    # initials = {}

    # for i in range(len(edge_strength_T[0])):
    #     initials[i] = edge_strength_T[0][i] / sum(edge_strength_T[0])
    #     initials[i] += image_array_T[0][i] / sum(image_array_T[0])

    # emissions = {}

    # for i in range(len(edge_strength_T)):
    #     probs = []
    #     for j in range(len(edge_strength_T[i])):
    #         prob = edge_strength_T[i][j] / sum(edge_strength_T[i])
    #         # prob += image_array_T[i][j] / sum(image_array_T[i])
            
    #         probs.append(prob)
        
    #     emissions[i] = probs

    # transitions = {}
    
    # c = Counter(initials)
    # airice_hmm.append(c.most_common(1)[0][0])

    # for i in range(1, len(edge_strength_T)):
    #     data = [x for x in range(len(edge_strength_T[0]))]
    #     temp = norm.pdf(data, loc=airice_hmm[-1], scale=5)
    #     # print(temp)

    #     c = Counter(emissions[i])

    #     mc = c.most_common(1)


    #     probs = []
    #     for j in range(len(edge_strength_T[i])):
    #         # if mc == airice_hmm[:-1]:
    #         #     prob = 1
    #         # else:
    #         prob = temp[j] * emissions[i][j]
    #         probs.append(prob)
    #         transitions[i] = probs
    #     ind = argmax(probs)

    #     while ind > airice_hmm[-1] + 10 or ind < airice_hmm[-1] - 10:
    #         probs[ind] = 0
    #         ind = argmax(probs)

    #     # print(transitions[1][22])
    #     airice_hmm.append(ind)

    '''
    Another attempt at viterbi is below. Couldn't figure out the syntax behind it. Tried to adapt it from wikipedia because I really don't understand the concept too well.
    '''
    # state_space = [x for x in range(image_array.shape[0])]  

    # print(len(edge_strength_T))  

    # trellis = [[0 for x in range(image_array.shape[0])] for x in range(image_array.shape[1])]  # To hold p. of each state given each observation.
    # pointers = [[0 for x in range(image_array.shape[0])] for x in range(image_array.shape[1])] # To hold backpointer to best prior state
    # # Determine each hidden state's p. at time 0...
    # for s in range(len(state_space)):
    #     trellis[0][s] = initials[s] * emissions[0][s]
    # # ...and afterwards, tracking each state's most likely prior state, k.
    # transitions = {}
    # for o in range(1, len(edge_strength_T)):
    #     transitions[o] = norm.pdf(state_space, loc = o, scale=5)
        
    # for o in range(1, len(edge_strength_T)):
    #     for s in range(len(state_space)):
    #         k = argmax(trellis[k][o-1] * transitions[k][s] * emissions[o][s])
    #         trellis[s][o] = trellis[k][o-1] * transitions[k][s] * emissions[o][s]
    #         pointers[s][o] = k
    #         print(k)
    # best_path = []

    
    # k = argmax( k in trellis[k, len(edge_strength_T)-1] )   # Find k of best final state
    # for o in range(len(edge_strength_T)-1, -1, -1):  # Backtrack from last observation.
    #     best_path.insert(0, state_space[k])         # Insert previous state on most likely path
    #     k = pointers[k, o]                # Use backpointer to find best previous state
    # print(best_path)

    airice_feedback= [ image_array.shape[0]*0.75 ] * image_array.shape[1]
    icerock_feedback= [ image_array.shape[0]*0.75 ] * image_array.shape[1]

    # Now write out the results as images and a text file
    write_output_image("air_ice_output.png", input_image, airice_simple, airice_hmm, airice_feedback, gt_airice)
    write_output_image("ice_rock_output.png", input_image, icerock_simple, icerock_hmm, icerock_feedback, gt_icerock)
    with open("layers_output.txt", "w") as fp:
        for i in (airice_simple, airice_hmm, airice_feedback, icerock_simple, icerock_hmm, icerock_feedback):
            fp.write(str(i) + "\n")
