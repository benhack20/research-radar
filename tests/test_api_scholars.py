import pytest
from fastapi.testclient import TestClient
import base64
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from backend.app.main import app

def basic_auth_header(username: str, password: str) -> str:
    import base64
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {token}"

client = TestClient(app)

def test_scholars_search_normal():
    """
    正常场景：输入合法姓名，返回学者列表。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get("/api/scholars", params={"name": "李明", "size": 2}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert isinstance(data["data"], list)

def test_scholars_search_empty_name():
    """
    边界场景：姓名为空，返回422。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get("/api/scholars", params={"name": ""}, headers=headers)
    assert resp.status_code == 422
    assert "error" in resp.text or "detail" in resp.text

def test_scholars_search_invalid_size():
    """
    异常场景：size参数非法，返回422。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get("/api/scholars", params={"name": "李明", "size": -1}, headers=headers)
    assert resp.status_code == 422

def test_scholars_search_no_result():
    """
    正常场景：姓名不存在，返回空列表。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get("/api/scholars", params={"name": "不存在的名字"}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert isinstance(data.get("data"), list)
    # 允许空列表或无结果

def test_scholars_search_permission():
    """
    权限场景：未认证用户访问，返回401。
    """
    resp = client.get("/api/scholars", params={"name": "李明"})
    assert resp.status_code == 401 or resp.status_code == 403 