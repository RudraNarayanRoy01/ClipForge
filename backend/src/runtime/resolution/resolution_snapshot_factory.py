class ResolutionSnapshotFactory:
    """Factory for creating immutable resolution snapshots."""
    
    @staticmethod
    def create(resolution: 'RuntimeResolution') -> 'ResolutionSnapshot':
        from .resolution_snapshot import ResolutionSnapshot
        return ResolutionSnapshot(
            ordered_components=tuple(c.component_id for c in resolution.ordered_components),
            dependency_ordering=resolution.dependency_order,
            metadata=resolution.metadata,
            statistics=resolution.statistics
        )
