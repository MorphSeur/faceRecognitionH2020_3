import time
from scipy.spatial import distance as dist
from imutils import face_utils
import imutils
import time
import dlib
import cv2
from tqdm import tqdm
import os

def saliency(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def recognise(contentMP4AVI):
    EYE_AR_THRESH = 0.20
    EYE_AR_CONSEC_FRAMES = 1
    COUNTER = 0
    TOTAL = 0

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('./lissilabmodels/models/spfl.dat')

    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']

    time.sleep(1.0)

    vs = cv2.VideoCapture(contentMP4AVI)
    length = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))

    for x in tqdm(range(length)):
        (ret, frame) = vs.read()
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)
        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = saliency(leftEye)
            rightEAR = saliency(rightEye)
            ear = (leftEAR + rightEAR) / 2.0
            if ear < EYE_AR_THRESH:
                COUNTER += 1
                realFrame = frame
                break
            else:
                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    TOTAL += 1
                COUNTER = 0
    return realFrame

def dpoDecodeTwo(dpoInfo, pathToTmp):

    ext1 = dpoInfo['iai_dpo_metadata'][0]['file:extension']
    ext2 = dpoInfo['iai_dpo_metadata'][1]['file:extension']

    if ext1 == 'png' and ext2 == 'png':
        imageName1 = dpoInfo['iai_dpo_metadata'][0]['id'] + '.dpo'
        imageName2 = dpoInfo['iai_dpo_metadata'][1]['id'] + '.dpo'

        statusPNG1 = os.system("base64 -d " + pathToTmp + '/' + imageName1 + "> " + pathToTmp + '/' + "r.png")
        statusPNG2 = os.system("base64 -d " + pathToTmp + '/' + imageName2 + "> " + pathToTmp + '/' + "7.png")
    elif ext1 == 'jpg' and ext2 == 'jpg':
        imageName1 = dpoInfo['iai_dpo_metadata'][0]['id'] + '.dpo'
        imageName2 = dpoInfo['iai_dpo_metadata'][1]['id'] + '.dpo'

        statusPNG1 = os.system("base64 -d " + pathToTmp + '/' + imageName1 + "> " + pathToTmp + '/' + "r.jpg")
        statusPNG2 = os.system("base64 -d " + pathToTmp + '/' + imageName2 + "> " + pathToTmp + '/' + "7.jpg")
    else:
        if ext1 == 'mp4' or ext2 == 'mp4':
            videoName1 = dpoInfo['iai_dpo_metadata'][0]['id'] + '.dpo'
            videoName2 = dpoInfo['iai_dpo_metadata'][1]['id'] + '.dpo'

            if 'mp4' in ext1:
                videoName = videoName1
            elif 'mp4' in ext2:
                videoName = videoName2
            statusMP4 = os.system("base64 -d " + pathToTmp + '/' + videoName + "> " + pathToTmp + '/' + "g.mp4")

        if ext1 == 'png' or ext2 == 'png':
            imageName1 = dpoInfo['iai_dpo_metadata'][0]['id'] + '.dpo'
            imageName2 = dpoInfo['iai_dpo_metadata'][1]['id'] + '.dpo'

            if 'png' in ext1:
                imageName = imageName1
            elif 'png' in ext2:
                imageName = imageName2

            statusPNG = os.system("base64 -d " + pathToTmp + '/' + imageName + "> " + pathToTmp + '/' + "r.png")

        if ext1 == 'jpg' or ext2 == 'jpg':
            imageName1 = dpoInfo['iai_dpo_metadata'][0]['id'] + '.dpo'
            imageName2 = dpoInfo['iai_dpo_metadata'][1]['id'] + '.dpo'

            if 'jpg' in ext1:
                imageName = imageName1
            elif 'jpg' in ext2:
                imageName = imageName2

            statusJPG = os.system("base64 -d " + pathToTmp + '/' + imageName + "> " + pathToTmp + '/' + "f.jpg")

        if ext1 == 'bag' or ext2 == 'bag':
            bagName1 = dpoInfo['iai_dpo_metadata'][0]['id'] + '.dpo'
            bagName2 = dpoInfo['iai_dpo_metadata'][1]['id'] + '.dpo'

            if 'bag' in ext1:
                bagName = bagName1
            elif 'bag' in ext2:
                bagName = bagName2

            statusBAG = os.system("base64 -d " + pathToTmp + '/' + bagName + "> " + pathToTmp + '/' + "a.bag")