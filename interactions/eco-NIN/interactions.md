# eco-NIN 交互记录

> 说明：每次交互按时间顺序追加；字段包括时间、Agent/模型、任务、prompt、Agent 输出、决策、问题与解决。

---

## 交互 1 — 本地部署 Open WebUI

- **时间**：2026-09-04
- **Agent/模型**：Codex / GPT-5.4
- **任务**：在刚 clone 的项目中完成本地部署并运行 Open WebUI，了解重启方式，并确认如何维护 Codex 交互记录。
- **Prompt（要点）**：先在我的本地部署并运行；如何重新启动；找不到运行 Open WebUI 的终端窗口；询问和 Codex 的交互记录如何生成，以及两名同学如何共同维护。
- **Agent 输出（要点）**：检查仓库配置后，创建 Python 3.11 虚拟环境并安装平台兼容的 `open-webui==0.11.3`；由于 8080 端口已有实例，确认现有服务健康接口返回 `{"status":true}`；说明项目要求每位成员在 `interactions/<github-username>/interactions.md` 中维护自己的记录，记录时间、Agent/模型、任务、Prompt、关键输出、决策和问题解决过程。
- **采纳的决策**：本成员使用 `interactions/eco-NIN/interactions.md`；另一位同学继续使用 `interactions/psa1K/interactions.md`；双方只追加自己的文件，不覆盖对方记录。
- **遇到的问题与解决**：项目原锁文件包含 Apple Silicon 不支持的 CUDA 依赖，改用平台兼容的 Open WebUI 安装方式；启动时遇到 8080 端口占用，确认已有 Open WebUI 实例正常运行，避免重复启动。

---

## 交互 3 — 撤销并重新实现 Issue #16

- **时间**：2026-09-04
- **Agent/模型**：Codex / GPT-5.4
- **任务**：删除旧版 Issue #16 配置，同步 Issue #15 最新知识库，并使用全部资料完成统一知识库的 RAG 检索与引用实现。
- **Prompt（要点）**：Issue #15 已完成；删除刚刚完成的 Issue #16，重新同步最新更改；`knowledge/` 是一个统一知识库，包含 Codex 实战课程和数学建模资料；完成真实上传、API 检索验证和文档更新。
- **Agent 输出（要点）**：已从最新 `origin/main` 创建 `feat/eco-nin-rag-knowledge-base`；清理旧版“仅配置方案”方向，改为一个 `course-knowledge-base`；新增统一上传脚本、API 检索验证脚本、系统提示词、RAG 参数、引用规范和验收模板，并更新 README。
- **采纳的决策**：两个课程目录全部上传到同一个 Open WebUI Knowledge，不拆分知识库；通过真实文件名和章节/片段进行引用；不保存凭据和 token。
- **遇到的问题与解决**：远程同步前本地 README 有未提交修改，先安全暂存后切换到最新 `origin/main`；旧上传脚本的 `--base` 未生效，重构为显式传递服务地址。
- **验证状态**：配置和脚本已完成；本地上传/API 验证待在管理员凭据环境中执行，未提前宣称检索结果通过。
