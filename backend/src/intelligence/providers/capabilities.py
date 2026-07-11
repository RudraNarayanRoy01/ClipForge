from typing import Protocol, List, Any, AsyncGenerator, Type, runtime_checkable
from pydantic import BaseModel

@runtime_checkable
class IReasoning(Protocol):
    async def generate_text(self, prompt: str, context: list) -> str:
        ...

@runtime_checkable
class IStructuredOutput(Protocol):
    async def generate_object(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        ...

@runtime_checkable
class IVision(Protocol):
    async def analyze_image(self, image_bytes: bytes, prompt: str) -> str:
        ...

@runtime_checkable
class IToolCalling(Protocol):
    async def execute_with_tools(self, prompt: str, tools: List[Any]) -> Any:
        ...
