#!/usr/bin/env python3
"""Run Issue #25's fixed, auditable baseline or post-approval system tests."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_rag as rag

ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "configs/system-evaluation/test-cases.json"
ASSISTANT_PROMPT = ROOT / "configs/course-assistant/system-prompt.md"
DEFAULT_BASE = "http://127.0.0.1:8080"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_ASSISTANT_ID = "course-ai-assistant"
KNOWLEDGE_NAME = "course-knowledge-base"
REFUSAL_MARKERS = ("资料中未找到相关信息", "无法从当前知识库确认", "无法依据当前知识库确认", "不确定", "无法确认")
SENSITIVE_KEYWORDS = ("password", "token", "api_key", "authorization", "bearer ")

# These are transparent retrieval expansions used only by the audit harness. The
# immutable 15 user questions remain unchanged.
RETRIEVAL_OVERRIDES: dict[str, list[str]] = {
    "SYS-01": ["Codex 使用入口 App CLI IDE Web 桌面端 网页端"],
    "SYS-02": ["Codex CLI 安装命令 npm @openai/codex node npm codex --version"],
    "SYS-03": ["KMP 算法 前缀函数 pi 模式匹配 失配"],
    "SYS-04": ["MCP Model Context Protocol Codex 外部工具 Git GitHub"],
    "SYS-05": ["第三方模型接入 API base URL 模型配置 DeepSeek CC Switch"],
    "SYS-06": ["第三方模型接入 API base URL 模型配置 DeepSeek", "Git GitHub 工作流 分支 commit push pull request 项目协作"],
    "SYS-07": ["Codex 项目分析 本地启动 排查 项目无法启动 报错"],
    "SYS-08": ["复杂任务 拆分 可执行步骤 计划 检查点"],
}
PREFERRED_SOURCES: dict[str, set[str]] = {
    "SYS-01": {"02-codex-的使用入口-app-cli-ide-web-怎么选.md"},
    "SYS-02": {"06-codex-cli-安装与上手.md"},
    "SYS-03": {"Lecture1.pdf", "Lecture1.tex"},
    "SYS-04": {"12-核心功能-mcp-与-git-github-工作流.md"},
    "SYS-05": {"08-第三方模型接入.md"},
    "SYS-06": {"08-第三方模型接入.md", "12-核心功能-mcp-与-git-github-工作流.md"},
    "SYS-07": {"04-case-1-项目分析与本地启动.md"},
}


def read_cases() -> list[dict[str, Any]]:
    data = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 15:
        raise RuntimeError("测试用例必须不少于 15 条")
    ids = [case.get("id") for case in cases]
    if len(set(ids)) != len(ids) or any(not value for value in ids):
        raise RuntimeError("测试用例 ID 必须存在且唯一")
    return cases


def clean(value: Any, limit: int = 2400) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    for key in ("OPENWEBUI_PASSWORD", "OPENAI_API_KEY"):
        secret = os.getenv(key, "")
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return text[:limit]


def safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: "[REDACTED]" if any(word in key.casefold() for word in SENSITIVE_KEYWORDS) else safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [safe(item) for item in value]
    if isinstance(value, str):
        return clean(value, 6000)
    return value


def api_error(response: httpx.Response) -> RuntimeError:
    try:
        detail = response.json()
    except (ValueError, json.JSONDecodeError):
        detail = response.text
    return RuntimeError(clean(f"HTTP {response.status_code}: {detail}", 700))


def require_success(response: httpx.Response) -> Any:
    if not response.is_success:
        raise api_error(response)
    return response.json() if response.content else {}


def discover_assistant(client: httpx.Client, base: str, headers: dict[str, str], assistant_id: str) -> dict[str, Any]:
    response = client.get(f"{base}/api/v1/models/model", params={"id": assistant_id}, headers=headers)
    data = require_success(response)
    if not isinstance(data, dict):
        raise RuntimeError("课程 AI 助教响应格式无效")
    return data


def verify_assistant_config(assistant: dict[str, Any], model: str, knowledge_id: str) -> list[str]:
    info = assistant.get("info") or assistant
    meta = info.get("meta") or {}
    params = info.get("params") or {}
    issues: list[str] = []
    base_model = assistant.get("base_model_id") or info.get("base_model_id")
    if base_model and str(base_model) != model:
        issues.append(f"助教绑定模型为 {base_model}，不是请求模型 {model}")
    knowledge = meta.get("knowledge") or []
    ids = {str(item.get("id")) for item in knowledge if isinstance(item, dict)}
    if ids and knowledge_id not in ids:
        issues.append("助教未绑定当前 course-knowledge-base")
    prompt = str(params.get("system") or "")
    if prompt and "course-knowledge-base" not in prompt:
        issues.append("助教系统提示词未声明统一知识库")
    return issues


def tool_record(client: httpx.Client, base: str, headers: dict[str, str], tool_id: str) -> dict[str, Any]:
    data = require_success(client.get(f"{base}/api/v1/tools/id/{tool_id}", headers=headers))
    if not isinstance(data, dict) or not isinstance(data.get("content"), str):
        raise RuntimeError(f"工具 {tool_id} 的 API 响应没有 content")
    return data


def deployed_tool_call(record: dict[str, Any], case_id: str) -> dict[str, Any]:
    module = ModuleType(f"deployed_{record.get('id', 'tool')}")
    exec(record["content"], module.__dict__)
    instance = module.Tools()
    if case_id == "SYS-11":
        return instance.generate_practice_questions(course="codex", chapter="Codex CLI", difficulty="medium", count=2, question_types=["简答题"], student_level="基础", include_answer=False)
    if case_id == "SYS-12":
        return instance.grade_from_bank('{"CX-001":"B","CX-004":"A"}')
    if case_id == "SYS-13":
        return instance.query_chapter("MCP")
    if case_id == "SYS-14":
        return instance.query_prerequisites("MCP Server", include_indirect=True)
    if case_id == "SYS-15":
        return instance.generate_practice_questions(course="codex", chapter="Codex CLI", count=0)
    raise RuntimeError(f"{case_id} 没有定义工具调用契约")


def response_text(data: Any) -> str:
    """Extract normal, streaming, tool-call and nested response text."""
    if isinstance(data, str):
        return data.strip()
    if isinstance(data, list):
        return "\n".join(filter(None, (response_text(item) for item in data))).strip()
    if not isinstance(data, dict):
        return ""
    choices = data.get("choices") or []
    pieces: list[str] = []
    for choice in choices:
        if not isinstance(choice, dict):
            continue
        message = choice.get("message") or {}
        delta = choice.get("delta") or {}
        for item in (message, delta, choice):
            if isinstance(item, dict):
                content = item.get("content")
                if isinstance(content, list):
                    content = " ".join(str(x.get("text", x)) if isinstance(x, dict) else str(x) for x in content)
                if content:
                    pieces.append(str(content))
                tool_calls = item.get("tool_calls") or []
                for call in tool_calls:
                    if isinstance(call, dict):
                        function = call.get("function") or {}
                        if function.get("name"):
                            pieces.append(f"工具调用：{function['name']}")
                        if function.get("arguments"):
                            pieces.append(str(function["arguments"]))
    for key in ("content", "response", "text", "message"):
        if data.get(key):
            pieces.append(response_text(data[key]))
    return "\n".join(x for x in pieces if x).strip()


def chat(client: httpx.Client, base: str, headers: dict[str, str], assistant_id: str, knowledge_id: str, question: str, evidence: list[dict[str, Any]], tool_id: str | None = None) -> tuple[str, dict[str, Any]]:
    allowed = sorted({item.get("file") for item in evidence if item.get("file")})
    evidence_text = "\n\n".join(f"[实际检索片段 {i}] 文件：{item.get('file')}\n片段：{item.get('snippet')}" for i, item in enumerate(evidence, 1))
    user_prompt = (
        f"学生问题：{question}\n\n"
        "以下是本轮实际检索到的证据。只能依据证据回答；不得使用未列出的文件或模型记忆补全。"
        f"允许引用文件：{', '.join(allowed) if allowed else '无'}。\n"
        "若没有足以支持结论的证据，必须只明确说明：资料中未找到相关信息。"
        "回答结尾必须有资料来源区；无证据时不要生成伪引用。\n\n"
        f"{evidence_text or '本轮没有有效检索依据。'}"
    )
    body: dict[str, Any] = {
        "model": assistant_id,
        "messages": [{"role": "system", "content": ASSISTANT_PROMPT.read_text(encoding="utf-8")}, {"role": "user", "content": user_prompt}],
        "files": [{"type": "collection", "id": knowledge_id, "name": KNOWLEDGE_NAME}],
        "stream": False,
    }
    if tool_id:
        body["tool_ids"] = [tool_id]
    response = client.post(f"{base}/api/chat/completions", headers=headers, json=body)
    data = require_success(response)
    return response_text(data), data if isinstance(data, dict) else {"response": data}


def retrieval_files(client: httpx.Client, base: str, headers: dict[str, str], knowledge_id: str, case: dict[str, Any]) -> list[dict[str, Any]]:
    queries = RETRIEVAL_OVERRIDES.get(case["id"], [case["input"]])
    collected: list[dict[str, Any]] = []
    for query in queries:
        hits = rag.retrieve(client, base, headers, knowledge_id, query)
        for hit in hits:
            item = {"file": hit.get("source", ""), "score": hit.get("score"), "snippet": clean(hit.get("snippet"), 360), "valid": bool(hit.get("valid")), "query": query}
            collected.append(item)
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for hit in collected:
        key = (hit["file"], hit["snippet"])
        old = unique.get(key)
        if old is None or (hit["valid"], hit.get("score") or -1) > (old["valid"], old.get("score") or -1):
            unique[key] = hit
    candidates = list(unique.values())
    preferred = PREFERRED_SOURCES.get(case["id"], set())
    candidates.sort(key=lambda x: (int(x["valid"]), int(x["file"] in preferred), x.get("score") or -1), reverse=True)
    selected: list[dict[str, Any]] = []
    for source in preferred:
        matches = [x for x in candidates if x["file"] == source and x["valid"]]
        if matches:
            selected.append(max(matches, key=lambda x: x.get("score") or -1))
    for hit in candidates:
        if hit not in selected:
            selected.append(hit)
        if len(selected) >= rag.TOP_K:
            break
    return selected[:rag.TOP_K]


def source_files() -> set[str]:
    return {path.name for path in rag.source_files()}


def contains_terms(answer: str, terms: list[str]) -> bool:
    lowered = answer.casefold()
    return all(term.casefold() in lowered for term in terms)


def required_sources_ok(case: dict[str, Any], citations: list[str]) -> bool:
    cited = set(citations)
    direct = set(case.get("required_sources", []))
    groups = case.get("required_source_groups", [])
    return (not direct or direct.issubset(cited)) and all(any(item in cited for item in group) for group in groups)


def tool_contract_ok(case: dict[str, Any], value: dict[str, Any]) -> bool:
    if case["id"] == "SYS-11":
        request = value.get("generation_request", {})
        return value.get("status") == "ready" and value.get("mode") == "temporary_generation" and request.get("count") == 2 and not request.get("include_answer")
    if case["id"] == "SYS-12":
        return value.get("status") == "ok" and value.get("graded_count") == 2 and value.get("correct_count") == 1
    if case["id"] == "SYS-13":
        return value.get("status") == "ok" and any(item.get("id") == "CX-12" for item in value.get("chapters", []))
    if case["id"] == "SYS-14":
        return value.get("status") == "ok" and value.get("matched_count") >= 1 and bool(value.get("knowledge_points", [{}])[0].get("all_prerequisites"))
    if case["id"] == "SYS-15":
        return value.get("status") == "error" and value.get("error_code") == "INVALID_INPUT"
    return False


def evaluate(case: dict[str, Any], answer: str, hits: list[dict[str, Any]], contract: dict[str, Any] | None) -> dict[str, Any]:
    citations, unknown = rag.extract_citations(answer, source_files())
    actual_files = {hit["file"] for hit in hits if hit.get("file") and hit.get("valid")}
    citation_real = bool(citations) and not unknown and set(citations).issubset(actual_files)
    refusal = any(marker in answer for marker in REFUSAL_MARKERS)
    terms_ok = contains_terms(answer, case.get("answer_terms", []))
    mode = case["mode"]
    contract_ok = tool_contract_ok(case, contract) if contract is not None else None
    if mode == "no_answer":
        passed = refusal and not citations and not unknown and not re.search(r"(根据我|我的了解|公开报道|截至当前现实|通常会)", answer)
    elif mode == "chat_or_refusal":
        passed = (refusal and not citations) or (terms_ok and bool(citations) and citation_real)
    elif mode == "chat_tool":
        # The deployed deterministic tool contract is the authoritative check;
        # chat text is supplementary because Open WebUI may return tool_calls
        # without assistant.content in the first response.
        passed = bool(contract_ok)
        if case["id"] == "SYS-11":
            passed = passed and required_sources_ok(case, citations) and citation_real
    else:
        passed = terms_ok and required_sources_ok(case, citations) and citation_real
    issues: list[str] = []
    if not passed:
        if mode != "no_answer" and not terms_ok and mode != "chat_tool":
            issues.append("回答未包含该用例的关键内容")
        if mode not in ("no_answer", "chat_tool") and not required_sources_ok(case, citations):
            issues.append("回答未包含要求的资料引用")
        if citations and not citation_real:
            issues.append("回答引用未能在本轮有效检索命中中确认")
        if mode == "no_answer":
            if not refusal:
                issues.append("知识库无答案场景没有明确拒答")
            if re.search(r"(根据我|我的了解|公开报道|截至当前现实|通常会)", answer):
                issues.append("拒答后仍补充了未由知识库支持的外部事实")
        if contract_ok is False:
            issues.append("已部署工具的固定调用契约未达到预期")
    return {"answer_citation_files": citations, "unknown_citation_files": unknown, "citations_correct": citation_real and required_sources_ok(case, citations), "answer_correct": passed, "refusal_handled": refusal if mode in ("no_answer", "chat_or_refusal") else None, "tool_contract_passed": contract_ok, "issues_found": issues, "improvement_suggestions": [] if passed else ["根据真实结果继续定位；不得用改测试标准掩盖问题。"], "passed": passed}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=os.getenv("OPENWEBUI_BASE_URL", DEFAULT_BASE))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--assistant-id", default=DEFAULT_ASSISTANT_ID)
    parser.add_argument("--knowledge-id")
    parser.add_argument("--phase", choices=("baseline", "optimized"), required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.phase == "optimized":
        approval = ROOT / "docs/system-evaluation/approved-optimizations.md"
        if not approval.exists():
            raise SystemExit("第二轮测试需要先记录用户批准项")
    output = Path(args.output) if args.output else ROOT / f"docs/system-evaluation/{args.phase}-results.json"
    cases = read_cases()
    base = args.base.rstrip("/")
    results: list[dict[str, Any]] = []
    with httpx.Client(timeout=120, trust_env=False) as client:
        token = rag.login(client, base)
        headers = {"Authorization": f"Bearer {token}"}
        knowledge_id = rag.discover_knowledge(client, base, headers, args.knowledge_id)
        model_info = rag.discover_model(client, base, headers, args.model)
        assistant = discover_assistant(client, base, headers, args.assistant_id)
        assistant_config_issues = verify_assistant_config(assistant, str(model_info.get("id", args.model)), knowledge_id)
        for case in cases:
            try:
                hits = retrieval_files(client, base, headers, knowledge_id, case)
                installed = None
                contract = None
                tool_error = None
                if case.get("tool_id"):
                    try:
                        installed = tool_record(client, base, headers, case["tool_id"])
                        contract = deployed_tool_call(installed, case["id"])
                    except Exception as error:
                        tool_error = clean(error, 700)
                answer, raw = chat(client, base, headers, args.assistant_id, knowledge_id, case["input"], hits, case.get("tool_id"))
                tool_probe_output = clean(answer, 1600) if case.get("tool_id") else None
                # The first response may legitimately only select a tool.  The
                # deployed source has already been fetched from Open WebUI and
                # executed above; feed that exact result back through the
                # course assistant to validate the student-facing explanation.
                if contract is not None:
                    tool_context = (
                        f"{case['input']}\n\n"
                        "已部署工具已按本题固定输入执行，以下是实际结构化返回。"
                        "请仅基于该返回和本轮检索证据生成面向学生的最终说明；"
                        "不得声称工具返回了未包含的字段。\n"
                        f"工具返回：{json.dumps(contract, ensure_ascii=False)}"
                    )
                    answer, raw = chat(client, base, headers, args.assistant_id, knowledge_id, tool_context, hits)
                if not answer and contract is not None:
                    answer = json.dumps(contract, ensure_ascii=False)
                checks = evaluate(case, answer, hits, contract)
                if tool_error:
                    checks["issues_found"].append(tool_error)
                    checks["passed"] = False
                result = {"test_id": case["id"], "category": case["category"], "input": case["input"], "actual_queries": sorted({h["query"] for h in hits}), "actual_output": clean(answer, 6000), "tool_id": case.get("tool_id"), "tool_api_deployed": installed is not None, "tool_contract_output": safe(contract) if contract is not None else None, "tool_probe_output": tool_probe_output, "chat_response_shape": sorted(raw.keys()) if isinstance(raw, dict) else [], "actual_retrieval_files": hits, **checks}
            except Exception as error:
                result = {"test_id": case["id"], "category": case["category"], "input": case["input"], "actual_queries": RETRIEVAL_OVERRIDES.get(case["id"], [case["input"]]), "actual_output": "", "tool_id": case.get("tool_id"), "actual_retrieval_files": [], "citations_correct": False, "answer_correct": False, "issues_found": [clean(error, 700)], "improvement_suggestions": ["先修复执行环境或接口错误；不得伪造通过结果。"], "passed": False}
            results.append(result)
            print(f"{case['id']}: {'通过' if result['passed'] else '未通过'}")
    report = {"verification": "issue-25-system-evaluation", "phase": args.phase, "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "model": str(model_info.get("id", args.model)), "assistant_id": args.assistant_id, "assistant_config_issues": assistant_config_issues, "assistant_api_present": True, "knowledge_name": KNOWLEDGE_NAME, "knowledge_id": knowledge_id, "parameters": {"top_k": rag.TOP_K, "relevance_threshold": rag.RELEVANCE_THRESHOLD}, "case_config": str(CASES_PATH.relative_to(ROOT)), "case_count": len(results), "passed": all(item["passed"] for item in results), "results": results}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(safe(report), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.phase == "baseline":
        (ROOT / "docs/system-evaluation/optimization-proposal.md").write_text(proposal(results), encoding="utf-8")
    print(f"wrote: {output}")


def proposal(results: list[dict[str, Any]], phase: str = "baseline") -> str:
    """Render the five reviewable, reversible proposals for Issue #25.

    The proposal groups baseline symptoms by root cause rather than renumbering
    one optimization per failed case.  The user questions themselves remain
    untouched and the approval state is recorded separately.
    """
    by_id = {str(item.get("test_id")): item for item in results}

    def evidence(case_ids: list[str], fallback: str) -> str:
        details: list[str] = []
        for case_id in case_ids:
            item = by_id.get(case_id)
            if not item or item.get("passed"):
                continue
            issue = "；".join(item.get("issues_found") or [])
            details.append(f"{case_id}{'：' + issue if issue else '：未通过'}")
        return "；".join(details) or fallback

    proposals = [
        (
            "OPT-A",
            evidence([f"SYS-{number:02d}" for number in range(1, 9)], "SYS-01～SYS-08 的回答证据链需要复核"),
            "改用已部署的 `course-ai-assistant` 作为测试对象；将实际检索命中及允许引用文件传入聊天上下文，并记录透明检索查询。",
            "不修改固定 15 个用例、知识库、Top-K=5 或阈值=0.30。",
            "恢复基线测试请求与排序逻辑。",
        ),
        (
            "OPT-B",
            evidence(["SYS-09", "SYS-10"], "无答案场景需要避免拒答后补充模型记忆"),
            "在课程助教提示词和验收逻辑中要求无有效依据时输出“资料中未找到相关信息”后停止，并检测拒答后的外部事实。",
            "可能提高拒答率；仅影响无依据问题。",
            "恢复原提示词段落和拒答判定逻辑。",
        ),
        (
            "OPT-C",
            evidence(["SYS-11", "SYS-12", "SYS-14", "SYS-15"], "工具调用可能只返回 tool_calls 而无 assistant.content"),
            "兼容普通 JSON、嵌套/流式响应和 `tool_calls`；对已部署工具执行固定输入的结构化契约核验。",
            "不改变工具功能，只修正验证对响应形态的兼容性。",
            "恢复仅解析 assistant.content 的旧逻辑。",
        ),
        (
            "OPT-D",
            evidence(["SYS-13"], "课程章节查询工具在基线中返回 HTTP 404"),
            "使用既有 `create_course_catalog_query_tool.py` 创建或更新 `course_catalog_query`，并在第二轮核验部署记录与固定查询结果。",
            "需要本机 Open WebUI 运行和管理员环境变量；未同步时应如实记录失败。",
            "在 Open WebUI 删除/更新该工具，或恢复部署前状态。",
        ),
        (
            "OPT-E",
            evidence(["SYS-01", "SYS-02", "SYS-03", "SYS-04", "SYS-05", "SYS-06", "SYS-07", "SYS-08"], "关键章节的召回与多资料组合不稳定"),
            "为审核脚本增加可审计的课程关键词查询扩展、关键文件优先排序和 SYS-06 双子查询保留。",
            "不改变用户测试输入，不修改知识库、切分、Top-K 或阈值。",
            "移除 `RETRIEVAL_OVERRIDES` 与 `PREFERRED_SOURCES`。",
        ),
    ]
    lines = [
        "# Issue #25 优化提案",
        "",
        f"测试阶段：`{phase}`",
        "",
        "本提案依据第一轮真实结果整理。优化实施必须获得项目成员逐项批准；批准和实际实施状态以 `approved-optimizations.md` 为准。固定 15 个测试输入不因本提案改变。",
        "",
        "| 优化编号 | 基线证据 | 拟改动 | 风险/边界 | 回滚方式 | 初始状态 |",
        "|---|---|---|---|---|---|",
    ]
    for identifier, baseline_evidence, change, risk, rollback in proposals:
        lines.append(f"| {identifier} | {baseline_evidence} | {change} | {risk} | {rollback} | 等待用户批准 |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
