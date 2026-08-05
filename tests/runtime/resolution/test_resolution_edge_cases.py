import pytest
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from backend.src.runtime.registry.component_types import RuntimeComponentType
from backend.src.runtime.dependency.runtime_dependency import RuntimeDependency
from backend.src.runtime.dependency.dependency_type import DependencyType
from backend.src.runtime.composition.runtime_composition import RuntimeComposition
from backend.src.runtime.composition.composition_metadata import CompositionMetadata
from backend.src.runtime.composition.composition_statistics import CompositionStatistics
from backend.src.runtime.resolution.resolution_algorithm import ResolutionAlgorithm
from backend.src.runtime.resolution.runtime_dependency_resolver import RuntimeDependencyResolver

def _create_comp(cid: str) -> RuntimeComponent:
    return RuntimeComponent(cid, cid, RuntimeComponentType.CORE, "1.0")

def _create_dep(src: str, tgt: str) -> RuntimeDependency:
    return RuntimeDependency(f"{src}_to_{tgt}", src, tgt, DependencyType.REQUIRED)

def _mock_composition(comps, deps) -> RuntimeComposition:
    from datetime import datetime
    metadata = CompositionMetadata("1", "1", datetime.now(), "1")
    stats = CompositionStatistics(len(comps), len(deps), 0, 0, 0)
    return RuntimeComposition("comp-1", comps, deps, metadata, stats)

def test_duplicate_dependencies_ignored():
    c1, c2 = _create_comp("c1"), _create_comp("c2")
    # Duplicate dependencies from graph should not affect layers or stability
    comp = _mock_composition((c1, c2), (_create_dep("c2", "c1"), _create_dep("c2", "c1")))
    ordered, layers = ResolutionAlgorithm.compute_ordering(comp)
    assert len(ordered) == 2
    assert len(layers) == 2

def test_self_dependency_cycle():
    c1 = _create_comp("c1")
    comp = _mock_composition((c1,), (_create_dep("c1", "c1"),))
    from backend.src.runtime.resolution.resolution_exceptions import ResolutionCycleException
    with pytest.raises(ResolutionCycleException):
        ResolutionAlgorithm.compute_ordering(comp)

def test_large_number_of_independent_components():
    comps = tuple(_create_comp(f"c{i}") for i in range(100))
    comp = _mock_composition(comps, ())
    ordered, layers = ResolutionAlgorithm.compute_ordering(comp)
    assert len(ordered) == 100
    assert len(layers) == 1
    assert len(layers[0]) == 100

def test_resolver_with_no_components_or_deps():
    comp = _mock_composition((), ())
    res = RuntimeDependencyResolver.resolve(comp)
    assert res.success
    assert len(res.resolution.ordered_components) == 0

def test_statistics_average_depth_empty():
    comp = _mock_composition((), ())
    res = RuntimeDependencyResolver.resolve(comp)
    assert res.success
    assert res.resolution.statistics.average_dependency_depth == 0.0

def test_statistics_maximum_depth():
    c1, c2, c3 = _create_comp("c1"), _create_comp("c2"), _create_comp("c3")
    comp = _mock_composition((c1, c2, c3), (_create_dep("c3", "c2"), _create_dep("c2", "c1")))
    res = RuntimeDependencyResolver.resolve(comp)
    assert res.success
    assert res.resolution.statistics.maximum_dependency_depth == 3
    assert res.resolution.statistics.average_dependency_depth == 1.5
