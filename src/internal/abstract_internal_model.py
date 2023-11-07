import abc
import dataclasses
import enum

# Our model will prompt the user to first get all items on the table,
# then remove any unnecessary items.
class PromptState(str, enum.Enum):
    MISSING = "MISSING"
    DISTRACTOR = "DISTRACTOR"
    COMPLETE = "COMPLETE"

@dataclasses.dataclass
class ModelState:
    # The list of necessary items that have been acquired
    acquired: list[str, float]
    # The list of distractors on the table
    distractors: list[str, float]
    # The list of missing necessary items
    missing: list[str]
    state: PromptState

class AbstractInternalModel(abc.ABC):
    # Gets called when a data component has new data and updates the internal state
    @abc.abstractmethod
    def update(self, detected_objects: list[str]) -> ModelState:
        pass

    # Returns the current prompt to give the user given the internal state
    @abc.abstractmethod
    def get_prompt(self) -> str:
        pass