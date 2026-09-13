from collections.abc import AsyncIterable
from typing import Any

from fastapi import BackgroundTasks, FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent
from fastapi.testclient import TestClient


class CustomEventSourceResponse(EventSourceResponse):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.headers["X-Custom-SSE"] = "active"
        self.headers["X-AI-Model"] = "gpt-4-stream"


class CachedEventSourceResponse(EventSourceResponse):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.headers["Cache-Control"] = "public, max-age=120"


def test_custom_sse_subclass_headers_preserved() -> None:
    app = FastAPI()

    @app.get("/stream", response_class=CustomEventSourceResponse)
    async def sse_stream() -> AsyncIterable[ServerSentEvent]:
        yield ServerSentEvent(data="token-1", event="message")
        yield ServerSentEvent(data="token-2", event="message")

    client = TestClient(app)
    response = client.get("/stream")
    assert response.status_code == 200
    assert response.headers["x-custom-sse"] == "active"
    assert response.headers["x-ai-model"] == "gpt-4-stream"
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["cache-control"] == "no-cache"
    assert response.headers["x-accel-buffering"] == "no"
    assert 'data: "token-1"' in response.text
    assert 'data: "token-2"' in response.text


def test_custom_sse_subclass_cache_control_override() -> None:
    app = FastAPI()

    @app.get("/cached-stream", response_class=CachedEventSourceResponse)
    async def sse_cached_stream() -> AsyncIterable[ServerSentEvent]:
        yield ServerSentEvent(data={"chunk": 1})

    client = TestClient(app)
    response = client.get("/cached-stream")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=120"
    assert response.headers["x-accel-buffering"] == "no"
    assert "chunk" in response.text


def test_custom_sse_subclass_with_background_task() -> None:
    task_ran = False

    def background_task() -> None:
        nonlocal task_ran
        task_ran = True

    app = FastAPI()

    @app.get("/bg-stream", response_class=CustomEventSourceResponse)
    async def sse_bg(bg: BackgroundTasks) -> AsyncIterable[str]:
        bg.add_task(background_task)
        yield "event-data"

    client = TestClient(app)
    response = client.get("/bg-stream")
    assert response.status_code == 200
    assert response.headers["x-custom-sse"] == "active"
    assert task_ran is True
