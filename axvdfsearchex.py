import axvdf
import axvdfex
from datetime import datetime
import sys
import glob
import cv2
import pickle
import os
import signal
from uuid import uuid1

mdic = pickle.load(open(sys.argv[2], 'rb'))
keys = list(mdic.keys())
count = 0
f = open(sys.argv[1],"wt")
start = datetime.now()
for i in range(0,len(keys)):
    sigx = mdic[keys[i]]
    delta = sigx*5/100
    print(delta)
    for j in range(i+1,len(keys)):
        print(i,j,"    ", end='\r')
        sigy = mdic[keys[j]]
        d = abs(sigx - sigy)
        if d < delta:
            count += 1
            print("%s,%s,%d" % (keys[i],keys[j],d),file=f)
end = datetime.now()
print(count, end - start)


