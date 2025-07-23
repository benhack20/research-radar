import pytest
from fastapi.testclient import TestClient
import base64
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app.main import app

def basic_auth_header(username: str, password: str) -> str:
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {token}"

client = TestClient(app)

def test_papers_search_by_title_normal():
    """
    正常场景：输入合法论文标题，返回论文信息。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get("/api/papers", params={"title": "A Survey on Graph Neural Networks"}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert isinstance(data["data"], list)

def test_papers_search_by_title_empty():
    """
    边界场景：标题为空，返回422。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get("/api/papers", params={"title": ""}, headers=headers)
    assert resp.status_code == 422

def test_papers_search_by_title_no_result():
    """
    正常场景：标题不存在，返回空列表。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get("/api/papers", params={"title": "不存在的论文标题"}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert isinstance(data.get("data"), list)

def test_papers_search_by_scholar_normal():
    """
    正常场景：输入合法学者ID，返回论文列表。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get("/api/papers", params={"scholar_id": "56066a5245cedb339687488b"}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert isinstance(data["data"], list)

def test_papers_search_by_scholar_invalid():
    """
    异常场景：学者ID非法，返回空列表或错误。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get("/api/papers", params={"scholar_id": "invalid_id"}, headers=headers)
    assert resp.status_code in (200, 400, 404)

def test_papers_search_permission():
    """
    权限场景：未认证用户访问，返回401。
    """
    resp = client.get("/api/papers", params={"title": "A Survey on Graph Neural Networks"})
    assert resp.status_code == 401 or resp.status_code == 403 