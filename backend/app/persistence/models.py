from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, func, JSON
from sqlalchemy.orm import declarative_base, relationship

# SQLAlchemy基础模型
Base = declarative_base()

class Scholar(Base):
    """
    学者表（对齐AMiner person_detail.json结构）
    - id: 本地主键
    - aminer_id: AMiner学者ID，唯一
    - name: 姓名
    - name_zh: 中文名
    - avatar: 头像链接
    - nation: 国家
    - indices: 学者指标(JSON)
    - links: 外部链接(JSON)
    - profile: 个人信息(JSON)
    - tags: 研究标签(JSON)
    - tags_score: 标签分数(JSON)
    - tags_zh: 中文标签(JSON)
    - num_followed: 被关注数
    - num_upvoted: 被点赞数
    - num_viewed: 浏览数
    - gender: 性别
    - homepage: 主页
    - position: 职称
    - position_zh: 职称中文
    - work: 工作经历
    - work_zh: 工作经历中文
    - note: 备注
    - created_at/updated_at: 时间戳
    """
    __tablename__ = 'scholars'
    id = Column(Integer, primary_key=True)
    aminer_id = Column(String(64), unique=True, nullable=False, index=True, comment="AMiner学者ID")
    name = Column(String(128), nullable=False, comment="姓名")
    name_zh = Column(String(128), comment="中文名")
    avatar = Column(String(512), comment="头像链接")
    nation = Column(String(64), comment="国家")
    indices = Column(JSON, comment="学者指标(JSON)")
    links = Column(JSON, comment="外部链接(JSON)")
    profile = Column(JSON, comment="个人信息(JSON)")
    tags = Column(JSON, comment="研究标签(JSON)")
    tags_score = Column(JSON, comment="标签分数(JSON)")
    tags_zh = Column(JSON, comment="中文标签(JSON)")
    num_followed = Column(Integer, comment="被关注数")
    num_upvoted = Column(Integer, comment="被点赞数")
    num_viewed = Column(Integer, comment="浏览数")
    gender = Column(String(16), comment="性别")
    homepage = Column(String(256), comment="主页")
    position = Column(String(128), comment="职称")
    position_zh = Column(String(128), comment="职称中文")
    work = Column(Text, comment="工作经历")
    work_zh = Column(Text, comment="工作经历中文")
    note = Column(Text, comment="备注")
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
    authors = Column(JSON, comment="作者(JSON)")
    year = Column(Integer)
    lang = Column(String(16))
    num_citation = Column(Integer)
    pdf = Column(String(512))
    urls = Column(JSON, comment="相关链接(JSON)")
    versions = Column(JSON, comment="版本信息(JSON)")
    create_time = Column(String(32))
    update_times = Column(JSON, comment="更新时间(JSON)")
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
    title = Column(JSON, comment="标题(JSON，含中英文)")
    abstract = Column(JSON, comment="摘要(JSON，含中英文)")
    app_date = Column(String(32))
    app_num = Column(String(64))
    applicant = Column(JSON, comment="申请人(JSON)")
    assignee = Column(JSON, comment="专利权人(JSON)")
    country = Column(String(16))
    cpc = Column(JSON, comment="CPC分类号(JSON)")
    inventor = Column(JSON, comment="发明人(JSON)")
    ipc = Column(JSON, comment="IPC分类号(JSON)")
    ipcr = Column(JSON, comment="IPCR分类号(JSON)")
    pct = Column(JSON, comment="PCT信息(JSON)")
    priority = Column(JSON, comment="优先权信息(JSON)")
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