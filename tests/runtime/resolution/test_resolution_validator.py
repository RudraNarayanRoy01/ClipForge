import pytest
from backend.src.runtime.resolution.resolution_validator import ResolutionValidator
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from backend.src.runtime.registry.component_types import RuntimeComponentType
from backend.src.runtime.dependency.runtime_dependency import RuntimeDependency
from backend.src.runtime.dependency.dependency_type import DependencyType
from backend.src.runtime.composition.runtime_composition import RuntimeComposition
from backend.src.runtime.composition.composition_metadata import CompositionMetadata
from backend.src.runtime.composition.composition_statistics import CompositionStatistics

def _create_comp(cid: str) -> RuntimeComponent:
    return RuntimeComponent(cid, cid, RuntimeComponentType.CORE, "1.0")

def _create_dep(src: str, tgt: str) -> RuntimeDependency:
    return RuntimeDependency(f"{src}_to_{tgt}", src, tgt, DependencyType.REQUIRED)

def _mock_composition(comps, deps) -> RuntimeComposition:
    from datetime import datetime
    metadata = CompositionMetadata("1", "1", datetime.now(), "1")
    stats = CompositionStatistics(len(comps), len(deps), 0, 0, 0)
    return RuntimeComposition("comp-1", comps, deps, metadata, stats)

def test_validator_valid_graph():
    c1, c2 = _create_comp("c1"), _create_comp("c2")
    comp = _mock_composition((c1, c2), (_create_dep("c2", "c1"),))
    res = ResolutionValidator.validate(comp)
    assert res.is_valid
    assert not res.errors

def test_validator_detects_cycles():
    c1, c2 = _create_comp("c1"), _create_comp("c2")
    comp = _mock_composition((c1, c2), (_create_dep("c1", "c2"), _create_dep("c2", "c1")))
    res = ResolutionValidator.validate(comp)
    assert not res.is_valid
    assert "Dependency cycle detected in composition." in res.errors

def test_validator_invalid_references():
    c1 = _create_comp("c1")
    comp = _mock_composition((c1,), (_create_dep("c1", "missing"),))
    res = ResolutionValidator.validate(comp)
    assert not res.is_valid
    assert any("missing not found" in e for e in res.errors)

def test_validator_missing_components_but_has_dependencies():
    comp = _mock_composition((), (_create_dep("a", "b"),))
    res = ResolutionValidator.validate(comp)
    assert not res.is_valid
    assert "Composition has dependencies but no components." in res.errors

def test_validator_unreachable_disconnected_are_valid_in_resolution():
    # Having disconnected components is functionally valid in resolution 
    # (they just form another root).
    c1, c2 = _create_comp("c1"), _create_comp("c2")
    comp = _mock_composition((c1, c2), ())
    res = ResolutionValidator.validate(comp)
    assert res.is_valid

def test_validator_invalid_type():
    res = ResolutionValidator.validate("not_a_composition")
    assert not res.is_valid
    assert "Invalid composition type" in res.errors[0]
