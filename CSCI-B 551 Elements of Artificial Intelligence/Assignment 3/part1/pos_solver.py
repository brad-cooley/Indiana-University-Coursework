###################################
# CS B551 Spring 2021, Assignment #3
#
# Your names and user ids: McKenzie Quinn <redacted>, Brad Cooley <redacted>, John Holt <redacted> 
#
# (Based on skeleton code by D. Crandall)
#

from collections import Counter, defaultdict
import random
import math
import numpy as np 
import time 

# We've set up a suggested code structure, but feel free to change it. Just
# make sure your code still works with the label.py and pos_scorer.py code
# that we've supplied.
#
class Solver:
    def __init__(self):
        self.labels = list()

        self.emission_probs = dict()
        self.transition_probs = dict()
        self.transition2_probs = dict()
        self.prior_probs = dict()
        self.initial_probs = dict()

        self.emission_counts = dict()
        self.transition_counts = dict()
        self.transition2_counts = dict()

    # Calculate the log of the posterior probability of a given sentence
    #  with a given part-of-speech labeling. Right now just returns -999 -- fix this!
    def calculate_naive_posterior(self, word, label):
        return math.log(self.is_emission(word, label) * self.prior_probs[label])
   
    def get_prob(self, count_dict):
        total = sum(count_dict.values())
        probs = {word: count_dict[word]/total for word in count_dict}
        return probs

    def get_inital_counts(self, row, initial_state_dist):
        if row[1][0] in initial_state_dist:
            initial_state_dist[row[1][0]] += 1
        else:
            initial_state_dist[row[1][0]] = 1
        return initial_state_dist
    
    def get_transition_counts(self, pos1, pos2 ):
        if pos1 in self.transition_counts:
            if pos2 in self.transition_counts[pos1]:
                self.transition_counts[pos1][pos2] += 1
            else: 
                self.transition_counts[pos1][pos2] = 1
        else: 
            self.transition_counts[pos1] = {pos2 : 1}

    def get_transition_probability(self):
        for pos1 in self.transition_counts:
            for pos2 in self.transition_counts[pos1]:
                if pos1 not in self.transition_probs:
                    self.transition_probs[pos1] = {pos2 :self.transition_counts[pos1][pos2] / sum(self.transition_counts[pos1].values())}
                else:
                    self.transition_probs[pos1][pos2] = self.transition_counts[pos1][pos2] / sum(self.transition_counts[pos1].values())

    def is_transition(self, pos1, pos2):
        if pos1 in self.transition_probs and pos2 in self.transition_probs[pos1]:
            return self.transition_probs[pos1][pos2]
        else:
            return .0000001

    def get_transition_counts_2(self, before_prev_pos, prev_pos, current, ):
        if before_prev_pos in self.transition2_counts:
            if prev_pos in self.transition2_counts[before_prev_pos]:
                if current in self.transition2_counts[before_prev_pos][prev_pos]:
                    self.transition2_counts[before_prev_pos][prev_pos][current] += 1
                else:
                    self.transition2_counts[before_prev_pos][prev_pos][current]= 1
            else:
                self.transition2_counts[before_prev_pos][prev_pos] = {current : 1}
        else:
            self.transition2_counts[before_prev_pos]= {prev_pos:{current : 1}}
   
    def get_transition2_probs(self):
        for pos1 in self.transition2_counts:
            for pos2 in self.transition2_counts[pos1]:
                for pos3 in self.transition2_counts[pos1][pos2]:
                    if pos1 not in self.transition2_probs:
                        self.transition_probs[pos1] = {pos2 : {pos3 : self.transition2_counts[pos1][pos2][pos3]/sum(self.transition2_counts[pos1][pos2].values())}}
                    else:
                        self.transition2_probs[pos1][pos2][pos3] = self.transition2_counts[pos1][pos2][pos3]/sum(self.transition2_counts[pos1][pos2].values())

    def is_transition2(self, pos1, pos2, pos3):
        if pos1 in self.transition2_probs and pos2 in self.transition2_probs[pos1] and pos3 in  self.transition2_probs[pos1][pos2]:
            return self.transition2_probs[pos1][pos2][pos3]
        else: 
            return .0000001
    
    def get_emission_counts(self, word, pos):
        if word in self.emission_counts:
            if pos in self.emission_counts[word]:
                self.emission_counts[word][pos] += 1
            else:
                self.emission_counts[word][pos] = 1
        else:
            self.emission_counts[word] = { pos : 1}
    
    def get_emission_probability(self):
        for word in self.emission_counts:
            for pos in self.emission_counts[word]:
                if word not in self.emission_probs :
                    self.emission_probs[word]= {pos :self.emission_counts[word][pos] / sum(self.transition_counts[pos].values())}
                else:
                    self.emission_probs[word][pos] = self.emission_counts[word][pos] / sum(self.transition_counts[pos].values())

    def is_emission(self, word, pos):
        if word in self.emission_probs and pos in self.emission_probs[word]:
            return self.emission_probs[word][pos]
        else:
            return .0000001

    def posterior(self, model, sentence, label):
        if model == "Simple":

            return  sum([math.log(self.is_emission(sentence[i], label[i]) * self.prior_probs[label[i]])
   for i in range(len(sentence))])

        elif model == "HMM":
            intial = [math.log(self.initial_probs[label[0]]), math.log(self.is_emission(sentence[0], label[0]))]
            transition_p = [ math.log(self.is_transition(label[i-1], label[i])) for i in range(1, len(sentence))]
            emission_p = [ math.log(self.is_emission(sentence[i], label[i])) for i in range(1, len(sentence))]
            return sum(intial) + sum(transition_p) + sum(emission_p)

        elif model == "Complex":
            initial = [math.log(self.initial_probs[label[0]]), math.log(self.is_emission(sentence[0], label[0]))]
            emission_p = [math.log(self.is_emission(sentence[i], label[i])) for i in range(1, len(sentence))]
            transition_p = [math.log(self.is_transition(label[i-1], label[i])) for i in range(1, len(sentence))]
            transition2_p = [math.log(self.is_transition2(label[i-2], label[i-1], label[i])) for i in range(2, len(sentence))]
            return sum(initial) + sum(emission_p) + sum(transition_p) + sum(transition2_p)
        else:
            print("Unknown algo!")

    # Do the training!
    def train(self, data):
        #get corpus and tags
        intial_state = dict()
        tags = [row[1][word] for row in data for word in range(len(row[1]))]

        for row in data: 
            intial_state = self.get_inital_counts(row, intial_state)
            [self.get_emission_counts(row[0][word], row[1][word]) for word in range(len(row[0]))]
            [self.get_transition_counts(row[1][word-1], row[1][word]) for word in range(1, len(row[0]))]
            [self.get_transition_counts_2(row[1][word-2], row[1][word-1], row[1][word]) for word in range(2, len(row[0]))]

        #get corpus counts 
        tags_count = dict(Counter(tags))
        self.labels = list(tags_count.keys())
        self.initial_probs = self.get_prob(intial_state)       
        self.prior_probs = self.get_prob(tags_count) 
        self.get_emission_probability()
        self.get_transition2_probs()
        self.get_transition_probability()
        
    # Functions for each algorithm. Right now this just returns nouns -- fix this!
    def simplified(self, sentence):
        pos_list = list()
        for word in sentence:
            (probs, pos) = max([(self.calculate_naive_posterior(word, label), label) for label in self.labels])
            pos_list.append(pos)
        return pos_list

    def hmm_viterbi(self, sentence):
        ### REF: https://github.com/llrs/Viterbi/blob/master/Viterbi.py
        v_table = [{pos:math.log(self.initial_probs[pos] * self.is_emission(sentence[0],pos)) for pos in self.labels }]
        path = {pos: [pos] for pos in self.labels}
    
        # use transition probs for remaining setences
        for word_idx in range(1, len(sentence)):
            v_table.append({})
            newpath = {}
            for pos_now in self.labels:
                (prob, pos_pre) = max((v_table[word_idx-1][pos_pre] + math.log(self.is_transition(pos_pre, pos_now)* self.is_emission(sentence[word_idx], pos_now)), pos_pre) for pos_pre in self.labels)
   
                v_table[word_idx][pos_now] = prob
                newpath[pos_now] = path[pos_pre] + [pos_now]
            path = newpath

        (prob, pos_pre) = max((v_table[len(sentence)-1][pos_now], pos_now) for pos_now in self.labels)
               
        return  path[pos_pre]
   ### end of REF
        
    def get_sample(self, sentence, sample):
        
        for word_idx in range(len(sentence)):
            probs = [0] * len(self.labels)
            log_probs = [0] * len(self.labels)
            #s = [for label_idx in range(len)]

            for label_idx in range(len(self.labels)):
                sample[word_idx] = self.labels[label_idx]
                log_probs[label_idx] = self.posterior("Complex", sentence, sample)
            
            current_min = min(log_probs)

            log_probs = [p-current_min for p in log_probs]
            probs = [math.pow(10, log_probs[i]) for i in range(len(log_probs))]
    
            p_sum = sum(probs)
            probabilities = [x/p_sum for x in probs]
            
            rand = random.random()
            probabilities = np.cumsum(probabilities)
            for i in range(len(probabilities)):
                if rand < probabilities[i]: 
                    sample[word_idx] = self.labels[i]
                    break
         
        return sample

    def complex_mcmc(self, sentence):
        iterations = 150
        burn_iteration = 30
        count_tags = list()
        sample = ["noun"] * len(sentence)
        samples = list()
        for i in range(iterations):
            sample = self.get_sample(sentence, sample)
            if i >= burn_iteration:
                samples.append(sample)        

        for word_idx in range(len(sentence)):
            tag_count = defaultdict(int)
            for sample in samples: tag_count[sample[word_idx]] += 1
            count_tags.append(tag_count)
        return [max(count_tags[i], key = count_tags[i].get) for i in range(len(sentence))]
                    

    # This solve() method is called by label.py, so you should keep the interface the
    #  same, but you can change the code itself. 
    # It should return a list of part-of-speech labelings of the sentence, one
    #  part of speech per word.
    #
    def solve(self, model, sentence):
        if model == "Simple":
            return self.simplified(sentence)
        elif model == "HMM":
            return self.hmm_viterbi(sentence)
        elif model == "Complex":
            return self.complex_mcmc(sentence)
        else:
            print("Unknown algo!")

