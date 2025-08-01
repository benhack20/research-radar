# 科研成果监测平台 开发日志

本文件用于记录各阶段TDD开发循环的详细进展、关键决策与变更。

---

- 按TDD流程，基于需求与技术方案，完成后端学者检索RESTful API（/api/scholars）开发。
- 设计并实现了覆盖正常、异常、边界、权限等场景的详细测试用例。
- 测试用例全部通过，接口功能与安全性符合预期。
- 项目采用venv进行Python环境隔离，依赖管理规范。
- 代码与测试均有详细注释，接口支持OpenAPI文档。
- 下一步将继续推进论文/专利检索API、数据库持久化、前端开发等TDD循环。

---

1. **需求分析**

- 为 `search_papers_by_scholar_free` 和 `search_patents_by_scholar_free` 分别添加 RESTful 接口：
  - `/api/scholars/{id}/papers`
  - `/api/scholars/{id}/patents`

2. **测试用例设计与实现**

   - 在 `tests/test_api_scholar_products.py` 中，设计并实现了覆盖正常、异常、边界、权限等场景的详细测试用例。
3. **业务代码实现**

   - 在 `backend/app/main.py` 中实现了上述两个接口，集成 aminer.api，接口参数校验、权限控制、异常处理均符合规范，注释详细。
4. **测试运行**

   - 所有测试用例全部通过，接口功能、异常处理、权限控制均符合预期。

---

- 移除学者论文/专利接口的size参数上限，允许任意正整数。
- 增强测试用例，断言接口返回的hitList和hitsTotal均有实际内容，且数据结构完整。
- 所有接口和测试用例全部通过。
- 代码已提交至版本库。

---

1. **需求分析**

- 按TDD流程，推进后端数据库持久化能力，要求模型字段与AMiner API返回结构高度对齐，支持学者、论文、专利等信息的完整存储。
- 需支持复杂字段（如作者、标题、摘要、分类号等）的JSON结构，满足后续数据同步、查询、统计等需求。

2. **测试用例设计与实现**

   - 参考真实AMiner论文与专利案例（见aminer/demo/paper.json、patents.json），在 `tests/test_db_models.py`中设计并实现了覆盖所有字段、结构和边界场景的详细测试用例。
   - 用例覆盖学者、论文、专利的增删查改、唯一性、关联关系、复杂JSON字段、异常分支等。
3. **业务代码实现**

   - 重构 `backend/app/models.py`，补全并规范所有核心表字段，字段类型、注释、唯一性、外键、索引等均与AMiner数据结构对齐。
   - 支持复杂字段用Text存储JSON字符串，便于后续解析与扩展。
4. **测试运行**

   - 所有数据库模型相关测试用例全部通过，模型与实际数据高度一致，TDD测试覆盖全面。
5. **关键决策与变更**

   - 明确SyncLog表作为数据同步、刷新、异常等操作的日志表，便于后续数据追溯与运维。
   - 采用venv环境隔离，所有依赖与测试均在虚拟环境下运行。

下一步将进入数据库迁移脚本与API持久化开发TDD循环。

---

### 2024-07-24（API持久化与TDD集成测试）

1. **需求分析**

   - 完善后端学者、论文、专利的RESTful持久化API，要求支持真实业务数据的全链路增删查改，兼容复杂JSON字段。
   - PUT接口需支持部分字段更新，避免全量必填带来的422错误。
2. **测试用例设计与实现**

   - 在 `tests/test_api_persistence.py`中，基于真实aminer/demo/paper.json和patents.json数据，设计并实现了覆盖所有字段、结构和边界场景的详细集成测试用例。
   - 用例覆盖学者、论文、专利的新增、查询、更新（部分字段）、删除、列表、异常分支等。
   - 每个测试前自动清理数据库，保证测试隔离。
3. **业务代码实现**

   - 新增 `ScholarUpdate`、`PaperUpdate`、`PatentUpdate`模型，PUT接口用 `exclude_unset=True`只更新传入字段，所有字段均可选，兼容部分字段更新。
   - 优化数据库模型、API参数校验、异常处理，所有接口与测试用例完全对齐。
   - 持久化相关代码迁移至 `backend/app/persistence/`目录，结构更清晰。
4. **测试运行**

   - 所有API集成测试用例全部通过，CRUD、复杂字段、异常分支等均被充分验证。
5. **关键决策与变更**

   - 明确PUT接口应支持部分字段更新，采用Pydantic可选字段+exclude_unset方案。
   - 测试用例与真实业务数据高度一致，保证生产环境可用性。

- 下一步将推进日志、批量操作、权限细化、前端联调等TDD开发。

---

### 2024-07-24（数据库切换与环境一致性）

1. **需求分析**

   - 项目数据库彻底切换为PostgreSQL，移除所有sqlite相关逻辑，确保开发、测试、生产环境100%一致。
   - 所有数据库连接均通过 `DATABASE_URL`环境变量配置，便于本地、容器、生产环境灵活切换。
2. **测试用例与实现**

   - `main.py`和 `test_api_persistence.py`统一用dotenv/env方式读取数据库连接，未设置时报错，强制要求PostgreSQL。
   - 测试用例和主应用共用同一数据库配置，所有API集成测试在PostgreSQL下全部通过。
   - 测试前自动清理数据库，保证测试隔离。
3. **关键决策与变更**

   - 明确禁止sqlite，所有环境均用PostgreSQL，避免行为差异。
   - 生产部署、CI/CD、团队协作均只需维护一套数据库配置。

- 下一步将推进日志、批量操作、权限细化、前端联调等TDD开发。

---

### 2024-07-25（AMiner Free API扩展与测试）

1. **需求分析**
   
   - 新增根据person_id获取学者详细信息的free API，接口需与AMiner官方一致，返回结构参考person_detail.json。
   - 注释需详细列出返回结构，profile等嵌套字段需完整说明。
2. **测试用例设计与实现**
   
   - 在 `aminer/tests/test_aminer_api.py` 中新增 `test_get_person_detail_by_id`，使用真实person_id和person_detail.json中的字段进行断言。
   - 测试用例不做mock，直接发起真实网络请求，确保接口与数据结构完全一致。
3. **业务代码实现**
   
   - 在 `aminer/api.py` 中实现 `get_person_detail_by_id`，风格、异常处理、注释与其他free API保持一致。
   - docstring详细列出主要返回字段及profile嵌套结构，所有字段均有中英文注释。
4. **测试运行**
   
   - 所有相关测试用例全部通过，接口功能、注释、数据结构均符合预期。

- 下一步将根据需求继续扩展AMiner free API及其测试。

---
