import uuid

class ExecutionGraphIdFactory:
    @staticmethod
    def generate_graph_id() -> str:
        return f"exec-graph-{uuid.uuid4()}"
