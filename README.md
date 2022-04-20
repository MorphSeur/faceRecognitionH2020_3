# Face Recognition - E-Corridor - H2020 - Without Encryption
## [server.py](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/facerecognition2/blob/master/server.py)
The version of the IAI-skeleton is 1.1.  
This version of face recognition analytic is without file encrytption.  
For face recogntition analytic with encryption refers to [Face Recognition With Encryption](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/facerecognition)
The face recognition library is integrated with the new trained models - lissilab.  
[server.py](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/facerecognition2/blob/master/server.py) performs real face recognition, saliency detection and face recognition.

To run an example:
- Start the analytic
    ```sh
    $ python server.py
    $ python iai_test_client.py --target http://0.0.0.0:5000 start --datalake ./tmp/testiai k.mp4 7.png
    ```
- Stop the analytic
    ```sh
    $ python python iai_test_client.py --target http://0.0.0.0:5000 stop
    ```

## Requirements
Please refer to [requirements.txt](https://devecorridor.iit.cnr.it/gitlab/kmoulouel/facerecognition2/blob/master/requirements.txt).

## Dockerfile
Dockerfile contains necessary libraries to face recognition analytics.
- To build the docker
    ```
    $ sudo docker build --tag face_recognition .
    ```
- To run the analytic
    ```
    $ sudo docker run --publish 5000:5000 --volume="/path/to/tmp/testiai/:/path/to/tmp/testiai/tmp/testiai/" -v $(pwd):/app face_recognition sh /app/docker-entrypoint.sh
    ```
- To run the analytic with display
    ```
	$ xhost local:face_recognition
	$ sudo docker run -e DISPLAY=$DISPLAY --env="DISPLAY" -v /tmp/.X11-unix:/tmp/.X11-unix face_recognition
    ```