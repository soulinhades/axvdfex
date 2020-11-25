import sys
import subprocess
import numpy as np
import cv2
from sklearn.metrics import mean_squared_error
from skimage.metrics import structural_similarity as ssim
import av

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
    args = "ffmpeg -hide_banner -loglevel panic -skip_frame nokey -i %s -vsync 0 -f rawvideo -vframes %d -pix_fmt gray -s 128x128 -" % (name, maxframes)
    #args = "ffmpeg -hide_banner -loglevel panic -skip_frame nokey -i %s -vsync 0 -f rawvideo -pix_fmt gray -s 16x16 -" % name
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
    imgref = np.zeros((stream.codec_context.height, stream.codec_context.width),dtype='uint8')
    imgref[:] = 255
    stream.codec_context.skip_frame = 'NONKEY'
    for frame in container.decode(stream):
        p = frame.to_ndarray(format="gray")
        #p = autocrop(p)
        mse = ssim(p, imgref)
        #print(mse)

    
imgref = np.zeros((128,128),dtype='uint8')
imgref[:] = 255

def get_video_signature(name):
    imga, status = getvideothumbnail(name)
    frames = int(len(imga)/(128*128))
    if(frames != 5):
        print("Not enough frames")
        exit(1)
    #print(frames)
    imga = imga.reshape(frames,128,128)
    #imgb = imga[0].copy()
    #imgb[:] = 255
    #imga[:] = 255
    mse = 0.0
    factor = 1.0
    for i in range(0,frames):
        #img = autocrop(imga[i])
        #img = img.astype(np.uint8)
        #im = Image.fromarray(img)
        #print(img.shape)
        #img = cv2.resize(img, (16,16), interpolation = cv2.INTER_AREA)
        mse +=  mean_squared_error(imga[i], imgref)*factor
        #mse +=  ssim(img, imgref)*factor
        factor += 0.5
        #print(i,mse)
    #imgb = autocrop(imga[0])
    return mse
    
if __name__ == "__main__":
    get_video_signature2(sys.argv[1])
    #msea = get_video_signature(sys.argv[1])
    #mseb = get_video_signature(sys.argv[2])
    #print(msea,mseb,msea-mseb)
    #imga, status = getvideothumbnail(sys.argv[1])
    #imga = imga.reshape(4,128,128)
    #imgb = autocrop(imga[0])
    #print(imga[0].shape)
    #cv2.imwrite('sample.png', imgb)

