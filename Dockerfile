FROM continuumio/miniconda3

# install build deps
RUN apt update && apt install -y git gcc g++ libgoogle-perftools-dev libsparsehash-dev wget vim subversion automake libtool zlib1g-dev libbz2-dev liblzma-dev python-dev graphviz imagemagick make cmake autoconf doxygen libboost-all-dev libxmlrpc-c++8-dev libxmlrpc-c++8v5 libxmlrpc-core-c3 libxmlrpc-core-c3-dev xmlrpc-api-utils

RUN git clone https://github.com/artetxem/monoses.git

WORKDIR /monoses
RUN ./get-third-party.sh

WORKDIR /monoses/third-party/fast_align/build
RUN cmake .. && make -j50

WORKDIR /monoses/third-party/phrase2vec/
RUN make -j50

WORKDIR /monoses/third-party/
RUN git clone https://github.com/zvelo/cmph.git
WORKDIR /monoses/third-party/cmph
RUN ./configure && make -j50 && make install

WORKDIR /monoses/third-party/
RUN git clone https://github.com/moses-smt/salm.git
WORKDIR /monoses/third-party/salm/Distribution/Linux
RUN make -j50

WORKDIR /monoses/third-party/moses/contrib/sigtest-filter/
RUN make SALMDIR=/monoses/third-party/salm -j50

WORKDIR /monoses/third-party/moses/
RUN ./bjam -j50 --with-cmph=/usr/local/lib --with-xmlrpc-c=/usr/

WORKDIR /monoses
RUN conda install pytorch torchvision cpuonly -c pytorch

ENV FLASK_APP=monoses
EXPOSE 5000

COPY Pipfile .
COPY Pipfile.lock .

RUN pip install --upgrade pip && pip install pipenv && pipenv install

COPY . .

CMD ["pipenv", "run", "gunicorn", "--bind", "0.0.0.0:5000", "--log-level=info", "--timeout", "120", "apiserver:app"]
