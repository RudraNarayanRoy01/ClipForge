import pytest
from backend.src.runtime.dependency import DependencyGraphValidator

def test_validator_success():
    nodes = {"A", "B"}
    edges = {} # Not using edges for basic graph checks
    adj = {"A": ["B"], "B": []}
    rev_adj = {"B": ["A"], "A": []}
    
    result = DependencyGraphValidator.validate(nodes, edges, adj, rev_adj)
    assert result.success
    assert len(result.cycles_detected) == 0

def test_validator_cycles():
    nodes = {"A", "B", "C"}
    edges = {}
    adj = {"A": ["B"], "B": ["C"], "C": ["A"]}
    rev_adj = {"A": ["C"], "C": ["B"], "B": ["A"]}
    
    result = DependencyGraphValidator.validate(nodes, edges, adj, rev_adj)
    assert not result.success
    assert len(result.cycles_detected) > 0

def test_validator_orphans():
    nodes = {"A", "B", "Orphan"}
    edges = {}
    adj = {"A": ["B"], "B": [], "Orphan": []}
    rev_adj = {"B": ["A"], "A": [], "Orphan": []}
    
    result = DependencyGraphValidator.validate(nodes, edges, adj, rev_adj)
    assert result.success # Orphan doesn't fail validation, just a warning
    assert "Orphan" in result.orphan_nodes
    assert len(result.warnings) == 1
