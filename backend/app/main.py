import os
from fastapi import FastAPI, Query, HTTPException, status, Depends, Path, Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
import aminer.api as aminer_api
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError
from backend.app.persistence.models import Base, Scholar, Paper, Patent
import json
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, date, timedelta

app = FastAPI(title="科研成果监测平台API", description="学者检索等RESTful接口", version="0.1.0")

security = HTTPBasic()

def fake_verify_user(credentials: HTTPBasicCredentials = Depends(security)):
    # TODO: 替换为真实用户认证。目前的机制是，如果用户名和密码都为admin，则认为用户已认证。
    if credentials.username != "admin" or credentials.password != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials.username

# 只支持通过环境变量DATABASE_URL配置数据库，必须显式设置
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("请设置DATABASE_URL环境变量，格式如：postgresql+psycopg2://user:password@host:5432/dbname")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/scholars", summary="学者检索", tags=["Scholars"])
def search_scholars(
    name: str = Query(..., description="学者姓名", min_length=1),
    org: Optional[str] = Query(None, description="机构名称"),
    size: int = Query(10, ge=1, le=10, description="返回条数(1-10)"),
    offset: int = Query(0, ge=0, description="偏移量"),
    user: str = Depends(fake_verify_user)
):
    """
    按姓名（可选机构）检索学者信息，返回学者列表。
    - name: 必填，学者姓名
    - org: 可选，机构名称
    - size: 返回条数，1-10
    - offset: 偏移量
    - 权限：需认证
    """
    try:
        resp = aminer_api.search_person_by_name(name=name, org=org or "", size=size, offset=offset)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="AMiner API错误")
        data = resp.json()
        if data.get("code") != 200 or not data.get("success"):
            return {"data": []}
        return {"data": data.get("data", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scholars/{scholar_id}/papers", summary="学者论文列表", tags=["Scholars"])
def get_scholar_papers(
    scholar_id: str = Path(..., description="学者ID"),
    size: int = Query(10, ge=1, description="返回条数(>=1，无上限)"),
    user: str = Depends(fake_verify_user)
):
    """
    查询指定学者的论文列表。
    - scholar_id: 学者ID
    - size: 返回条数，默认10，无上限
    - 权限：需认证
    """
    try:
        result = aminer_api.search_papers_by_scholar_free(scholar_id, size=size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scholars/{scholar_id}/patents", summary="学者专利列表", tags=["Scholars"])
def get_scholar_patents(
    scholar_id: str = Path(..., description="学者ID"),
    size: int = Query(10, ge=1, description="返回条数(>=1，无上限)"),
    user: str = Depends(fake_verify_user)
):
    """
    查询指定学者的专利列表。
    - scholar_id: 学者ID
    - size: 返回条数，默认10，无上限
    - 权限：需认证
    """
    try:
        result = aminer_api.search_patents_by_scholar_free(scholar_id, size=size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import Body

# ------------------ 学者API持久化 ------------------
from pydantic import BaseModel as PBaseModel

class ScholarIn(PBaseModel):
    aminer_id: str
    name: str
    org: str = ""
    name_zh: str = ""
    org_zh: str = ""
    org_id: str = ""
    interests: str = ""
    n_citation: float = 0

class ScholarOut(ScholarIn):
    id: int

@app.post("/api/scholars", response_model=ScholarOut, status_code=201, tags=["Scholars"])
def create_scholar(scholar: ScholarIn, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    obj = Scholar(**scholar.model_dump())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="aminer_id已存在")

@app.get("/api/scholars/{scholar_id}", response_model=ScholarOut, tags=["Scholars"])
def get_scholar(scholar_id: int, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    obj = db.query(Scholar).filter_by(id=scholar_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="学者不存在")
    return obj

class ScholarUpdate(PBaseModel):
    aminer_id: Optional[str] = None
    name: Optional[str] = None
    org: Optional[str] = None
    name_zh: Optional[str] = None
    org_zh: Optional[str] = None
    org_id: Optional[str] = None
    interests: Optional[str] = None
    n_citation: Optional[float] = None

@app.put("/api/scholars/{scholar_id}", response_model=ScholarOut, tags=["Scholars"])
def update_scholar(scholar_id: int, scholar: ScholarUpdate, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    obj = db.query(Scholar).filter_by(id=scholar_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="学者不存在")
    update_data = scholar.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/scholars/{scholar_id}", status_code=204, tags=["Scholars"])
def delete_scholar(scholar_id: int, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    obj = db.query(Scholar).filter_by(id=scholar_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="学者不存在")
    db.delete(obj)
    db.commit()
    return

# ------------------ 论文API持久化 ------------------
class PaperIn(PBaseModel):
    aminer_id: str
    scholar_id: int
    title: str
    abstract: str = ""
    authors: str = ""
    year: int = 0
    lang: str = ""
    num_citation: int = 0
    pdf: str = ""
    urls: str = ""
    versions: str = ""
    create_time: str = ""
    update_times: str = ""

class PaperOut(PaperIn):
    id: int

@app.post("/api/papers", response_model=PaperOut, status_code=201, tags=["Papers"])
def create_paper(paper: PaperIn, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    obj = Paper(**paper.model_dump())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="aminer_id已存在")

@app.get("/api/papers/{paper_id}", response_model=PaperOut, tags=["Papers"])
def get_paper(paper_id: int, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    obj = db.query(Paper).filter_by(id=paper_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="论文不存在")
    return obj

class PaperUpdate(PBaseModel):
    aminer_id: Optional[str] = None
    scholar_id: Optional[int] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    authors: Optional[str] = None
    year: Optional[int] = None
    lang: Optional[str] = None
    num_citation: Optional[int] = None
    pdf: Optional[str] = None
    urls: Optional[str] = None
    versions: Optional[str] = None
    create_time: Optional[str] = None
    update_times: Optional[str] = None

@app.put("/api/papers/{paper_id}", response_model=PaperOut, tags=["Papers"])
def update_paper(paper_id: int, paper: PaperUpdate, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    obj = db.query(Paper).filter_by(id=paper_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="论文不存在")
    update_data = paper.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/papers/{paper_id}", status_code=204, tags=["Papers"])
def delete_paper(paper_id: int, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    obj = db.query(Paper).filter_by(id=paper_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="论文不存在")
    db.delete(obj)
    db.commit()
    return

@app.get("/api/papers", tags=["Papers"])
def list_papers(scholar_id: int = None, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    q = db.query(Paper)
    if scholar_id:
        q = q.filter_by(scholar_id=scholar_id)
    return q.all()

# ------------------ 专利API持久化 ------------------
class PatentIn(PBaseModel):
    aminer_id: str
    scholar_id: int
    title: str
    abstract: str = ""
    app_date: str = ""
    app_num: str = ""
    applicant: str = ""
    assignee: str = ""
    country: str = ""
    cpc: str = ""
    inventor: str = ""
    ipc: str = ""
    ipcr: str = ""
    pct: str = ""
    priority: str = ""
    pub_date: str = ""
    pub_kind: str = ""
    pub_num: str = ""
    pub_search_id: str = ""

class PatentOut(PatentIn):
    id: int

@app.post("/api/patents", response_model=PatentOut, status_code=201, tags=["Patents"])
def create_patent(patent: PatentIn, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    obj = Patent(**patent.model_dump())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="aminer_id已存在")

@app.get("/api/patents/{patent_id}", response_model=PatentOut, tags=["Patents"])
def get_patent(patent_id: int, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    obj = db.query(Patent).filter_by(id=patent_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="专利不存在")
    return obj

class PatentUpdate(PBaseModel):
    aminer_id: Optional[str] = None
    scholar_id: Optional[int] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    app_date: Optional[str] = None
    app_num: Optional[str] = None
    applicant: Optional[str] = None
    assignee: Optional[str] = None
    country: Optional[str] = None
    cpc: Optional[str] = None
    inventor: Optional[str] = None
    ipc: Optional[str] = None
    ipcr: Optional[str] = None
    pct: Optional[str] = None
    priority: Optional[str] = None
    pub_date: Optional[str] = None
    pub_kind: Optional[str] = None
    pub_num: Optional[str] = None
    pub_search_id: Optional[str] = None

@app.put("/api/patents/{patent_id}", response_model=PatentOut, tags=["Patents"])
def update_patent(patent_id: int, patent: PatentUpdate, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    obj = db.query(Patent).filter_by(id=patent_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="专利不存在")
    update_data = patent.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/patents/{patent_id}", status_code=204, tags=["Patents"])
def delete_patent(patent_id: int, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    obj = db.query(Patent).filter_by(id=patent_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="专利不存在")
    db.delete(obj)
    db.commit()
    return 

@app.get("/api/dashboard/stats", summary="首页统计数据", tags=["Dashboard"])
def dashboard_stats(db=Depends(get_db), user: str = Depends(fake_verify_user)):
    today = date.today()
    first_day_this_month = today.replace(day=1)
    # 上月第一天
    if first_day_this_month.month == 1:
        first_day_last_month = first_day_this_month.replace(year=first_day_this_month.year-1, month=12)
    else:
        first_day_last_month = first_day_this_month.replace(month=first_day_this_month.month-1)
    # 上月最后一天
    last_day_last_month = first_day_this_month - timedelta(days=1)

    # 本月总数
    total_scholars = db.query(Scholar).count()
    total_papers = db.query(Paper).count()
    total_patents = db.query(Patent).count()
    # 上月总数（统计created_at<本月1号的数据）
    scholars_last_month = db.query(Scholar).filter(Scholar.created_at < first_day_this_month).count()
    papers_last_month = db.query(Paper).filter(Paper.created_at < first_day_this_month).count()
    patents_last_month = db.query(Patent).filter(Patent.created_at < first_day_this_month).count()
    # 环比增长百分比
    def calc_mom(now, last):
        return round((now - last) / max(last, 1) * 100, 1)
    totalScholarsMoM = calc_mom(total_scholars, scholars_last_month)
    totalPapersMoM = calc_mom(total_papers, papers_last_month)
    totalPatentsMoM = calc_mom(total_patents, patents_last_month)
    # 今日新增
    recent_scholars = db.query(Scholar).filter(Scholar.created_at >= today).count()
    recent_papers = db.query(Paper).filter(Paper.created_at >= today).count()
    recent_patents = db.query(Patent).filter(Patent.created_at >= today).count()
    recent_updates = recent_scholars + recent_papers + recent_patents
    return {
        "totalScholars": total_scholars,
        "totalPapers": total_papers,
        "totalPatents": total_patents,
        "recentUpdates": recent_updates,
        "totalScholarsMoM": totalScholarsMoM,
        "totalPapersMoM": totalPapersMoM,
        "totalPatentsMoM": totalPatentsMoM
    }