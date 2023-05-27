FROM python
ENV WORKDIR=/opt/cv-notifier
WORKDIR $WORKDIR
COPY . .
ARG MODEL=yolov8n.pt
RUN apt-get update && \
    apt-get install -y curl libgl1-mesa-glx libglib2.0-0 libpython3-dev gnupg g++ && \
    apt-get upgrade -y && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install --upgrade pip wheel && \
    pip3 install -r requirements.txt && \
    curl -sL https://github.com/ultralytics/assets/releases/download/v0.0.0/$MODEL -o $MODEL

ENTRYPOINT ["python3", "main.py"]
