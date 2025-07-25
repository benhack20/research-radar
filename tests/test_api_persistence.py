import pytest
from fastapi.testclient import TestClient
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from backend.app.main import app
from backend.app.persistence.models import Base, Scholar, Paper, Patent, SyncLog
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

# 工具函数：读取真实paper和patent数据

def load_real_paper():
    """
    从aminer/demo/paper.json读取首条真实论文数据。
    """
    with open(os.path.join(os.path.dirname(__file__), '../aminer/demo/paper.json'), encoding='utf-8') as f:
        data = json.load(f)
    return data["data"][0]["data"]["hitList"][0]

def load_real_patent():
    """
    从aminer/demo/patents.json读取首条真实专利数据。
    """
    with open(os.path.join(os.path.dirname(__file__), '../aminer/demo/patents.json'), encoding='utf-8') as f:
        data = json.load(f)
    return data["data"]["hitList"][0]

def load_real_person():
    with open(os.path.join(os.path.dirname(__file__), '../aminer/demo/person_detail.json'), encoding='utf-8') as f:
        data = json.load(f)
    return data["data"][0]["data"][0]

def basic_auth_header(username: str, password: str) -> str:
    import base64
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {token}"

client = TestClient(app)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("请设置DATABASE_URL环境变量，格式如：postgresql+psycopg2://user:password@host:5432/dbname")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@pytest.fixture(autouse=True)
def clean_db():
    """每个测试前清理所有表，保证测试隔离。"""
    session = Session()
    session.query(Paper).delete()
    session.query(Patent).delete()
    session.query(Scholar).delete()
    session.query(SyncLog).delete()
    session.commit()
    session.close()

# ------------------ 学者API持久化测试 ------------------
def test_create_and_get_scholar():
    """
    测试新增学者并查询详情，使用真实person_detail.json数据。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    person = load_real_person()
    scholar_data = {
        "aminer_id": person["id"],
        "name": person["name"],
        "name_zh": person.get("name_zh", ""),
        "avatar": person.get("avatar", ""),
        "nation": person.get("nation", ""),
        "indices": person.get("indices", {}),
        "links": person.get("links", {}),
        "profile": person.get("profile", {}),
        "tags": person.get("tags", []),
        "tags_score": person.get("tags_score", []),
        "tags_zh": person.get("tags_zh", []),
        "num_followed": person.get("num_followed", 0),
        "num_upvoted": person.get("num_upvoted", 0),
        "num_viewed": person.get("num_viewed", 0),
        "gender": person.get("profile", {}).get("gender", ""),
        "homepage": person.get("profile", {}).get("homepage", ""),
        "position": person.get("profile", {}).get("position", ""),
        "position_zh": person.get("profile", {}).get("position_zh", ""),
        "work": person.get("profile", {}).get("work", ""),
        "work_zh": person.get("profile", {}).get("work_zh", ""),
        "note": person.get("profile", {}).get("note", "")
    }
    # 新增
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    assert resp.status_code == 201
    scholar_id = resp.json().get("id")
    # 查询详情
    resp = client.get(f"/api/scholars/{scholar_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    for k in scholar_data:
        assert data[k] == scholar_data[k]

def test_update_scholar():
    """
    测试更新学者信息。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    scholar_data = {"aminer_id": "A010", "name": "原名"}
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    scholar_id = resp.json()["id"]
    update_data = {"name": "新名字", "nation": "USA", "tags": ["NLP"]}
    resp = client.put(f"/api/scholars/{scholar_id}", json=update_data, headers=headers)
    assert resp.status_code == 200
    resp = client.get(f"/api/scholars/{scholar_id}", headers=headers)
    assert resp.json()["name"] == "新名字"
    assert resp.json()["nation"] == "USA"
    assert resp.json()["tags"] == ["NLP"]

