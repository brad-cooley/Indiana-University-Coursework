#!/usr/bin/env python3
import sys
import part1
import part2
import part3
import good_warp
import os
if sys.argv[1]=="part1":
    part1.p1(sys.argv)
elif sys.argv[1]=="part2":
    part2.p2(sys.argv)
elif sys.argv[1]=="part3":
    part2.p3(sys.argv)
    #com = 'python3 part3.py '+sys.argv[2]+' '+sys.argv[3]+' '+sys.argv[4]
    #os.system(com)
