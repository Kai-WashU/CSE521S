import sys
sys.path.append("..")

import cv2
import dataclasses
import math
import ultralytics
import ultralytics.utils.plotting as yolo_plotting
import ultralytics.engine.results as yolo_results
import internal
import os

MIN_LABEL_SIZE = 200
MAX_IMAGE_QUALITY = 1080 * 720

@dataclasses.dataclass
class Point:
    x: float
    y: float

@dataclasses.dataclass
class BoundingBox:
    top_left: Point
    bottom_right: Point

@dataclasses.dataclass
class InferneceEntry:
    bounds: BoundingBox
    confidence: float

@dataclasses.dataclass
class InferenceResult:
    raw: cv2.Mat
    annotated: cv2.Mat
    labels: dict[str, InferneceEntry]

CONFIDENCE_FACTOR = 0.5

class YoloInference:
    def __init__(self, internal_model: internal.AbstractInternalModel, model_path: str = "yolov8n.pt", webcam_id: int = 0):
        self.model = internal_model
        self.yolo = ultralytics.YOLO(f"rsrc/model/{model_path}")
        self.webcam = cv2.VideoCapture(webcam_id)

    # A blocking call which runs the YOLO inference model on webcam images as fast as possible
    def run(self):
        while True:
            success, image = self.webcam.read()
            if success:
                result = self.process(image)

                detected_objects: list[(str, float)] = []
                for label in result.labels:
                    detected_objects.append((label, result.labels[label].confidence * CONFIDENCE_FACTOR))
                self.model.update(detected_objects)

    def process(self, image: cv2.Mat) -> InferenceResult:
        inferences: list[yolo_results.Results] = self.yolo.predict(image)
        annotated_image = image.copy()
        annotator = yolo_plotting.Annotator(annotated_image)

        # name of label --> (bounds, confidence)
        labels: dict[str, InferneceEntry] = {}

        # Label image and extract identified objects list
        result: yolo_results.Results
        for result in inferences:
            if result.boxes is not None:
                box: yolo_results.Boxes
                for box in result.boxes:
                    # This is a 4-value array defining the top-left and bottom-right corners
                    bounding_box = box.xyxy[0]
                    name = result.names[int(box.cls)]
                    bounds = BoundingBox(Point(float(bounding_box[0]), float(bounding_box[1])),
                                         Point(float(bounding_box[2]), float(bounding_box[3])))

                    # If the label is unique, keep track of it
                    if name not in labels:
                        labels[name] = InferneceEntry(bounds, float(box.conf))
                    else:
                        print(f"Entry for {name}")
                        print(labels[name])
                    # If the label isn't unique, keep the one with the highest confidence
                    if name in labels and box.conf > labels[name].confidence:
                        labels[name] = InferneceEntry(bounds, float(box.conf))

                    # Annotate the image
                    annotator.box_label(bounding_box, f"{name} | {float(box.conf):.2}")
        
        # Resize images for visualization
        [height, width, channels] = image.shape
        target_height = height
        target_width = width
        downscale_factor = 1

        while (target_width * target_height) / (math.pow(downscale_factor, 2)) > MAX_IMAGE_QUALITY:
            downscale_factor *= 1.5
        dimensions = (math.floor(target_width / downscale_factor), math.floor(target_height / downscale_factor))

        downscaled_image = cv2.resize(image, dimensions)
        downscaled_annotation = cv2.resize(annotated_image, dimensions)

        return InferenceResult(downscaled_image, downscaled_annotation, labels)