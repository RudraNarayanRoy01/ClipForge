from datetime import datetime, timezone
from src.knowledge.dtos import VideoKnowledge, KnowledgeStatus
from .dtos import LifecycleDecision, LifecycleEvaluation, LifecycleEvaluationCriteria


class KnowledgeLifecyclePolicy:
    """
    A pure policy component that evaluates whether canonical VideoKnowledge snapshots
    remain authoritative or if they require regeneration.
    
    It performs deterministic evaluation based on version compatibility, freshness,
    and existing status, without any side-effects.
    """
    
    def evaluate(self, knowledge: VideoKnowledge, criteria: LifecycleEvaluationCriteria) -> LifecycleEvaluation:
        """
        Evaluates a knowledge snapshot against the provided criteria.
        
        Args:
            knowledge: The canonical domain model to evaluate.
            criteria: The expected versions and constraints to evaluate against.
            
        Returns:
            LifecycleEvaluation: Contains the deterministic decision and a provider-independent reason.
        """
        # 1. Check explicit invalidation first
        if knowledge.status == KnowledgeStatus.INVALID:
            return LifecycleEvaluation(
                decision=LifecycleDecision.INVALID,
                reason="Snapshot is explicitly marked as INVALID"
            )
            
        # 2. Check schema compatibility (exact match required)
        if knowledge.metadata.schema_version != criteria.expected_schema_version:
            return LifecycleEvaluation(
                decision=LifecycleDecision.INCOMPATIBLE,
                reason=f"Schema version mismatch: expected {criteria.expected_schema_version}, got {knowledge.metadata.schema_version}"
            )
            
        # 3. Check source version compatibility
        if knowledge.metadata.source_version != criteria.current_source_version:
            return LifecycleEvaluation(
                decision=LifecycleDecision.REFRESH_REQUIRED,
                reason=f"Source media changed: expected {criteria.current_source_version}, got {knowledge.metadata.source_version}"
            )
            
        # 4. Check knowledge version compatibility (exact match required)
        if knowledge.metadata.knowledge_version != criteria.expected_knowledge_version:
            return LifecycleEvaluation(
                decision=LifecycleDecision.REFRESH_REQUIRED,
                reason=f"Knowledge logic changed: expected {criteria.expected_knowledge_version}, got {knowledge.metadata.knowledge_version}"
            )
            
        # 5. Check snapshot freshness if applicable
        if criteria.max_age_seconds is not None:
            now = datetime.now(timezone.utc)
            processing_time = knowledge.metadata.processing_timestamp
            
            # Make processing_time timezone-aware if it's naive, assuming UTC
            if processing_time.tzinfo is None:
                processing_time = processing_time.replace(tzinfo=timezone.utc)
                
            age_seconds = (now - processing_time).total_seconds()
            if age_seconds > criteria.max_age_seconds:
                return LifecycleEvaluation(
                    decision=LifecycleDecision.REFRESH_REQUIRED,
                    reason=f"Snapshot expired: age {int(age_seconds)}s exceeds maximum {criteria.max_age_seconds}s"
                )
                
        # If all checks pass, keep the snapshot
        return LifecycleEvaluation(
            decision=LifecycleDecision.KEEP,
            reason="Snapshot is valid, compatible, and up-to-date"
        )
