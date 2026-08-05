import pytest
from dataclasses import FrozenInstanceError
from backend.src.runtime.composition.composition_statistics import CompositionStatistics

def test_composition_statistics_immutability():
    stats = CompositionStatistics(
        component_count=5,
        dependency_count=4,
        root_count=2,
        leaf_count=3,
        disconnected_count=0
    )
    
    with pytest.raises(FrozenInstanceError):
        stats.component_count = 10
        
    with pytest.raises(FrozenInstanceError):
        stats.dependency_count = 10

def test_composition_statistics_counts():
    stats = CompositionStatistics(
        component_count=5,
        dependency_count=4,
        root_count=2,
        leaf_count=3,
        disconnected_count=1
    )
    assert stats.component_count == 5
    assert stats.dependency_count == 4
    assert stats.root_count == 2
    assert stats.leaf_count == 3
    assert stats.disconnected_count == 1
