"""
aminer/api.py

本模块封装了与AMiner平台相关的API调用方法，便于在Python项目中集成学者、论文、专利等信息的检索功能。

包含的API及简要介绍：
- get_token: 读取AMiner API的Token（从aminer/TOKEN文件）。
- search_person_by_name: 按姓名、机构等条件检索学者信息。
- search_paper_by_title: 按论文标题检索论文详细信息。
- search_papers_by_scholar_free: 根据学者ID（person_id）检索其论文（免费API）。
- search_patents_by_scholar_free: 根据学者ID（person_id）检索其专利（免费API）。
- search_papers_by_scholar_paid: 根据学者ID（person_id）检索其论文（付费API）。

注意事项：
- 需将Token存放于aminer/TOKEN文件中。
- 本模块配合独立的测试用例文件（如tests/test_aminer_api.py）进行功能验证。
- 修改本模块后，务必运行pytest以确保功能正确。

"""


from warnings import deprecated
import requests
import json
from typing import Optional, Dict


def get_token():
    """
    从 aminer/TOKEN 文件中读取 API Token。
    返回：
        str: API Token 字符串。
    """
    with open("aminer/TOKEN", "r", encoding="utf-8") as f:
        return f.read().strip()


def search_person_by_name(name="", offset=0, org="", size=1):
    """
    调用 Aminer Person Search API，查询学者信息。
    参数：
        name (str): 学者姓名，可为空。
        offset (int): 起始位置，默认为0。
        org (str): 机构名，可为空。
        size (int): 返回条数，最大为10。
    返回：
        requests.Response: API 的 HTTP 响应对象。
    响应格式：
        {
            "code": 200,
            "success": true,
            "data": [
                {
                    "id": str,           # 学者ID
                    "interests": list,   # 研究兴趣
                    "n_citation": int/float, # 引用值
                    "name": str,        # 姓名
                    "name_zh": str,     # 中文名
                    "org": str,         # 英文机构
                    "org_id": str,      # 机构id
                    "org_zh": str       # 中文机构
                },
                ...
            ]
        }
    """
    API_URL = "https://datacenter.aminer.cn/gateway/open_platform/api/person/search"
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "Authorization": get_token()
    }
    payload = {
        "name": name,
        "offset": offset,
        "org": org,
        "size": size
    }
    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    return response

@deprecated("付费API，请使用search_papers_by_scholar_free替代")
def search_papers_by_scholar_paid(scholar_id):
    """
    付费API，调用 Aminer 学者论文关系 API，根据学者ID获取其论文ID和标题。
    参数：
        scholar_id (str): 学者ID。
    返回：
        requests.Response: API 的 HTTP 响应对象。
    响应格式：
        {
            "author_id": str,  # 学者ID
            "id": str,        # 论文ID
            "title": str,     # 论文标题
            "total": float    # 总数
        }
    """
    PAPER_RELATION_API_URL = "https://datacenter.aminer.cn/gateway/open_platform/api/person/paper/relation"
    headers = {
        "Authorization": get_token()
    }
    params = {
        "id": scholar_id
    }
    response = requests.get(PAPER_RELATION_API_URL, headers=headers, params=params)
    return response

