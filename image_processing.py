import sys
print("PYTHON:", sys.executable)

import cv2
print("CV2:", cv2.__file__)

import base64

import easyocr
import numpy as np
from ultralytics import YOLO


class ImageProcessing:
    def __init__(self, model_path:str, lang:list[str]):
        self.model = YOLO(model_path)
        self.reader = easyocr.Reader(lang)

    def process_image(self, image, show=False):
        if image is None:
            raise ValueError(f"Could not load image: {image}")

        results = self.model(image)

        detections = []

        for result in results:
            boxes = result.boxes

            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                # Only process price rows (adjust if needed)
                if cls_id != 0:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                crop = image[y1:y2, x1:x2]

                # Preprocessing (optional)
                gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

                ocr_results = self.reader.readtext(thresh)

                extracted_texts = []
                for (bbox, text, ocr_conf) in ocr_results:
                    extracted_texts.append({
                        "text": text,
                        "confidence": ocr_conf
                    })

                detections.append({
                    "class_id": cls_id,
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2],
                    "ocr": extracted_texts
                })

                # Show crop if needed
                if show:
                    cv2.imshow("crop", crop)
                    cv2.waitKey(0)

        if show:
            cv2.destroyAllWindows()
        return detections
    
    def load_image(self, image:bytes):
        data_str = image.decode()
        
        header, encoded = data_str.split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return image