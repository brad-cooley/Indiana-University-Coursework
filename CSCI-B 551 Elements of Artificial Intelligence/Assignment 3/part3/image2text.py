#!/usr/bin/python
#
# Perform optical character recognition, usage:
#     python3 ./image2text.py train-image-file.png train-text.txt test-image-file.png
# 
# Authors: McKenzie Quinn <redacted>, Brad Cooley <redacted>, John Holt <redacted>
#
# (based on skeleton code by D. Crandall, Oct 2020)
#

from PIL import Image, ImageDraw, ImageFont
import sys

CHARACTER_WIDTH=14
CHARACTER_HEIGHT=25


def load_letters(fname):
    im = Image.open(fname)
    px = im.load()
    (x_size, y_size) = im.size
#    print(im.size)
#    print(int(x_size / CHARACTER_WIDTH) * CHARACTER_WIDTH)
    result = []
    for x_beg in range(0, int(x_size / CHARACTER_WIDTH) * CHARACTER_WIDTH, CHARACTER_WIDTH):
        result += [ [ "".join([ '*' if px[x, y] < 1 else ' ' for x in range(x_beg, x_beg+CHARACTER_WIDTH) ]) for y in range(0, CHARACTER_HEIGHT) ], ]
    return result

def load_training_letters(fname):
    TRAIN_LETTERS="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789(),.-!?\"' "
    letter_images = load_letters(fname)
    return { TRAIN_LETTERS[i]: letter_images[i] for i in range(0, len(TRAIN_LETTERS) ) }

# main program
if len(sys.argv) != 4:
    raise Exception("Usage: python3 ./image2text.py train-image-file.png train-text.txt test-image-file.png")

(train_img_fname, train_txt_fname, test_img_fname) = sys.argv[1:]
train_letters = load_training_letters(train_img_fname)
test_letters = load_letters(test_img_fname)
train_text = open(train_txt_fname).read().lower()

# code to clean train_text to contain only single instances of each word
#   - capitalization is ignored
#   - punctuation is removed
dirty_text_list = train_text.split()
clean_text = []
for word in dirty_text_list:
    if word not in clean_text:
        clean_text.append(word)
train_text = ""
for word in clean_text:
    train_text += " " + word

# initials
initials = []
for i in range(46):
    initials.append(0)
    
# transitions will contain be a 46x46 list of transitional probabilities
#   - Conceptually a 46x46 grid, where row = index//46, col = index%46
#   - row = letter_n, column = letter_n+1
#   - transition from 30th character to 40th character would be findable:
#           index = row*46 + col
#                 = 30 *46 + 40
#                 = 1420
char_list = ['a','b','c','d','e','f','g','h','i','j','k','l','m',
             'n','o','p','q','r','s','t','u','v','w','x','y','z',
             '0','1','2','3','4','5','6','7','8','9',
             '(',')',',','.','-','!','?','"',"'",' ']
transitions = []
for i in range(46*46):
    transitions.append(0)

# population of initials and transitions lists
total_chars = 0
for i in range(len(train_text)):
    if train_text[i] in char_list:
        letter_index = char_list.index(train_text[i])
        initials[letter_index]+=1
        total_chars+=1
        if i < len(train_text)-1:
            if train_text[i+1] in char_list:
                t_index = letter_index*46 + char_list.index(train_text[i+1])
                transitions[t_index]+=1
number_trans = 0
for i in range(26,36):
    for j in range(26,36):
        number_trans += transitions[i*46+j]
ave_num_trans = number_trans/100
for i in range(26,36):
    for j in range(26,36):
        transitions[i*46+j]=ave_num_trans
for i in range(len(initials)):
    initials[i] = initials[i]/total_chars
for i in range(len(transitions)):
    if transitions[i] == 0:
        min_trans = max(transitions)
        for trans in transitions:
            if trans > 0 and trans < min_trans:
                min_trans = trans
        transitions[i] = min_trans 
