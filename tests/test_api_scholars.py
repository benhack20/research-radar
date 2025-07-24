import pytest
from fastapi.testclient import TestClient
import base64
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from backend.app.main import app
from backend.app.persistence.models import Base, Scholar
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()
import json

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@pytest.fixture(autouse=True)
def clean_db():
    session = Session()
    session.query(Scholar).delete()
    session.commit()
    session.close()

def basic_auth_header(username: str, password: str) -> str:
    import base64
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {token}"

client = TestClient(app)

def load_real_persons():
    with open(os.path.join(os.path.dirname(__file__), '../aminer/demo/person_detail.json'), encoding='utf-8') as f:
        data = json.load(f)
    # 兼容结构：data->list->data->list
    persons = data["data"][0]["data"]
    return persons

def insert_real_scholars(n=25):
    session = Session()
    persons = load_real_persons()
    for i in range(n):
        p = persons[i % len(persons)]
        s = Scholar(
            aminer_id=f"TEST{i}_{p['id']}",
            name=p["name"],
            name_zh=p.get("name_zh", ""),
            avatar=p.get("avatar", ""),
            nation=p.get("nation", ""),
            indices=p.get("indices", {}),
            links=p.get("links", {}),
            profile=p.get("profile", {}),
            tags=p.get("tags", []),
            tags_score=p.get("tags_score", []),
            tags_zh=p.get("tags_zh", []),
            num_followed=p.get("num_followed", 0),
            num_upvoted=p.get("num_upvoted", 0),
            num_viewed=p.get("num_viewed", 0),
            gender=p.get("profile", {}).get("gender", ""),
            homepage=p.get("profile", {}).get("homepage", ""),
            position=p.get("profile", {}).get("position", ""),
            position_zh=p.get("profile", {}).get("position_zh", ""),
            work=p.get("profile", {}).get("work", ""),
            work_zh=p.get("profile", {}).get("work_zh", ""),
            note=p.get("profile", {}).get("note", "")
        )
        session.add(s)
    session.commit()
    session.close()

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

def test_scholars_list_normal():
    insert_real_scholars(25)
    """
    正常场景：分页获取学者列表。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get("/api/scholars/list", params={"size": 10, "offset": 0}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "data" in data and "total" in data
    assert isinstance(data["data"], list)
    assert isinstance(data["total"], int)
    assert data["total"] == 25
    assert len(data["data"]) == 10


def test_scholars_list_pagination():
    insert_real_scholars(25)
    """
    分页场景：请求不同页码，数据不重复。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp1 = client.get("/api/scholars/list", params={"size": 10, "offset": 0}, headers=headers)
    resp2 = client.get("/api/scholars/list", params={"size": 10, "offset": 10}, headers=headers)
    assert resp1.status_code == 200 and resp2.status_code == 200
    data1 = resp1.json()["data"]
    data2 = resp2.json()["data"]
    ids1 = set(s["id"] for s in data1)
    ids2 = set(s["id"] for s in data2)
    assert ids1.isdisjoint(ids2)
    assert len(data1) == 10 and len(data2) == 10


def test_scholars_list_empty():
    insert_real_scholars(25)
    """
    边界场景：offset超出范围，返回空列表。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get("/api/scholars/list", params={"size": 10, "offset": 100}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["data"], list)
    assert data["data"] == [] or len(data["data"]) == 0


def test_scholars_list_invalid_param():
    insert_real_scholars(25)
    """
    异常场景：size非法，返回422。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.get("/api/scholars/list", params={"size": -1, "offset": 0}, headers=headers)
    assert resp.status_code == 422


def test_scholars_list_permission():
    insert_real_scholars(25)
    """
    权限场景：未认证用户访问，返回401。
    """
    resp = client.get("/api/scholars/list", params={"size": 2, "offset": 0})
    assert resp.status_code == 401 or resp.status_code == 403 