import os
from fastapi import FastAPI, Query, HTTPException, status, Depends, Path, Body, Response
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
from datetime import datetime, date, timedelta, timezone, timedelta
from pydantic import BaseModel as PBaseModel, Field
from typing import Optional, Dict, Any, List

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
    功能：
        根据学者姓名（必填）和机构名称（可选）检索学者信息，返回符合条件的学者列表。

    输入参数：
        - name (str): 学者姓名，必填，最小长度1。
        - org (str, 可选): 机构名称，默认为None。
        - size (int): 返回条数，范围1-10，默认10。
        - offset (int): 偏移量，默认0。
        - user (str): 认证用户，需通过认证。

    输出：
        dict: 
            {
                "data": list  # 学者信息列表，每个元素为学者的详细信息字典
            }

    权限要求：
        需要认证用户（用户名和密码均为admin）。

    异常：
        - 若AMiner API请求失败，返回502错误。
        - 若其他异常，返回500错误。
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

@app.get("/api/scholars/list", summary="分页获取全部学者", tags=["Scholars"])
def list_scholars(
    size: int = Query(10, ge=1, le=100, description="每页条数(1-100)"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db=Depends(get_db),
    user: str = Depends(fake_verify_user)
):
    """
    功能：
        分页获取全部学者信息列表。

    输入参数：
        - size (int): 每页返回的学者数量，默认10，最大100。
        - offset (int): 数据偏移量，默认0。
        - db: 数据库会话，由依赖注入提供。
        - user (str): 认证用户，需通过认证。

    输出：
        dict:
            {
                "total": int,   # 学者总数
                "data": list    # 学者信息列表，每个元素为学者的详细信息字典
            }

    权限要求：
        需要认证用户（用户名和密码均为admin）。

    异常：
        - 若数据库查询异常，返回500错误。
    """
    q = db.query(Scholar)
    total = q.count()
    scholars = q.order_by(Scholar.id.desc()).offset(offset).limit(size).all()
    # 序列化
    def scholar_to_dict(obj):
        return {
            "id": obj.id,
            "aminer_id": obj.aminer_id,
            "name": obj.name,
            "name_zh": obj.name_zh,
            "avatar": obj.avatar,
            "nation": obj.nation,
            "indices": obj.indices or {},
            "links": obj.links or {},
            "profile": obj.profile or {},
            "tags": obj.tags or [],
            "tags_score": obj.tags_score or [],
            "tags_zh": obj.tags_zh or [],
            "num_followed": obj.num_followed or 0,
            "num_upvoted": obj.num_upvoted or 0,
            "num_viewed": obj.num_viewed or 0,
            "gender": obj.gender,
            "homepage": obj.homepage,
            "position": obj.position,
            "position_zh": obj.position_zh,
            "work": obj.work,
            "work_zh": obj.work_zh,
            "note": obj.note,
        }
    return {"total": total, "data": [scholar_to_dict(s) for s in scholars]}

@app.get("/api/scholars/aminer/{aminer_id}/detail", summary="AMiner学者详细信息", tags=["Scholars"])
def get_person_detail_by_id_api(
    aminer_id: str = Path(..., description="AMiner学者ID"),
    user: str = Depends(fake_verify_user)
):
    """
    根据AMiner学者ID获取学者详细信息（通过AMiner免费API），并转换为可直接传入create_scholar的格式。
    - aminer_id: AMiner学者ID
    - 权限：需认证
    """
    try:
        detail = aminer_api.get_person_detail_by_id(aminer_id)
        if not detail:
            raise HTTPException(status_code=404, detail="未找到学者详细信息")
        # 字段映射
        scholar_data = {
            "aminer_id": detail.get("id", ""),
            "name": detail.get("name", ""),
            "name_zh": detail.get("name_zh", ""),
            "avatar": detail.get("avatar", ""),
            "nation": detail.get("nation", ""),
            "indices": detail.get("indices") or {},
            "links": detail.get("links") or {},
            "profile": detail.get("profile") or {},
            "tags": detail.get("tags") or [],
            "tags_score": detail.get("tags_score") or [],
            "tags_zh": detail.get("tags_zh") or [],
            "num_followed": detail.get("num_followed") or 0,
            "num_upvoted": detail.get("num_upvoted") or 0,
            "num_viewed": detail.get("num_viewed") or 0,
            "gender": detail.get("profile", {}).get("gender", ""),
            "homepage": detail.get("profile", {}).get("homepage", ""),
            "position": detail.get("profile", {}).get("position", ""),
            "position_zh": detail.get("profile", {}).get("position_zh", ""),
            "work": detail.get("profile", {}).get("work", ""),
            "work_zh": detail.get("profile", {}).get("work_zh", ""),
            "note": detail.get("profile", {}).get("note", ""),
        }
        return scholar_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scholars/{scholar_id}/papers", summary="学者论文列表", tags=["Scholars"])
def get_scholar_papers(
    scholar_id: str = Path(..., description="学者ID"),
    size: int = Query(10, ge=1, description="返回条数(>=1，无上限)"),
    user: str = Depends(fake_verify_user)
):
    """
    从数据源拉取指定学者的论文列表。
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
    从数据源拉取指定学者的专利列表。
    - scholar_id: 学者ID
    - size: 返回条数，默认10，无上限
    - 权限：需认证
    """
    try:
        result = aminer_api.search_patents_by_scholar_free(scholar_id, size=size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------ 学者API持久化 ------------------

class ScholarIn(PBaseModel):
    aminer_id: str
    name: str
    name_zh: Optional[str] = ""
    avatar: Optional[str] = ""
    nation: Optional[str] = ""
    indices: Optional[Dict[str, Any]] = Field(default_factory=dict)
    links: Optional[Dict[str, Any]] = Field(default_factory=dict)
    profile: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tags: Optional[List[str]] = Field(default_factory=list)
    tags_score: Optional[List[int]] = Field(default_factory=list)
    tags_zh: Optional[List[str]] = Field(default_factory=list)
    num_followed: Optional[int] = 0
    num_upvoted: Optional[int] = 0
    num_viewed: Optional[int] = 0
    gender: Optional[str] = ""
    homepage: Optional[str] = ""
    position: Optional[str] = ""
    position_zh: Optional[str] = ""
    work: Optional[str] = ""
    work_zh: Optional[str] = ""
    note: Optional[str] = ""

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
    name_zh: Optional[str] = None
    avatar: Optional[str] = None
    nation: Optional[str] = None
    indices: Optional[Dict[str, Any]] = None
    links: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    tags_score: Optional[List[int]] = None
    tags_zh: Optional[List[str]] = None
    num_followed: Optional[int] = None
    num_upvoted: Optional[int] = None
    num_viewed: Optional[int] = None
    gender: Optional[str] = None
    homepage: Optional[str] = None
    position: Optional[str] = None
    position_zh: Optional[str] = None
    work: Optional[str] = None
    work_zh: Optional[str] = None
    note: Optional[str] = None

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
    """
    插入一条新的论文记录。

    参数:
        paper (PaperIn): 论文输入数据，包含aminer_id、scholar_id、title等字段。
        db: 数据库会话，由依赖注入提供。
        user (str): 认证用户，需通过认证。

    返回:
        PaperOut: 创建成功的论文记录，包含数据库生成的id。

    权限要求:
        需要认证用户（用户名和密码均为admin）。

    异常:
        - 若aminer_id已存在，返回409错误。
    """
    obj = Paper(**paper.model_dump())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="aminer_id已存在")

# --- 将 list 路由提前 ---
@app.get("/api/papers/list", summary="分页获取全部论文", tags=["Papers"])
def list_papers_api(
    size: int = Query(10, ge=1, le=100, description="每页条数(1-100)"),
    offset: int = Query(0, ge=0, description="偏移量"),
    year: Optional[int] = Query(None, description="发表年份"),
    author: Optional[str] = Query(None, description="作者名(模糊包含)"),
    lang: Optional[str] = Query(None, description="语言"),
    min_citation: Optional[int] = Query(None, description="最小引用数"),
    max_citation: Optional[int] = Query(None, description="最大引用数"),
    scholar_id: Optional[int] = Query(None, description="学者ID"),
    db=Depends(get_db),
    user: str = Depends(fake_verify_user)
):
    """
    功能：
        分页获取全部论文信息列表，并支持多条件筛选。
    输入参数：
        - size (int): 每页返回的论文数量，默认10，最大100。
        - offset (int): 数据偏移量，默认0。
        - year (int, 可选): 发表年份。
        - author (str, 可选): 作者名（模糊包含）。
        - lang (str, 可选): 语言。
        - min_citation (int, 可选): 最小引用数。
        - max_citation (int, 可选): 最大引用数。
        - scholar_id (int, 可选): 学者ID。
        - db: 数据库会话，由依赖注入提供。
        - user (str): 认证用户，需通过认证。
    输出：
        dict:
            {
                "total": int,   # 论文总数
                "data": list   # 论文信息列表，每个元素为论文详细信息字典
            }
    权限要求：
        需要认证用户（用户名和密码均为admin）。
    异常：
        - 若数据库查询异常，返回500错误。
    """
    q = db.query(Paper)
    if year:
        q = q.filter(Paper.year == year)
    if author:
        q = q.filter(Paper.authors.contains([{ 'name': author }]))
    if lang:
        q = q.filter(Paper.lang == lang)
    if min_citation is not None:
        q = q.filter(Paper.num_citation >= min_citation)
    if max_citation is not None:
        q = q.filter(Paper.num_citation <= max_citation)
    if scholar_id is not None:
        q = q.filter(Paper.scholar_id == scholar_id)
    total = q.count()
    papers = q.order_by(Paper.id.asc()).offset(offset).limit(size).all()
    def paper_to_dict(obj):
        return {
            "id": obj.id,
            "aminer_id": obj.aminer_id,
            "scholar_id": obj.scholar_id,
            "title": obj.title,
            "abstract": obj.abstract,
            "authors": obj.authors or [],
            "year": obj.year,
            "lang": obj.lang,
            "num_citation": obj.num_citation,
            "pdf": obj.pdf,
            "urls": obj.urls or [],
            "versions": obj.versions or [],
            "create_time": obj.create_time,
            "update_times": obj.update_times or {},
        }
    return {"total": total, "data": [paper_to_dict(p) for p in papers]}

@app.get("/api/papers/{paper_id}", response_model=PaperOut, tags=["Papers"])
def get_paper(paper_id: int, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    """
    功能：
        根据论文ID获取论文详细信息。
    输入参数：
        - paper_id (int): 论文ID。
        - db: 数据库会话。
        - user (str): 认证用户。
    输出：
        论文详细信息（PaperOut模型）。
    权限要求：
        需要认证用户。
    异常：
        - 论文不存在时返回404。
    """
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
    """
    功能：
        更新指定论文的信息。
    输入参数：
        - paper_id (int): 论文ID。
        - paper (PaperUpdate): 更新内容。
        - db: 数据库会话。
        - user (str): 认证用户。
    输出：
        更新后的论文详细信息。
    权限要求：
        需要认证用户。
    异常：
        - 论文不存在时返回404。
    """
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
    """
    功能：
        删除指定论文。
    输入参数：
        - paper_id (int): 论文ID。
        - db: 数据库会话。
        - user (str): 认证用户。
    输出：
        无内容，204状态码。
    权限要求：
        需要认证用户。
    异常：
        - 论文不存在时返回404。
    """
    obj = db.query(Paper).filter_by(id=paper_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="论文不存在")
    db.delete(obj)
    db.commit()
    return

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

# --- 将 list 路由提前 ---
@app.get("/api/patents/list", summary="分页获取全部专利", tags=["Patents"])
def list_patents_api(
    size: int = Query(10, ge=1, le=100, description="每页条数(1-100)"),
    offset: int = Query(0, ge=0, description="偏移量"),
    country: Optional[str] = Query(None, description="国家"),
    inventor: Optional[str] = Query(None, description="发明人名(模糊包含)"),
    pub_status: Optional[str] = Query(None, description="公开状态(published/pending)"),
    scholar_id: Optional[int] = Query(None, description="学者ID"),
    db=Depends(get_db),
    user: str = Depends(fake_verify_user)
):
    """
    功能：
        分页获取全部专利信息列表，并支持多条件筛选。
    输入参数：
        - size (int): 每页返回的专利数量，默认10，最大100。
        - offset (int): 数据偏移量，默认0。
        - country (str, 可选): 国家。
        - inventor (str, 可选): 发明人名（模糊包含）。
        - pub_status (str, 可选): 公开状态（published/pending）。
        - scholar_id (int, 可选): 学者ID。
        - db: 数据库会话。
        - user (str): 认证用户。
    输出：
        dict:
            {
                "total": int,   # 专利总数
                "data": list   # 专利信息列表，每个元素为专利详细信息字典
            }
    权限要求：
        需要认证用户（用户名和密码均为admin）。
    异常：
        - 若数据库查询异常，返回500错误。
    """
    q = db.query(Patent)
    if country:
        q = q.filter(Patent.country == country)
    if inventor:
        q = q.filter(Patent.inventor.contains([{ 'name': inventor }]))
    if pub_status == "published":
        q = q.filter(Patent.pub_date != None)
    elif pub_status == "pending":
        q = q.filter(Patent.pub_date == None)
    if scholar_id is not None:
        q = q.filter(Patent.scholar_id == scholar_id)
    total = q.count()
    patents = q.order_by(Patent.id.asc()).offset(offset).limit(size).all()
    def patent_to_dict(obj):
        return {
            "id": obj.id,
            "aminer_id": obj.aminer_id,
            "scholar_id": obj.scholar_id,
            "title": obj.title or {},
            "abstract": obj.abstract or {},
            "appDate": obj.app_date,
            "pubDate": obj.pub_date,
            "appNum": obj.app_num,
            "pubNum": obj.pub_num,
            "pubSearchId": obj.pub_search_id,
            "pubKind": obj.pub_kind,
            "country": obj.country,
            "inventor": obj.inventor or [],
            "applicant": obj.applicant or [],
            "assignee": obj.assignee or [],
            "ipc": obj.ipc or [],
            "priority": obj.priority or [],
        }
    return {"total": total, "data": [patent_to_dict(p) for p in patents]}

@app.get("/api/patents/{patent_id}", response_model=PatentOut, tags=["Patents"])
def get_patent(patent_id: int, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    """
    功能：
        根据专利ID获取专利详细信息。
    输入参数：
        - patent_id (int): 专利ID。
        - db: 数据库会话。
        - user (str): 认证用户。
    输出：
        专利详细信息（PatentOut模型）。
    权限要求：
        需要认证用户。
    异常：
        - 专利不存在时返回404。
    """
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
    """
    功能：
        更新指定专利的信息。
    输入参数：
        - patent_id (int): 专利ID。
        - patent (PatentUpdate): 更新内容。
        - db: 数据库会话。
        - user (str): 认证用户。
    输出：
        更新后的专利详细信息。
    权限要求：
        需要认证用户。
    异常：
        - 专利不存在时返回404。
    """
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
    """
    功能：
        删除指定专利。
    输入参数：
        - patent_id (int): 专利ID。
        - db: 数据库会话。
        - user (str): 认证用户。
    输出：
        无内容，204状态码。
    权限要求：
        需要认证用户。
    异常：
        - 专利不存在时返回404。
    """
    obj = db.query(Patent).filter_by(id=patent_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="专利不存在")
    db.delete(obj)
    db.commit()
    return 


# ------------------ 首页统计数据 ------------------
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

class ActivityOut(PBaseModel):
    id: int
    type: str  # scholar/paper/patent
    action: str  # 新增/更新
    name: str  # 标题或姓名
    time: str  # ISO时间字符串

@app.get("/api/activities", response_model=List[ActivityOut], tags=["Dashboard"])
def get_recent_activities(limit: int = 10, db=Depends(get_db), user: str = Depends(fake_verify_user)):
    """
    获取最近的学者、论文、专利的新增/更新活动，按时间倒序。
    - limit: 返回条数，默认10
    - 权限：需认证
    # 返回内容格式：
    # [
    #   {
    #     "id": int,           # 活动对应的实体ID
    #     "type": str,         # 活动类型: "scholar" | "paper" | "patent"
    #     "action": str,       # 活动动作: "新增" | "更新"
    #     "name": str,         # 学者姓名、论文标题或专利标题
    #     "time": str          # 活动时间，ISO8601格式字符串
    #   },
    #   ...
    # ]
    """
    # 查询最近的scholar、paper、patent的新增/更新
    scholar_q = db.query(Scholar).with_entities(
        Scholar.id, Scholar.name_zh, Scholar.created_at, Scholar.updated_at
    )
    paper_q = db.query(Paper).with_entities(
        Paper.id, Paper.title, Paper.created_at, Paper.updated_at
    )
    patent_q = db.query(Patent).with_entities(
        Patent.id, Patent.title, Patent.created_at, Patent.updated_at
    )
    activities = []
    # 学者
    for row in scholar_q:
        # 新增
        # 转为北京时间（UTC+8）
        dt = row.updated_at or row.created_at
        if dt and dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(timezone(timedelta(hours=8))) if dt else None
        activities.append({
            "id": row.id,
            "type": "scholar",
            "action": "新增" if row.created_at == row.updated_at else "更新",
            "name": row.name_zh,
            "time": dt.isoformat() if dt else None
        })
    # 论文
    for row in paper_q:
        dt = row.updated_at or row.created_at
        if dt and dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(timezone(timedelta(hours=8))) if dt else None
        activities.append({
            "id": row.id,
            "type": "paper",
            "action": "新增" if row.created_at == row.updated_at else "更新",
            "name": row.title,
            "time": dt.isoformat() if dt else None
        })
    # 专利
    for row in patent_q:
        # 专利title为JSON，取中文或英文
        title = row.title
        # 新增：如果title为str，尝试json.loads恢复为dict
        if isinstance(title, str):
            try:
                import json
                title_dict = json.loads(title)
                title = title_dict
            except Exception:
                title = title  # 保持原样
        name = None
        if isinstance(title, dict):
            zh = title.get("zh")
            en = title.get("en")
            if isinstance(zh, list) and zh:
                name = zh[0]
            elif isinstance(zh, str):
                name = zh
            elif isinstance(en, list) and en:
                name = en[0]
            elif isinstance(en, str):
                name = en
            else:
                name = str(title)
        else:
            name = str(title)
        dt = row.updated_at or row.created_at
        if dt and dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(timezone(timedelta(hours=8))) if dt else None
        activities.append({
            "id": row.id,
            "type": "patent",
            "action": "新增" if row.created_at == row.updated_at else "更新",
            "name": name,
            "time": dt.isoformat() if dt else None
        })
    # 按时间倒序，取前limit条
    activities.sort(key=lambda x: x["time"], reverse=True)
    return [ActivityOut(**a) for a in activities[:limit]]

@app.post("/api/papers/batch", response_model=List[PaperOut], status_code=201, tags=["Papers"])
def batch_create_papers(papers: List[PaperIn] = Body(...), db=Depends(get_db), user: str = Depends(fake_verify_user)):
    """
    批量插入论文。
    参数: papers: PaperIn 列表
    返回: 所有成功插入的论文对象列表
    """
    objs = [Paper(**paper.model_dump()) for paper in papers]
    db.add_all(objs)
    try:
        db.commit()
        for obj in objs:
            db.refresh(obj)
        return objs
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="存在aminer_id重复，批量插入失败")

@app.post("/api/patents/batch", response_model=List[PatentOut], status_code=201, tags=["Patents"])
def batch_create_patents(patents: List[PatentIn] = Body(...), db=Depends(get_db), user: str = Depends(fake_verify_user)):
    """
    批量插入专利。
    参数: patents: PatentIn 列表
    返回: 所有成功插入的专利对象列表
    """
    objs = [Patent(**patent.model_dump()) for patent in patents]
    db.add_all(objs)
    try:
        db.commit()
        for obj in objs:
            db.refresh(obj)
        return objs
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="存在aminer_id重复，批量插入失败")