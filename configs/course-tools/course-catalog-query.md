# 课程章节查询工具

## 用途

`课程章节查询工具`（Tool ID：`course_catalog_query`）是一个 Open WebUI Workspace Tool，基于**结构化课程目录**（`data/course-catalog.json`，两门课程共 22 章）按关键词/章节查询，输出对应章节的**知识点与资料位置**。

与知识库 RAG 检索（全文向量召回）不同，本工具是**确定性目录检索**：章节标题、关键词、知识点、小节、来源文件均由人工整理入库，查询结果精确、可复现、带明确资料路径。

## 数据来源

`data/course-catalog.json`（安装时内嵌进工具源码），结构：

- **codex 课程**：16 章（14 个单元课件/实验 + 协作工具 PDF + 示例代码），章节对应 `knowledge/codex-course/` 下的文件名
- **math-modeling 课程**：6 章（KMP 算法、等价变化与重要假设、问题规模与计算机硬件、组合优化、图论、统计），对应 `knowledge/math-modeling/Lecture1.pdf` 各小节

每章含 `id / title / type / keywords / knowledge_points / sections / source{file, dir, section}`。

## 查询逻辑（真实结构化）

- **关键词匹配**：对章节的标题、关键词、知识点、小节做规范化（小写、去空白）子串匹配
- **相关性排序**：标题命中（rank 4）> 关键词命中（3）> 知识点命中（2）> 小节命中（1）
- 支持中文/英文关键词（如 `MCP`、`KMP`、`沙盒`）、大小写不敏感
- 无匹配返回 `matched_count=0` 并提示换关键词，不崩溃

## 输入参数

| 参数 | 类型 | 约束 |
|---|---|---|
| `keyword` | `string` | `query_chapter` 必填，非空 |
| `course` | `string \| null` | 可选；`codex` 或 `math-modeling`，用于限定课程 |

方法二 `list_chapters(course=None)`：列出全部/指定课程的章节清单。

## 输出结构

```json
{
  "status": "ok",
  "mode": "catalog_query",
  "query": {"keyword": "MCP", "course": null},
  "matched_count": 2,
  "chapters": [{
    "id": "CX-12",
    "course": "codex",
    "course_name": "Codex 实战课程",
    "title": "核心功能：MCP 与 Git / GitHub 工作流",
    "type": "课件",
    "knowledge_points": ["MCP", "Git 工作流", "Pull Request"],
    "sections": ["MCP(Model Context Protocol)", "代码管理（Git 与 GitHub 工作流）"],
    "source": {"file": "12-核心功能-mcp-与-git-github-工作流.md", "dir": "knowledge/codex-course"}
  }]
}
```

## Open WebUI 使用

```bash
# 安装/更新（目录内嵌 + 校验）
.venv/bin/python scripts/create_course_catalog_tool.py --dry-run
.venv/bin/python scripts/create_course_catalog_tool.py
```

对话中直接说：

```text
查一下 MCP 相关的章节。
```

```text
列出数学建模课程的所有章节。
```

## 数据维护

- 扩充课程/章节：修改 `data/course-catalog.json` 后重新运行安装脚本
- 安装器校验：章节总数 ≥ 8、至少两门课程、每章含必填字段、来源文件/目录真实存在、工具含两个查询方法、无网络/数据库/敏感依赖
- 工具不联网、不访问数据库、不含密钥