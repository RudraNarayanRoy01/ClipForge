"""
Adaptive AI Runtime

This subsystem acts as the sole orchestrator for all AI computation within the 
ClipForge platform. It abstracts away specific AI providers (Ollama, Gemini, OpenAI) 
and hardware considerations (CUDA, VRAM) from the core Application layer.

It ensures that the application only requests Capabilities (e.g. "Reasoning"), 
leaving the Runtime to determine the optimal Provider and Schedule for execution.
"""

from .core import RuntimeBootstrap, RuntimeLifecycleState, RuntimeContext, RuntimeMetadata
from .contracts import ILifecycleAware

__all__ = [
    "RuntimeBootstrap",
    "RuntimeLifecycleState",
    "RuntimeContext",
    "RuntimeMetadata",
    "ILifecycleAware",
]
