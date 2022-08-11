# -*- coding: utf-8 -*-

import os
from flask import Flask, jsonify, request
import json
import jsonschema
from iai_toolbox import AnalyticsRequest, AnalyticsAgent, get_analytics_pool
import time
import lissilab
from PIL import Image
from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils.video import WebcamVideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
from tqdm import tqdm
import io
import tempfile

__author__ = 'Vincenzo Farruggia'
__license__ = 'GPL'
__version_info__ = ('2021', '11', '30')
__version__ = ''.join(__version_info__)

app = Flask(__name__)
DEBUG = 'DEBUG' in os.environ and os.environ['DEBUG'] in ['1', 'true']

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

def dpoDecodeTwo(pathToTmp, pathToJSON):

    r = open(pathToJSON)
    y = json.load(r)

    ext1 = y[0]['iai_dpo_metadata'][0]['file:extension']
    ext2 = y[0]['iai_dpo_metadata'][1]['file:extension']

    if ext1 == 'png' and ext2 == 'png':
        imageName1 = y[0]['iai_dpo_metadata'][0]['id'] + '.dpo'
        imageName2 = y[0]['iai_dpo_metadata'][1]['id'] + '.dpo'

        statusPNG1 = os.system("base64 -d " + pathToTmp + imageName1 + "> " + pathToTmp + "r.png")
        statusPNG2 = os.system("base64 -d " + pathToTmp + imageName2 + "> " + pathToTmp + "7.png")
    elif ext1 == 'jpg' and ext2 == 'jpg':
        imageName1 = y[0]['iai_dpo_metadata'][0]['id'] + '.dpo'
        imageName2 = y[0]['iai_dpo_metadata'][1]['id'] + '.dpo'

        statusPNG1 = os.system("base64 -d " + pathToTmp + imageName1 + "> " + pathToTmp + "r.jpg")
        statusPNG2 = os.system("base64 -d " + pathToTmp + imageName2 + "> " + pathToTmp + "7.jpg")
    else:
        if ext1 == 'mp4' or ext2 == 'mp4':
            videoName1 = y[0]['iai_dpo_metadata'][0]['id'] + '.dpo'
            videoName2 = y[0]['iai_dpo_metadata'][1]['id'] + '.dpo'

            if 'mp4' in ext1:
                videoName = videoName1
            elif 'mp4' in ext2:
                videoName = videoName2
            statusMP4 = os.system("base64 -d " + pathToTmp + videoName + "> " + pathToTmp + "g.mp4")

        if ext1 == 'png' or ext2 == 'png':
            imageName1 = y[0]['iai_dpo_metadata'][0]['id'] + '.dpo'
            imageName2 = y[0]['iai_dpo_metadata'][1]['id'] + '.dpo'

            if 'png' in ext1:
                imageName = imageName1
            elif 'png' in ext2:
                imageName = imageName2

            statusPNG = os.system("base64 -d " + pathToTmp + imageName + "> " + pathToTmp + "r.png")

        if ext1 == 'jpg' or ext2 == 'jpg':
            imageName1 = y[0]['iai_dpo_metadata'][0]['id'] + '.dpo'
            imageName2 = y[0]['iai_dpo_metadata'][1]['id'] + '.dpo'

            if 'jpg' in ext1:
                imageName = imageName1
            elif 'jpg' in ext2:
                imageName = imageName2

            statusJPG = os.system("base64 -d " + pathToTmp + imageName + "> " + pathToTmp + "f.jpg")

        if ext1 == 'bag' or ext2 == 'bag':
            bagName1 = y[0]['iai_dpo_metadata'][0]['id'] + '.dpo'
            bagName2 = y[0]['iai_dpo_metadata'][1]['id'] + '.dpo'

            if 'bag' in ext1:
                bagName = bagName1
            elif 'bag' in ext2:
                bagName = bagName2

            statusBAG = os.system("base64 -d " + pathToTmp + bagName + "> " + pathToTmp + "a.bag")

