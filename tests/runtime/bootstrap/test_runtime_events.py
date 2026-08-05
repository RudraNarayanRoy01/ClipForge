from datetime import datetime
from backend.src.runtime.bootstrap.runtime_events import (
    RuntimeCreated,
    BootstrapStarted,
    InitializationStarted,
    ValidationStarted,
    RuntimeReady,
    ShutdownStarted,
    RuntimeStopped,
    BootstrapFailed,
)

def test_runtime_events_structure():
    event = RuntimeCreated(configuration_summary={"timeout": 10})
    assert event.event_id is not None
    assert isinstance(event.timestamp, datetime)
    assert event.configuration_summary == {"timeout": 10}
    
    events = [
        BootstrapStarted(),
        InitializationStarted(),
        ValidationStarted(),
        RuntimeReady(duration=1.5, initialized_components=["test"]),
        ShutdownStarted(),
        RuntimeStopped(),
        BootstrapFailed(reason="error", state="BOOTSTRAPPING", diagnostics={})
    ]
    
    for e in events:
        assert e.event_id is not None
        assert isinstance(e.timestamp, datetime)
