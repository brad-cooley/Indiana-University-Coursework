#!/usr/local/bin/python3
# assign.py : Assign people to teams
#
# Code by: Brad Cooley <redacted>, McKenzie Quinn <redacted>
#
# Based on skeleton code by D. Crandall and B551 Staff, September 2021
#

import sys
import time
import numpy as np

def get_student_profile(data):
    student_profile = dict()       #{user_id: [want_to_work_with, dont_want_to_work_with, 'desired_group_size]}
    for row in data: 
        student_profile[row[0]] = [row[1], row[2], len(row[1].split('-'))]
    return student_profile
    
def get_first_grouping(student_profiles):
    #get first grouping as everyone working on their own.
    groups = list(student_profiles.keys())
    # find cost of grouping 
    cost = time_cost(groups, student_profiles)
    return groups, cost

def get_new_grouping(student_profile):
    # we can have group sizes of [3, 2, 1]
    # we may not always be able to break up groups in to the same amount of people per group
    group_sizes = [1, 2, 3]
    students = list(student_profile.keys())
    groups = list()
    while students:
        #randomly pick group sizes 
        size = list(np.random.choice(group_sizes, 1))[0]
        try:
            #randomly pick groups based on random group size selection
            group_list = list(np.random.choice(students, size, replace = False))
        except: 
            # if group size selected is less than remaining students, resample with
            # smaller group size options and randomly select.
            size = list(np.random.choice([i+1 for i in range(len(students))], 1))[0]
            group_list = list(np.random.choice(students, size, replace = False))
        group_name = '-'.join(group_list)
        groups.append(group_name)
        #remove selected students from pool of options.
        for picked in group_list:
            students.remove(picked)

    cost = time_cost(groups, student_profile)

    return groups, cost
       
def wrong_group_size(group_mems, profile, counter):
    if len(group_mems) != profile[2]:
        counter += 1
    return counter

def not_with_requested(group_mems, profile, counter):
    requested = profile[0].split('-')
    for student in requested: 
        if student not in ['xxx', 'zzz']:
            if student not in group_mems:
                counter += 1
    return counter

def not_want_to_work_with(group_mems, profile, counter):
    not_requested = profile[1].split(',')
    for student in not_requested:
        if student in group_mems:
            counter+=1
        
    return counter

def time_cost(assigned_group, student_profile):
    total_cost = 0
    #each group takes 5min to grade assignments (len(groups)*5)
    total_cost += (len(assigned_group) * 5)
    #counters 
    wrong_group_size_counter = 0
    not_with_requested_counter = 0
    not_want_to_work_with_counter = 0        
    for group in assigned_group:
        group_mems = group.split('-')
        for mem in group_mems:
            #recall... profile = [want_to_work_with, don't want to work with, desired_group_size]
            profile = student_profile.get(mem)
            wrong_group_size_counter = wrong_group_size(group_mems, profile, wrong_group_size_counter)
            not_with_requested_counter = not_with_requested(group_mems, profile, not_with_requested_counter)
            not_want_to_work_with_counter = not_want_to_work_with(group_mems, profile, not_want_to_work_with_counter)

    #wrong group size (if persons group size != desired group size, 1*2)
    total_cost += (wrong_group_size_counter * 2)
    #didn't get to work with someone they requested (# of people *.05*60)
    total_cost += (not_with_requested_counter * .05 * 60)
    #student gets assigned to someone they did NOT want to work with, (#of students *10)
    total_cost += (not_want_to_work_with_counter * 10)
    return total_cost

def solver(input_file):
    """
    1. This function should take the name of a .txt input file in the format indicated in the assignment.
    2. It should return a dictionary with the following keys:
        - "assigned-groups" : a list of groups assigned by the program, each consisting of usernames separated by hyphens
        - "total-cost" : total cost (time spent by instructors in minutes) in the group assignment
    3. Do not add any extra parameters to the solver() function, or it will break our grading and testing code.
    4. Please do not use any global variables, as it may cause the testing code to fail.
    5. To handle the fact that some problems may take longer than others, and you don't know ahead of time how
       much time it will take to find the best solution, you can compute a series of solutions and then
       call "yield" to return that preliminary solution. Your program can continue yielding multiple times;
       our test program will take the last answer you 'yielded' once time expired.
    """
    #read in data 
    data = list()
    try:
        with open(input_file, 'r') as file:
                for line in file:
                    data.append(line.strip('\n').split(' ')) 
    except: 
        raise(Exception('File not found, please check file name and try again.'))
    # create student profiles for quick reference via dictionary.
    # {student_id : [desired_group, undesired_group, desired_group_size]}   
    student_profile = get_student_profile(data)
    #default determine cost if everyone works on their own.
    group, cost_to_beat = get_first_grouping(student_profile)
    # Simple example. First we yield a quick solution 
    yield({"assigned-groups": group,
               "total-cost" : cost_to_beat})
    # This solution will never be found, but that's ok; program will be killed eventually by the
    # test script.
    while True:
        #find more groupings
        new_group, new_cost = get_new_grouping(student_profile)
        if new_cost < cost_to_beat:
            # only yield new grouping if it's better than previous grouping displayed.
            yield({"assigned-groups": new_group,
               "total-cost" : new_cost})
            group = new_group
            cost_to_beat = new_cost

if __name__ == "__main__":
    if(len(sys.argv) != 2):
        raise(Exception("Error: expected an input filename"))

    for result in solver(sys.argv[1]):
        print("----- Latest solution:\n" + "\n".join(result["assigned-groups"]))
        print("\nAssignment cost: %d \n" % result["total-cost"])
    
