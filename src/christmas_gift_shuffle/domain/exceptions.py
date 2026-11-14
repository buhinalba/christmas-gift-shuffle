class DomainError(ValueError):
    pass


class ConfigurationError(DomainError):
    pass


class AssignmentError(DomainError):
    pass
