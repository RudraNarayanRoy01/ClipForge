class RuntimeExecutionException(Exception):
    pass

class ExecutionValidationException(RuntimeExecutionException):
    pass

class ExecutionMetadataException(RuntimeExecutionException):
    pass

class ExecutionSnapshotException(RuntimeExecutionException):
    pass

class ExecutionStateException(RuntimeExecutionException):
    pass
