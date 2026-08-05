import pytest
from dataclasses import FrozenInstanceError
from typing import Mapping
from types import MappingProxyType
from backend.src.runtime.resolution.resolution_metadata import ResolutionMetadata
from backend.src.runtime.resolution.resolution_statistics import ResolutionStatistics
from backend.src.runtime.resolution.resolution_snapshot import ResolutionSnapshot
from backend.src.runtime.resolution.resolution_result import ResolutionResult
from backend.src.runtime.resolution.runtime_resolution import RuntimeResolution
from backend.src.runtime.resolution.resolution_validator import ResolutionValidationResult
from backend.src.runtime.resolution.resolution_exceptions import (
    ResolutionException, ResolutionBuildException, ResolutionValidationException,
    ResolutionOrderingException, ResolutionCycleException, ResolutionFrozenException
)
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from backend.src.runtime.registry.component_types import RuntimeComponentType
from backend.src.runtime.registry.component_status import RuntimeComponentStatus

def test_resolution_metadata_immutability():
    metadata = ResolutionMetadata(
        schema_version="1.0.0",
        resolver_version="1.0.0",
        runtime_version="1.0.0",
        timestamp=123.45,
        resolution_uuid="uuid-123",
        additional_info=MappingProxyType({})
    )
    with pytest.raises(FrozenInstanceError):
        metadata.schema_version = "2.0.0"

def test_resolution_statistics_immutability():
    stats = ResolutionStatistics(1, 0, 1, 1, 1, 0, 0.0)
    with pytest.raises(FrozenInstanceError):
        stats.total_components = 2

def test_resolution_snapshot_immutability():
    metadata = ResolutionMetadata("1", "1", "1", 1.0, "u", MappingProxyType({}))
    stats = ResolutionStatistics(1, 0, 1, 1, 1, 0, 0.0)
    snapshot = ResolutionSnapshot(("c1",), (frozenset(["c1"]),), metadata, stats)
    with pytest.raises(FrozenInstanceError):
        snapshot.ordered_components = ("c2",)
        
def test_resolution_result_immutability():
    res = ResolutionResult(success=True)
    with pytest.raises(FrozenInstanceError):
        res.success = False

def test_runtime_resolution_immutability():
    comp = RuntimeComponent("c1", "c1", RuntimeComponentType.CORE, "1.0.0")
    metadata = ResolutionMetadata("1", "1", "1", 1.0, "u", MappingProxyType({}))
    stats = ResolutionStatistics(1, 0, 1, 1, 1, 0, 0.0)
    val = ResolutionValidationResult(True, (), ())
    res = RuntimeResolution("res-1", (comp,), (frozenset(["c1"]),), metadata, stats, val)
    
    with pytest.raises(FrozenInstanceError):
        res.resolution_id = "res-2"

def test_exception_hierarchy():
    assert issubclass(ResolutionBuildException, ResolutionException)
    assert issubclass(ResolutionValidationException, ResolutionException)
    assert issubclass(ResolutionOrderingException, ResolutionException)
    assert issubclass(ResolutionCycleException, ResolutionException)
    assert issubclass(ResolutionFrozenException, ResolutionException)
    
    with pytest.raises(ResolutionCycleException):
        raise ResolutionCycleException("cycle")

def test_resolution_snapshot_generation():
    comp = RuntimeComponent("c1", "c1", RuntimeComponentType.CORE, "1.0.0")
    metadata = ResolutionMetadata("1", "1", "1", 1.0, "u", MappingProxyType({}))
    stats = ResolutionStatistics(1, 0, 1, 1, 1, 0, 0.0)
    val = ResolutionValidationResult(True, (), ())
    res = RuntimeResolution("res-1", (comp,), (frozenset(["c1"]),), metadata, stats, val)
    
    snap = res.get_snapshot()
    assert snap.ordered_components == ("c1",)
    assert snap.dependency_ordering == (frozenset(["c1"]),)
    assert snap.metadata == metadata
    assert snap.statistics == stats

def test_resolution_result_contains_immutable_tuples():
    res = ResolutionResult(success=False, errors=("error1",), warnings=("warn1",))
    assert isinstance(res.errors, tuple)
    assert isinstance(res.warnings, tuple)
