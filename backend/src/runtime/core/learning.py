import time
import uuid
from typing import List, Dict, Any

from .observation_model import ObservationResult
from .learning_model import (
    LearningResult,
    LearningPattern,
    LearningCategory,
    LearningConfidence,
    LearningSummary
)

class RuntimeLearning:
    """
    The Runtime learning engine.
    
    Defines "How Runtime learns."
    Performs exactly one responsibility: Consumes ObservationResult -> Produces LearningResult.
    
    It is NOT an executor, scheduler, lifecycle manager, retry engine, 
    monitoring engine, analytics engine, optimization engine, recommendation engine, 
    workflow engine, queue manager, or resource manager.
    
    It does NOT execute work, optimize execution, predict future execution, or allocate resources.
    """
    
    def learn(self, observation_result: ObservationResult) -> LearningResult:
        """
        Consume an immutable ObservationResult and produce an immutable LearningResult.
        """
        now = time.time()
        
        # 1. Generate learning identity
        learning_id = f"learn-{uuid.uuid4().hex[:8]}"
        
        # 2. Extract patterns based on observations (without optimizing or predicting)
        patterns: List[LearningPattern] = []
        high_count = 0
        medium_count = 0
        low_count = 0
        
        for record in observation_result.records:
            # We classify knowledge strictly based on observation records without executing logic
            category = LearningCategory.UNKNOWN
            confidence = LearningConfidence.LOW
            description = f"Learned from observation: {record.message}"
            
            if record.category.value == "RETRY":
                category = LearningCategory.RETRY
                if record.severity.value == "WARNING":
                    confidence = LearningConfidence.MEDIUM
                    medium_count += 1
                elif record.severity.value == "ERROR":
                    confidence = LearningConfidence.HIGH
                    high_count += 1
                else:
                    low_count += 1
            else:
                low_count += 1
                
            pattern = LearningPattern(
                category=category,
                confidence=confidence,
                description=description,
                supporting_observations=[observation_result.observation_identity.observation_id],
                context={"source_category": record.category.value, "source_severity": record.severity.value}
            )
            patterns.append(pattern)
            
        # 3. Create summary
        total_patterns = len(patterns)
        summary_text = (
            f"Learning extracted from observation {observation_result.observation_identity.observation_id}. "
            f"Identified {total_patterns} pattern(s)."
        )
        
        summary = LearningSummary(
            summary=summary_text,
            pattern_count=total_patterns,
            high_confidence_count=high_count,
            medium_confidence_count=medium_count,
            low_confidence_count=low_count
        )
        
        # 4. Produce immutable outcome
        return LearningResult(
            learning_identity=learning_id,
            observation_identity=observation_result.observation_identity,
            summary=summary,
            patterns=patterns,
            created_at=now
        )
