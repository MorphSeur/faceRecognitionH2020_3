# Face Recognition - E-Corridor - H2020 - Without Encryption - DPO Decoding
## [server.py](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/facerecognition2/blob/23092022/server.py)
The version of the [IAI-skeleton is 1.4.1](https://devecorridor.iit.cnr.it/gitlab/dalbanese/iai-skeleton/-/tree/v1.4.1).    
The face recognition library is integrated with the new trained models - lissilab.  
[server.py](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/facerecognition2/blob/23092022/server.py) performs decoding of .dpo files, real face recognition, saliency detection and face recognition for both RGB and RGB-D cameras.

To run an example:
- Start the analytic server:
    ```sh
    $ python server.py
    ```
- Querying the server when using RGB Camera (Without [Real Face Extraction DMO](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/realfaceextractiondmo), i.e., the server exploits a video and an a groundtruth image) or when using RGB-D Camera (With [Real Face Extraction DMO](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/realfaceextractiondmo), i.e., the server exploits the DMO image and a groundtruth image):
    ```sh
    $ python iai_test_client.py --target http://0.0.0.0:5001 start
    ```
- Stop the analytic:
    ```sh
    $ python iai_test_client.py --target http://0.0.0.0:5001 stop
    ```

## Requirements
- Please refer to [requirements.txt](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/facerecognition2/blob/20230325/requirements.txt).
- Python 3.7.7 was used.

## Dockerfile
Dockerfile contains necessary libraries to face recognition analytic.
- To build the docker
    ```
    $ sudo docker build --tag face_recognition .
    ```
- To run the analytic
    ```
    $ sudo docker run --publish 5001:5001 --volume="/path/to/tmp/testiai/:/app/" face_recognition sh docker-entrypoint.sh
    ```
- To run the analytic with display
    ```
	$ xhost local:face_recognition
	$ sudo docker run -e DISPLAY=$DISPLAY --env="DISPLAY" -v /tmp/.X11-unix:/tmp/.X11-unix face_recognition
    ```