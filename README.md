# Monoses Docker packaging and API server

This is a distribution of [Monoses](https://github.com/artetxem/monoses), an unsupervised Machine Translation system using monolingual corpora only.

It containes everything needed to run trainings and tests (so it contains Moses, fast_align, PyTorch (CPU), VecMap and Phrase2Vec), plus a drop-in HTTP API server that reads the model built by Monoses. All in a self-contained, handy Docker image. 

## Building
This is just an addon for a proper Monoses installation, it won't work alone. 
*Please build the Docker image, it will supply everything*:

```
docker build -t aijanai/monoses .
```

## Getting started
1. Create a directory with 2 big files inside (e.g, /it-no/ with it.txt and no.txt inside): these files are your monolingual training corpora.
2. Issue the following (RECOMMENDED that you run this in tmux since it will take _days_):
```
docker run --rm --name train-it-no -v ~/it-no:/it-no aijanai/monoses:3 python3 train.py --src /it-no/no.txt --src-lang sv --trg /it-no/it.txt --trg-lang it --working /it-no/model --threads 49
```
3. When the process has finished, you will have several GBs of files inside your training directory.
4. Launch your translation server with the following (point environment variable MODEL to the directory containing the steps and the ini files):
```
docker run --rm --name translate-it-no -v ~/it-no:/it-no -e MODEL=/it-no/model -p 5000:5000 aijanai/monoses:3
```
5. Now query your server with the following:
```
curl "130.61.252.183:5000/translate?q=Ulver&source=sv&target=it"
```
Queries are rather slow (~ 4 seconds each) since the model is loaded in RAM every time, but works.
