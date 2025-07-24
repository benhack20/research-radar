import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from aminer import api


def test_get_token():
    """
    测试 get_token 能否正确读取 TOKEN 文件。
    """
    token = api.get_token()
    assert isinstance(token, str)
    assert len(token) > 0


def test_search_person_by_name():
    """
    测试 search_person_by_name 能否查到学者信息。
    """
    resp = api.search_person_by_name(name="喻纯", size=1)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("code") == 200
    assert data.get("success") is True
    assert isinstance(data.get("data"), list)


def test_search_paper_by_title():
    """
    测试 search_paper_by_title 能否查到论文。
    """
    result = api.search_paper_by_title("From Operation to Cognition: Automatic Modeling Cognitive Dependencies from User Demonstrations for GUI Task Automation")
    assert result is None or isinstance(result, dict)
    if result:
        assert "id" in result
        assert "title" in result


def test_search_papers_by_scholar_free():
    """
    测试 search_papers_by_scholar_free 能否查到学者论文。
    """
    scholar_id = "56066a5245cedb339687488b"  # 示例ID
    result = api.search_papers_by_scholar_free(scholar_id, size=1)
    assert isinstance(result, dict)
    assert "hitList" in result
    assert "hitsTotal" in result


def test_search_patents_by_scholar_free():
    """
    测试 search_patents_by_scholar_free 能否查到学者专利。
    """
    scholar_id = "56066a5245cedb339687488b"  # 示例ID
    result = api.search_patents_by_scholar_free(scholar_id, size=1)
    assert isinstance(result, dict)
    assert "hitList" in result
    assert "hitsTotal" in result 


def test_get_person_detail_by_id():
    """
    测试 get_person_detail_by_id 能否查到学者详细信息。
    """
    person_id = "56066a5245cedb339687488b"
    result = api.get_person_detail_by_id(person_id)
    assert isinstance(result, dict)
    assert result["id"] == person_id
    assert result["name"] == "Chun Yu"
    assert result["name_zh"] == "喻纯"
    assert "indices" in result and isinstance(result["indices"], dict)
    assert "profile" in result and isinstance(result["profile"], dict) 