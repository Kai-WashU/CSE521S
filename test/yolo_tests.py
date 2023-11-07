import cv2
import sys
sys.path.insert(0, "..")

import src

test_path = "Test.jpeg"

def image_test():
    print("Starting test")
    model = src.YoloInference(model_path="yolov8n.pt")
    print("Loaded model")
    image = cv2.imread(f"../rsrc/input/{test_path}")
    print("Loaded image")

    result = model.process(image)

    cv2.imshow("Original", result.raw)
    cv2.imshow("Annotated", result.annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    image_test()