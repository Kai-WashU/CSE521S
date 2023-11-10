import abc
import dataclasses
import enum

@dataclasses.dataclass
class ModelState:
    # The list of necessary items that have been acquired
    acquired: list[str, float, bool]
    # The list of distractors on the table
    distractors: list[str, float, bool]
    # The list of missing necessary items
    missing: list[str]

class AbstractInternalModel(abc.ABC):
    # Gets called when a data component has new data and updates the internal state
    @abc.abstractmethod
    def update(self, detected_objects: list[str, int]) -> ModelState:
        pass

    # Returns the current prompt to give the user given the internal state
    @abc.abstractmethod
    def get_prompt(self) -> str:
        pass