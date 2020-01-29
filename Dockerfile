FROM continuumio/miniconda3

RUN apt update && apt install -y git gcc g++ libgoogle-perftools-dev libsparsehash-dev wget vim subversion automake libtool zlib1g-dev libbz2-dev liblzma-dev python-dev graphviz imagemagick make cmake autoconf doxygen libboost-all-dev
RUN git clone https://github.com/artetxem/monoses.git

WORKDIR /monoses
RUN ./get-third-party.sh

WORKDIR /monoses/third-party/moses/
RUN ./bjam -j5
RUN bin/moses --version

WORKDIR /monoses/third-party/fast_align/build
RUN cmake .. && make -j5

WORKDIR /monoses/third-party/phrase2vec/
RUN make -j5
RUN ./word2vec || true

WORKDIR /monoses
RUN conda install pytorch torchvision cpuonly -c pytorch

ENV FLASK_APP=monoses
EXPOSE 5000

COPY Pipfile .
COPY Pipfile.lock .

RUN pip install --upgrade pip && pip install pipenv && pipenv install

COPY . .

CMD ["pipenv", "run", "gunicorn", "--bind", "0.0.0.0:5000", "--log-level=debug", "apiserver:app"]
