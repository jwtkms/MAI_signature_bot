FROM python:3.10
ADD app.py /opt/api/
ADD model.py /opt/api/
ADD train_yolo.ipynb /opt/api/
ADD yolov8m.pt /opt/api/

COPY requirements.txt /opt/api/requirements.txt
WORKDIR /opt/api
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
EXPOSE 7860
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY . /opt/api
ADD Docs /opt/api/Docs
ADD Predicts /opt/api/Predicts
ADD Signatures /opt/api/Signatures
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y



CMD ["python", "/opt/api/app.py"] 