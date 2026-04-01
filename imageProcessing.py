import cv2
import easyocr
from ultralytics import YOLO


class ImageProcessing:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.reader = easyocr.Reader(['en'])

    def process_image(self, image_path, show=False):
        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(f"Could not load image: {image_path}")

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