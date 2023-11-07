import abc
import cv2
import dataclasses

@dataclasses.dataclass
class Point:
    x: float
    y: float

@dataclasses.dataclass
class BoundingBox:
    top_left: Point
    bottom_right: Point

@dataclasses.dataclass
class InferenceResult:
    raw: cv2.Mat
    annotated: cv2.Mat
    labels: list[str]
    boxes: list[BoundingBox]

@dataclasses.dataclass
class BatchedInferenceResult:
    results: InferenceResult

class AbstractInferenceModel(abc.ABC):
    # Given an image, return the inference results
    @abc.abstractmethod
    def process(self, image: cv2.Mat) -> InferenceResult:
        pass

    # Given a list of images, return the inference results
    @abc.abstractmethod
    def batched_process(self, images: list[cv2.Mat]) -> BatchedInferenceResult:
        pass