import axvdf
import axvdfx
from datetime import datetime
import sys
import glob
import cv2
import pickle
import os
import signal
import axvdfex

class GracefulInterruptHandler(object):

    def __init__(self, sig=signal.SIGINT):
        self.sig = sig

    def __enter__(self):
        self.interrupted = False
        self.released = False
        self.original_handler = signal.getsignal(self.sig)
        def handler(signum, frame):
            self.release()
            self.interrupted = True
        signal.signal(self.sig, handler)
        return self

    def __exit__(self, type, value, tb):
        self.release()

    def release(self):
        if self.released:
            return False
        signal.signal(self.sig, self.original_handler)
        self.released = True
        return True

try:
    mdic = pickle.load(open(sys.argv[1], 'rb'))
except FileNotFoundError:
    print("creating new dictionary..")
    mdic = {}
  
paths = glob.glob(sys.argv[2] + "/*.mp4")
with GracefulInterruptHandler() as h:
    timefirst = datetime.now()
    for index, path in enumerate(paths):
        size = os.path.getsize(path)
        x = os.path.split(path)
        if x[1] in mdic:
            print(index, len(paths), "      ", end='\r')
        else:
            img = axvdfex.get_video_signature(path)
            mdic[x[1]] = img
            print(index, len(paths), "      ", end='\r')
        if h.interrupted:
            break
    timesecond = datetime.now()
    pickle.dump(mdic, open(sys.argv[1], 'wb')) 
    print(timesecond - timefirst) 

