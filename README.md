# Face Recognition - E-Corridor - H2020 - Without Encryption - DPO Decoding
## [server.py](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/facerecognition2/blob/11082022/server.py)
The version of the IAI-skeleton is 1.1.  
This version of face recognition analytic is without file encryption.  
For face recogntition analytic with encryption refers to [Face Recognition With Encryption](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/facerecognition).  
The face recognition library is integrated with the new trained models - lissilab.  
[server.py](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/facerecognition2/blob/11082022/server.py) performs decoding of .dpo files, real face recognition, saliency detection and face recognition for both RGB and RGB-D cameras.

To run an example:
- Start the analytic server:
    ```sh
    $ python server.py
    ```
- Querying the server when using RGB Camera (Without [Real Face Extraction DMO](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/realfaceextractiondmo), i.e., the server exploits a video and an a groundtruth image):
    ```sh
    $ python iai_test_client.py --target http://0.0.0.0:50000 start --datalake ./tmp/testiai g.mp4 r.png
    ```
- Querying the server when using RGB-D Camera (With [Real Face Extraction DMO](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/realfaceextractiondmo), i.e., the server exploits the DMO image and a groundtruth image):
    ```sh
    $ python iai_test_client.py --target http://0.0.0.0:50000 start --datalake ./tmp/testiai r.png 7.png
    ```
- Stop the analytic:
    ```sh
    $ python iai_test_client.py --target http://0.0.0.0:50000 stop
    ```

## Requirements
- Please refer to [requirements.txt](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/facerecognition2/blob/11082022/requirements.txt).
- Python 3.7.7 was used.  
- Set path to .dpo json on lines [157](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/facerecognition2/blob/11082022/server.py#L157) and [158](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/facerecognition2/blob/11082022/server.py#L157) of [server.py](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/facerecognition2/blob/11082022/server.py) (To decode the .dpo files).

## Dockerfile
Dockerfile contains necessary libraries to face recognition analytic.
- To build the docker
    ```
    $ sudo docker build --tag face_recognition .
    ```
- To run the analytic
    ```
    $ sudo docker run --publish 50000:50000 --volume="/path/to/tmp/testiai/:/path/to/tmp/testiai/tmp/testiai/" -v $(pwd):/app face_recognition sh /app/docker-entrypoint.sh
    ```
- To run the analytic with display
    ```
	$ xhost local:face_recognition
	$ sudo docker run -e DISPLAY=$DISPLAY --env="DISPLAY" -v /tmp/.X11-unix:/tmp/.X11-unix face_recognition
    ```