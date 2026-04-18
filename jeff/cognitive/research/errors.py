"""Research-specific synthesis errors."""


class ResearchSynthesisError(Exception):
    """Research synthesis failed closed."""


class ResearchSynthesisValidationError(ResearchSynthesisError):
    """Research synthesis output failed validation."""


class ResearchProvenanceValidationError(ResearchSynthesisValidationError):
    """Research provenance linkage failed validation."""


class ResearchOperatorSurfaceError(ResearchSynthesisError):
    """Structured research failure for operator-facing surface projection."""

    def __init__(
        self,
        *,
        failure_kind: str,
        error_code: str,
        reason: str,
        research_mode: str | None = None,
        project_id: str | None = None,
        work_unit_id: str | None = None,
        run_id: str | None = None,
        question: str | None = None,
        stage: str | None = None,
        checkpoint: str | None = None,
        provided_input_count: int | None = None,
        resolved_source_count: int | None = None,
        missing_inputs: tuple[str, ...] = (),
    ) -> None:
        self.failure_kind = failure_kind
        self.error_code = error_code
        self.reason = _bounded_reason(reason)
        self.research_mode = research_mode
        self.project_id = project_id
        self.work_unit_id = work_unit_id
        self.run_id = run_id
        self.question = _bounded_context(question)
        self.stage = stage
        self.checkpoint = checkpoint
        self.provided_input_count = provided_input_count
        self.resolved_source_count = resolved_source_count
        self.missing_inputs = tuple(missing_inputs)
        super().__init__(self.operator_message)

    @property
    def operator_message(self) -> str:
        prefix = {
            "input_problem": "research input problem",
            "source_acquisition_problem": "research source acquisition problem",
            "synthesis_problem": "research synthesis problem",
            "projection_problem": "research projection problem",
            "render_problem": "research render problem",
        }.get(self.failure_kind, "research failure")
        details: list[str] = [f"error_code={self.error_code}"]
        if self.research_mode:
            details.append(f"mode={self.research_mode}")
        if self.stage:
            details.append(f"stage={self.stage}")
        if self.checkpoint:
            details.append(f"checkpoint={self.checkpoint}")
        if self.provided_input_count is not None:
            details.append(f"provided_inputs={self.provided_input_count}")
        if self.resolved_source_count is not None:
            details.append(f"resolved_sources={self.resolved_source_count}")
        if self.question:
            details.append(f"question={self.question}")
        if self.missing_inputs:
            details.append(f"missing_inputs={','.join(self.missing_inputs)}")
        if self.reason:
            details.append(f"reason={self.reason}")
        suffix = f" ({' '.join(details)})" if details else ""
        return f"{prefix}{suffix}"

    def to_payload(self) -> dict[str, object]:
        return {
            "failure_kind": self.failure_kind,
            "error_code": self.error_code,
            "message": self.operator_message,
            "reason": self.reason,
            "question": self.question,
            "stage": self.stage,
            "checkpoint": self.checkpoint,
            "provided_input_count": self.provided_input_count,
            "resolved_source_count": self.resolved_source_count,
            "missing_inputs": list(self.missing_inputs),
        }

    def __str__(self) -> str:
        return self.operator_message


class ResearchSynthesisRuntimeError(ResearchSynthesisError):
    """Research synthesis failed at the adapter/runtime invocation boundary."""

    def __init__(
        self,
        *,
        failure_class: str,
        reason: str,
        adapter_id: str | None = None,
        provider_name: str | None = None,
        model_name: str | None = None,
        base_url: str | None = None,
        research_mode: str | None = None,
        project_id: str | None = None,
        work_unit_id: str | None = None,
        run_id: str | None = None,
    ) -> None:
        self.failure_class = failure_class
        self.reason = _bounded_reason(reason)
        self.adapter_id = adapter_id
        self.provider_name = provider_name
        self.model_name = model_name
        self.base_url = base_url
        self.research_mode = research_mode
        self.project_id = project_id
        self.work_unit_id = work_unit_id
        self.run_id = run_id
        super().__init__(self.operator_message)

    @property
    def operator_message(self) -> str:
        details: list[str] = []
        research_mode = getattr(self, "research_mode", None)
        stage = getattr(self, "stage", None)
        checkpoint = getattr(self, "checkpoint", None)
        provided_input_count = getattr(self, "provided_input_count", None)
        resolved_source_count = getattr(self, "resolved_source_count", None)
        question = _bounded_context(getattr(self, "question", None))
        missing_inputs = tuple(getattr(self, "missing_inputs", ()))
        if research_mode:
            details.append(f"mode={research_mode}")
        if stage:
            details.append(f"stage={stage}")
        if checkpoint:
            details.append(f"checkpoint={checkpoint}")
        if self.provider_name:
            details.append(f"provider={self.provider_name}")
        if self.adapter_id:
            details.append(f"adapter={self.adapter_id}")
        if self.model_name:
            details.append(f"model={self.model_name}")
        if self.base_url:
            details.append(f"base_url={self.base_url}")
        if provided_input_count is not None:
            details.append(f"provided_inputs={provided_input_count}")
        if resolved_source_count is not None:
            details.append(f"resolved_sources={resolved_source_count}")
        if question:
            details.append(f"question={question}")
        if missing_inputs:
            details.append(f"missing_inputs={','.join(missing_inputs)}")
        if self.reason:
            details.append(f"reason={self.reason}")
        suffix = f" ({' '.join(details)})" if details else ""
        return f"research synthesis failed: {self.failure_class}{suffix}"

    def with_context(
        self,
        *,
        research_mode: str | None,
        project_id: str | None,
        work_unit_id: str | None,
        run_id: str | None,
    ) -> "ResearchSynthesisRuntimeError":
        return ResearchSynthesisRuntimeError(
            failure_class=self.failure_class,
            reason=self.reason,
            adapter_id=self.adapter_id,
            provider_name=self.provider_name,
            model_name=self.model_name,
            base_url=self.base_url,
            research_mode=research_mode,
            project_id=project_id,
            work_unit_id=work_unit_id,
            run_id=run_id,
        )

    def to_payload(self) -> dict[str, object]:
        return {
            "failure_kind": "synthesis_runtime_problem",
            "error_code": self.failure_class,
            "message": self.operator_message,
            "reason": self.reason,
            "research_mode": self.research_mode,
            "question": _bounded_context(getattr(self, "question", None)),
            "stage": getattr(self, "stage", None),
            "checkpoint": getattr(self, "checkpoint", None),
            "provided_input_count": getattr(self, "provided_input_count", None),
            "resolved_source_count": getattr(self, "resolved_source_count", None),
            "missing_inputs": list(getattr(self, "missing_inputs", ())),
            "provider_name": self.provider_name,
            "adapter_id": self.adapter_id,
            "model_name": self.model_name,
            "base_url": self.base_url,
        }

    def __str__(self) -> str:
        return self.operator_message


def _bounded_reason(message: str, *, max_chars: int = 180) -> str:
    normalized = " ".join(message.split())
    if len(normalized) <= max_chars:
        return normalized
    return f"{normalized[: max_chars - 3].rstrip()}..."


def _bounded_context(message: str | None, *, max_chars: int = 140) -> str | None:
    if message is None:
        return None
    normalized = " ".join(message.split())
    if len(normalized) <= max_chars:
        return normalized
    return f"{normalized[: max_chars - 3].rstrip()}..."
