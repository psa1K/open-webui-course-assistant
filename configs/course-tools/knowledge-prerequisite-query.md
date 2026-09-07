# 知识点先修关系查询工具

`知识点先修关系查询工具`（Tool ID：`knowledge_prerequisite_query`）根据仓库内的结构化数据 `data/knowledge-prerequisites.json` 查询知识点的推荐学习依赖关系，并通过 `data/course-catalog.json` 返回对应的课程章节和资料文件。

它不调用模型、不联网、不读数据库，也不根据模型记忆推断不存在的关系。关系表示项目维护的“推荐学习先后依赖”，资料来源表示该知识点对应的课程材料位置。

## 输入

- `knowledge_point`：必填。知识点名称、别名或关键词，例如 `KMP`、`Codex CLI 安装`、`MCP Server`。
- `course`：可选。`codex` 或 `math-modeling`；不填时可跨课程匹配。
- `include_indirect`：可选，布尔值，默认 `false`。开启后同时返回间接前置依赖和间接后续知识点。

无效输入返回：

```json
{
  "status": "error",
  "error_code": "INVALID_INPUT",
  "message": "knowledge_point 不能为空。"
}
```

## 输出

成功结果固定包含：

- `status`：`ok`；
- `mode`：`knowledge_prerequisite_query`；
- `relation_scope`：关系的维护范围；
- `query`：规范化后的查询参数；
- `matched_count`：匹配知识点数量；
- `knowledge_points`：每个匹配项的名称、课程、所属章节、资料来源、`prerequisites`（直接前置依赖）和 `successors`（直接后续知识点）。

当 `include_indirect=true` 时，每个匹配项还包含 `all_prerequisites` 和 `all_successors`。每个节点均带有真实章节 ID、章节标题、资料文件名与目录。

例如查询 `KMP`：

```json
{
  "status": "ok",
  "mode": "knowledge_prerequisite_query",
  "matched_count": 1,
  "knowledge_points": [
    {
      "name": "KMP 算法",
      "prerequisites": [{"name": "前缀函数"}],
      "successors": [],
      "chapter": {
        "id": "MM-01",
        "title": "KMP 算法",
        "source": {"file": "Lecture1.pdf", "dir": "knowledge/math-modeling"}
      }
    }
  ]
}
```

找不到知识点时，工具返回 `matched_count=0`，并明确写出“资料中未找到相关信息”，不会虚构前置关系或资料来源。

## 安装与调用

```bash
export OPENWEBUI_EMAIL="你的管理员邮箱"
export OPENWEBUI_PASSWORD="你的管理员密码"

# 仅检查工具源码和嵌入数据，不写入 Open WebUI
.venv/bin/python scripts/create_prerequisite_query_tool.py \
  --base http://127.0.0.1:8080 \
  --dry-run

# 创建；同 ID 已存在时更新
.venv/bin/python scripts/create_prerequisite_query_tool.py \
  --base http://127.0.0.1:8080
```

同步后在 Open WebUI 的“工作空间 → 工具”中选择“知识点先修关系查询工具”。调用示例：

> 查询数学建模课程中 KMP 算法的前置依赖和后续知识点。

> 查询 Codex 课程中 MCP Server 的前置知识点，并返回间接依赖。

> 查询 Git/GitHub 工作流的后续知识点和资料来源。
