import json
import logging
from flask import Flask, request, make_response

# Flask app setup
app = Flask(__name__, instance_relative_config=True)
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

@app.route("/translate")
def translate():
    q = request.args.get("q")
    source = request.args.get("source")
    target = request.args.get("target")

    result = {"data": {"translations": [{"translatedText": q, "sentence_confidence": 1.0}]}}
    
    res = make_response(json.dumps(result))
    res.mimetype = "application/json"

    return res

