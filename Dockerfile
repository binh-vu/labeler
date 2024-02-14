FROM continuumio/anaconda3:2023.09-0

RUN apt update -y && apt install -y tree

WORKDIR /opt

# install nodejs
RUN wget https://nodejs.org/dist/v12.18.1/node-v12.18.1-linux-x64.tar.xz && \
    tar -xf node-v12.18.1-linux-x64.tar.xz && \
    rm node-v12.18.1-linux-x64.tar.xz
ENV PATH="/opt/node-v12.18.1-linux-x64/bin:${PATH}"

# setup jupyter lab and other dependencies
RUN pip install jupyterlab ipywidgets ipyevents ipycallback && \
    jupyter nbextension enable --py widgetsnbextension && \
    jupyter nbextension enable --py --sys-prefix ipyevents && \
    # install requirejs extension
    git clone https://github.com/binh-vu/jupyterlab_requirejs && \
    cd jupyterlab_requirejs && \
    npm install && \
    jupyter labextension install && \
    # enable widgets, ipyevents, and ipycallback
    jupyter labextension install @jupyter-widgets/jupyterlab-manager ipyevents ipycallback

RUN pip install labext

# change the workdir back to root
WORKDIR /

# the labext extension is not installed by default as this image is aim to be a base image
#RUN pip install labext