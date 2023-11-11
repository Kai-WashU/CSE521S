import src

writer = src.BackendWriter()
internal = src.InternalModel(writer)
yolo = src.YoloInference(internal)
iot = src.ThreeBeaconIoT(internal)

iot.run()   # non-blocking
yolo.run()  # blocking