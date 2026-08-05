import pytest
from typing import Tuple
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from backend.src.runtime.registry.component_types import RuntimeComponentType
from backend.src.runtime.dependency.runtime_dependency import RuntimeDependency
from backend.src.runtime.dependency.dependency_type import DependencyType
from backend.src.runtime.composition.runtime_composition import RuntimeComposition
from backend.src.runtime.composition.composition_metadata import CompositionMetadata
from backend.src.runtime.composition.composition_statistics import CompositionStatistics
from backend.src.runtime.resolution.resolution_algorithm import ResolutionAlgorithm
from backend.src.runtime.resolution.resolution_exceptions import ResolutionCycleException

def _create_comp(cid: str) -> RuntimeComponent:
    return RuntimeComponent(cid, cid, RuntimeComponentType.CORE, "1.0")

def _create_dep(src: str, tgt: str) -> RuntimeDependency:
    return RuntimeDependency(f"{src}_to_{tgt}", src, tgt, DependencyType.REQUIRED)

def _mock_composition(comps: Tuple[RuntimeComponent, ...], deps: Tuple[RuntimeDependency, ...]) -> RuntimeComposition:
    from datetime import datetime
    metadata = CompositionMetadata("1", "1", datetime.now(), "1")
    stats = CompositionStatistics(len(comps), len(deps), 0, 0, 0)
    return RuntimeComposition("comp-1", comps, deps, metadata, stats)

def test_deterministic_ordering_simple():
    c1, c2, c3 = _create_comp("c1"), _create_comp("c2"), _create_comp("c3")
    # c3 depends on c2, c2 depends on c1
    # Evaluation order: c1 must be initialized first, then c2, then c3.
    deps = (
        _create_dep("c3", "c2"),
        _create_dep("c2", "c1")
    )
    comp = _mock_composition((c1, c2, c3), deps)
    ordered, layers = ResolutionAlgorithm.compute_ordering(comp)
    assert ordered == (c1, c2, c3)
    assert layers == (frozenset(["c1"]), frozenset(["c2"]), frozenset(["c3"]))

def test_multiple_valid_roots():
    c1, c2, c3 = _create_comp("c1"), _create_comp("c2"), _create_comp("c3")
    # c3 depends on c1 and c2. Both c1 and c2 are roots.
    deps = (
        _create_dep("c3", "c1"),
        _create_dep("c3", "c2")
    )
    comp = _mock_composition((c1, c2, c3), deps)
    ordered, layers = ResolutionAlgorithm.compute_ordering(comp)
    # Roots should be ordered alphabetically by ID to guarantee stability
    assert ordered == (c1, c2, c3)
    assert layers == (frozenset(["c1", "c2"]), frozenset(["c3"]))

def test_isolated_components():
    c1, c2 = _create_comp("c1"), _create_comp("c2")
    comp = _mock_composition((c1, c2), ())
    ordered, layers = ResolutionAlgorithm.compute_ordering(comp)
    assert ordered == (c1, c2)
    assert layers == (frozenset(["c1", "c2"]),)

def test_disconnected_graphs():
    c1, c2, c3, c4 = _create_comp("A"), _create_comp("B"), _create_comp("C"), _create_comp("D")
    # A->B (B depends on A), C->D (D depends on C)
    deps = (_create_dep("B", "A"), _create_dep("D", "C"))
    comp = _mock_composition((c1, c2, c3, c4), deps)
    ordered, layers = ResolutionAlgorithm.compute_ordering(comp)
    # Roots A, C in first layer
    assert layers == (frozenset(["A", "C"]), frozenset(["B", "D"]))

def test_cycle_detection():
    c1, c2 = _create_comp("c1"), _create_comp("c2")
    # c1->c2, c2->c1
    deps = (_create_dep("c1", "c2"), _create_dep("c2", "c1"))
    comp = _mock_composition((c1, c2), deps)
    with pytest.raises(ResolutionCycleException):
        ResolutionAlgorithm.compute_ordering(comp)

def test_empty_composition():
    comp = _mock_composition((), ())
    ordered, layers = ResolutionAlgorithm.compute_ordering(comp)
    assert ordered == ()
    assert layers == ()

def test_single_component():
    c1 = _create_comp("c1")
    comp = _mock_composition((c1,), ())
    ordered, layers = ResolutionAlgorithm.compute_ordering(comp)
    assert ordered == (c1,)
    assert layers == (frozenset(["c1"]),)

def test_deep_dependency_chain():
    comps = tuple(_create_comp(f"c{i}") for i in range(1, 6)) # c1 to c5
    deps = tuple(_create_dep(f"c{i+1}", f"c{i}") for i in range(1, 5))
    comp = _mock_composition(comps, deps)
    ordered, layers = ResolutionAlgorithm.compute_ordering(comp)
    assert len(layers) == 5
    assert layers[0] == frozenset(["c1"])
    assert layers[4] == frozenset(["c5"])

def test_ordering_stability():
    c1, c2, c3 = _create_comp("Z"), _create_comp("A"), _create_comp("M")
    comp = _mock_composition((c1, c2, c3), ())
    ordered, layers = ResolutionAlgorithm.compute_ordering(comp)
    # Should sort A, M, Z
    assert ordered[0].component_id == "A"
    assert ordered[1].component_id == "M"
    assert ordered[2].component_id == "Z"
