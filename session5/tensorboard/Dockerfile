FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
python3 \
python3-pip

RUN python3 -m pip --no-cache-dir install --upgrade \
"pip>=20.3" \
setuptools

RUN python3 -m pip install --no-cache-dir \
jupyterlab \
matplotlib \
pandas \
torch \
torchvision \
tensorboard \
scipy \
imutils \
opencv-python \
tqdm \
kaggle

RUN apt-get install -y --no-install-recommends \
zip \
unzip \
wget \
git \
libgl1-mesa-glx

EXPOSE 8888

ENV NB_PREFIX /

CMD ["bash","-c", "jupyter lab --notebook-dir=/home/jovyan --ip=0.0.0.0 --no-browser --allow-root --port=8888 --NotebookApp.token='' --NotebookApp.password='' --NotebookApp.allow_origin='*' --NotebookApp.base_url=${NB_PREFIX}"]
