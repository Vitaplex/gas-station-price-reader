import json
import os
import numpy as np
from flask import Flask, request, jsonify, render_template

from src.exif_extractor import get_coords
from src.detection import DetectionEncoder
from src.dataset_class_fetcher import DatasetClassFetcher
from src.image_processing import ImageProcessing
from src.station_mapper import StationMapper
from src.image_converter import ImageConverter
from src.output_formatter import OutputFormatter

LABELS_MODEL_PATH = os.path.abspath(os.path.join(os.path.curdir, "test-model", "labels.pt"))
DIGITS_MODEL_PATH = os.path.abspath(os.path.join(os.path.curdir, "test-model", "digits.pt"))
CLASS_PATH = os.path.abspath(os.path.join(os.path.curdir, "..", "dataset","data.yaml"))
STATION_SOURCE = "https://drivstoffpriser.github.io/Drivstoffpriser-App/data/stations.json"
JVINSNES_STATION_SOURCE = "https://ssh.guttespinat.no/api/files/cat?path=%2Fstations.json&share=7kGsCbm"

class_fetcher = None
image_processor = None
image_converter = None
station_mapper = None
jvinsnes_station_mapper = None
output_formatter = None

app = Flask(__name__)

@app.route("/parse-gas-station-picture", methods=["POST"])
def parse_gas_station():
    image_raw = request.get_data()
    if not image_raw:
        return jsonify({"error": "No image provided"}), 400
    
    image = image_converter.get_image_bytes(image_raw)
    jpg_image = image_converter.convert_to_jpg(image)
    
    print("converted to jpeg...")
    
    coordinates = request.headers.get("User-Coordinates")

    if coordinates == None or coordinates == "0, 0":
        coordinates = get_coords(jpg_image)
    print(coordinates)
      
    station = station_mapper.map_coordinates_to_station(coordinates)
    if station != None:
        print(f"Found station: {json.dumps(station)}")

    cv2_image = image_converter.convert_to_cv2_image(jpg_image)
    
    detections = image_processor.detect_labels(cv2_image)
    grouped_results = image_processor.group_detections(detections)
    textResults = image_processor.extract_text(grouped_results, cv2_image)
    
    raw_json = {
        "station": station,
        "detection_results": textResults
    }
    
    output_format = request.args.get('format')
    annotated_image = request.args.get('annotate')

    processed_item = output_formatter.format(raw_json, output_format)

    jsonResponse = json.dumps(processed_item, cls=DetectionEncoder)

    return jsonResponse


@app.route("/get-as-jpg", methods=["POST"])
def get_as_jpg():
    image_raw = request.get_data()
    image = image_converter.get_image_bytes(image_raw)
    return image_converter.convert_to_jpg(image)


@app.route("/class-id", methods=["GET"])
def class_ids():
    return class_fetcher.get_classes()


@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        class_fetcher = DatasetClassFetcher(CLASS_PATH)
        image_processor = ImageProcessing(LABELS_MODEL_PATH, DIGITS_MODEL_PATH, ['en'])
        image_converter = ImageConverter()
        station_mapper = StationMapper(STATION_SOURCE, 360)
        jvinsnes_station_mapper = StationMapper(JVINSNES_STATION_SOURCE, 360)
        output_formatter = OutputFormatter(station_mapper, jvinsnes_station_mapper)

    app.run(host="0.0.0.0", port=5000, debug=True)