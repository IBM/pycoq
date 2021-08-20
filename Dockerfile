FROM ubuntu:20.04

MAINTAINER Vasily Pestun "pestun@ibm.com"

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ssh \
    git \
    opam \
    wget \
    ca-certificates \
    rsync \
    strace

RUN useradd -m bot
WORKDIR /home/bot
USER bot

RUN wget https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh \
  && chmod +x Anaconda3-2020.02-Linux-x86_64.sh \
  && bash Anaconda3-2020.02-Linux-x86_64.sh -b -f
ENV PATH="/home/bot/anaconda3/bin:${PATH}"
RUN conda create -n synthesis python=3.9 -y
ENV PATH="/home/bot/anaconda3/envs/synthesis/bin:${PATH}"

RUN python3.9 -m pip install numpy

ADD https://api.github.com/repos/IBM/pycoq/git/refs/heads/main version.json
RUN git clone https://github.com/IBM/pycoq.git

RUN python3.9 -m pip install -e pycoq
RUN pytest pycoq/pycoq/tests
