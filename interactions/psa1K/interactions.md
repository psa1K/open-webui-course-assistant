# psa1K 交互记录

> 说明：每次交互按时间顺序追加；字段包括时间、Agent/模型、任务、prompt、Agent 输出、决策、问题与解决。

---

## 交互 1 — Open WebUI 本地部署（issue #14）

- **时间**：2026-09-03 17:10
- **Agent/模型**：opencode / DeepSeek-V4-Flash-0731
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
- **Agent/模型**：opencode / DeepSeek-V4-Flash-0731
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

---

## 交互 3 — 可复现性修改

- **时间**：2026-09-03 19:18
- **Agent/模型**：opencode / DeepSeek-V4-Flash-0731
- **任务**：保证仓库可复现，使同伴 clone 后能独立跑通 Open WebUI 环境。
- **Prompt（要点）**：锁定依赖版本；API key 环境化；AGENTS.md 新增可复现性规则；README 增加克隆复现说明。
- **Agent 输出（要点）**：
  1. 生成 `requirements.lock`：`uv pip freeze` 锁定 282 个依赖精确版本（open-webui 0.11.3、torch 2.14.0）。
  2. 新增 `.env.example`（OpenAI 兼容模板，DeepSeek base_url + key 占位符），`.gitignore` 增加 `.env`。
  3. 新增 `scripts/setup.sh`：创建 Python 3.11 venv + 按锁文件安装依赖。
  4. AGENTS.md 新增第 5 节「可复现性要求」。
  5. README 新增「克隆并复现」「手动安装」「克隆后验证清单」章节。
  6. 验证：在临时 venv 中按 `requirements.lock` 安装，open-webui 0.11.3 可正常 import。
- **采纳的决策**：
  | 决策 | 理由 |
  |---|---|
  | 用 `uv pip freeze` 锁定全部依赖 | 保证两台机器环境完全一致 |
  | 密钥走 `.env`（gitignore） | Open WebUI 自动加载项目根 `.env`，且真实 key 不入库 |
  | 加一键 `setup.sh` | 同伴克隆后一条命令完成环境搭建 |
  | 每条密钥由各自独立申请 | 避免共享 key 的泄露风险 |
- **遇到的问题与解决**：验证临时 venv 占用约 7.2G，验证后已删除释放空间。
- **结果**：可复现验证通过，PR 待用户审核后合并。

---

## 交互 4 — 课程知识库搭建（issue #15）

- **时间**：2026-09-04 11:20
- **Agent/模型**：opencode / DeepSeek-V4-Flash-0731
- **任务**：认领并完成 issue #15「课程知识库：建立课程专属知识库（≥8 个资料/≥30页，按章节分类）」，并上传到 Open WebUI 验证 RAG。
- **Prompt（要点）**：把 `notes/2026summer internship/` 的课程资料整理为知识库；course-1-14 拆成 Markdown；两门课程都建 collection。
- **Agent 输出（要点）**：
  1. 编写 `scripts/export_units.py`：解析 `course-1-14/index.html` 的 14 个 `course-unit`，转成 14 个 Markdown 文件（含标题、正文、代码块、清洗空白）。
  2. 整理 `knowledge/`：`codex-course/`（14 个 MD + 协作工具 PDF 85页 + courses_mcp01.py）、`math-modeling/`（Lecture1.pdf 24页 + Lecture1.tex）、`knowledge/README.md` 索引。
  3. 编写 `scripts/upload_knowledge.py`：登录→建 collection→上传文件→等处理完成→挂载到知识库。
  4. 上传：codex-course 16 个文件、math-modeling 2 个文件。
  5. RAG 验证：`POST /api/v1/retrieval/query/collection` 查询两库均返回相关文档。
- **采纳的决策**：
  | 决策 | 理由 |
  |---|---|
  | 课件拆成 Markdown 入库 | 便于 RAG 检索与引用，HTML 解析效果差 |
  | 79 张图片不入库 | 占 25M 体积，RAG 意义有限 |
  | 两门课程各建一个 collection | 用户确认"两门都建" |
  | collection 名用知识库 ID 查询 | Open WebUI collection 实际名称是知识库 ID |
- **遇到的问题与解决**：
  - 上传后立即 `file/add` 报 "content is empty"：文件异步处理未完成，加 `wait_for_processing` 轮询 status=completed。
  - 重复上传导致 "Duplicate content"：清理残留文件 + `--reset` 重建知识库后重传。
  - 用 collection 名 "codex-course" 查询为空：改用知识库 ID 作为 collection 名查询成功。
