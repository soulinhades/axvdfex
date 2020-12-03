import sys
import subprocess
import numpy as np
import cv2
from sklearn.metrics import mean_squared_error
from skimage.metrics import structural_similarity as ssim
import av
import scipy.fftpack

maxframes = 5

def autocrop(image, threshold=0):
    if len(image.shape) == 3:
        flatImage = np.max(image, 2)
    else:
        flatImage = image
    assert len(flatImage.shape) == 2
    rows = np.where(np.max(flatImage, 0) > threshold)[0]
    if rows.size:
        cols = np.where(np.max(flatImage, 1) > threshold)[0]
        image = image[cols[0]: cols[-1] + 1, rows[0]: rows[-1] + 1]
    else:
        image = image[:1, :1]
    return image

def getvideothumbnail(name):
    #args = "ffmpeg -hide_banner -loglevel panic -skip_frame nokey -i %s -vsync 0 -f rawvideo -vframes %d -pix_fmt gray -s 128x128 -" % (name, maxframes)
    args = "ffmpeg -hide_banner -loglevel panic -skip_frame nokey -i %s -vsync 0 -f rawvideo -pix_fmt gray -s 128x128 -" % name
    process = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
    try:
        output, error = process.communicate(timeout=15)
    except TimeoutExpired:
        process.kill()
        output, error = process.communicate()
    status = process.wait()
    #print(list(output))
    return (np.array(list(output),dtype='uint8'), status)

def get_video_signature2(name):
    container = av.open(name)
    stream = container.streams.video[0]
    #print(float(stream.duration*stream.time_base))
    #print(stream.codec_context.width, stream.codec_context.height)
    #imgref = np.zeros((stream.codec_context.height, stream.codec_context.width),dtype='uint8')
    #imgref[:] = 255
    sig = []
    stream.codec_context.skip_frame = 'NONKEY'
    for frame in container.decode(stream):
        p = frame.to_ndarray(format="gray")
        p = autocrop(p)
        framex = frame.from_ndarray(p, format='gray')
        framex = framex.reformat(width=8,height=8,format="gray")
        #print(frame)    
        p = framex.to_ndarray(format="gray")
        #print(p.shape)
        #p = autocrop(p)
        #mse = ssim(p, imgref)
        time = float(frame.pts*frame.time_base)
        #print(time,mse)
        sig.append((time,p))
        #if frame.index > 5:
        #    break
    return sig

def binary_array_to_hex(arr):
	bit_string = ''.join(str(b) for b in 1 * arr.flatten())
	width = int(np.ceil(len(bit_string)/4))
	return '{:0>{width}x}'.format(int(bit_string, 2), width=width)

class ImageHash(object):

    def __init__(self, binary_array):
        self.hash = binary_array

    def __str__(self):
        return binary_array_to_hex(self.hash.flatten())
    
    def __repr__(self):
        return repr(self.hash)

    def __sub__(self, other):
        return np.count_nonzero(self.hash.flatten() != other.hash.flatten())

    def __eq__(self, other):
        if other is None:
            return False
        return np.array_equal(self.hash.flatten(), other.hash.flatten())
    
    def __ne__(self, other):
        if other is None:
            return False
        return not np.array_equal(self.hash.flatten(), other.hash.flatten())

    def __hash__(self):
        return sum([2**(i % 8) for i, v in enumerate(self.hash.flatten()) if v])
    
    def __len__(self):
        return self.hash.size

def phash(image):
    dct = scipy.fftpack.dct(scipy.fftpack.dct(image, axis=0), axis=1)
    dctlowfreq = dct[:8,:8]
    med = np.median(dctlowfreq)
    diff = dctlowfreq > med
    return ImageHash(diff)

dimage = np.zeros((32,32),dtype='uint8')
dhash = phash(dimage)

def get_video_signature3(name):
    sig = []
    container = av.open(name)
    stream = container.streams.video[0]
    stream.codec_context.skip_frame = 'NONKEY'
    for frame in container.decode(stream):
        p = frame.to_ndarray(format="gray")
        p = autocrop(p)
        framex = frame.from_ndarray(p, format='gray')
        #framex.to_image().save(
        #    'xnight-sky.{:04d}.jpg'.format(frame.index),
        #    quality=80,
        #)
        framex = framex.reformat(width=32,height=32,format="gray")
        #print(frame)    
        image = framex.to_ndarray(format="gray")
        #frame = frame.reformat(width=32,height=32,format="gray")
        #image = frame.to_ndarray()
        xhash = phash(image)
        time = float(frame.pts*frame.time_base)
        sig.append((time,xhash))
        #print(time, xhash)
    return sig

imgref = np.zeros((16,16),dtype='uint8')
imgref[:] = 255