class SampleAnalytics(AnalyticsAgent):
    def run(self):
        app.logger.info('--- run() started!')
        # Hints:
        # - self.params.iai_files will contains input files to process
        # - self.read_input('dopid') will read input file from datalake
        # - self.write_output('filename', 'content') will write content to datalake

        # do real analytics here
        
        currentPath = os.getcwd()
        pathToTmp   = currentPath + '/tmp/testiai/'
        pathToJSON = pathToTmp + 'faceRecognitionDPO.json'
        pathToJSON2 = pathToTmp + 'faceRecognitionDPO2.json'

        time.sleep(3)

        if self.params.iai_files[0][-4:] == ".jpg" and self.params.iai_files[1][-4:] == ".png" or \
           self.params.iai_files[0][-4:] == ".jpg" and self.params.iai_files[1][-4:] == ".png" or \
           self.params.iai_files[0][-4:] == ".png" and self.params.iai_files[1][-4:] == ".png" or \
           self.params.iai_files[0][-4:] == ".jpg" and self.params.iai_files[1][-4:] == ".jpg":
            content1 = self.params.iai_files[0]
            content2 = self.params.iai_files[1]

            dpoDecodeTwo(pathToTmp, pathToJSON2)

            kous_image = lissilab.load_image_file(pathToTmp + content1)
            kous_face_encoding = lissilab.face_encodings(kous_image)[0]

            test_image = lissilab.load_image_file(pathToTmp + content2)
            test_face_encoding = lissilab.face_encodings(test_image)[0]
            
            plaintext_output = lissilab.compare_faces([kous_face_encoding], test_face_encoding)

        else:
            for infile in self.params.iai_files:
                
                dpoDecodeTwo(pathToTmp, pathToJSON)
                
                app.logger.info('- Processing {}'.format(infile))
                if infile[-4:] == '.png' or infile[-4:] == '.jpg':
                    # contentPNGJPG = self.read_input(infile)
                    contentPNGJPG = os.getcwd()
                    contentPNGJPG = contentPNGJPG + '/tmp/testiai/' + infile
                    app.logger.info('[dump input:{}]: {}'.format(infile, contentPNGJPG))
                elif infile[-4:] == '.mp4' or infile[-4:] == '.avi':
                    # contentMP4AVI = self.read_input(infile)
                    contentMP4AVI = os.getcwd()
                    contentMP4AVI = contentMP4AVI + '/tmp/testiai/' + infile
                    app.logger.info('[dump input:{}]: {}'.format(infile, contentMP4AVI))

                time.sleep(2)

            if contentMP4AVI:
                realFrame = recognise(contentMP4AVI)

                face_locations = lissilab.face_locations(realFrame)

                for face_location in face_locations:
                    (top, right, bottom, left) = face_location

                    face_image = realFrame[top:bottom, left:right]
                    pil_image = Image.fromarray(face_image)
                    # tf1 = tempfile.NamedTemporaryFile(suffix='.py', delete=True)
                    # tf1.write(contentPNGJPG)
                    # tf1.flush()
                    # kous_image = lissilab.load_image_file(tf1.name)
                    kous_image = lissilab.load_image_file(contentPNGJPG)
                    kous_face_encoding = lissilab.face_encodings(kous_image)[0]

                    test_image = np.array(pil_image)
                    test_face_encoding = lissilab.face_encodings(test_image)[0]

                    plaintext_output = lissilab.compare_faces([kous_face_encoding], test_face_encoding)
                    break
            else:
                print("There is an issue in the uploaded video")

        # Because write_output will manage byte streams we need to convert string to
        # bytes content
        plaintext_output = str(plaintext_output[0]).encode('utf-8', 'ignore')
        # plaintext_output = "The ID of the recognized person is ".encode('utf-8','ignore') + plaintext_output + " - server".encode('utf-8','ignore')
        self.write_output('faceRecognitionOutputFile', plaintext_output)
        app.logger.info('--- run() ended!')
        # when analytics finished do callback to server
        success = True
        value = 'Face recognition analytic finished with success!!!'
        results = []
        self.on_finish(success, value, results)

    def end(self):
        app.logger.info('--- Termination request for analytics')
        # insert code here for graceful terminate analytics
        # and after signal IAI for termination
        success = False
        value = 'Face recognition analytic interrupted!!!'
        results = []
        self.on_finish(success, value, results)

@app.route('/startAnalytics', methods=['POST'])
def do_start_analytics():
    payload = request.json
    jsonschema.validate(payload, AnalyticsRequest.SCHEMA)
    app.logger.debug('New request: {}'.format(payload))
    try:
        iai_req = AnalyticsRequest.from_params(payload)
        # Create analytics process object
        process = SampleAnalytics(iai_req)
        analytics_pool = get_analytics_pool()
        # Add analytics process to the pool of running analytics
        analytics_pool.add(process)
        # Start analytics
        process.start()
    #
    # Return 204 (empty response) when the processing doesn't produce output files
    # to be stored into ISI
    # Otherwise return HTTP 200 status with json array containing paths of the
    # files which will be stored into ISI.
    #
    # IMPORTANT: All the files have to be placed inside the datalake provided
    #
        return ('', 204)
    except Exception as e:
        # return (jsonify(['file1.ext', 'file2.ext']), 200)
        app.logger.exception(e)
        return (jsonify({'error': 'Error occured'}), 500)

@app.route('/stopAnalytics', methods=['PUT'])
def do_stop_analytics():
    session_id = request.args.get('session_id')
    try:
        # Retrieve running analytics from pool
        analytics_pool = get_analytics_pool()
        process = analytics_pool.get(session_id)
        # Signal analytics to terminate
        process.terminate()
        analytics_pool.remove(session_id)
        return ('', 204)
    except KeyError:
        return (jsonify({'error': 'Analytics {} not running'.format(session_id)}), 500)
    except Exception as e:
        app.logger.exception(e)
        return (jsonify({'error': 'Error occured'}), 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50000, debug=DEBUG)