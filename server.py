import os
import numpy as np
from flask import Flask, request, jsonify, render_template

from dataset_class_fetcher import DatasetClassFetcher
from image_processing import ImageProcessing


MODEL_PATH = os.path.abspath(os.path.join(os.path.curdir, "test-model", "best.pt"))
CLASS_PATH = os.path.abspath(os.path.join(os.path.curdir, "..", "dataset","data.yaml"))

class_fetcher = DatasetClassFetcher(CLASS_PATH)
processor = ImageProcessing(MODEL_PATH, ['en'])

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    imageRaw = request.get_data()
    if not imageRaw:
        return jsonify({"error": "No image provided"}), 400

    image = processor.load_image(imageRaw)

    if image is None:
        return jsonify({"error": "Invalid image"}), 400

    results = processor.process_image(image, show=False)

    return jsonify({"detections": results})

@app.route("/class-id", methods=["GET"])
def class_ids():
    return class_fetcher.get_classes()

@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)