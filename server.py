# -*- coding: utf-8 -*-

import os
from flask import Flask, jsonify, request
import json
import jsonschema
from iai_toolbox import AnalyticsRequest, AnalyticsAgent, get_analytics_pool
import time
import lissilab
from PIL import Image
import numpy as np
import time

from mainUtilities import *

__author__ = 'Vincenzo Farruggia'
__license__ = 'GPL'
__version_info__ = ('2021', '11', '30')
__version__ = ''.join(__version_info__)

app = Flask(__name__)
DEBUG = 'DEBUG' in os.environ and os.environ['DEBUG'] in ['1', 'true']

class SampleAnalytics(AnalyticsAgent):
    def run(self):
        app.logger.info('--- run() started!')

        dpoInfo = request.json
        dpoInfo = json.loads(json.dumps(dpoInfo))
        pathToTmp = dpoInfo['iai_datalake']

        dpoDecodeTwo(dpoInfo, pathToTmp)

        time.sleep(3)

        fileList = []
        fileListExt = []
        fileListJPGPNG = []

        for element in os.listdir(pathToTmp):
            file = os.path.join(pathToTmp, element)
            if os.path.isfile(file):
                fileList.append(file)
                fileListExt.append(file[-4:])

        counting = {i:fileListExt.count(i) for i in fileListExt}

        if ".mp4" in fileListExt:
            if counting[".mp4"]:
                for fileElement in fileList:
                    if fileElement[-4:] == '.png' or fileElement[-4:] == '.jpg':
                        contentPNGJPG = fileElement
                        app.logger.info('[dump input:{}]: {}'.format(fileElement, contentPNGJPG))
                    elif fileElement[-4:] == '.mp4' or fileElement[-4:] == '.avi':
                        contentMP4AVI = fileElement
                        app.logger.info('[dump input:{}]: {}'.format(fileElement, contentMP4AVI))

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
            for fileElement in fileList:
                if fileElement[-4:] == '.png':
                    fileListJPGPNG.append(fileElement)
                elif fileElement[-4:] == '.jpg':
                    fileListJPGPNG.append(fileElement)

            content1 = fileListJPGPNG[0]
            app.logger.info('[dump input:{}]: {}'.format(fileElement, content1))

            content2 = fileListJPGPNG[1]
            app.logger.info('[dump input:{}]: {}'.format(fileElement, content2))

            kous_image = lissilab.load_image_file(content1)
            kous_face_encoding = lissilab.face_encodings(kous_image)[0]

            test_image = lissilab.load_image_file(content2)
            test_face_encoding = lissilab.face_encodings(test_image)[0]
            
            plaintext_output = lissilab.compare_faces([kous_face_encoding], test_face_encoding)
        
        dictionary = {
            "passengerID": "pdgID001",
            "recognized": str(plaintext_output[0])
        }

        # Because write_output will manage byte streams we need to convert string to
        # bytes content
        plaintext_output = str(dictionary).encode('utf-8', 'ignore')
        # plaintext_output = "The ID of the recognized person is ".encode('utf-8','ignore') + plaintext_output + " - server".encode('utf-8','ignore')
        self.write_output('faceRecognitionOutputFile', plaintext_output)
        app.logger.info('--- run() ended!')
        # when analytics finished do callback to server
        success = True
        value = 'Face recognition analytic finished with success!!!'
        results = [dictionary]
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
    app.run(host='0.0.0.0', port=5001, debug=DEBUG)