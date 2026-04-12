"""Minimal Ollama HTTP model adapter."""

from __future__ import annotations

import json
import socket
import time
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from ..errors import (
    ModelInvocationError,
    ModelMalformedOutputError,
    ModelProviderHTTPError,
    ModelTimeoutError,
    ModelTransportError,
)
from ..types import (
    ModelInvocationStatus,
    ModelRequest,
    ModelResponse,
    ModelResponseMode,
    ModelUsage,
)


def _coerce_non_negative_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    if value < 0:
        return None
    return value


@dataclass(frozen=True, slots=True)
class OllamaModelAdapter:
    adapter_id: str
    model_name: str
    base_url: str = "http://127.0.0.1:11434"
    timeout_seconds: int | None = None
    provider_name: str = "ollama"
    context_length: int | None = None

    def invoke(self, request_model: ModelRequest) -> ModelResponse:
        started = time.monotonic()
        endpoint_path, payload = self._build_request_payload(request_model)
        url = f"{self.base_url.rstrip('/')}{endpoint_path}"

        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as http_response:
                response_payload = json.loads(http_response.read().decode("utf-8"))
        except error.HTTPError as exc:
            raise ModelProviderHTTPError(f"ollama HTTP failure for adapter {self.adapter_id}") from exc
        except (TimeoutError, socket.timeout, error.URLError) as exc:
            reason = getattr(exc, "reason", None)
            if isinstance(exc, (TimeoutError, socket.timeout)) or isinstance(
                reason,
                (TimeoutError, socket.timeout),
            ):
                raise ModelTimeoutError(
                    f"ollama invocation timed out for adapter {self.adapter_id}",
                ) from exc
            raise ModelTransportError(
                f"ollama transport failed for adapter {self.adapter_id}",
            ) from exc
        except json.JSONDecodeError as exc:
            raise ModelInvocationError(f"ollama returned invalid JSON envelope for adapter {self.adapter_id}") from exc

        response_mode = request_model.response_mode
        output_text = self._extract_output_text(response_payload, response_mode=response_mode)

        output_json = None
        if response_mode is ModelResponseMode.JSON:
            try:
                parsed = json.loads(output_text)
            except json.JSONDecodeError as exc:
                raise ModelMalformedOutputError(
                    f"ollama text output was not valid JSON for adapter {self.adapter_id}",
                    raw_output=output_text,
                ) from exc
            if not isinstance(parsed, dict):
                raise ModelMalformedOutputError(
                    f"ollama JSON mode requires an object result for adapter {self.adapter_id}",
                    raw_output=output_text,
                )
            output_json = parsed

        latency_ms = max(round((time.monotonic() - started) * 1000), 0)
        input_tokens = _coerce_non_negative_int(
            response_payload.get("prompt_eval_count", response_payload.get("input_tokens")),
        )
        output_tokens = _coerce_non_negative_int(
            response_payload.get("eval_count", response_payload.get("output_tokens")),
        )
        total_tokens = None
        if input_tokens is not None and output_tokens is not None:
            total_tokens = input_tokens + output_tokens
        else:
            total_tokens = _coerce_non_negative_int(response_payload.get("total_tokens"))

        return ModelResponse(
            request_id=request_model.request_id,
            adapter_id=self.adapter_id,
            provider_name=self.provider_name,
            model_name=self.model_name,
            status=ModelInvocationStatus.COMPLETED,
            output_text=output_text,
            output_json=output_json,
            usage=ModelUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                estimated_cost=None,
                latency_ms=latency_ms,
            ),
            warnings=(),
            raw_response_ref=None,
        )

    def _build_request_payload(self, request_model: ModelRequest) -> tuple[str, dict[str, Any]]:
        if request_model.response_mode is ModelResponseMode.JSON:
            return "/api/chat", self._build_chat_payload(request_model)
        return "/api/generate", self._build_generate_payload(request_model)

    def _build_generate_payload(self, request_model: ModelRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model_name,
            "prompt": request_model.prompt,
            "stream": False,
        }
        if request_model.system_instructions is not None:
            payload["system"] = request_model.system_instructions
        if self.context_length is not None:
            payload["options"] = {"num_ctx": self.context_length}
        return payload

    def _build_chat_payload(self, request_model: ModelRequest) -> dict[str, Any]:
        messages: list[dict[str, str]] = []
        if request_model.system_instructions is not None:
            messages.append({"role": "system", "content": request_model.system_instructions})
        messages.append({"role": "user", "content": request_model.prompt})

        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "format": request_model.json_schema if request_model.json_schema is not None else "json",
        }
        if self.context_length is not None:
            payload["options"] = {"num_ctx": self.context_length}
        return payload

    def _extract_output_text(
        self,
        response_payload: dict[str, Any],
        *,
        response_mode: ModelResponseMode,
    ) -> str:
        if response_mode is ModelResponseMode.JSON:
            message = response_payload.get("message")
            if not isinstance(message, dict):
                raise ModelInvocationError(f"ollama chat response missing message output for adapter {self.adapter_id}")
            output_text = message.get("content")
            if not isinstance(output_text, str) or not output_text.strip():
                raise ModelInvocationError(f"ollama chat response missing message content for adapter {self.adapter_id}")
            return output_text.strip()

        output_text = response_payload.get("response")
        if not isinstance(output_text, str) or not output_text.strip():
            raise ModelInvocationError(f"ollama response missing text output for adapter {self.adapter_id}")
        return output_text.strip()