- **结果**：两个知识库已建且 RAG 检索正常（codex-course 16 文件、math-modeling 2 文件）。

---

## 交互 5 — 同步队友改动与课程工具安装（issue #18）

- **时间**：2026-09-05 01:10
- **Agent/模型**：opencode / glm-5.3-flash
- **任务**：同步远程仓库（队友 PR #40-#43），审阅 #16/#17 交付；在本机 Open WebUI 安装 `create_course_tool.py` 对应的 Workspace Tool（issue #18）。
- **Agent 输出（要点）**：
  1. 同步：远程 main 领先 15 提交，`git pull` 完成同步；队友交付统一知识库 `course-knowledge-base`（18 文件）、RAG 验证（6 类通过）、课程助教（`course-ai-assistant`）。
  2. 审阅：19 项单元测试（venv）全部通过；验证结果无密钥泄露；发现本机 Open WebUI 尚无统一知识库与助教（队友验证在其本机完成）。
  3. 工具安装：`create_course_tool.py --dry-run` 通过后实际执行，Open WebUI 创建成功 `course_practice_generator`（章节练习题生成器）。
  4. 验证：工具详情确认 `class Tools` 与 `generate_practice_questions` 完整；chat function calling 中模型正确发起 `tool_calls`；本地执行逻辑验证合法输入返回 `ready`、非法输入返回 `INVALID_INPUT`。
- **采纳的决策**：
  | 决策 | 理由 |
  |---|---|
  | 用 `--dry-run` 预检再安装 | 避免覆盖现有配置 |
  | function calling 验证而非 REST execute | Workspace Tool 由对话内模型调用，无独立 execute 端点 |
- **遇到的问题与解决**：直接 REST 调用工具执行端点返回 405；读源码确认 Workspace Tool 仅在 chat 中由模型调用，改用 chat/completions + `tool_ids` 验证。
- **结果**：工具已安装并可用；待办——本机尚需同步统一知识库与助教（`upload_knowledge.py --reset` + `create_course_assistant.py`）。

---

## 交互 6 — 随机抽题工具实现与安装（issue #19）

- **时间**：2026-09-05 10:30
- **Agent/模型**：opencode / glm-5.3-flash
- **任务**：认领并完成 issue #19「自定义扩展：随机抽题工具」——基于真实题库按章节/难度/题型随机抽题。
- **Agent 输出（要点）**：
  1. 编写题库 `data/question-bank.json`：23 题（codex 16 题 + math-modeling 7 题），三档难度、五种题型，每题标注来源文件与章节（来源全部真实存在于 knowledge/）。
  2. 实现工具 `tools/random_question_picker.py`：参数校验（course/chapter 模糊匹配/difficulty/question_type/count 1-10/include_answer/seed 可复现抽取）、无匹配时报 NO_MATCHING_QUESTIONS、默认不含答案。
  3. 安装器 `scripts/create_random_picker_tool.py`：校验题库完整性（题量≥8、必填字段、来源真实）后把题库内嵌进工具源码（Workspace Tool 无文件系统访问），dry-run + create。
  4. 测试 `tests/test_random_picker_tool.py` 18 项（种子可复现、答案策略、输入校验、来源存在性、安装器内嵌/防篡改），全量 57 项回归通过。
  5. 配置文档 `configs/course-tools/random-question-picker.md`。
  6. 本机 Open WebUI 安装成功（bank=23 内嵌），chat function calling 中模型正确发起 `pick_random_questions` 调用。
- **采纳的决策**：
  | 决策 | 理由 |
  |---|---|
  | 题库 JSON 入库 + 安装器内嵌 | 题库可维护可审查；Workspace Tool 沙箱无文件系统，运行时必须内嵌 |
  | seed 参数支持复现 | 题目固定可定位，便于测试与复习，区别于 #18 的临时生成 |
  | 选择题答案取 options[answer_index] | 答案确定；简答/建模题只给参考要点，避免代写 |
- **遇到的问题与解决**：
  - 题库内嵌后 `json.loads` 报 TypeError：占位符替换时丢了 `json.dumps()` 包裹，注入成了 dict 字面量；改为对 JSON 字符串再编码成字符串字面量。
  - 测试假定抽到选择题但 seed 命中简答题：拆分为两个用例，选择题校验精确答案、简答题校验参考要点前缀。
- **结果**：#19 完成——题库+工具+安装器+测试+文档齐备，本机已安装并验证可调用。
---

## 交互 7 — 客观题自动判分工具（issue #20）