for i in range(46):
    total_transitions = 0
    for j in range(46):
        total_transitions += transitions[i*46+j]
    for j in range(46):
        transitions[i*46+j] = transitions[i*46+j]/total_transitions
        
#eissions will contain a list of emission probabilities for each digit in image
emissions = []
simple_output = ""
#threshold will determine when the percent of expected stars that are actually
#present is low enough to justify the space character
ave_clean = 0
ave_noisy = 0
for i in range(len(test_letters)):
    for s in range(len(test_letters[i])):
        for char in test_letters[i][s]:
            if char == "*":
                ave_noisy+=1
ave_noisy = ave_noisy/len(test_letters)
for key in train_letters:
    for r in range(len(train_letters[key])):
        for char in train_letters[key][r]:
            if char == "*":
                ave_clean+=1
ave_clean = ave_clean/72
if ave_noisy < 20:
    threshold = 0.24*ave_noisy/ave_clean
elif ave_noisy < 35:
    threshold = 0.24*.5
else:
    threshold = 0.24
for i in range(len(test_letters)):
    test_string = ""
    for s in range(len(test_letters[i])):
        test_string+=test_letters[i][s]
    char_list = []
    for key in train_letters:
        train_string = ""
        for r in range(len(train_letters[key])):
            train_string+=train_letters[key][r]
        correct = 0
        total = 0
        for j in range(len(train_string)):
            if test_string[j] == train_string[j] and train_string[j] == "*":
                correct+=1
                total+=1
            elif test_string[j] == "*" or train_string[j] == "*":
                total+=1
        if total==0:
            total=1
        char_list.append([(correct/total)**8*10**6,key])
    total = 0
    best_match = 0
    total_num = 0
    for j in range(len(char_list)):
        if char_list[j][0]>best_match:
            best_match = char_list[j][0]
    best_match2 = 0
    for j in range(len(char_list)):
        if char_list[j][0]>best_match2 and char_list[j][0] != best_match:
            best_match2 = char_list[j][0]
    best_match3 = 0
    for j in range(len(char_list)):
        if char_list[j][0]>best_match3 and char_list[j][0] != best_match and char_list[j][0] != best_match2:
            best_match3 = char_list[j][0]  
    for j in range(len(char_list)):
        if char_list[j][0] < best_match3 or char_list[j][0] < threshold:
            char_list[j][0] = 0
        else:
            total+=char_list[j][0]
            total_num+=1
    if total == 0:
        char_list[71][0] = 1
    emissions.append(char_list)
    if max(char_list)[0] > threshold:
        simple_output+=max(char_list)[1]
    else:
        simple_output+=" "
        
# implementation of Viterbi for HMM
prior = []
for i in range(len(emissions[0])):
    if i>25:
        adj_i = i-26
    else:
        adj_i = i
    if initials[adj_i]==0:
        min_init = max(initials)
        for init in initials:
            if init > 0 and init < min_init:
                min_init = init
        initials[adj_i] = min_init
    prior.append([emissions[0][i][0]*initials[adj_i],emissions[0][i][1]])
for i in range(1,len(test_letters)): #i represents t
    current = []
    for j in range(len(emissions[i])): #j cycles through state column in viterbi
        vmax = 0
        vmax_letter = ""
        for k in range(len(prior)): #k cycles through prior jstates for maximization
            if k>25:
                adj_k = k-26
            else:
                adj_k = k
            if j>25:
                adj_j = j-26
            else:
                adj_j = j
            max_check = prior[k][0]*transitions[adj_k*46 + adj_j]
            if max_check > vmax:
                vmax = max_check
                vmax_letter = prior[k][1]
        current.append([emissions[i][j][0]*vmax*100,vmax_letter+emissions[i][j][1]])
    prior = current

print("Simple: " + simple_output)
print("   HMM: " + max(prior)[1]) 
