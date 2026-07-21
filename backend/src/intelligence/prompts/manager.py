import os
import re
import json
from pathlib import Path
from typing import Dict, Any

from pydantic import ValidationError
from src.intelligence.prompts.models import PromptMetadata, PromptTemplate, RenderedPrompt
from src.intelligence.prompts.exceptions import PromptNotFoundError, PromptValidationError

class PromptManager:
    """
    Manages loading, parsing, validating, and rendering of text prompts.
    Operates strictly independently of AI execution or business logic.
    """
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self._cache: Dict[str, PromptTemplate] = {}

    def get_prompt(self, prompt_identifier: str, reload: bool = False) -> PromptTemplate:
        """
        Loads a prompt by logical identifier (e.g., 'campaign/extract_topics').
        Caches the parsed template to avoid repeated I/O.
        """
        if not reload and prompt_identifier in self._cache:
            return self._cache[prompt_identifier]

        # Prevent directory traversal
        clean_name = os.path.normpath(prompt_identifier)
        if clean_name.startswith("..") or os.path.isabs(clean_name):
            raise PromptNotFoundError(f"Invalid prompt path: {prompt_identifier}")

        prompt_path = self.base_dir / f"{clean_name}.md"
        if not prompt_path.is_file():
            raise PromptNotFoundError(f"Prompt file not found: {prompt_path}")

        try:
            content = prompt_path.read_text(encoding="utf-8")
        except Exception as e:
            raise PromptNotFoundError(f"Failed to read prompt file {prompt_path}: {e}")

        # Split JSON frontmatter from markdown body
        parts = content.split("---", 1)
        if len(parts) < 2:
            raise PromptValidationError(f"Prompt {prompt_identifier} is missing the '---' separator between metadata and body.")
            
        frontmatter, body = parts[0].strip(), parts[1].strip()

        try:
            metadata_dict = json.loads(frontmatter)
            metadata = PromptMetadata(**metadata_dict)
        except json.JSONDecodeError as e:
            raise PromptValidationError(f"Invalid JSON frontmatter in prompt {prompt_identifier}: {e}")
        except ValidationError as e:
            raise PromptValidationError(f"Invalid metadata structure in prompt {prompt_identifier}: {e}")

        template = PromptTemplate(metadata=metadata, body=body)

        # Validate that declared variables actually appear in the template body
        for var in metadata.variables:
            if not re.search(r'\{\{\s*' + re.escape(var) + r'\s*\}\}', body):
                raise PromptValidationError(
                    f"Prompt '{prompt_identifier}' declares variable '{var}' in metadata, "
                    f"but it does not appear in the template body."
                )

        self._cache[prompt_identifier] = template
        return template

    def render(self, prompt_identifier: str, reload: bool = False, **kwargs: Any) -> RenderedPrompt:
        """
        Locates and renders a prompt by injecting kwargs into {{variable}} placeholders.
        Raises PromptValidationError if required variables are missing or unmapped variables remain.
        """
        template = self.get_prompt(prompt_identifier, reload=reload)
        
        # 1. Validate provided kwargs against metadata requirements
        missing_vars = [var for var in template.metadata.variables if var not in kwargs]
        if missing_vars:
            raise PromptValidationError(f"Prompt '{prompt_identifier}' missing required variables: {missing_vars}")

        # 2. Render placeholders
        rendered = template.body
        for key, value in kwargs.items():
            # Replace {{key}} with the stringified value
            rendered = re.sub(r'\{\{\s*' + re.escape(key) + r'\s*\}\}', str(value), rendered)

        # 3. Security check: Ensure no unmapped placeholders remain
        unmapped = re.findall(r'\{\{\s*([^}]+)\s*\}\}', rendered)
        if unmapped:
            raise PromptValidationError(f"Prompt '{prompt_identifier}' contains unmapped placeholders after rendering: {unmapped}")

        return RenderedPrompt(
            prompt_identifier=prompt_identifier,
            text=rendered,
            metadata=template.metadata
        )
