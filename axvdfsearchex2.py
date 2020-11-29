import axvdfex
from datetime import datetime
import sys
import glob
import cv2
import pickle
import os
import signal
from uuid import uuid1
from skimage.metrics import structural_similarity as ssim

mdic = pickle.load(open(sys.argv[2], 'rb'))
keys = list(mdic.keys())
count = 0
f = open(sys.argv[1],"wt")
start = datetime.now()
for i in range(0,len(keys)):
    sigx = mdic[keys[i]]
    for j in range(i+1,len(keys)):
        print(i,j,"    ", end='\r')
        sigy = mdic[keys[j]]
        #print(sigy[0])
        if axvdfex.search_video3(sigx,sigy,10) > 0:
            print(keys[i], keys[j])
            print("-----------------------------------------------------------------------------------")
end = datetime.now()
print(count, end - start)


