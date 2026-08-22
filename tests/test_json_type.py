import json
from typing import Annotated, Any

from fastapi import Cookie, FastAPI, Form, Header, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, Json

app = FastAPI()


@app.post("/form-json-list")
def form_json_list(items: Annotated[Json[list[str]], Form()]) -> list[str]:
    return items


@app.get("/query-json-list")
def query_json_list(items: Annotated[Json[list[str]], Query()]) -> list[str]:
    return items


@app.get("/header-json-list")
def header_json_list(x_items: Annotated[Json[list[str]], Header()]) -> list[str]:
    return x_items


@app.get("/cookie-json-list")
def cookie_json_list(items: Annotated[Json[list[str]], Cookie()]) -> list[str]:
    return items


@app.post("/form-json-list-optional")
def form_json_list_optional(items: Annotated[Json[list[str]] | None, Form()] = None) -> list[str] | None:
    return items


@app.get("/query-json-list-optional")
def query_json_list_optional(items: Annotated[Json[list[str]] | None, Query()] = None) -> list[str] | None:
    return items


@app.get("/header-json-list-optional")
def header_json_list_optional(x_items: Annotated[Json[list[str]] | None, Header()] = None) -> list[str] | None:
    return x_items


@app.get("/cookie-json-list-optional")
def cookie_json_list_optional(items: Annotated[Json[list[str]] | None, Cookie()] = None) -> list[str] | None:
    return items


class Item(BaseModel):
    name: str
    number: int


@app.post("/form-json-model-list-optional")
def form_json_model_list_optional(
    items: Annotated[Json[list[Item]] | None, Form()] = None
) -> list[dict[str, Any]] | None:
    if items is None:
        return None
    return [item.model_dump() for item in items]


@app.post("/form-json-model-single-optional")
def form_json_model_single_optional(
    item: Annotated[Json[Item] | None, Form()] = None
) -> dict[str, Any] | None:
    if item is None:
        return None
    return item.model_dump()


client = TestClient(app)


def test_form_json_list():
    response = client.post(
        "/form-json-list", data={"items": json.dumps(["abc", "def"])}
    )
    assert response.status_code == 200, response.text
    assert response.json() == ["abc", "def"]


def test_query_json_list():
    response = client.get(
        "/query-json-list", params={"items": json.dumps(["abc", "def"])}
    )
    assert response.status_code == 200, response.text
    assert response.json() == ["abc", "def"]


def test_header_json_list():
    response = client.get(
        "/header-json-list", headers={"x-items": json.dumps(["abc", "def"])}
    )
    assert response.status_code == 200, response.text
    assert response.json() == ["abc", "def"]


def test_cookie_json_list():
    client.cookies.set("items", json.dumps(["abc", "def"]))
    response = client.get("/cookie-json-list")
    assert response.status_code == 200, response.text
    assert response.json() == ["abc", "def"]
    client.cookies.clear()


def test_form_json_list_optional():
    response = client.post(
        "/form-json-list-optional", data={"items": json.dumps(["abc", "def"])}
    )
    assert response.status_code == 200, response.text
    assert response.json() == ["abc", "def"]

    response = client.post("/form-json-list-optional")
    assert response.status_code == 200, response.text
    assert response.json() is None


def test_query_json_list_optional():
    response = client.get(
        "/query-json-list-optional", params={"items": json.dumps(["abc", "def"])}
    )
    assert response.status_code == 200, response.text
    assert response.json() == ["abc", "def"]

    response = client.get("/query-json-list-optional")
    assert response.status_code == 200, response.text
    assert response.json() is None


def test_header_json_list_optional():
    response = client.get(
        "/header-json-list-optional", headers={"x-items": json.dumps(["abc", "def"])}
    )
    assert response.status_code == 200, response.text
    assert response.json() == ["abc", "def"]

    response = client.get("/header-json-list-optional")
    assert response.status_code == 200, response.text
    assert response.json() is None


def test_cookie_json_list_optional():
    client.cookies.set("items", json.dumps(["abc", "def"]))
    response = client.get("/cookie-json-list-optional")
    assert response.status_code == 200, response.text
    assert response.json() == ["abc", "def"]
    client.cookies.clear()

    response = client.get("/cookie-json-list-optional")
    assert response.status_code == 200, response.text
    assert response.json() is None


def test_form_json_model_list_optional():
    payload = '[{"name": "first", "number": 1}, {"name": "second", "number": 2}]'
    response = client.post("/form-json-model-list-optional", data={"items": payload})
    assert response.status_code == 200, response.text
    assert response.json() == [
        {"name": "first", "number": 1},
        {"name": "second", "number": 2},
    ]

    response = client.post("/form-json-model-list-optional")
    assert response.status_code == 200, response.text
    assert response.json() is None


def test_form_json_model_single_optional():
    payload = '{"name": "first", "number": 1}'
    response = client.post("/form-json-model-single-optional", data={"item": payload})
    assert response.status_code == 200, response.text
    assert response.json() == {"name": "first", "number": 1}

    response = client.post("/form-json-model-single-optional")
    assert response.status_code == 200, response.text
    assert response.json() is None


