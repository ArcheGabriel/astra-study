from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ValidationWarning:
    """
    Represents a non-fatal validation issue.
    """

    message: str

    severity: str = "warning"


@dataclass(slots=True)
class ValidationMetric:
    """
    One metric produced by a validator.
    """

    name: str

    value: Any


@dataclass(slots=True)
class ValidationResult:
    """
    Output returned by every validator.

    Every validator returns exactly one
    ValidationResult.

    The test runner combines these into
    a validation report.
    """

    name: str

    passed: bool

    score: float = 1.0

    metrics: list[ValidationMetric] = field(
        default_factory=list
    )

    warnings: list[
        ValidationWarning
    ] = field(
        default_factory=list
    )

    def add_metric(
        self,
        name: str,
        value: Any,
    ) -> None:

        self.metrics.append(

            ValidationMetric(

                name=name,

                value=value,

            )

        )

    def warn(
        self,
        message: str,
        severity: str = "warning",
    ) -> None:

        self.warnings.append(

            ValidationWarning(

                message=message,

                severity=severity,

            )

        )