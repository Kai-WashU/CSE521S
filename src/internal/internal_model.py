import src
import threading

ENABLE_THRESHOLD = 70
DISABLE_THRESHOLD = 50
MAX_SCORE = 100

class InternalModel(src.AbstractInferenceModel):
    def __init__(self, backend_writer: src.BackendWriter):
        self.backend_writer = backend_writer

        self.state: src.ModelState = src.ModelState({}, {}, src.REQUIRED_ITEMS)
        self.lock = threading.Lock()

        self.entry_num = -1

    def reevaluate_entries(self, entries: dict[str, src.ItemData]) -> list[str]:
        removed_entries: list[str] = []

        for name in entries:
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
                    del entries[name]
                    removed_entries.append(name)
        
        return removed_entries

    def update(self, detected_objects: list[(str, float)]) -> src.ModelState:
        with self.lock:            
            for (name, confidence_delta) in detected_objects:
                # If the item is already in the acquired list, update the confidence score
                if name in self.state.acquired:
                    self.state.acquired[name].confidence_score += confidence_delta
                # If the item is already in the distractor list, update the confidence score
                elif name in self.state.distractors:
                    self.state.distractors[name].confidence_score += confidence_delta
                # If the confidence delta is positive, we create a new entry
                elif confidence_delta > 0:
                    # If the item was in the missing list, remove it and create a new entry in the acquired list
                    if name in self.state.missing:
                        self.state.acquired[name] = src.ItemData(confidence_delta, False)
                        self.state.missing.remove(name)
                    # Otherwise, it is a new distractor
                    else:
                        self.state.distractors[name] = src.ItemData(confidence_delta, False)
                
            # Update flags/remove entries
            for name in self.reevaluate_entries(self.state.acquired):
                self.state.missing.add(name)
            self.reevaluate_entries(self.state.distractors)
            self.entry_num += 1

            # Send the new state to the writer
            self.backend_writer.write_data(self.state, self.entry_num)