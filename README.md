# Monoses Docker packaging and API server

This is a distribution of [Monoses](https://github.com/artetxem/monoses), an unsupervised Machine Translation system using monolingual corpora only.

It containes everything needed to run trainings and tests (so it contains Moses, fast_align, PyTorch (CPU), VecMap and Phrase2Vec), plus a drop-in HTTP API server that reads the model built by Monoses. All in a self-contained, handy Docker image. 

## Gettint started
1. Create a directory with 2 big files inside (e.g, /it-no/ with it.txt and no.txt inside): these files are your monolingual training corpora.
2. Issue the following (REOMMENDED that you run this in tmux since it will take days):
```
docker run --rm --name train-it-no -v ~/it-no:/it-no aijanai/monoses:3 python3 train.py --src /it-no/no.txt --src-lang sv --trg /it-no/it.txt --trg-lang it --working /it-no/model --threads 49
```
3. When the process has finished, you will have several GBs of files inside your training directory.
4. Launch your translation server with the following:
```
docker run --rm --name translate-it-no -v ~/it-no:/it-no -p 5000:5000 aijanai/monoses:3
```
