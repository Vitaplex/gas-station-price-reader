import base64
import json
import os
import numpy as np
import cv2
from flask import Flask, request, jsonify, render_template

from imageProcessing import ImageProcessing

app = Flask(__name__)

MODEL_PATH = os.path.abspath(os.path.join(os.path.curdir, "test-model", "best.pt"))

processor = ImageProcessing(MODEL_PATH)

@app.route("/predict", methods=["POST"])
def predict():
    file = request.get_data()
    if not file:
        return jsonify({"error": "No file provided"}), 400

    data_str = file.decode()
    
    header, encoded = data_str.split(",", 1)
    nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return jsonify({"error": "Invalid image"}), 400

    results = processor.process_image(image, show=False)

    return jsonify({"detections": results})

@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)