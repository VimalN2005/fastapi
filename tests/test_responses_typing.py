from collections.abc import Mapping
from http import HTTPStatus
from typing import Any, TypedDict

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str


class ResponseMetadata(TypedDict):
    model: type[ErrorResponse]
    description: str


RESPONSES: Mapping[int | str, ResponseMetadata] = {
    int(HTTPStatus.BAD_REQUEST): {
        "model": ErrorResponse,
        "description": "Bad Request Error",
    },
    404: {
        "model": ErrorResponse,
        "description": "Not Found Error",
    },
}


def test_responses_with_typeddict_mapping_on_app_and_route() -> None:
    app = FastAPI(responses=RESPONSES)

    @app.get("/items", responses=RESPONSES)
    def read_items() -> dict[str, str]:
        return {"hello": "world"}

    client = TestClient(app)
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == {"hello": "world"}

    openapi = app.openapi()
    item_responses = openapi["paths"]["/items"]["get"]["responses"]
    assert "400" in item_responses
    assert item_responses["400"]["description"] == "Bad Request Error"
    assert "404" in item_responses
    assert item_responses["404"]["description"] == "Not Found Error"


def test_responses_with_typeddict_mapping_on_router() -> None:
    router = APIRouter(responses=RESPONSES)

    @router.post("/items", responses=RESPONSES)
    def create_item() -> dict[str, str]:
        return {"created": "ok"}

    app = FastAPI()
    app.include_router(router, prefix="/api", responses=RESPONSES)

    client = TestClient(app)
    response = client.post("/api/items")
    assert response.status_code == 200
    assert response.json() == {"created": "ok"}

    openapi = app.openapi()
    item_responses = openapi["paths"]["/api/items"]["post"]["responses"]
    assert "400" in item_responses
    assert "404" in item_responses
