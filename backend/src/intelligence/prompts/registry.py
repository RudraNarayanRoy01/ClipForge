from typing import Dict, Optional

class PromptRegistry:
    def __init__(self):
        # MVP: simple in-memory registry of string templates
        self._registry: Dict[str, str] = {}

    def register(self, name: str, template_str: str) -> None:
        self._registry[name] = template_str

    def get_template(self, name: str) -> Optional[str]:
        return self._registry.get(name)

# Example usage
prompt_registry = PromptRegistry()
