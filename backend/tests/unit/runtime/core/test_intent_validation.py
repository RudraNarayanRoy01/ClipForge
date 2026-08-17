import pytest
from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.intent_validation import ExecutionIntentValidator, IntentValidationError

def test_valid_execution_intent_is_accepted():
    validator = ExecutionIntentValidator()
    intent = ExecutionIntent(capability_id="valid", payload={})
    validator.validate(intent)

def test_valid_vertical_slice_intent_is_accepted():
    validator = ExecutionIntentValidator()
    intent = ExecutionIntent(
        capability_id="campaign.summary.generate",
        payload="opaque payload",
        output_contract="ExtractionSummarySchema"
    )
    validator.validate(intent)

def test_non_execution_intent_input_raises_intent_validation_error():
    validator = ExecutionIntentValidator()
    with pytest.raises(IntentValidationError, match="intent must be an ExecutionIntent"):
        validator.validate(object())

def test_empty_capability_id_raises_intent_validation_error():
    validator = ExecutionIntentValidator()
    intent = ExecutionIntent(capability_id="", payload={})
    with pytest.raises(IntentValidationError, match="capability_id must be a non-empty string"):
        validator.validate(intent)

def test_whitespace_only_capability_id_raises_intent_validation_error():
    validator = ExecutionIntentValidator()
    intent = ExecutionIntent(capability_id="   ", payload={})
    with pytest.raises(IntentValidationError, match="capability_id must be a non-empty string"):
        validator.validate(intent)

def test_valid_capability_id_is_preserved():
    validator = ExecutionIntentValidator()
    intent = ExecutionIntent(capability_id="valid.id", payload={})
    validator.validate(intent)
    assert intent.capability_id == "valid.id"

def test_payload_may_be_none_and_remains_accepted():
    validator = ExecutionIntentValidator()
    intent = ExecutionIntent(capability_id="valid", payload=None)
    validator.validate(intent)

def test_payload_may_be_an_arbitrary_object_and_remains_accepted():
    validator = ExecutionIntentValidator()
    class CustomObj:
        pass
    intent = ExecutionIntent(capability_id="valid", payload=CustomObj())
    validator.validate(intent)

def test_payload_object_identity_is_preserved_not_transformed():
    validator = ExecutionIntentValidator()
    payload_obj = {"key": "value"}
    intent = ExecutionIntent(capability_id="valid", payload=payload_obj)
    validator.validate(intent)
    assert intent.payload is payload_obj

def test_output_contract_none_is_accepted():
    validator = ExecutionIntentValidator()
    intent = ExecutionIntent(capability_id="valid", payload={}, output_contract=None)
    validator.validate(intent)

def test_valid_output_contract_string_is_accepted():
    validator = ExecutionIntentValidator()
    intent = ExecutionIntent(capability_id="valid", payload={}, output_contract="ValidSchema")
    validator.validate(intent)

def test_empty_output_contract_raises_intent_validation_error():
    validator = ExecutionIntentValidator()
    intent = ExecutionIntent(capability_id="valid", payload={}, output_contract="")
    with pytest.raises(IntentValidationError, match="output_contract must be None or a non-empty string"):
        validator.validate(intent)

def test_whitespace_only_output_contract_raises_intent_validation_error():
    validator = ExecutionIntentValidator()
    intent = ExecutionIntent(capability_id="valid", payload={}, output_contract="   \t")
    with pytest.raises(IntentValidationError, match="output_contract must be None or a non-empty string"):
        validator.validate(intent)

def test_non_string_non_none_output_contract_raises_intent_validation_error():
    validator = ExecutionIntentValidator()
    intent = ExecutionIntent(capability_id="valid", payload={}, output_contract=123)
    with pytest.raises(IntentValidationError, match="output_contract must be None or a non-empty string"):
        validator.validate(intent)

def test_successful_validation_returns_none():
    validator = ExecutionIntentValidator()
    intent = ExecutionIntent(capability_id="valid", payload={})
    result = validator.validate(intent)
    assert result is None

def test_validation_does_not_mutate_the_intent():
    validator = ExecutionIntentValidator()
    intent = ExecutionIntent(capability_id="valid", payload={"a": 1}, output_contract="Contract")
    validator.validate(intent)
    assert intent.capability_id == "valid"
    assert intent.payload == {"a": 1}
    assert intent.output_contract == "Contract"
