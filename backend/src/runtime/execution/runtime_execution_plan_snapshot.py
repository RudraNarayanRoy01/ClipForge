from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionPlanSnapshot:
    descriptor_hash: str
    layer_hash: str
    batch_hash: str
    lookup_hash: str
    plan_lookup_hash: str
    metadata_hash: str
    statistics_hash: str
    plan_hash: str
