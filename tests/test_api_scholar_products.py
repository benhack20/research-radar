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

SCHOLAR_ID = "56066a5245cedb339687488b"  # 示例ID

# --- 论文接口测试 ---
def test_papers_normal():
    """
    正常场景：合法学者ID，返回论文列表。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get(f"/api/scholars/{SCHOLAR_ID}/papers", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "hitList" in data
    assert "hitsTotal" in data
    assert isinstance(data["hitList"], list)
    assert isinstance(data["hitsTotal"], int)
    assert data["hitsTotal"] > 0
    assert len(data["hitList"]) > 0
    # 如果有数据，校验内容结构
    if data["hitList"]:
        paper = data["hitList"][0]
        assert "title" in paper
        assert "id" in paper
        assert "year" in paper or "create_time" in paper

def test_papers_invalid_id():
    """
    异常场景：非法学者ID，返回500或空。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get("/api/scholars/invalid_id/papers", headers=headers)
    assert resp.status_code in (200, 500)

def test_papers_permission():
    """
    权限场景：未认证用户访问，返回401。
    """
    resp = client.get(f"/api/scholars/{SCHOLAR_ID}/papers")
    assert resp.status_code == 401 or resp.status_code == 403

# --- 专利接口测试 ---
def test_patents_normal():
    """
    正常场景：合法学者ID，返回专利列表。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get(f"/api/scholars/{SCHOLAR_ID}/patents", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "hitList" in data
    assert "hitsTotal" in data
    assert isinstance(data["hitList"], list)
    assert isinstance(data["hitsTotal"], int)
    assert data["hitsTotal"] > 0
    assert len(data["hitList"]) > 0
    # 如果有数据，校验内容结构
    if data["hitList"]:
        patent = data["hitList"][0]
        assert "title" in patent
        assert "id" in patent
        assert "appDate" in patent or "pubDate" in patent

def test_patents_invalid_id():
    """
    异常场景：非法学者ID，返回500或空。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get("/api/scholars/invalid_id/patents", headers=headers)
    assert resp.status_code in (200, 500)

def test_patents_permission():
    """
    权限场景：未认证用户访问，返回401。
    """
    resp = client.get(f"/api/scholars/{SCHOLAR_ID}/patents")
    assert resp.status_code == 401 or resp.status_code == 403 