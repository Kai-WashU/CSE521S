import sys
sys.path.append("..")

import threading
from . import abstract_internal_model
import tooling
import time

ENABLE_THRESHOLD = 50
DISABLE_THRESHOLD = 30
MAX_SCORE = 100
DECAY_FACTOR = 1

class InternalModel(abstract_internal_model.AbstractInternalModel):
    def __init__(self, backend_writer: tooling.BackendWriter):
        self.backend_writer = backend_writer

        self.state: abstract_internal_model.ModelState = abstract_internal_model.ModelState({}, {}, abstract_internal_model.REQUIRED_ITEMS)
        self.lock = threading.Lock()

        self.entry_num = -1

    def reevaluate_entries(self, entries: dict[str, abstract_internal_model.ItemData]) -> list[str]:
        removed_entries: list[str] = []
        current_time = time.time()

        for name in entries:
            # Decay the value
            entries[name].confidence_score -= (current_time - entries[name].last_updated) * DECAY_FACTOR
            entries[name].last_updated = current_time

            # If the entry is valid
            if entries[name].valid:
                # Check if it should be disabled
                if entries[name].confidence_score < DISABLE_THRESHOLD:
                    entries[name].valid = False
                # Check if the score needs to be clamped
                elif entries[name].confidence_score > MAX_SCORE:
                    entries[name].confidence_score = MAX_SCORE
            # If the entry isn't valid
            else:
                # Check if it should be enabled
                if entries[name].confidence_score > ENABLE_THRESHOLD:
                    entries[name].valid = True
                # Check if it should be removed
                elif entries[name].confidence_score < 0:
                    removed_entries.append(name)
        
        return removed_entries

    def update(self, detected_objects: list[(str, float)]) -> abstract_internal_model.ModelState:
        with self.lock:            
            # Apply confidence deltas
            for (name, confidence_delta) in detected_objects:
                # If the item is already in the acquired list, update the confidence score
                if name in self.state.acquired:
                    self.state.acquired[name].confidence_score += confidence_delta
                    # TODO: Decay
                # If the item is already in the distractor list, update the confidence score
                elif name in self.state.distractors:
                    self.state.distractors[name].confidence_score += confidence_delta
                    # TODO: Decay
                # If the confidence delta is positive, we create a new entry
                elif confidence_delta > 0:
                    # If the item was in the missing list, remove it and create a new entry in the acquired list
                    if name in self.state.missing:
                        self.state.acquired[name] = abstract_internal_model.ItemData(confidence_delta, False, time.time())
                        self.state.missing.remove(name)
                    # Otherwise, it is a new distractor
                    else:
                        self.state.distractors[name] = abstract_internal_model.ItemData(confidence_delta, False, time.time())
            
            # Update flags/remove entries
            for name in self.reevaluate_entries(self.state.acquired):
                del self.state.acquired[name]
                self.state.missing.add(name)
            for name in self.reevaluate_entries(self.state.distractors):
                del self.state.distractors[name]
            self.entry_num += 1

            # Send the new state to the writer
            self.backend_writer.write_data(self.state, self.entry_num)