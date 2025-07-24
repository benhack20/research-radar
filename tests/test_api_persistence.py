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
    测试新增学者并查询详情。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    scholar_data = {
        "aminer_id": "A001",
        "name": "张三",
        "org": "清华大学"
    }
    # 新增
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    assert resp.status_code == 201
    scholar_id = resp.json().get("id")
    # 查询详情
    resp = client.get(f"/api/scholars/{scholar_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["aminer_id"] == "A001"
    assert data["name"] == "张三"

def test_update_scholar():
    """
    测试更新学者信息。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    scholar_data = {"aminer_id": "A010", "name": "原名"}
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    scholar_id = resp.json()["id"]
    update_data = {"name": "新名字", "org": "新机构"}
    resp = client.put(f"/api/scholars/{scholar_id}", json=update_data, headers=headers)
    assert resp.status_code == 200
    resp = client.get(f"/api/scholars/{scholar_id}", headers=headers)
    assert resp.json()["name"] == "新名字"
    assert resp.json()["org"] == "新机构"

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
    scholar_data = {"aminer_id": real_paper["authors"][-1].get("id", "A999"), "name": real_paper["authors"][-1]["name"], "org": "清华大学"}
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

def test_paper_list_by_scholar():
    """
    测试按学者ID查询论文列表，使用真实paper数据。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    real_paper = load_real_paper()
    scholar_data = {"aminer_id": real_paper["authors"][-1].get("id", "A998"), "name": real_paper["authors"][-1]["name"]}
    resp = client.post("/api/scholars", json=scholar_data, headers=headers)
    scholar_id = resp.json()["id"]
    paper_data = {
        "aminer_id": real_paper["id"] + "_list",  # 避免冲突
        "scholar_id": scholar_id,
        "title": real_paper["title"]
    }
    client.post("/api/papers", json=paper_data, headers=headers)
    resp = client.get(f"/api/papers?scholar_id={scholar_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(p["aminer_id"] == paper_data["aminer_id"] for p in data)

def test_update_paper():
    """
    测试更新论文信息，使用真实paper数据。
    """
    headers = {"Authorization": basic_auth_header("admin", "admin")}
    real_paper = load_real_paper()
    scholar_data = {"aminer_id": real_paper["authors"][-1].get("id", "A997"), "name": real_paper["authors"][-1]["name"]}
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
    scholar_data = {"aminer_id": real_paper["authors"][-1].get("id", "A996"), "name": real_paper["authors"][-1]["name"]}
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
    scholar_data = {"aminer_id": real_patent["inventor"][1].get("personId", "A995"), "name": real_patent["inventor"][1]["name"], "org": "清华大学"}
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
    scholar_data = {"aminer_id": real_patent["inventor"][1].get("personId", "A994"), "name": real_patent["inventor"][1]["name"]}
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
    scholar_data = {"aminer_id": real_patent["inventor"][1].get("personId", "A993"), "name": real_patent["inventor"][1]["name"]}
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
    scholar_data = {"aminer_id": real_paper["authors"][-1].get("id", "A900"), "name": real_paper["authors"][-1]["name"], "org": "清华大学"}
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