def get_video_signature(name):
    imga, status = getvideothumbnail(name)
    frames = int(len(imga)/(128*128))
    #print(frames)
    imga = imga.reshape(frames,128,128)
    #imgb = imga[0].copy()
    #imgb[:] = 255
    #imga[:] = 255
    mse = 0.0
    sig = []
    #factor = 1.0
    for i in range(0,frames):
        #img = autocrop(imga[i])
        #img = img.astype(np.uint8)
        #im = Image.fromarray(img)
        #print(img.shape)
        #img = cv2.resize(img, (16,16), interpolation = cv2.INTER_AREA)
        #mse =  mean_squared_error(imga[i], imgref)
        mse =  ssim(imga[i], imgref)
        #factor += 0.5
        print(i,mse)
        sig.append(mse)
    #imgb = autocrop(imga[0])
    return sig
 
def search_video(siga,sigb,m=0.99):
    if len(siga) > len(sigb):
        sigax = sigb
        sigbx = siga
    else:
        sigax = siga
        sigbx = sigb
    match = 0
    start = 0
    for i in range(0,len(sigax)):
        x = sigax[i]
        found = False
        for j in range(start,len(sigbx)):
            y = sigbx[j]
            #print(x)
            d = ssim(x[1],y[1])
            if d > m:
                start = j + 1
                found = True
            #    match += 1
                print("Match found (", x[0], ",", y[0], ")")
            #    #px.append(i)
            #    #py.append(j)
                break
        if found == False:
            break
 
def search_video3(siga,sigb,m=10):
    if len(siga) > len(sigb):
        sigax = sigb
        sigbx = siga
    else:
        sigax = siga
        sigbx = sigb
    match = 0
    start = 0
    for i in range(0,len(sigax)):
        x = sigax[i]
        if x[1] - dhash < 10:
            continue
        found = False
        for j in range(start,len(sigbx)):
            y = sigbx[j]
            d = x[1] - y[1]
            #print(d)
            if d < m:
                start = j + 1
                found = True
                match += 1
                print("Match found (", x[0], ",", y[0], ") ", d)
                if x[0] != y[0]: print("SUBSET*****************************************************************")
                break
        if found == False:
            break
    return match

def search_video3x(siga,sigb,m=10):
    print("--------------------------------------------------------------------------------")
    if len(siga) > len(sigb):
        sigax = sigb
        sigbx = siga
    else:
        sigax = siga
        sigbx = sigb
    match = 0
    start = 0
    sub = False
    for i in range(0,len(sigax)):
        x = sigax[i]
        found = False
        for j in range(start,len(sigbx)):
            y = sigbx[j]
            d = x[1] - y[1]
            if d < m:
                start = j + 1
                found = True
                match += 1
                print("Match found (", x[0], ",", y[0], ") ", d)
                if i != j: sub = True
                break
        if found == False:
            break
    return match, sub
 
def search_video3xxold(siga,sigb,m=20):
    if len(siga) > len(sigb):
        sigax = sigb
        sigbx = siga
    else:
        sigax = siga
        sigbx = sigb
    match = 0
    start = 0
    seq = 0
    sj = 0
    for i in range(0,len(sigax)):
        x = sigax[i]
        found = False
        for j in range(start,len(sigbx)):
            y = sigbx[j]
            d = x[1] - y[1]
            if d < m:
                start = j + 1
                found = True
                if match == 0:
                    oj = j
                    sj = j
                    seq += 1
                else:
                    if j == oj + 1:
                        seq += 1
                    oj += 1
                match += 1
                #print("Match found (", x[0], ",", y[0], ") ", d)
                break
        if found == False:
            break
    return match, seq, sj
    
def search_video3xx(siga,sigb,m=20):
    if len(siga) > len(sigb): siga,sigb = sigb,siga
    #print(len(siga),len(sigb))
    match = 0
    start = 0
    seq = 0
    sj = None
    oj = -2
    for i in range(0,len(siga)):
        x = siga[i]
        found = False
        for j in range(start,len(sigb)):
            y = sigb[j]
            d = x[1] - y[1]
            #print(i,j,d)
            if d < m:
                #print("Match found (", x[0], ",", y[0], ") ", d)
                match += 1
                start = j + 1
                found = True
                if j == oj + 1:
                    seq += 1
                    oj += 1
                else:
                    #if sj != None:
                    #    print("==>",sj,seq)
                    seq = 1
                    oj = j
                    sj = j
                break
        if found == False:
            break
    #print("==>",sj,seq)
    return match, seq, sj
 

if __name__ == "__main__":
    a = get_video_signature3(sys.argv[1])
    b = get_video_signature3(sys.argv[2])
    match, seq, start= search_video3xx(a,b,int(sys.argv[3]))
    print(match,seq,start)
    #msea = get_video_signature(sys.argv[1])
    #mseb = get_video_signature(sys.argv[2])
    print(a[0][1])
    #imga, status = getvideothumbnail(sys.argv[1])
    #imga = imga.reshape(4,128,128)
    #imgb = autocrop(imga[0])
    #print(imga[0].shape)
    #cv2.imwrite('sample.png', imgb)

