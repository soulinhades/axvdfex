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
m = int(sys.argv[4])
start = datetime.now()
for i in range(0,len(keys)):
    sigx = mdic[keys[i]]
    for j in range(i+1,len(keys)):
        print(i,j,"    ", end='\r')
        sigy = mdic[keys[j]]
        match, seq, sj = axvdfex.search_video3xx(sigx,sigy,int(sys.argv[3]))
        if seq > m:
            print(keys[i], keys[j], seq, len(sigx), len(sigy), "SUB" if sj!=0 else "")
            print("-----------------------------------------------------------------------------------")
            print("%s,%s,%d,%d,%d,%s" % (keys[i],keys[j],seq,len(sigx),len(sigy),"SUB" if sj!=0 else ""),file=f)
            #if sj != 0: input("Press Enter to continue...")
end = datetime.now()
print(count, end - start)


