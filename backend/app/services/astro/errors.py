class AstroInputError(ValueError):
    """Invalid or unsupported calculation input. `field` names the offending request field."""

    def __init__(self, field: str, message: str):
        super().__init__(message)
        self.field = field
        self.message = message


class EngineUnavailableError(RuntimeError):
    """The calculation engine could not be loaded (e.g. pyswisseph is not installed)."""
