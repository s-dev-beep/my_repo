"""Identity graph exceptions."""


class IdentityGraphError(Exception):
    """Base exception for identity graph operations."""
    pass


class InvalidPhoneError(IdentityGraphError):
    """Phone number is missing or invalid."""
    pass


class ImmutabilityViolationError(IdentityGraphError):
    """Attempted to overwrite immutable data."""
    pass


class MissingEvidenceError(IdentityGraphError):
    """Write operation missing required SourceEvidence."""
    pass


class HistoryDeletionError(IdentityGraphError):
    """Attempted to delete historical data."""
    pass
