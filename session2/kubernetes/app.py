import os
import numpy as np

from flask import Flask, request, jsonify
from model.inference import Model


app = Flask(__name__)
model = Model()


@app.route("/api/v1/healthcheck", methods = ["GET"])
def healthcheck():
    return jsonify({"status": "ok"})


@app.route("/api/v1/readiness_check", methods = ["GET"])
def readiness_check():
    # TODO: edit code start
    probs = model(['i love you to the moon and back'])[0]
    assert model.labels[np.argmax(probs)] == "POS"
    # TODO: edit code end
    return jsonify({"status": "ok"})


@app.route("/api/v1/predict", methods = ["POST"])
def predict():
    payload = request.json
    # TODO: edit code start
    probs = model(payload["prompts"])
    label_probs = [dict(zip(model.labels, x.tolist())) for x in probs]
    # TODO: edit code end
    return jsonify(label_probs)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=(os.environ['LOG_LEVEL'] == 'DEBUG'))
