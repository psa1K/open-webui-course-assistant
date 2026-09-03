# AGENTS.md — 团队协作约定

本仓库为「软件工程编程实训」课程项目 *课程专属 AI 助手*（李正丹、朱静雯 出题）的协作仓库，基于 Open WebUI + Codex 开发。

## 团队成员

- **psa1K** (Jialiang Cai)
- **eco-NIN** (Yuzhe Guo)

## 基本要求

### 1. 保留与 Agent 的交互记录

本项目要求综合使用 Codex / Claude / opencode 等 AI 编程工具完成开发。**两名成员必须分别保留各自与 Agent 的交互记录**，作为课程成果之一提交（题目要求提交"与 Codex 的交互记录"）。

- 记录存放位置：`interactions/<github-username>/` 目录
- 文件命名：每位成员在自己的目录下**仅维护一个** Markdown 文件，文件名固定为 `interactions.md`
- 记录内容：**每次交互**包含
  - **时间**：交互发生的时间（如 `2026-09-03 17:10`）
  - **Agent/模型**：使用的 Agent 与模型（如 `opencode / DeepSeek-V4-Flash-0731`）
  - 任务描述与输入的 prompt
  - Agent 返回的关键输出（可截取要点）
  - 采纳/修改的决策与理由
  - 遇到的问题与解决办法
- 每次交互按时间顺序追加到 `interactions.md`；随代码一同提交，记录文件由各自成员负责维护，互不覆盖

### 2. 所有提交走 PR-Merge 流程

- 禁止直接推送 `main`
- 所有改动在功能分支上开发：`feat/<name>` / `fix/<name>` / `docs/<name>`
- 通过 Pull Request 合并到 `main`，合并前确认 diff 干净、无敏感信息
- **PR 须经用户审核通过后方可合并**：Agent 不得自行合并 PR，需等待用户（成员）明确批准后再执行 merge
- **合并后删除分支**：PR merge 后立即删除本地与远程的 feature 分支，避免残留
- 提交信息遵循 Conventional Commits：`<type>(<scope>): <subject>`（类型 `feat` `fix` `docs` `refactor` `test` `chore` 等）
- 提交与 PR 使用 agent 身份时用该成员所用 agent 的标识注明：如 psa1K 使用 opencode，则以 `opencode[bot]` 署名；另一同伴按其实际使用的 agent（如 Codex / Claude 等）署名，方便区分人类与 Agent 提交

### 3. README.md 的创建与维护

- 新建 `README.md`，并在每次更新后维护它
- README 至少包含：项目简介、安装与部署方式、使用说明、目录结构、测试与优化记录入口
- 每次功能更新、部署变更或文档调整后，同步更新 README 的对应章节，保持与仓库实际状态一致

### 4. 代码与文档约定

- 不引入未使用的依赖；不添加冗余注释
- 课程资料（知识库原始文件）按章节/模块分类存放
- 关键配置（模型配置、系统提示词、RAG 参数）需在仓库中留档，便于测试与优化对比

### 5. 可复现性要求

- 项目任何编辑/更改必须保证**仓库拥有者（其他成员）克隆后可按 README 复现**，不得依赖个人本机的私有数据（数据库、密钥、缓存等）才能运行
- 涉及依赖、配置、知识库、模型、工具的改动，须同步更新 `requirements.lock`、`.env.example`、`scripts/` 与 README，使「全新 clone → `./scripts/setup.sh` → 启动」可一次通过
- 真实密钥（如 API key）一律放入本机 `.env`（已 gitignore），只提交 `.env.example` 模板
- 依赖变更后须重新生成 `requirements.lock`，保证环境一致
