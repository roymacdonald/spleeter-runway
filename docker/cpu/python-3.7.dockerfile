FROM python:3.7

RUN apt-get update && apt-get install -y ffmpeg libsndfile
RUN pip install spleeter
RUN mkdir -p /model
ENV MODEL_PATH /model
ENTRYPOINT ["spleeter"]