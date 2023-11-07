import abc
import cv2

class AbstractImageSupplier(abc.ABC):
    # A blocking method which gets the next image.
    @abc.abstractmethod
    def supply(self) -> cv2.Mat:
        pass