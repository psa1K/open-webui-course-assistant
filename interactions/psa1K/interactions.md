# psa1K 交互记录

> 说明：每次交互按时间顺序追加；字段包括时间、模型/Agent、任务、prompt、Agent 输出、决策、问题与解决。

---

## 交互 1 — Open WebUI 本地部署（issue #14）

- **时间**：2026-09-03 17:10
- **模型/Agent**：opencode / DeepSeek-V4-Flash-0731
- **任务**：认领并完成 issue #14「系统部署：Open WebUI 本地部署并连接至少一种大语言模型」。按官方 README 安装并启动 Open WebUI，验证可访问。
- **Prompt（要点）**：阅读 `2. 李正丹-朱静雯老师的题目.docx` 与 Open WebUI README，完成本地部署。
- **Agent 输出（要点）**：
  1. 环境探测：本机无 Docker、无 sudo，但已安装 `uv`；有 NVIDIA RTX 3060 GPU；官方 README 建议 Python 3.11。
  2. 用 `uv venv --python 3.11 .venv` 创建虚拟环境，`uv pip install open-webui` 安装依赖（约 573 个包）。
  3. `setsid` 后台启动 `.venv/bin/open-webui serve`，完成数据库迁移与 embedding 模型加载。
  4. 验证 `curl http://localhost:8080/` 返回 200。
- **采纳的决策**：
  | 决策 | 理由 |
  |---|---|
  | 采用 pip/uv 安装而非 Docker | 本机无 Docker 且无 sudo 权限 |
  | 使用 Python 3.11 | 官方 README 明确建议 3.11 以避免兼容性问题 |
  | 虚拟环境放仓库内 `.venv/` | 本地开发方便，且已加入 `.gitignore` 不入库 |
  | `.webui_secret_key` 与数据库不入库 | 运行时敏感文件，避免泄露 |
- **遇到的问题与解决**：`uv pip install` 首次超时（torch 等依赖较大），改为后台执行、轮询日志确认完成。
- **结果**：Open WebUI 启动于 http://localhost:8080（HTTP 200）。

---

## 交互 2 — 创建管理员账号并配置 DeepSeek API

- **时间**：2026-09-03 18:50
- **模型/Agent**：opencode / DeepSeek-V4-Flash-0731
- **任务**：创建 Open WebUI 管理员账号，接入 DeepSeek 大语言模型。
- **Prompt（要点）**：阅读 https://api-docs.deepseek.com/zh-cn/，创建管理员账号并连接 DeepSeek API。
- **Agent 输出（要点）**：
  1. 确认 DeepSeek base_url 为 `https://api.deepseek.com`，OpenAI 兼容格式。
  2. 验证 API key：`GET https://api.deepseek.com/models` 成功，返回 `deepseek-v4-flash`、`deepseek-v4-pro`、`deepseek-v4-flash-vision-exp`。
  3. 通过 `POST /api/v1/auths/signup` 创建管理员账号（kei2332@qq.com，role=admin）。
  4. 排查配置端点：初试 `/api/v1/openai/config/update` 返回 405，读源码发现 openai 路由挂载于 `/openai`（非 `/api/v1`）。
  5. 用 `POST /openai/config/update` 写入 base_url + api_key + ENABLE_OPENAI_API，`POST /openai/verify` 验证连通。
  6. 端到端验证：`/api/models` 列出 deepseek 模型；`/api/chat/completions` 调用 deepseek-v4-flash 返回正常回答。
- **采纳的决策**：
  | 决策 | 理由 |
  |---|---|
  | 用 `/openai` 前缀端点 | openai.router 在 main.py 中挂载于 `/openai` |
  | base_url 用 `https://api.deepseek.com` | DeepSeek 官方文档指定（OpenAI 兼容） |
  | 模型选 deepseek-v4-flash | 官方最新版，速度快、成本低，适合课程问答 |
- **遇到的问题与解决**：
  - 405 Method Not Allowed：端点前缀错误，源码定位后改用 `/openai/config/update`。
  - API key 不入库：仅写入 Open WebUI 配置存储，不提交仓库。
- **结果**：DeepSeek 已接入，管理员账号可用。
