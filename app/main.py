from fastapi import FastAPI, Query, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
import aminer.api as aminer_api

app = FastAPI(title="科研成果监测平台API", description="学者检索等RESTful接口", version="0.1.0")

security = HTTPBasic()

def fake_verify_user(credentials: HTTPBasicCredentials = Depends(security)):
    # TODO: 替换为真实用户认证。目前的机制是，如果用户名和密码都为admin，则认为用户已认证。
    if credentials.username != "admin" or credentials.password != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials.username

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

@app.get("/api/papers", summary="论文检索", tags=["Papers"])
def search_papers(
    title: Optional[str] = Query(None, description="论文标题"),
    scholar_id: Optional[str] = Query(None, description="学者ID"),
    size: int = Query(10, ge=1, le=20, description="返回条数(1-20)"),
    user: str = Depends(fake_verify_user)
):
    """
    支持按论文标题或学者ID检索论文。
    - title: 论文标题，支持模糊查找
    - scholar_id: 学者ID，返回该学者的论文列表
    - size: 返回条数，1-20
    - 权限：需认证
    """
    if not title and not scholar_id:
        raise HTTPException(status_code=422, detail="title和scholar_id至少提供一个")
    try:
        if title:
            # 按标题查找，aminer_api.search_paper_by_title返回单条，需包装为列表
            result = aminer_api.search_paper_by_title(title=title, size=size)
            if result:
                return {"data": [result]}
            else:
                return {"data": []}
        elif scholar_id:
            # 按学者ID查找，aminer_api.search_papers_by_scholar_free返回dict，需取hitList
            result = aminer_api.search_papers_by_scholar_free(scholar_id, size=size)
            papers = result.get("hitList", []) if isinstance(result, dict) else []
            return {"data": papers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 