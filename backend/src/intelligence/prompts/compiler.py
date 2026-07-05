from typing import Dict, Any
from pydantic import BaseModel

class PromptCompiler:
    def __init__(self):
        # In MVP, this is a simple template compiler
        pass

    def compile(self, template_str: str, variables: BaseModel) -> str:
        # MVP: simple string formatting with dict conversion of the pydantic model
        try:
            return template_str.format(**variables.model_dump())
        except KeyError as e:
            raise ValueError(f"Missing required prompt variable: {e}")
