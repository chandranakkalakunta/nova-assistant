"""
Nova Observability Module
=========================
Structured logging for Google Cloud Logging.
Captures: requests, tool executions, Gemini calls, errors, latency.

Usage:
    from observability import log_request, log_tool, log_gemini, log_error
"""

import os
import json
import time
import logging
import traceback
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import Optional

# ── Detect environment ─────────────────────────────────────
# On Cloud Run, we write structured JSON to stdout.
# Cloud Logging automatically ingests it with full queryability.
IS_CLOUD_RUN = os.environ.get("K_SERVICE") is not None
SERVICE_NAME = os.environ.get("K_SERVICE", "nova-assistant-local")
SERVICE_VERSION = os.environ.get("K_REVISION", "local")
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "unknown")


# ── Core structured logger ─────────────────────────────────
def _emit(severity: str, message: str, **fields):
    """
    Emit a structured log entry.
    On Cloud Run → JSON to stdout (ingested by Cloud Logging automatically).
    Locally → formatted print for readability.
    """
    entry = {
        # Standard Cloud Logging fields
        "severity": severity,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        # Custom Nova fields
        **fields
    }

    if IS_CLOUD_RUN:
        # Cloud Logging ingests structured JSON from stdout
        print(json.dumps(entry), flush=True)
    else:
        # Local dev — pretty print
        icon = {"INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌", "DEBUG": "🔍"}.get(severity, "📋")
        ts = datetime.now().strftime("%H:%M:%S")
        extra = {k: v for k, v in fields.items() if k not in ("service", "version")}
        print(f"{icon} [{ts}] {message} {json.dumps(extra) if extra else ''}", flush=True)


# ── Request logging ────────────────────────────────────────
def log_request_start(question: str, session_id: Optional[str] = None) -> dict:
    """
    Log the start of a user request. Returns context for downstream logging.
    """
    context = {
        "request_id": f"req_{int(time.time() * 1000)}",
        "session_id": session_id or "anonymous",
        "start_time": time.time(),
    }

    _emit(
        severity="INFO",
        message="Nova request started",
        event="request_start",
        request_id=context["request_id"],
        session_id=context["session_id"],
        question_length=len(question),
        # Don't log full question — could contain PII
        question_preview=question[:50] + "..." if len(question) > 50 else question,
    )

    return context


def log_request_end(context: dict, tools_used: list, success: bool):
    """
    Log the completion of a user request with full latency.
    """
    latency_ms = round((time.time() - context["start_time"]) * 1000)

    _emit(
        severity="INFO" if success else "ERROR",
        message="Nova request completed" if success else "Nova request failed",
        event="request_end",
        request_id=context["request_id"],
        session_id=context["session_id"],
        latency_ms=latency_ms,
        tools_used=tools_used,
        tool_count=len(tools_used),
        success=success,
    )


# ── Tool execution logging ─────────────────────────────────
@contextmanager
def log_tool_execution(tool_name: str, query: str, request_id: str):
    """
    Context manager to wrap tool execution with timing and error capture.

    Usage:
        with log_tool_execution("search_jobs", query, request_id) as ctx:
            result = search_jobs(query)
            ctx["result_size"] = len(result)
    """
    start = time.time()
    ctx = {}

    _emit(
        severity="DEBUG",
        message=f"Tool started: {tool_name}",
        event="tool_start",
        tool_name=tool_name,
        query_preview=query[:80] if query else "",
        request_id=request_id,
    )

    try:
        yield ctx
        latency_ms = round((time.time() - start) * 1000)
        _emit(
            severity="INFO",
            message=f"Tool succeeded: {tool_name}",
            event="tool_success",
            tool_name=tool_name,
            latency_ms=latency_ms,
            result_size=ctx.get("result_size", 0),
            request_id=request_id,
        )

    except Exception as e:
        latency_ms = round((time.time() - start) * 1000)
        _emit(
            severity="ERROR",
            message=f"Tool failed: {tool_name}",
            event="tool_error",
            tool_name=tool_name,
            latency_ms=latency_ms,
            error_type=type(e).__name__,
            error_message=str(e),
            request_id=request_id,
        )
        raise  # Re-raise so caller handles it


# ── Gemini call logging ────────────────────────────────────
@contextmanager
def log_gemini_call(call_type: str, request_id: str):
    """
    Context manager to wrap Gemini API calls.
    call_type: 'planning' | 'synthesis'

    Usage:
        with log_gemini_call("planning", request_id) as ctx:
            response = client.models.generate_content(...)
            ctx["token_count"] = response.usage_metadata.total_token_count
    """
    start = time.time()
    ctx = {}

    try:
        yield ctx
        latency_ms = round((time.time() - start) * 1000)
        _emit(
            severity="INFO",
            message=f"Gemini call succeeded: {call_type}",
            event="gemini_call_success",
            call_type=call_type,
            latency_ms=latency_ms,
            input_tokens=ctx.get("input_tokens", 0),
            output_tokens=ctx.get("output_tokens", 0),
            total_tokens=ctx.get("total_tokens", 0),
            request_id=request_id,
        )

    except Exception as e:
        latency_ms = round((time.time() - start) * 1000)
        _emit(
            severity="ERROR",
            message=f"Gemini call failed: {call_type}",
            event="gemini_call_error",
            call_type=call_type,
            latency_ms=latency_ms,
            error_type=type(e).__name__,
            error_message=str(e),
            request_id=request_id,
        )
        raise


# ── Error logging ──────────────────────────────────────────
def log_error(message: str, error: Exception, request_id: str = "unknown", **extra):
    """
    Log an unhandled error with full stack trace.
    """
    _emit(
        severity="ERROR",
        message=message,
        event="unhandled_error",
        error_type=type(error).__name__,
        error_message=str(error),
        stack_trace=traceback.format_exc(),
        request_id=request_id,
        **extra,
    )


# ── Startup log ────────────────────────────────────────────
def log_startup():
    """Log service startup — useful for deployment verification."""
    _emit(
        severity="INFO",
        message="Nova assistant starting up",
        event="startup",
        environment="cloud_run" if IS_CLOUD_RUN else "local",
        project_id=PROJECT_ID,
        gemini_key_present=bool(os.environ.get("GEMINI_API_KEY")),
        tavily_key_present=bool(os.environ.get("TAVILY_API_KEY")),
    )
