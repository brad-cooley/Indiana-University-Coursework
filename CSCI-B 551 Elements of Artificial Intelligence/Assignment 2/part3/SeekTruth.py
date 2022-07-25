# SeekTruth.py : Classify text objects into two categories
#
# Code by: Brad Cooley <redacted>, McKenzie Quinn <redacted>
#
# Based on skeleton code by D. Crandall, October 2021
#

from math import log
import sys
from collections import Counter
import numpy as np

def load_file(filename):
    objects=[]
    labels=[]
    with open(filename, "r") as f:
        for line in f:
            parsed = line.strip().split(' ',1)
            labels.append(parsed[0] if len(parsed)>0 else "")
            objects.append(parsed[1] if len(parsed)>1 else "")

    return {"objects": objects, "labels": labels, "classes": list(set(labels))}

def word_in_dict(word_dict, word):
    '''Check if element in dictionary.
    '''
    if word in word_dict:
        word_dict[word] += 1
    else:
        word_dict[word] = 1
    return word_dict

def get_clean_text(words):
    clean_sentence = list()
    puncutation = ".,!;?'$)#(/" 
    stop_words = ['i', 'and', 'it', 'the', 'had', 'a', 'is', 'are', 'am', 'an',
    'be', 'by', 'you', 'your', 'yours', 'do', 'he', 'she', 'in', 'as', 'me', 'its',
    'of', 'off', 'or', 'on', 'only', 'to', 'too', 'this', 'was', 'we', 'was']
    #stop_words = list()
    for word in words:
        word = word.lower()
        word = word.strip(puncutation)
        if not any(char.isdigit() for char in word):
            clean_sentence.append(word)
        if word not in stop_words:
            clean_sentence.append(word)
    return clean_sentence

def get_vocab_counts(train_data):
    '''Get vocabulary within trianing data. Assuming words are broken up by
    spaces. No punctuation, caps, and lemmas are taken into account.
    Input: 
        train_data(dict): training data where objects is a string.
    Return: 
        words_dcitionary(dict): words and their count of occurance in data.
        deceptive_words_dict(dict): words and their count of occurance in deceptive labeled data.
        truthful_words_dict(dict): words and their count of occurance in truthful labeled data.
    '''
    words_dictionary = dict()
    deceptive_words_dict = dict()
    truthful_words_dict = dict()
    for sentence in range(len(train_data['objects'])):
        words = train_data['objects'][sentence].split(' ')
        words = get_clean_text(words)
        for w in words: 
            #word occurance in dataset
            words_dictionary = word_in_dict(words_dictionary, w)
            #sentence labeled as deceptive
            if train_data['labels'][sentence] == 'deceptive':
                deceptive_words_dict = word_in_dict(deceptive_words_dict, w)
            #sentence labeled as truthful
            else:
                truthful_words_dict = word_in_dict(truthful_words_dict, w)
    class_dict = dict(Counter(train_data['labels']))
    return words_dictionary, truthful_words_dict, deceptive_words_dict, class_dict

def calculate_tfidf(class_dict, words_in_class):
    tfidf = dict()
    for word in class_dict:
        count = class_dict[word]
        tfidf[word] = words_in_class[word]/count
    return tfidf

def get_tfidf(train_data):
    vocab, truth_vocab, decep_vocab, class_dict = get_vocab_counts(train_data)
    words_in_class = dict()
    for word in vocab:
        counter = 0 
        if word in decep_vocab:
            counter += 1
        if word in truth_vocab:
            counter += 1
        words_in_class[word] = counter
    tfidf_truthful = calculate_tfidf(truth_vocab, words_in_class)
    tfidf_deceptful = calculate_tfidf(decep_vocab, words_in_class)
    return vocab, tfidf_truthful, tfidf_deceptful

def get_classifier_tfidf(train_data):
    vocab, tfidf_truth, tfidf_decep = get_tfidf(train_data)
    bayes_components = dict()
    for word in vocab:
        probs = list()
        p_of_word = get_basic_prob(word, vocab)
        probs.append(p_of_word)
        try:
            p_word_truth = tfidf_truth[word]
            probs.append(p_word_truth)
            p_word_decep = tfidf_decep[word]
            probs.append(p_word_decep)
        except: 
            if len(probs) == 1:
                #put in low probability
                probs.append(.00001)
                probs.append(.00001)

            elif len(probs) == 2: 
                #put in extremely low probability
                probs.append(.00001)
        p_of_truth = .5
        probs.append(p_of_truth)
        p_of_decept = .5
        probs.append(p_of_decept)
        bayes_components[word] = probs

    return bayes_components



