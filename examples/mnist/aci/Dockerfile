FROM tensorflow/tensorflow:1.12.0-gpu-py3
WORKDIR /data
ENTRYPOINT ["/bin/bash", "-c", "python -c 'mnist.py' |& log.txt"]