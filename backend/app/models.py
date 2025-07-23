from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, func
from sqlalchemy.orm import declarative_base, relationship

# SQLAlchemy基础模型
Base = declarative_base()

class Scholar(Base):
    """
    学者表
    - id: 本地主键
    - aminer_id: AMiner学者ID，唯一
    - name: 姓名
    - name_zh: 中文名
    - org: 英文机构
    - org_zh: 中文机构
    - org_id: 机构ID
    - interests: 研究兴趣（JSON字符串）
    - n_citation: 总引用数
    - created_at/updated_at: 时间戳
    """
    __tablename__ = 'scholars'
    id = Column(Integer, primary_key=True)
    aminer_id = Column(String(64), unique=True, nullable=False, index=True, comment="AMiner学者ID")
    name = Column(String(128), nullable=False, comment="姓名")
    name_zh = Column(String(128), comment="中文名")
    org = Column(String(256), comment="英文机构")
    org_zh = Column(String(256), comment="中文机构")
    org_id = Column(String(64), comment="机构ID")
    interests = Column(Text, comment="研究兴趣(JSON字符串)")
    n_citation = Column(Float, comment="引用数")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    papers = relationship('Paper', back_populates='scholar', cascade="all, delete-orphan")
    patents = relationship('Patent', back_populates='scholar', cascade="all, delete-orphan")

class Paper(Base):
    """
    论文表
    - id: 本地主键
    - aminer_id: AMiner论文ID，唯一
    - scholar_id: 外键，关联学者
    - title: 论文标题
    - abstract: 摘要
    - authors: 作者列表(JSON字符串)
    - year: 发表年份
    - lang: 语言
    - num_citation: 引用数
    - pdf: PDF链接
    - urls: 相关链接(JSON字符串)
    - versions: 版本信息(JSON字符串)
    - create_time: 创建时间
    - update_times: 更新时间(JSON字符串)
    - created_at/updated_at: 本地时间戳
    """
    __tablename__ = 'papers'
    id = Column(Integer, primary_key=True)
    aminer_id = Column(String(64), unique=True, nullable=False, index=True, comment="AMiner论文ID")
    scholar_id = Column(Integer, ForeignKey('scholars.id'), nullable=False)
    title = Column(String(512), nullable=False)
    abstract = Column(Text)
    authors = Column(Text, comment="作者(JSON字符串)")
    year = Column(Integer)
    lang = Column(String(16))
    num_citation = Column(Integer)
    pdf = Column(String(512))
    urls = Column(Text, comment="相关链接(JSON字符串)")
    versions = Column(Text, comment="版本信息(JSON字符串)")
    create_time = Column(String(32))
    update_times = Column(Text, comment="更新时间(JSON字符串)")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    scholar = relationship('Scholar', back_populates='papers')

class Patent(Base):
    """
    专利表
    - id: 本地主键
    - aminer_id: AMiner专利ID，唯一
    - scholar_id: 外键，关联学者
    - title: 标题(JSON字符串，含中英文)
    - abstract: 摘要(JSON字符串，含中英文)
    - app_date: 申请日期
    - app_num: 申请号
    - applicant: 申请人(JSON字符串)
    - assignee: 专利权人(JSON字符串)
    - country: 国家
    - cpc: CPC分类号(JSON字符串)
    - inventor: 发明人(JSON字符串)
    - ipc: IPC分类号(JSON字符串)
    - ipcr: IPCR分类号(JSON字符串)
    - pct: PCT信息(JSON字符串)
    - priority: 优先权信息(JSON字符串)
    - pub_date: 公开号日期
    - pub_kind: 公开号类型
    - pub_num: 公开号
    - pub_search_id: 公开号搜索ID
    - created_at/updated_at: 本地时间戳
    """
    __tablename__ = 'patents'
    id = Column(Integer, primary_key=True)
    aminer_id = Column(String(64), unique=True, nullable=False, index=True, comment="AMiner专利ID")
    scholar_id = Column(Integer, ForeignKey('scholars.id'), nullable=False)
    title = Column(Text, comment="标题(JSON字符串)")
    abstract = Column(Text, comment="摘要(JSON字符串)")
    app_date = Column(String(32))
    app_num = Column(String(64))
    applicant = Column(Text, comment="申请人(JSON字符串)")
    assignee = Column(Text, comment="专利权人(JSON字符串)")
    country = Column(String(16))
    cpc = Column(Text, comment="CPC分类号(JSON字符串)")
    inventor = Column(Text, comment="发明人(JSON字符串)")
    ipc = Column(Text, comment="IPC分类号(JSON字符串)")
    ipcr = Column(Text, comment="IPCR分类号(JSON字符串)")
    pct = Column(Text, comment="PCT信息(JSON字符串)")
    priority = Column(Text, comment="优先权信息(JSON字符串)")
    pub_date = Column(String(32))
    pub_kind = Column(String(32))
    pub_num = Column(String(64))
    pub_search_id = Column(String(64))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    scholar = relationship('Scholar', back_populates='patents')

class SyncLog(Base):
    """
    数据同步日志表
    - id: 主键
    - scholar_id: 外键，关联学者
    - action: 同步动作（如refresh/add）
    - status: 状态（success/fail）
    - message: 详细信息
    - created_at: 时间戳
    """
    __tablename__ = 'sync_log'
    id = Column(Integer, primary_key=True)
    scholar_id = Column(Integer, ForeignKey('scholars.id'), nullable=False)
    action = Column(String(32), nullable=False)
    status = Column(String(16), nullable=False)
    message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    scholar = relationship('Scholar') 