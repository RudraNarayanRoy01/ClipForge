import uuid

class ExecutionIdFactory:
    @staticmethod
    def generate_execution_id() -> str:
        return f"exec-{uuid.uuid4()}"
