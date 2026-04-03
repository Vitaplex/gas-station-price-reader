import easyocr
import numpy as np
from ultralytics import YOLO
from src.detection import Detection

class ImageProcessing:
    def __init__(self, object_model_path:str, digit_model_path:str, lang:list[str]):
        self.object_model = YOLO(object_model_path)
        self.digit_model = YOLO(digit_model_path)
        self.reader = easyocr.Reader(lang)

    def detect_labels(self, image) -> list[Detection]:
        results = self.object_model(image)
        return self.process_detection_results(results)

    def detect_digits(self, image) -> list[Detection]:
        results = self.digit_model(image)
        return self.process_detection_results(results)

    def group_detections(self, detections:list[Detection]):
        # Group detections by class_id, then the horizontal alignment of the bounding boxes
        price_rows_centered = [crop_and_center_detections(detection) for detection in detections if detection.class_id == 0]
        fuel_type_rows = [crop_and_center_detections(d) for d in detections if d.class_id not in [0, 1]]
        
        # List with the price rows and None for filling in the matching fuel_type_rows
        grouped = [[(det, center), None] for det, center in price_rows_centered]

        for fuel_det, fuel_center in fuel_type_rows:
            # Find closest price row by Y distance
            best_idx = find_closest_entry(fuel_center, price_rows_centered)
            if best_idx is None: continue

            grouped[best_idx][1] = fuel_det

        return grouped

    def extract_text(self, grouped_results, cv2_image):
        results_with_text = []

        for price_row, fuel_type in grouped_results:
            detection, center = price_row

            x1, y1, x2, y2 = detection.bbox
            crop = cv2_image[y1:y2, x1:x2]

            result = self.reader.readtext(crop)[0]
            _, text, _ = result
            text_clean = self.clean_text(text)
            new_price_row = price_row + (text_clean,)
            results_with_text.append((new_price_row, fuel_type))

        return results_with_text

    def clean_text(self, text:str):
        text = do_replaces(text)
        text = [it for it in text if it not in ['',' ']]
        text = text[:4]
        return f"{''.join(text[:2])}.{''.join(text[2:4])}" if len(text) >= 4 else ''.join(text)

    def process_detection_results(self, results):
        detections = []

        for result in results:
            boxes = result.boxes

            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                name = result.names.get(cls_id)

                detections.append(Detection(cls_id,name,conf,[x1, y1, x2, y2]))
        return detections


def find_closest_entry(reference, detection):
    if len(detection) == 0: return
    return min(
        range(len(detection)),
        key=lambda i: abs(reference - detection[i][1])
    )

# Helpers
def crop_and_center_detections(detection:Detection):
    x1, y1, x2, y2 = detection.bbox
    center = (y1 + y2) / 2
    return detection, center

def process_text(text):
    return text


def do_replaces(text:str):
    return (text
            .replace("e","2")
            .replace("s","5")
            .replace("I","1")
            .replace("i","1")
            .replace("F","2")
            .replace("o","0")
            .replace("O","0")
            .replace("c","5")
            .replace("E","2")
            .replace("p","2")
            .replace("[","1")
        )