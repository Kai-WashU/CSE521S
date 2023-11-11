import abc
import dataclasses

@dataclasses.dataclass
class ItemData:
    confidence_score: float
    valid: bool

@dataclasses.dataclass
class ModelState:
    # Acquired items
    acquired: dict[str, ItemData]
    # Distractors on the table
    distractors: dict[str, ItemData]
    # The list of missing necessary items
    missing: set[str]

REQUIRED_ITEMS: set[str] = {
    "oatmeal",
    "salt",
    "measuring_cup",
    "measuring_cup_1-2",
    "measuring_cup_1-4",
    "pan",
    "stirring_spoon",
    "timer",
    "bowl",
    "metal_spoon",
    "hot_pad"
}

class AbstractInternalModel(abc.ABC):
    # Gets called when a data component has new data and updates the internal state
    @abc.abstractmethod
    def update(self, detected_objects: list[(str, float)]) -> ModelState:
        pass