import json
import logging
from flask import Flask, request, make_response
import sys
import tempfile
import os
import subprocess

MOSES = '/monoses/third-party/moses'

# Flask app setup
app = Flask(__name__, instance_relative_config=True)
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

if os.environ.get("MODEL") is None or len(os.environ.get("MODEL").strip()) == 0:
    app.logger.fatal("MODEL env var is not set: can't read model to perform translations")
    sys.exit(4)

@app.route("/coffee")
def coffee():
    """A joke for service liveness"""
    return '', 418

@app.route("/translate")
def translate():
    result = None

    # parse input
    q = request.args.get("q")
    source = request.args.get("source")
    target = request.args.get("target")

    # stash query in a temporary file since Moses can only read files (-_-)'
    temp = tempfile.NamedTemporaryFile(mode='w+t')
    temp.write(q)
    temp.seek(0)
    input_file = temp.name

    # compose input params
    params = {"src": source, "trg": target, "model": os.environ.get("MODEL").strip(), "threads": 20, "reverse": False, "tok": False, "input_file": input_file}

    try:
        # invoke moses
        output_string = _call_moses_fullchain(params).strip()
	
        app.logger.info(output_string)

        # evenlope response in DTO
        result = {"data": {"translations": [{"translatedText": output_string, "sentence_confidence": 1.0}]}}
    
    finally:
        temp.close()

        # prepare response
        res = make_response(json.dumps(result))
        res.mimetype = "application/json"

    return res

def _call_moses_fullchain(args):

    # set options
    direction = 'trg2src' if args['reverse'] else 'src2trg'
    detok = '' if args['tok'] else ' | ' + MOSES + '/scripts/tokenizer/detokenizer.perl' + ' -q -l ' + args['trg']

    # compose command
    command = MOSES + '/scripts/tokenizer/tokenizer.perl -l ' + args['src'] + ' -threads ' + str(args['threads']) + ' < ' + args['input_file'] + ' | ' + MOSES + '/scripts/recaser/truecase.perl --model ' + args['model'] + '/step1/truecase-model.' + direction[:3] + ' | ' + MOSES + '/bin/moses2 -f ' + args['model'] + '/' + direction + '.moses.ini --threads ' + str(args['threads']) + ' | ' + MOSES + '/scripts/recaser/detruecase.perl' + detok + ' > ' + args['input_file'] + "_output"

    # log command
    app.logger.info(command)

    # execute command
    subprocess.run(command, shell=True)

    # read output
    output_file_name = args['input_file'] + '_output'
    output_file = open(output_file_name, 'r')
    output_string = output_file.read()
    output_file.close()
    os.unlink(output_file_name)

    return output_string
