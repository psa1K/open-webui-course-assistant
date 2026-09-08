# Issue #25 已批准优化记录

- **批准时间**：2026-09-08 11:25（Asia/Shanghai；实际交互时间）
- **批准人**：用户
- **批准内容**：OPT-A、OPT-B、OPT-C、OPT-D、OPT-E
- **基线证据**：`baseline-results.json` 保留第一轮 15 项真实失败结果，未覆盖、未改写。

## 已批准优化的实施记录

| 编号 | 对应基线证据 | 已实施改动 | 修改位置 | 状态 | 风险与回滚 |
|---|---|---|---|---|---|
| OPT-A | SYS-01～SYS-08 缺少可验证的资料证据链，关键章节召回不稳定。 | 验证请求改为调用已部署的 `course-ai-assistant`；验证助教模型与 Knowledge 绑定；把实际检索片段和本轮允许引用文件传入聊天上下文并记录 `actual_queries`。 | `scripts/verify_system_evaluation.py` | 已实施，待第二轮真实复测。 | 保持固定 15 题、Top-K=5、阈值=0.30；恢复基线请求/排序逻辑即可回滚。 |
| OPT-B | SYS-09、SYS-10 在声明资料未覆盖后继续给出外部事实。 | 系统提示词要求无有效资料时输出“资料中未找到相关信息”后停止；验收逻辑检测拒答后补充的模型记忆或外部事实。 | `configs/course-assistant/system-prompt.md`、`scripts/verify_system_evaluation.py` | 已实施，待第二轮真实复测。 | 可能增加无依据问题的拒答率；恢复原提示词段落和判定逻辑即可回滚。 |
| OPT-C | SYS-11、SYS-12、SYS-14、SYS-15 因首个响应没有普通 `assistant.content` 被误判。 | 兼容普通 JSON、嵌套/流式响应、`tool_calls` 与函数参数；取得已部署工具源码，对固定输入执行结构化契约核验，并记录探测输出及响应形态。 | `scripts/verify_system_evaluation.py` | 已实施，待第二轮真实复测。 | 不改工具业务功能；恢复只读取文本响应的旧解析逻辑即可回滚。 |
| OPT-D | SYS-13 对 `course_catalog_query` 返回 HTTP 404。 | 保留并复核 `scripts/create_course_catalog_tool.py` 的创建/更新流程；离线 dry-run 已确认会部署 22 个结构化章节。 | `scripts/create_course_catalog_tool.py`、`tools/course_catalog_query.py`（既有实现） | **待本机真实同步**：当前验证执行环境无法连接本机 Open WebUI，且未提供管理员环境变量。 | 服务恢复后可重新运行创建脚本；必要时在 Open WebUI 删除或更新该工具。不得将 dry-run 记为真实部署成功。 |
| OPT-E | SYS-01～SYS-08 的课程关键词、跨资料组合和关键文件选择不稳定。 | 增加透明检索查询扩展；按有效性、关键来源和分数排序；SYS-06 保留“模型接入”和“Git/GitHub 工作流”两个子查询的核心来源。 | `scripts/verify_system_evaluation.py` | 已实施，待第二轮真实复测。 | 不修改固定用户题目、知识库、切分、Top-K 或阈值；移除 `RETRIEVAL_OVERRIDES` 与 `PREFERRED_SOURCES` 即可回滚。 |

## 未获批准的改动

无。除上表列出的 OPT-A～OPT-E 外，本轮没有修改模型配置、课程资料、知识库切分策略、Top-K、相关性阈值或固定 15 个测试输入。

## 第二轮真实验收结果

用户已在本机 Open WebUI 完成第二轮固定用例运行，结果写入 `optimized-results.json`：15 项中 10 项通过、5 项未通过。详细逐项变化、真实失败原因和后续建议见 `before-after-comparison.md`。

本轮没有为处理仍未通过项而新增或未经批准地修改提示词、知识库、切分、检索参数、工具或模型配置。

## 已执行验收步骤

1. 启动本机 Open WebUI，并在**本机终端**设置 `OPENWEBUI_EMAIL`、`OPENWEBUI_PASSWORD`；不要把密码写入本文件、聊天记录或仓库。
2. 真实同步 OPT-D：

   ```bash
   .venv/bin/python scripts/create_course_catalog_tool.py \
     --base http://127.0.0.1:8080
   ```

3. 使用相同 15 个固定用例运行第二轮：

   ```bash
   .venv/bin/python scripts/verify_system_evaluation.py \
     --base http://127.0.0.1:8080 \
     --model deepseek-v4-flash \
     --phase optimized
   ```

4. 保存真实 `optimized-results.json`，再生成 `before-after-comparison.md`。以上步骤已完成；Issue #25 的两轮测试与对比归档验收已完成，但不表示 15 项均已通过。
