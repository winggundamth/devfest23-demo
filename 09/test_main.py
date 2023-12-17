import pytest

from main import app

from fastapi.testclient import TestClient

@pytest.mark.parametrize(
    "path, expected_status_code, expected_json",
    [
        ("/", 200, {"Hello": "World v4"}),
        ("/items/1", 200, {"item_id": 1, "q": None}),
        ("/io_task", 200, "IO bound task finish!"),
        ("/cpu_task", 200, "CPU bound task finish!"),
        ("/random_sleep", 200, {"path": "/random_sleep"}),
        ("/plus/1/2", 200, {"result": 3}),
    ],
)
def test_app(path, expected_status_code, expected_json):
    response = TestClient(app).get(path)
    assert response.status_code == expected_status_code
    assert response.json() == expected_json
