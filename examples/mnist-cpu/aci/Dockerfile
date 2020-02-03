FROM tensorflow/tensorflow:1.12.0-py3
WORKDIR /data
ENTRYPOINT ["/bin/bash", "-c", "python mnist.py |& tee log.txt"]