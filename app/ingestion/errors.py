class IngestionError(Exception):
    """Base para erros da camada de ingestão."""


class SourceNotFoundError(IngestionError):
    pass


class SourceNotEligibleError(IngestionError):
    pass


class ConfigNotFoundError(IngestionError):
    pass


class ConfigDisabledError(IngestionError):
    pass


class ModeIncompatibleError(IngestionError):
    pass


class RunNotFoundError(IngestionError):
    pass


class RunInProgressError(IngestionError):
    pass


class InvalidTransitionError(IngestionError):
    pass