@deprecated("该API只能返回论文的id和title，作用不大")
def search_paper_by_title(title: str, page: int = 1, size: int = 1) -> Optional[Dict]:
    """
    Search for a paper by its title using the AMiner paper search API.

    Args:
        title (str): The title of the paper to search for.
        page (int): The page number for pagination (default is 1).
        size (int): The number of results to return (default is 1).

    Returns:
        Optional[Dict]: A dictionary with 'id', 'title', and 'doi' if found, else None.
    """
    API_URL = "https://datacenter.aminer.cn/gateway/open_platform/api/paper/search"
    headers = {
        "Authorization": get_token()
    }
    params = {
        "page": page,
        "size": size,
        "title": title
    }
    try:
        response = requests.get(API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("code") == 200 and data.get("success") and data.get("data"):
            # Return the first result
            result = data["data"][0]
            doi = result.get("doi")
            if doi is None:
                print(f"Warning: DOI is None for title '{result.get('title')}' (id: {result.get('id')})")
            return {
                "id": result.get("id"),
                "title": result.get("title"),
                "doi": doi
            }
        else:
            print(f"API error or no data for title: {title}. Message: {data.get('msg')}")
            return None
    except Exception as e:
        print(f"Exception occurred while searching for title '{title}': {e}")
        return None 


def search_papers_by_scholar_free(scholar_id, size=10, needDetails=True):
    """
    Search for papers authored by a specific scholar using the free AMiner API. Refer to aminer/demo/paper.json for raw network response.

    Args:
        scholar_id (str): The AMiner person_id of the scholar whose papers are to be searched.
        size (int, optional): The number of results to return. Defaults to 10.
        needDetails (bool, optional): Whether to include detailed information in the results. Defaults to True.

    Returns:
        dict: 返回格式示例：
            {
                "hitList": [
                    {
                        "abstract": str,
                        "authors": list,
                        "create_time": str,
                        "id": str,
                        "lang": str,
                        "num_citation": int,
                        "pdf": str,
                        "title": str,
                        "update_times": dict,
                        "urls": list,
                        "versions": list,
                        "year": int
                    },
                    ...
                ],
                "hitsTotal": int
            }
    """
    url = "https://apiv2.aminer.cn/n"
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Host": "apiv2.aminer.cn",
        "Origin": "https://www.aminer.cn",
        "Referer": "https://www.aminer.cn/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }

    payload = [
        {
            "action": "person.SearchPersonPaper",
            "parameters": {
                "person_id": scholar_id,
                "search_param": {
                    "needDetails": needDetails,
                    "page": 0,
                    "size": size,
                    "sort": [
                        {
                            "field": "year",
                            "asc": False
                        }
                    ]
                }
            }
        }
    ]

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code != 200:
        # 如果响应状态码不是200，抛出异常并包含错误信息
        raise Exception(f"AMiner API请求失败，状态码: {response.status_code}, 响应内容: {response.text}")

    try:
        result = response.json()
    except Exception as e:
        # 如果解析JSON失败，抛出异常
        raise Exception(f"响应内容不是有效的JSON格式: {e}")

    # 检查返回结构，提取data字段
    if "data" in result and isinstance(result["data"], list) and len(result["data"]) > 0:
        return result["data"][0].get("data", {})
    else:
        # 如果data字段不存在或格式不正确，抛出异常
        raise Exception(f"AMiner API返回数据格式异常: {result}")
    

def search_patents_by_scholar_free(scholar_id: str, size: int = 10, needDetails: bool = True, page: int = 0, query: str = ""):
    """
    使用AMiner免费API，根据学者ID查询其相关专利。 Refer to aminer/demo/patents.json for raw network response.

    参数：
        scholar_id (str): 发明人AMiner person_id。
        size (int, optional): 返回结果数量，默认为10。
        needDetails (bool, optional): 是否需要详细信息，默认为True。
        page (int, optional): 分页页码，默认为0。
        query (str, optional): 关键词查询，默认为空字符串。

    返回：
        dict: 返回格式如下：
            {
                "hitList": [  # 专利详细信息列表，每个元素结构如下：
                    {
                        "abstract": dict,     # 摘要（含中英文，结构不再展开）
                        "appDate": str,       # 申请日期
                        "appNum": str,        # 申请号
                        "applicant": list,    # 申请人列表
                        "assignee": list,     # 专利权人列表
                        "country": str,       # 国家代码
                        "cpc": list,          # CPC分类号列表
                        "id": str,            # 专利ID
                        "inventor": list,     # 发明人列表
                        "ipc": list,          # IPC分类号列表
                        "ipcr": list,         # IPCR分类号列表
                        "pct": list,          # PCT信息列表
                        "priority": list,     # 优先权信息列表
                        "pubDate": str,       # 公开号日期
                        "pubKind": str,       # 公开号类型
                        "pubNum": str,        # 公开号
                        "pubSearchId": str,   # 公开号搜索ID
                        "title": dict         # 标题（含中英文，结构不再展开）
                    },
                    ...
                ],
                "hitsTotal": int  # 专利总数
            }
    异常：
        请求失败或返回格式异常时抛出异常。
    """
    url = "https://searchtest.aminer.cn/aminer-search/search/patentV2"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Origin": "https://www.aminer.cn",
        "Referer": "https://www.aminer.cn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    }
    # 构造请求体
    data = {
        "filters": [
            {
                "boolOperator": 3,
                "field": "inventor.person_id",
                "type": "term",
                "value": scholar_id
            }
        ],
        "sort": [
            {
                "field": "pub_date",
                "asc": False
            }
        ],
        "needDetails": needDetails,
        "query": query,
        "page": page,
        "size": size
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        # 如果响应状态码不是200，抛出异常并包含错误信息
        raise Exception(f"AMiner专利API请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
    try:
        result = response.json()
    except Exception as e:
        # 如果解析JSON失败，抛出异常
        raise Exception(f"专利API响应内容不是有效的JSON格式: {e}")
    # 检查返回结构，提取hitList和hitsTotal
    if (
        isinstance(result, dict)
        and result.get("code") == 200
        and result.get("success")
        and isinstance(result.get("data"), dict)
        and "hitList" in result["data"]
        and "hitsTotal" in result["data"]
    ):
        return {
            "hitList": result["data"]["hitList"],
            "hitsTotal": result["data"]["hitsTotal"]
        }
    else:
        # 如果返回结构异常，抛出异常
        raise Exception(f"AMiner专利API返回数据格式异常: {result}")


def get_person_detail_by_id(person_id: str):
    """
    使用AMiner免费API，根据学者ID获取学者详细信息。

    参数：
        person_id (str): 学者AMiner person_id。
    返回：
        dict: 学者详细信息，主要结构如下（参考person_detail.json）：
            {
                "id": str,                # 学者ID
                "name": str,              # 英文名
                "name_zh": str,           # 中文名
                "avatar": str,            # 头像URL
                "nation": str,            # 国家
                "num_viewed": int,        # 被浏览次数
                "num_followed": int,      # 被关注次数
                "num_upvoted": int,       # 被点赞次数
                "indices": {              # 学术指标
                    "hindex": int,
                    "gindex": int,
                    "pubs": int,
                    "citations": int,
                    "newStar": float,
                    "risingStar": float,
                    "activity": float,
                    "diversity": float,
                    "sociability": float
                },
                "links": {                # 外部链接
                    ...
                },
                "profile": {              # 个人简介
                    "position": str,         # 职称（英文）
                    "position_zh": str,      # 职称（中文）
                    "affiliation": str,      # 单位（英文）
                    "affiliation_zh": str,   # 单位（中文）
                    "work": str,             # 工作经历（英文）
                    "work_zh": str,          # 工作经历（中文）
                    "gender": str,           # 性别
                    "lang": str,             # 语言
                    "homepage": str,         # 主页
                    "phone": str,            # 电话
                    "email": str,            # 邮箱
                    "fax": str,              # 传真
                    "bio": str,              # 简介（英文）
                    "bio_zh": str,           # 简介（中文）
                    "edu": str,              # 教育经历（英文）
                    "edu_zh": str,           # 教育经历（中文）
                    "address": str,          # 地址
                    "note": str,             # 备注
                    "title": str,            # 头衔
                    "titles": list           # 头衔列表
                },
                "tags": list,             # 英文标签
                "tags_zh": list           # 中文标签
            }
    异常：
        请求失败或返回格式异常时抛出异常。
    """
    url = "https://apiv2.aminer.cn/magic?a=getPerson__personapi.get___"
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "origin": "https://www.aminer.cn",
        "referer": "https://www.aminer.cn/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    }
    payload = [
        {
            "action": "personapi.get",
            "parameters": {
                "ids": [person_id]
            },
            "schema": {
                "person": [
                    "id", "name", "name_zh", "avatar", "num_view", "is_follow", "work", "work_zh",
                    "hide", "nation", "language", "bind", "acm_citations", "links", "educations",
                    "tags", "tags_zh", "num_view", "num_follow", "is_upvoted", "num_upvoted",
                    "is_downvoted", "is_lock",
                    {
                        "indices": [
                            "hindex", "gindex", "pubs", "citations", "newStar", "risingStar",
                            "activity", "diversity", "sociability"
                        ]
                    },
                    {
                        "profile": [
                            "position", "position_zh", "affiliation", "affiliation_zh", "work",
                            "work_zh", "gender", "lang", "homepage", "phone", "email", "fax", "bio",
                            "bio_zh", "edu", "edu_zh", "address", "note", "homepage", "title", "titles"
                        ]
                    }
                ]
            }
        }
    ]
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"AMiner get_person_detail_by_id API请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
    try:
        result = response.json()
    except Exception as e:
        raise Exception(f"响应内容不是有效的JSON格式: {e}")
    # 检查返回结构，提取data字段
    if "data" in result and isinstance(result["data"], list) and len(result["data"]) > 0:
        return result["data"][0]["data"][0] if "data" in result["data"][0] and len(result["data"][0]["data"]) > 0 else None
    else:
        raise Exception(f"AMiner get_person_detail_by_id API返回数据格式异常: {result}")


if __name__ == "__main__":
    
    # 测试search_papers_by_scholar_free
    scholar_id = "56066a5245cedb339687488b"
    response = search_papers_by_scholar_free(scholar_id, size=1, needDetails=True)
    print(response)
    
    # 测试search_patents_by_scholar_free
    scholar_id = "56066a5245cedb339687488b"
    response = search_patents_by_scholar_free(scholar_id, size=1, needDetails=True)
    print(response)