def get_classifier_count(train_data):
    vocab, truth_vocab, decep_vocab, class_dict = get_vocab_counts(train_data)
    bayes_components = dict()
    for word in vocab:
        probs = list()
        p_of_word = get_basic_prob(word, vocab)
        probs.append(p_of_word)
        try:
            p_word_truth = get_basic_prob(word, truth_vocab)
            probs.append(p_word_truth)
            p_word_decep = get_basic_prob(word, decep_vocab)
            probs.append(p_word_decep)
        except: 
            if len(probs) == 1:
                #put in low probability
                probs.append(.000001)
                probs.append(.000001)

            elif len(probs) == 2: 
                #put in extremely low probability
                probs.append(.00001)
        p_of_truth = get_basic_prob('truthful',class_dict)
        probs.append(p_of_truth)
        p_of_decept = get_basic_prob('deceptive',class_dict)
        probs.append(p_of_decept)
        bayes_components[word] = probs

    return bayes_components


def get_basic_prob(word, vocab):
    #get probability of occurance in trianing data
    #assuming word occurs in dictionary
    return vocab[word]/sum(vocab.values())

def prob_of_class_given_words(classifier, sentence, mode):
    #classifier = {word:[p_of_word, p_of_word_truth, p_of_word_decep, p_of_truth, p_of_decep]}
    #sentence = string in question
    #mode = truthful or deceptive
    prob = list()
    sentence = sentence.split(' ')
    sentence = get_clean_text(sentence)
    for word in sentence:
        if mode == 'deceptive':
                idx = 2
                idx_prior = 4
        else:
            idx = 1
            idx_prior = 3
        try:
            word_probs = classifier[word]
            prob.append(log(word_probs[idx] * word_probs[idx_prior]))
        except: 
            #prob.append(.0000000000000001)
            #prob.append(.00000000001)
            prob.append(log(.000001 * .5))
    prob.append(log(word_probs[idx_prior]))
          
    return sum(prob)

# classifier : Train and apply a bayes net classifier
#
# This function should take a train_data dictionary that has three entries:
#        train_data["objects"] is a list of strings corresponding to reviews
#        train_data["labels"] is a list of strings corresponding to ground truth labels for each review
#        train_data["classes"] is the list of possible class names (always two)
#
# and a test_data dictionary that has objects and classes entries in the same format as above. It
# should return a list of the same length as test_data["objects"], where the i-th element of the result
# list is the estimated classlabel for test_data["objects"][i]
#
# Do not change the return type or parameters of this function!
#
def classifier(train_data, test_data):
    #trained_classifier: {word:[p_of_word_truth, p_of_word_decep, p_of_word]}
    #trained_classifier = get_classifier_tfidf(train_data)
    trained_classifier = get_classifier_count(train_data)
    #classes, truthful = 0, deceptive = 1
    classes = train_data['classes']

    results = list()
    for sentence in test_data['objects']:
        #calcuations to get results for each sentence.
        #prob of truthful
        p_truth = prob_of_class_given_words(trained_classifier, sentence, classes[0])
        #prob of deception
        p_decep = prob_of_class_given_words(trained_classifier, sentence, classes[1])

        #determine_label and append to result
        if p_truth > p_decep: 
            results.append(classes[0])
        elif p_truth <= p_decep:
            results.append(classes[1])

    #should list of results in order of test data.
    return results


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise Exception("Usage: classify.py train_file.txt test_file.txt")

    (_, train_file, test_file) = sys.argv
    # Load in the training and test datasets. The file format is simple: one object
    # per line, the first word one the line is the label.
    train_data = load_file(train_file)
    test_data = load_file(test_file)
    if(sorted(train_data["classes"]) != sorted(test_data["classes"]) or len(test_data["classes"]) != 2):
        raise Exception("Number of classes should be 2, and must be the same in test and training data")

    # make a copy of the test data without the correct labels, so the classifier can't cheat!
    test_data_sanitized = {"objects": test_data["objects"], "classes": test_data["classes"]}

    results= classifier(train_data, test_data_sanitized)

    # calculate accuracy
    correct_ct = sum([ (results[i] == test_data["labels"][i]) for i in range(0, len(test_data["labels"])) ])
    print("Classification accuracy = %5.2f%%" % (100.0 * correct_ct / len(test_data["labels"])))