def test_delete_scholar():
    """
    测试删除学者。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    scholar_data = {"aminer_id": "A011", "name": "待删除"}
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    scholar_id = resp.json()["id"]
    resp = client.delete(f"/api/scholars/{scholar_id}", headers=headers)
    assert resp.status_code == 204
    resp = client.get(f"/api/scholars/{scholar_id}", headers=headers)
    assert resp.status_code == 404

# ------------------ 论文API持久化测试 ------------------
def test_create_and_get_paper():
    """
    用aminer/demo/paper.json真实数据测试论文API持久化。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    # 先插入学者
    real_paper = load_real_paper()
    scholar_data = {
        "aminer_id": real_paper["authors"][-1].get("id", "A999"),
        "name": real_paper["authors"][-1]["name"],
        "name_zh": "测试作者",
        "avatar": "http://example.com/avatar.jpg",
        "nation": "China",
        "indices": {"hindex": 5},
        "tags": ["AI"]
    }
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    scholar_id = resp.json()["id"]
    # 取真实paper数据
    paper_data = {
        "aminer_id": real_paper["id"],
        "scholar_id": scholar_id,
        "title": real_paper["title"],
        "abstract": real_paper["abstract"],
        "authors": json.dumps(real_paper["authors"]),
        "create_time": real_paper["create_time"],
        "lang": real_paper["lang"],
        "num_citation": real_paper["num_citation"],
        "pdf": real_paper["pdf"],
        "urls": json.dumps(real_paper["urls"]),
        "versions": json.dumps(real_paper["versions"]),
        "year": real_paper["year"],
        "update_times": json.dumps(real_paper["update_times"])
    }
    resp = client.post("/api/papers", json=paper_data, headers=headers)
    assert resp.status_code == 201
    paper_id = resp.json()["id"]
    # 查询详情
    resp = client.get(f"/api/papers/{paper_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["aminer_id"] == paper_data["aminer_id"]
    assert data["title"] == paper_data["title"]
    assert data["year"] == paper_data["year"]
    assert data["lang"] == paper_data["lang"]
    assert data["num_citation"] == paper_data["num_citation"]
    assert data["pdf"] == paper_data["pdf"]
    assert json.loads(data["authors"])[-1]["name"] == real_paper["authors"][-1]["name"]
    assert json.loads(data["urls"])[0].startswith("https://www.alphaxiv.org/")
    assert json.loads(data["versions"])[0]["src"] == "alphaxiv"
    assert "u_a_t" in json.loads(data["update_times"])

def test_update_paper():
    """
    测试更新论文信息，使用真实paper数据。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    real_paper = load_real_paper()
    scholar_data = {
        "aminer_id": real_paper["authors"][-1].get("id", "A997"),
        "name": real_paper["authors"][-1]["name"],
        "name_zh": "测试作者",
        "avatar": "http://example.com/avatar.jpg",
        "nation": "China",
        "indices": {"hindex": 5},
        "tags": ["AI"]
    }
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    scholar_id = resp.json()["id"]
    paper_data = {"aminer_id": real_paper["id"] + "_upd", "scholar_id": scholar_id, "title": real_paper["title"]}
    resp = client.post("/api/papers", json=paper_data, headers=headers)
    paper_id = resp.json()["id"]
    update_data = {"title": real_paper["title"] + "-更新"}
    resp = client.put(f"/api/papers/{paper_id}", json=update_data, headers=headers)
    assert resp.status_code == 200
    resp = client.get(f"/api/papers/{paper_id}", headers=headers)
    assert resp.json()["title"] == update_data["title"]

def test_delete_paper():
    """
    测试删除论文，使用真实paper数据。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    real_paper = load_real_paper()
    scholar_data = {
        "aminer_id": real_paper["authors"][-1].get("id", "A996"),
        "name": real_paper["authors"][-1]["name"],
        "name_zh": "测试作者",
        "avatar": "http://example.com/avatar.jpg",
        "nation": "China",
        "indices": {"hindex": 5},
        "tags": ["AI"]
    }
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    scholar_id = resp.json()["id"]
    paper_data = {"aminer_id": real_paper["id"] + "_del", "scholar_id": scholar_id, "title": real_paper["title"]}
    resp = client.post("/api/papers", json=paper_data, headers=headers)
    paper_id = resp.json()["id"]
    resp = client.delete(f"/api/papers/{paper_id}", headers=headers)
    assert resp.status_code == 204
    resp = client.get(f"/api/papers/{paper_id}", headers=headers)
    assert resp.status_code == 404

# ------------------ 专利API持久化测试 ------------------
def test_create_and_get_patent():
    """
    用aminer/demo/patents.json真实数据测试专利API持久化。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    # 先插入学者
    real_patent = load_real_patent()
    scholar_data = {
        "aminer_id": real_patent["inventor"][1].get("personId", "A995"),
        "name": real_patent["inventor"][1]["name"],
        "name_zh": "测试作者",
        "avatar": "http://example.com/avatar.jpg",
        "nation": "China",
        "indices": {"hindex": 5},
        "tags": ["AI"]
    }
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    scholar_id = resp.json()["id"]
    # 取真实patent数据
    patent_data = {
        "aminer_id": real_patent["id"],
        "scholar_id": scholar_id,
        "title": json.dumps(real_patent["title"]),
        "abstract": json.dumps(real_patent["abstract"]),
        "app_date": real_patent["appDate"],
        "app_num": real_patent["appNum"],
        "applicant": json.dumps(real_patent["applicant"]),
        "assignee": json.dumps(real_patent["assignee"]),
        "country": real_patent["country"],
        "cpc": json.dumps(real_patent["cpc"]),
        "inventor": json.dumps(real_patent["inventor"]),
        "ipc": json.dumps(real_patent["ipc"]),
        "ipcr": json.dumps(real_patent["ipcr"]),
        "pct": json.dumps(real_patent["pct"]),
        "priority": json.dumps(real_patent["priority"]),
        "pub_date": real_patent["pubDate"],
        "pub_kind": real_patent["pubKind"],
        "pub_num": real_patent["pubNum"],
        "pub_search_id": real_patent["pubSearchId"]
    }
    resp = client.post("/api/patents", json=patent_data, headers=headers)
    assert resp.status_code == 201
    patent_id = resp.json()["id"]
    # 查询详情
    resp = client.get(f"/api/patents/{patent_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["aminer_id"] == patent_data["aminer_id"]
    assert json.loads(data["title"])["zh"][0] == real_patent["title"]["zh"][0]
    assert data["app_num"] == patent_data["app_num"]
    assert data["country"] == "CN"
    assert json.loads(data["applicant"])[0]["name"] == "清华大学"
    assert json.loads(data["assignee"])[0]["name"].startswith("UNIV TSINGHUA")
    assert json.loads(data["inventor"])[1]["name"] == "喻纯"
    assert json.loads(data["ipc"])[0]["l4"] == "G06F003/01"
    assert json.loads(data["ipcr"])[0]["l4"] == "G06F3/01"
    assert data["pub_date"] == real_patent["pubDate"]
    assert data["pub_kind"] == real_patent["pubKind"]
    assert data["pub_num"] == real_patent["pubNum"]
    assert data["pub_search_id"] == real_patent["pubSearchId"]

def test_update_patent():
    """
    测试更新专利信息，使用真实patent数据。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    real_patent = load_real_patent()
    scholar_data = {
        "aminer_id": real_patent["inventor"][1].get("personId", "A994"),
        "name": real_patent["inventor"][1]["name"],
        "name_zh": "测试作者",
        "avatar": "http://example.com/avatar.jpg",
        "nation": "China",
        "indices": {"hindex": 5},
        "tags": ["AI"]
    }
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    scholar_id = resp.json()["id"]
    patent_data = {"aminer_id": real_patent["id"] + "_upd", "scholar_id": scholar_id, "title": json.dumps(real_patent["title"])}
    resp = client.post("/api/patents", json=patent_data, headers=headers)
    patent_id = resp.json()["id"]
    update_data = {"app_num": real_patent["appNum"] + "NEW"}
    resp = client.put(f"/api/patents/{patent_id}", json=update_data, headers=headers)
    assert resp.status_code == 200
    resp = client.get(f"/api/patents/{patent_id}", headers=headers)
    assert resp.json()["app_num"] == update_data["app_num"]

def test_delete_patent():
    """
    测试删除专利，使用真实patent数据。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    real_patent = load_real_patent()
    scholar_data = {
        "aminer_id": real_patent["inventor"][1].get("personId", "A993"),
        "name": real_patent["inventor"][1]["name"],
        "name_zh": "测试作者",
        "avatar": "http://example.com/avatar.jpg",
        "nation": "China",
        "indices": {"hindex": 5},
        "tags": ["AI"]
    }
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    scholar_id = resp.json()["id"]
    patent_data = {"aminer_id": real_patent["id"] + "_del", "scholar_id": scholar_id, "title": json.dumps(real_patent["title"])}
    resp = client.post("/api/patents", json=patent_data, headers=headers)
    patent_id = resp.json()["id"]
    resp = client.delete(f"/api/patents/{patent_id}", headers=headers)
    assert resp.status_code == 204
    resp = client.get(f"/api/patents/{patent_id}", headers=headers)
    assert resp.status_code == 404

# ------------------ 权限与异常场景 ------------------
def test_create_scholar_no_auth():
    """
    未认证用户新增学者，返回401。
    """
    resp = client.post("/api/scholars", json={"aminer_id": "A004", "name": "无权用户"})
    assert resp.status_code == 401 or resp.status_code == 403

def test_create_duplicate_scholar():
    """
    新增重复aminer_id学者，返回409。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    scholar_data = {"aminer_id": "A005", "name": "重复用户"}
    resp1 = client.post("/api/scholars", json=scholar_data, headers=headers)
    resp2 = client.post("/api/scholars", json=scholar_data, headers=headers)
    assert resp2.status_code == 409 

def test_update_nonexistent_scholar():
    """
    更新不存在的学者，返回404。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.put("/api/scholars/99999", json={"name": "不存在"}, headers=headers)
    assert resp.status_code == 404

def test_delete_nonexistent_paper():
    """
    删除不存在的论文，返回404。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    resp = client.delete("/api/papers/99999", headers=headers)
    assert resp.status_code == 404 


# ------------------ 首页统计数据测试 ------------------
def test_dashboard_stats():
    """
    测试首页统计数据接口，验证总数和今日新增。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    # 初始应为0
    resp = client.get("/api/dashboard/stats", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["totalScholars"] == 0
    assert data["totalPapers"] == 0
    assert data["totalPatents"] == 0
    assert data["recentUpdates"] == 0

    # 新增一名学者、一篇论文、一项专利，created_at为今天
    scholar_data = {"aminer_id": "DASH001", "name": "首页统计学者"}
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    assert resp.status_code == 201
    scholar_id = resp.json()["id"]

    paper_data = {"aminer_id": "DASHP001", "scholar_id": scholar_id, "title": "首页统计论文"}
    resp = client.post("/api/papers", json=paper_data, headers=headers)
    assert resp.status_code == 201
    paper_id = resp.json()["id"]

    patent_data = {"aminer_id": "DASHT001", "scholar_id": scholar_id, "title": "首页统计专利"}
    resp = client.post("/api/patents", json=patent_data, headers=headers)
    assert resp.status_code == 201
    patent_id = resp.json()["id"]

    # 再次请求统计接口
    resp = client.get("/api/dashboard/stats", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["totalScholars"] == 1
    assert data["totalPapers"] == 1
    assert data["totalPatents"] == 1
    # 今日新增应为3
    assert data["recentUpdates"] == 3 

def test_dashboard_stats_mom():
    """
    测试首页统计数据接口的环比增长（较上月）字段。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    # 初始应为0，环比为0
    resp = client.get("/api/dashboard/stats", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["totalScholarsMoM"] == 0.0
    assert data["totalPapersMoM"] == 0.0
    assert data["totalPatentsMoM"] == 0.0

    # 构造一条上月数据
    from backend.app.persistence.models import Scholar, Paper, Patent
    from datetime import datetime, timedelta
    session = Session()
    last_month = (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1)
    s = Scholar(aminer_id="MOM001", name="上月学者", created_at=last_month)
    session.add(s)
    session.commit()
    p = Paper(aminer_id="MOMP001", scholar_id=s.id, title="上月论文", created_at=last_month)
    t = Patent(aminer_id="MOMT001", scholar_id=s.id, title="上月专利", created_at=last_month)
    session.add_all([p, t])
    session.commit()
    session.close()

    # 再查，环比应为0（本月与上月持平）
    resp = client.get("/api/dashboard/stats", headers=headers)
    data = resp.json()
    assert data["totalScholars"] == 1
    assert data["totalPapers"] == 1
    assert data["totalPatents"] == 1
    assert data["totalScholarsMoM"] == 0.0
    assert data["totalPapersMoM"] == 0.0
    assert data["totalPatentsMoM"] == 0.0

    # 新增一条本月数据，环比应为100%
    scholar_data = {"aminer_id": "MOM002", "name": "本月学者"}
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    scholar_id = resp.json()["id"]
    paper_data = {"aminer_id": "MOMP002", "scholar_id": scholar_id, "title": "本月论文"}
    client.post("/api/papers", json=paper_data, headers=headers)
    patent_data = {"aminer_id": "MOMT002", "scholar_id": scholar_id, "title": "本月专利"}
    client.post("/api/patents", json=patent_data, headers=headers)

    resp = client.get("/api/dashboard/stats", headers=headers)
    data = resp.json()
    assert data["totalScholars"] == 2
    assert data["totalPapers"] == 2
    assert data["totalPatents"] == 2
    assert data["totalScholarsMoM"] == 100.0
    assert data["totalPapersMoM"] == 100.0
    assert data["totalPatentsMoM"] == 100.0 

def test_get_recent_activities():
    """
    用aminer/demo/paper.json和patents.json真实数据测试最近活动API。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    # 插入学者
    real_paper = load_real_paper()
    real_patent = load_real_patent()
    scholar_data = {"aminer_id": real_paper["authors"][-1].get("id", "A900"), "name": real_paper["authors"][-1]["name"]}
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    scholar_id = resp.json()["id"]
    # 插入论文
    paper_data = {
        "aminer_id": real_paper["id"] + "_act",
        "scholar_id": scholar_id,
        "title": real_paper["title"]
    }
    resp = client.post("/api/papers", json=paper_data, headers=headers)
    assert resp.status_code == 201
    # 插入专利
    patent_data = {
        "aminer_id": real_patent["id"] + "_act",
        "scholar_id": scholar_id,
        "title": json.dumps(real_patent["title"])
    }
    resp = client.post("/api/patents", json=patent_data, headers=headers)
    assert resp.status_code == 201
    # 查询最近活动
    resp = client.get("/api/activities", headers=headers)
    assert resp.status_code == 200
    activities = resp.json()
    assert isinstance(activities, list)
    # 检查至少包含论文和专利
    types = set(a["type"] for a in activities)
    assert "paper" in types
    assert "patent" in types
    # 检查专利标题为真实数据中的zh或en
    patent_acts = [a for a in activities if a["type"] == "patent"]
    zh = real_patent["title"].get("zh")
    en = real_patent["title"].get("en")
    found = False
    for act in patent_acts:
        if (zh and ((isinstance(zh, list) and zh[0] in act["name"]) or (isinstance(zh, str) and zh in act["name"]))) or \
           (en and ((isinstance(en, list) and en[0] in act["name"]) or (isinstance(en, str) and en in act["name"]))) :
            found = True
    assert found, "专利标题未正确解析"
    # 检查时间字段为ISO格式且带+08:00
    for act in activities:
        assert "T" in act["time"] and "+08:00" in act["time"] 

# ------------------ 论文和专利分页测试 ------------------
def test_papers_list_api_pagination_and_scholar_id():
    """
    测试 /api/papers/list 分页和 scholar_id 筛选功能（插入更多数据，覆盖多页）。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    # 新增两个学者
    scholar1 = client.post("/api/scholars", json={"aminer_id": "S1", "name": "学者1"}, headers=headers).json()
    scholar2 = client.post("/api/scholars", json={"aminer_id": "S2", "name": "学者2"}, headers=headers).json()
    # 新增更多论文
    for i in range(15):
        client.post("/api/papers", json={"aminer_id": f"P1_{i}", "scholar_id": scholar1["id"], "title": f"论文1_{i}"}, headers=headers)
    for i in range(5):
        client.post("/api/papers", json={"aminer_id": f"P2_{i}", "scholar_id": scholar2["id"], "title": f"论文2_{i}"}, headers=headers)
    # 分页获取全部
    resp = client.get("/api/papers/list?size=10&offset=0", headers=headers)
    if resp.status_code != 200:
        print('papers/list 422 detail:', resp.text)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 20
    assert len(data["data"]) == 10
    # 第二页
    resp = client.get("/api/papers/list?size=10&offset=10", headers=headers)
    if resp.status_code != 200:
        print('papers/list 422 detail:', resp.text)
    assert resp.status_code == 200
    data2 = resp.json()
    assert len(data2["data"]) == 10
    # scholar_id筛选
    resp = client.get(f"/api/papers/list?scholar_id={int(scholar1['id'])}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 15
    for p in data["data"]:
        assert p["scholar_id"] == int(scholar1["id"])
    # 边界：无结果
    resp = client.get("/api/papers/list?scholar_id=999999", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["data"] == []

def test_patents_list_api_pagination_and_scholar_id():
    """
    测试 /api/patents/list 分页和 scholar_id 筛选功能（插入更多数据，覆盖多页）。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    # 新增两个学者
    scholar1 = client.post("/api/scholars", json={"aminer_id": "T1", "name": "学者T1"}, headers=headers).json()
    scholar2 = client.post("/api/scholars", json={"aminer_id": "T2", "name": "学者T2"}, headers=headers).json()
    # 新增更多专利
    for i in range(10):
        client.post("/api/patents", json={"aminer_id": f"PT1_{i}", "scholar_id": scholar1["id"], "title": "{}"}, headers=headers)
    for i in range(5):
        client.post("/api/patents", json={"aminer_id": f"PT2_{i}", "scholar_id": scholar2["id"], "title": "{}"}, headers=headers)
    # 分页获取全部
    resp = client.get("/api/patents/list?size=7&offset=0", headers=headers)
    if resp.status_code != 200:
        print('patents/list 422 detail:', resp.text)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 15
    assert len(data["data"]) == 7
    # 第二页
    resp = client.get("/api/patents/list?size=7&offset=7", headers=headers)
    if resp.status_code != 200:
        print('patents/list 422 detail:', resp.text)
    assert resp.status_code == 200
    data2 = resp.json()
    assert len(data2["data"]) == 7
    # scholar_id筛选
    resp = client.get(f"/api/patents/list?scholar_id={int(scholar2['id'])}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    for t in data["data"]:
        assert t["scholar_id"] == int(scholar2["id"])
    # 边界：无结果
    resp = client.get("/api/patents/list?scholar_id=999999", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["data"] == [] 

def test_aminer_detail_api_to_create_scholar():
    """
    测试 /api/scholars/aminer/{aminer_id}/detail 返回的数据能直接用于 /api/scholars 创建学者。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    person = load_real_person()
    aminer_id = person["id"]
    # 获取API返回
    resp = client.get(f"/api/scholars/aminer/{aminer_id}/detail", headers=headers)
    assert resp.status_code == 200
    scholar_data = resp.json()
    # 用返回数据直接创建学者
    resp2 = client.post("/api/scholars", json=scholar_data, headers=headers)
    assert resp2.status_code == 201
    scholar_id = resp2.json()["id"]
    # 再查详情，字段一致
    resp3 = client.get(f"/api/scholars/{scholar_id}", headers=headers)
    assert resp3.status_code == 200
    scholar_db = resp3.json()
    for k in scholar_data:
        assert scholar_db[k] == scholar_data[k] 

def test_batch_create_papers():
    """
    测试 /api/papers/batch 批量插入论文。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    real_paper = load_real_paper()
    # 先插入学者
    scholar_data = {
        "aminer_id": real_paper["authors"][-1].get("id", "A901"),
        "name": real_paper["authors"][-1]["name"]
    }
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    scholar_id = resp.json()["id"]
    # 构造两条论文
    papers = [
        {
            "aminer_id": real_paper["id"] + "_b1",
            "scholar_id": scholar_id,
            "title": real_paper["title"] + "-1"
        },
        {
            "aminer_id": real_paper["id"] + "_b2",
            "scholar_id": scholar_id,
            "title": real_paper["title"] + "-2"
        }
    ]
    resp = client.post("/api/papers/batch", json=papers, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 2
    assert data[0]["aminer_id"].endswith("_b1")
    assert data[1]["aminer_id"].endswith("_b2")
    # 再次插入重复aminer_id，应该失败
    resp = client.post("/api/papers/batch", json=papers, headers=headers)
    assert resp.status_code == 409
    # 未认证
    resp = client.post("/api/papers/batch", json=papers)
    assert resp.status_code in (401, 403)


def test_batch_create_patents():
    """
    测试 /api/patents/batch 批量插入专利。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    real_patent = load_real_patent()
    # 先插入学者
    scholar_data = {
        "aminer_id": real_patent["inventor"][1].get("personId", "A902"),
        "name": real_patent["inventor"][1]["name"]
    }
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    scholar_id = resp.json()["id"]
    # 构造两条专利
    patents = [
        {
            "aminer_id": real_patent["id"] + "_b1",
            "scholar_id": scholar_id,
            "title": "{}"
        },
        {
            "aminer_id": real_patent["id"] + "_b2",
            "scholar_id": scholar_id,
            "title": "{}"
        }
    ]
    resp = client.post("/api/patents/batch", json=patents, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 2
    assert data[0]["aminer_id"].endswith("_b1")
    assert data[1]["aminer_id"].endswith("_b2")
    # 再次插入重复aminer_id，应该失败
    resp = client.post("/api/patents/batch", json=patents, headers=headers)
    assert resp.status_code == 409
    # 未认证
    resp = client.post("/api/patents/batch", json=patents)
    assert resp.status_code in (401, 403) 