import cv2
import math
import ultralytics
import ultralytics.utils.plotting as yolo_plotting
import ultralytics.engine.results as yolo_results
import src
import typing

MIN_LABEL_SIZE = 200
MAX_IMAGE_QUALITY = 1080 * 720

class YoloInference(src.AbstractInferenceModel):
    def __init__(self, model_path: str = "yolov8n.pt", dataset: typing.Optional[str] = None, confidence_threshold: float = 0.5):
        self.yolo = ultralytics.YOLO(f"../rsrc/model/{model_path}")
        if dataset is not None:
            self.yolo.train(data=f"../rsrc/model/{dataset}", epochs=100, imgsz=640)
        self.confidence = confidence_threshold

    def process(self, image: cv2.Mat) -> src.InferenceResult:
        inferences: list[yolo_results.Results] = self.yolo.predict(image)
        annotated_image = image.copy()
        annotator = yolo_plotting.Annotator(annotated_image)

        labels: list[str] = []
        bounds: list[src.BoundingBox] = []

        # Label image and extract identified objects list
        result: yolo_results.Results
        for result in inferences:
            if result.boxes is not None:
                box: yolo_results.Boxes
                print("new result")
                for box in result.boxes:
                    # This is a 4-value array defining the top-left and bottom-right corners
                    bounding_box = box.xyxy[0]
                    name = result.names[int(box.cls)]

                    # Save the relevant data
                    labels.append(name)
                    bounds.append(src.BoundingBox(src.Point(float(bounding_box[0]), float(bounding_box[1])),
                                                  src.Point(float(bounding_box[2]), float(bounding_box[3]))))

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

        return src.InferenceResult(downscaled_image, downscaled_annotation, labels, bounds)

    def batched_process(self, images: list[cv2.Mat]) -> src.BatchedInferenceResult:
        pass