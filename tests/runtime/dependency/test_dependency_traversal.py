import pytest
from backend.src.runtime.dependency import (
    DependencyTraversal,
    TraversalException
)

def test_dfs_traversal():
    adj = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": [],
        "D": []
    }
    visited = []
    DependencyTraversal.dfs("A", adj, visited.append)
    
    # Deterministic order: A -> B -> D -> C (because B < C)
    assert visited == ["A", "B", "D", "C"]

def test_bfs_traversal():
    adj = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["E"],
        "D": [],
        "E": []
    }
    visited = []
    DependencyTraversal.bfs("A", adj, visited.append)
    
    # A, then B, C, then D, E
    assert visited == ["A", "B", "C", "D", "E"]

def test_topological_sort():
    adj = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D"],
        "D": []
    }
    nodes = {"A", "B", "C", "D"}
    
    order = DependencyTraversal.topological_sort(nodes, adj)
    # A has 0 in-degree. Wait!
    # A -> B means A depends on B. B's in-degree is 1, A's in-degree is 0.
    # Therefore A is the root and pops out first in our Kahn's algorithm.
    assert order.index("A") < order.index("B")
    assert order.index("A") < order.index("C")
    assert order.index("B") < order.index("D")
    assert order.index("C") < order.index("D")

def test_topological_sort_cycle():
    adj = {
        "A": ["B"],
        "B": ["C"],
        "C": ["A"]
    }
    nodes = {"A", "B", "C"}
    with pytest.raises(TraversalException):
        DependencyTraversal.topological_sort(nodes, adj)
