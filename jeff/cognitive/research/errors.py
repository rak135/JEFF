"""Research-specific synthesis errors."""


class ResearchSynthesisError(Exception):
    """Research synthesis failed closed."""


class ResearchSynthesisValidationError(ResearchSynthesisError):
    """Research synthesis output failed validation."""
