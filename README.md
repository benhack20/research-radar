# Research Radar

科研成果监测平台

## 目录结构

- `backend/` 后端 FastAPI 服务
- `aminer/` AMiner API 封装
- `frontend/` 前端 Next.js 应用
- `venv/` Python 虚拟环境

## 后端启动方法

1. 安装依赖（建议在虚拟环境下）：
   ```bash
   pip install -r requirements.txt
   ```
2. 配置数据库环境变量（如 PostgreSQL）：
   ```bash
   # .env 文件或系统环境变量
   DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname
   ```
3. 启动服务：
   ```bash
   # Windows PowerShell
   .\venv\Scripts\Activate
   $env:PYTHONPATH="."
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   访问接口文档: http://localhost:8000/docs

## 前端启动方法

1. 进入 frontend 目录：
   ```bash
   cd frontend
   ```
2. 安装依赖：
   ```bash
   npm install
   ```
3. 启动开发服务器：
   ```bash
   npm run dev
   ```

   访问前端: http://localhost:3000

## 主要环境变量说明

- `DATABASE_URL`：数据库连接字符串，必填。
- 其他敏感信息建议放在 `.env` 文件中。

## 其他

- 后端接口文档自动生成，访问 `/docs`。
- 前后端均支持热重载。
- 如需测试，见 `tests/` 目录。
