import pytest
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from backend.src.runtime.registry.component_types import RuntimeComponentType
from backend.src.runtime.dependency.runtime_dependency import RuntimeDependency
from backend.src.runtime.dependency.dependency_type import DependencyType
from backend.src.runtime.composition.runtime_composition import RuntimeComposition
from backend.src.runtime.composition.composition_metadata import CompositionMetadata
from backend.src.runtime.composition.composition_statistics import CompositionStatistics
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

def test_resolver_successful_execution():
    c1, c2 = _create_comp("c1"), _create_comp("c2")
    comp = _mock_composition((c1, c2), (_create_dep("c2", "c1"),))
    
    result = RuntimeDependencyResolver.resolve(comp)
    assert result.success
    assert result.resolution is not None
    assert result.resolution.resolution_id.startswith("res-")
    assert not result.errors
    
    res = result.resolution
    assert len(res.ordered_components) == 2
    assert res.ordered_components[0].component_id == "c1"
    assert res.ordered_components[1].component_id == "c2"
    assert len(res.dependency_order) == 2
    
def test_resolver_validation_failure():
    c1 = _create_comp("c1")
    comp = _mock_composition((c1,), (_create_dep("c1", "missing"),))
    
    result = RuntimeDependencyResolver.resolve(comp)
    assert not result.success
    assert result.resolution is None
    assert len(result.errors) > 0
    assert any("missing" in e for e in result.errors)

def test_resolver_cycle_failure():
    c1, c2 = _create_comp("c1"), _create_comp("c2")
    comp = _mock_composition((c1, c2), (_create_dep("c1", "c2"), _create_dep("c2", "c1")))
    
    result = RuntimeDependencyResolver.resolve(comp)
    assert not result.success
    assert result.resolution is None
    assert "Dependency cycle detected" in result.errors[0]

def test_repeated_resolver_execution():
    c1, c2 = _create_comp("c1"), _create_comp("c2")
    comp = _mock_composition((c1, c2), (_create_dep("c2", "c1"),))
    
    # Should be deterministic
    res1 = RuntimeDependencyResolver.resolve(comp)
    res2 = RuntimeDependencyResolver.resolve(comp)
    
    assert res1.success and res2.success
    assert res1.resolution.resolution_id != res2.resolution.resolution_id # Different IDs
    assert [c.component_id for c in res1.resolution.ordered_components] == [c.component_id for c in res2.resolution.ordered_components]
    assert res1.resolution.dependency_order == res2.resolution.dependency_order

def test_resolver_snapshot_creation():
    c1 = _create_comp("c1")
    comp = _mock_composition((c1,), ())
    
    result = RuntimeDependencyResolver.resolve(comp)
    assert result.success
    snap = result.resolution.get_snapshot()
    assert snap.ordered_components == ("c1",)
    assert snap.statistics.total_components == 1

def test_resolver_statistics():
    c1, c2, c3 = _create_comp("c1"), _create_comp("c2"), _create_comp("c3")
    comp = _mock_composition((c1, c2, c3), (_create_dep("c2", "c1"),))
    
    result = RuntimeDependencyResolver.resolve(comp)
    assert result.success
    stats = result.resolution.statistics
    assert stats.total_components == 3
    assert stats.total_dependencies == 1
    assert stats.root_nodes == 2 # c1 and c3
    assert stats.leaf_nodes == 2 # c2 and c3
    assert stats.disconnected_groups == 2 # (c1, c2) and (c3)
