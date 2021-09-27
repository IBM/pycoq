FROM ubuntu:20.04

MAINTAINER Vasily Pestun "pestun@ihes.fr"

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ssh \
    git \
    m4 \
    libgmp-dev \
    opam \
    wget \
    ca-certificates \
    rsync \
    strace

RUN useradd -m bot
WORKDIR /home/bot
USER bot

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
  && sh Miniconda3-latest-Linux-x86_64.sh -b -f
ENV PATH="/home/bot/miniconda3/bin:${PATH}"
RUN conda create -n pycoq python=3.9 -y
ENV PATH="/home/bot/miniconda3/envs/pycoq/bin:${PATH}"

ADD https://api.github.com/repos/IBM/pycoq/git/refs/heads/main version.json

RUN pip install pycoq
RUN pytest --pyargs pycoq