- **时间**：2026-09-05 17:46
- **Agent/模型**：opencode / DeepSeek-V4-Flash-0731
- **任务**：认领并完成 issue #20「自定义扩展：客观题自动判分工具」——输入学生答案与标准答案，输出判分与解析。
- **Agent 输出（要点）**：
  1. 实现 `tools/objective_grader.py`：两种模式——`grade_from_bank`（对照题库内嵌标准答案判分）与 `grade_answers`（调用方直接给题的通用判分）。
  2. 真实结构化判分逻辑：单选/概念题支持字母、1 起始序号、选项文本三种答案规整；多选按无序集合比较；填空/判断规范化精确匹配（可多个可接受值）；支持加权计分与及格阈值。
  3. 安装器 `scripts/create_objective_grader_tool.py`：校验题库完整性、工具方法存在、无网络/数据库/敏感依赖后内嵌题库。
  4. 测试 `tests/test_objective_grader_tool.py` 25 项（题库对照、字母/序号/文本匹配、多选无序、填空别名、加权阈值、主观题跳过、未知题号、非法输入等），全量 82 项回归通过。
  5. 配置文档 `configs/course-tools/objective-grader.md`。
  6. 本机 Open WebUI 安装成功（bank=23 内嵌），chat function calling 中模型正确发起 `grade_from_bank` 调用。
- **采纳的决策**：
  | 决策 | 理由 |
  |---|---|
  | 复用题库做标准答案 | 题库题目的 options+answer_index 已是权威客观标准，无需重复录入 |
  | 客观题判分、主观题标注跳过 | 简答/建模等无法结构化判分，诚实返回 NOT_OBJECTIVE 需人工判分，不伪造分数 |
  | 字母/序号/文本三路规整 | 覆盖学生实际作答习惯，且不依赖提示词猜答案 |
- **遇到的问题与解决**：
  - 多选标准集合判错：正确为选项[1,3]（B,D），学生选 A,C 被正确判为错——确认判分逻辑无误，补充了顺序无关测试用例。
  - `_entry` 的 `number` 字段取值写法怪异且有缩进错误：改为循环内统一赋 `item["number"]=idx`，修正缩进。
- **结果**：#20 完成——判分工具+安装器+测试+文档齐备，本机已安装并验证可调用。

---

## 交互 8 — 课程章节查询工具（issue #22）

- **时间**：2026-09-07 17:34
- **Agent/模型**：opencode / deepseek-v4-pro-0813
- **任务**：认领并完成 issue #22「自定义扩展：课程章节查询工具」——输入关键词/章节，输出对应章节的知识点与资料位置。
- **Agent 输出（要点）**：
  1. 建立 `data/course-catalog.json`：两门课程 22 章的结构化目录（章节标题、类型、关键词、知识点、小节、来源文件/目录/小节），来源全部真实存在于 knowledge/。
  2. 实现 `tools/course_catalog_query.py`：`query_chapter`（关键词/章节查询）与 `list_chapters`（列出课程章节）；规范化子串匹配，标题 > 关键词 > 知识点 > 小节四级相关性排序；支持中英文、大小写不敏感、按课程限定。
  3. 安装器 `scripts/create_course_catalog_tool.py`：校验目录完整性（≥8 章、至少两门课、必填字段、来源真实、无网络/数据库/敏感依赖）后内嵌目录。
  4. 测试 `tests/test_course_catalog_tool.py` 20 项（标题/关键词/英文/大小写/课程限定/排序/无匹配/非法输入/来源存在性/编号唯一等），全量 102 项回归通过。
  5. 配置文档 `configs/course-tools/course-catalog-query.md`。
  6. 本机 Open WebUI 安装成功（chapters=22 内嵌），chat function calling 中模型正确发起 `query_chapter(keyword=MCP)` 调用。
- **采纳的决策**：
  | 决策 | 理由 |
  |---|---|
  | 目录数据独立于题库 JSON | 章节结构/知识点/资料位置与题目是两类数据，职责分离 |
  | 确定性目录检索而非向量召回 | 与 RAG 全文检索互补：目录查询结果精确、可复现、带明确资料路径 |
  | 四级相关性排序 | 标题命中最相关，其次关键词、知识点、小节，符合查询直觉 |
- **遇到的问题与解决**：
  - Open WebUI 服务随 WSL 会话关闭而停止：重启 `open-webui serve` 并等待 SentenceTransformer 加载完成后恢复健康检查。
- **结果**：#22 完成——目录数据+查询工具+安装器+测试+文档齐备，本机已安装并验证可调用。
