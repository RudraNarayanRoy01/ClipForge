from abc import ABC, abstractmethod

from src.editing.domain.pipeline.editing import EditingRequest, EditingSequence


class IEditingService(ABC):
    """
    Service contract for generating the editing sequence.
    """

    @abstractmethod
    def generate_edit_sequence(self, request: EditingRequest) -> EditingSequence:
        """
        Generates the editing sequence.
        """
        pass
