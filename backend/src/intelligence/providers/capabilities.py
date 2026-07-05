from typing import Protocol, List, Any, AsyncGenerator, Type
from pydantic import BaseModel

class IReasoning(Protocol):
    async def generate_text(self, prompt: str, context: list) -> str:
        ...

class IStructuredOutput(Protocol):
    async def generate_object(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        ...

class IVision(Protocol):
    async def analyze_image(self, image_bytes: bytes, prompt: str) -> str:
        ...

class IToolCalling(Protocol):
    async def execute_with_tools(self, prompt: str, tools: List[Any]) -> Any:
        ...
