import sys
sys.path.append("src")

from src import tooling
from src import iot
from src import cv
from src import internal

print("Running")

writer = tooling.BackendWriter()
internal_model = internal.InternalModel(writer)
yolo_model = cv.YoloInference(internal_model, model_path="beta.pt")
iot_model = iot.ThreeBeaconIoT(internal_model)

iot_model.run()   # non-blocking
yolo_model.run()  # blocking