
FROM nvcr.io/nvidia/pytorch:22.01-py3

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN apt -yqq update

RUN apt install -yqq python3-pip software-properties-common wget ffmpeg

RUN mkdir -p /root/.torch/models

RUN mkdir -p /data/{models,upload,result_images}

RUN wget -O /root/.torch/models/vgg16_bn-6c64b313.pth https://download.pytorch.org/models/vgg16_bn-6c64b313.pth

RUN wget -O /root/.torch/models/resnet34-333f7ec4.pth https://download.pytorch.org/models/resnet34-333f7ec4.pth

ADD . /data/

WORKDIR /data

RUN pip install -r requirements.txt

ENV RENDER_FACTOR 30

ENV BOT_TOKEN ""


ENTRYPOINT ["python3"]

CMD ["app.py"]

