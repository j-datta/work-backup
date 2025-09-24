FROM ubuntu:20.04

ARG USER_ID
ARG GROUP_ID

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq && \
    apt-get install -y -qq \
    build-essential \
    libboost-all-dev \
    cmake \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    python3.8 \
    python3-pip \
    wget \
    jq \
    zip \
    git \
    passwd \
    && rm -rf /var/lib/apt/lists/*

RUN python3.8 -m pip install --upgrade pip && \
    python3.8 -m pip install nltk spacy sentencepiece transformers && \
    python3.8 -m spacy download de_core_news_sm

RUN wget https://github.com/kpu/kenlm/archive/master.zip -O master.zip && \
    unzip master.zip && \
    rm master.zip && \
    cd kenlm-master && \
    mkdir -p build && \
    cd build && \
    cmake .. && \
    make -j 4

RUN rm -rf /root/.cache

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -g $GROUP_ID user && \
    mkdir -p /app/data && \
    chown -R user:user /app && \
    chmod -R 755 /app && \
    chmod -R 777 /app/data

WORKDIR /app

USER user
