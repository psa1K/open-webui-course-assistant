#!/usr/bin/env python3
"""Run Issue #25's fixed, auditable baseline or post-approval system tests.

The script calls the local Open WebUI chat and retrieval APIs.  For Workspace
Tools it additionally downloads the installed tool source through the Open
WebUI API and executes its deterministic contract with the fixed test input.
This records both deployment evidence and the exact structured tool output.
"""
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
    """Remove authentication-shaped values before writing a result file."""
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


def discover_assistant(client: httpx.Client, base: str, headers: dict[str, str], assistant_id: str) -> bool:
    response = client.get(f"{base}/api/v1/models/model", params={"id": assistant_id}, headers=headers)
    if response.status_code == 404:
        return False
    require_success(response)
    return True


def tool_record(client: httpx.Client, base: str, headers: dict[str, str], tool_id: str) -> dict[str, Any]:
    response = client.get(f"{base}/api/v1/tools/id/{tool_id}", headers=headers)
    data = require_success(response)
    if not isinstance(data, dict) or not isinstance(data.get("content"), str):
        raise RuntimeError(f"工具 {tool_id} 的 API 响应没有 content")
    return data


def deployed_tool_call(record: dict[str, Any], case_id: str) -> dict[str, Any]:
    """Execute the exact source returned by Open WebUI for deterministic tools."""
    module = ModuleType(f"deployed_{record.get('id', 'tool')}")
    exec(record["content"], module.__dict__)  # trusted source read from this local Open WebUI deployment
    instance = module.Tools()
    if case_id == "SYS-11":
        return instance.generate_practice_questions(
            course="codex", chapter="Codex CLI", difficulty="medium", count=2,
            question_types=["简答题"], student_level="基础", include_answer=False,
        )
    if case_id == "SYS-12":
        return instance.grade_from_bank('{"CX-001":"B","CX-004":"A"}')
    if case_id == "SYS-13":
        return instance.query_chapter("MCP")
    if case_id == "SYS-14":
        return instance.query_prerequisites("MCP Server", include_indirect=True)
    if case_id == "SYS-15":
        return instance.generate_practice_questions(course="codex", chapter="Codex CLI", count=0)
    raise RuntimeError(f"{case_id} 没有定义工具调用契约")


def chat(
    client: httpx.Client, base: str, headers: dict[str, str], model: str,
    knowledge_id: str, question: str, tool_id: str | None = None,
) -> tuple[str, dict[str, Any]]:
    body: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": ASSISTANT_PROMPT.read_text(encoding="utf-8")},
            {"role": "user", "content": question},
        ],
        "files": [{"type": "collection", "id": knowledge_id, "name": KNOWLEDGE_NAME}],
        "stream": False,
    }
    if tool_id:
        body["tool_ids"] = [tool_id]
    response = client.post(f"{base}/api/chat/completions", headers=headers, json=body)
    data = require_success(response)
    answer = rag.parse_chat_response(response)
    if not answer:
        raise RuntimeError("聊天响应未包含 assistant content")
    return answer, data if isinstance(data, dict) else {"response": data}


def retrieval_files(client: httpx.Client, base: str, headers: dict[str, str], knowledge_id: str, question: str) -> list[dict[str, Any]]:
    hits = rag.retrieve(client, base, headers, knowledge_id, question)
    return [{"file": hit.get("source", ""), "score": hit.get("score"), "snippet": clean(hit.get("snippet"), 360), "valid": bool(hit.get("valid"))} for hit in hits]


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
    all_sources = source_files()
    citations, unknown = rag.extract_citations(answer, all_sources)
    actual_files = {hit["file"] for hit in hits if hit["file"]}
    citation_real = not unknown and set(citations).issubset(actual_files) if citations else False
    refusal = any(marker in answer for marker in REFUSAL_MARKERS)
    terms_ok = contains_terms(answer, case.get("answer_terms", []))
    mode = case["mode"]
    contract_ok = tool_contract_ok(case, contract) if contract is not None else None
    if mode == "no_answer":
        passed = refusal and not citations and not unknown
        correct = passed
    elif mode == "chat_or_refusal":
        passed = (refusal and not citations) or (terms_ok and bool(citations) and citation_real)
        correct = passed
    elif mode == "chat_tool":
        if case["id"] == "SYS-11":
            passed = bool(contract_ok) and terms_ok and required_sources_ok(case, citations) and citation_real
        else:
            passed = bool(contract_ok) and terms_ok
        correct = passed
    else:
        passed = terms_ok and required_sources_ok(case, citations) and citation_real
        correct = passed
    issues = []
    if not correct:
        if not terms_ok:
            issues.append("回答未包含该用例的关键内容")
        if mode not in ("no_answer", "chat_tool") and not required_sources_ok(case, citations):
            issues.append("回答未包含要求的资料引用")
        if citations and not citation_real:
            issues.append("回答引用未能在本轮检索命中中确认")
        if mode == "no_answer" and not refusal:
            issues.append("知识库无答案场景没有明确拒答")
        if contract_ok is False:
            issues.append("已部署工具的固定调用契约未达到预期")
    return {
        "answer_citation_files": citations,
        "unknown_citation_files": unknown,
        "citations_correct": citation_real and required_sources_ok(case, citations),
        "answer_correct": correct,
        "refusal_handled": refusal if mode in ("no_answer", "chat_or_refusal") else None,
        "tool_contract_passed": contract_ok,
        "issues_found": issues,
        "improvement_suggestions": [] if passed else ["根据本条真实输出定位原因；未经用户批准，不调整提示词、知识库或检索参数。"],
        "passed": passed,
    }


def proposal(results: list[dict[str, Any]], phase: str) -> str:
    failed = [result for result in results if not result["passed"]]
    lines = ["# Issue #25 优化提案", "", f"测试阶段：`{phase}`", "", "本提案根据本轮真实结果生成。以下项目均为 **等待用户批准**；在用户明确批准前，不得实施任何提示词、知识库、切分、检索参数、工具或模型改动。", ""]
    if not failed:
        lines.extend(["本轮全部用例通过，未提出优化改动。仍应保留本文件作为审批审计记录。", ""])
        return "\n".join(lines)
    lines.extend(["| 优化编号 | 证据 | 拟改动 | 预期影响 | 风险与回滚 | 状态 |", "|---|---|---|---|---|---|"])
    for number, result in enumerate(failed, 1):
        issues = "；".join(result["issues_found"]) or "用例未通过"
        lines.append(f"| OPT-{number:02d} | {result['test_id']}：{issues} | 先分析对应提示词、检索或工具调用链；只在获批后修改明确文件 | 改善 {result['test_id']} 的可验证指标 | 修改前保留基线结果；可还原获批提交 | 等待用户批准 |")
    lines.extend(["", "批准格式示例：`批准 OPT-01` 或 `批准 OPT-01、OPT-03，不批准 OPT-02`。", ""])
    return "\n".join(lines)


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
            raise SystemExit("第二轮测试需要先创建 docs/system-evaluation/approved-optimizations.md，记录用户批准项。")
    output = Path(args.output) if args.output else ROOT / f"docs/system-evaluation/{args.phase}-results.json"
    cases = read_cases()
    base = args.base.rstrip("/")
    results = []
    with httpx.Client(timeout=120, trust_env=False) as client:
        token = rag.login(client, base)
        headers = {"Authorization": f"Bearer {token}"}
        knowledge_id = rag.discover_knowledge(client, base, headers, args.knowledge_id)
        model = rag.discover_model(client, base, headers, args.model)
        assistant_exists = discover_assistant(client, base, headers, args.assistant_id)
        for case in cases:
            try:
                hits = retrieval_files(client, base, headers, knowledge_id, case["input"])
                installed = None
                contract = None
                if case.get("tool_id"):
                    installed = tool_record(client, base, headers, case["tool_id"])
                    contract = deployed_tool_call(installed, case["id"])
                answer, _raw = chat(client, base, headers, str(model.get("id", args.model)), knowledge_id, case["input"], case.get("tool_id"))
                checks = evaluate(case, answer, hits, contract)
                result = {
                    "test_id": case["id"], "category": case["category"], "input": case["input"],
                    "actual_output": clean(answer, 6000), "tool_id": case.get("tool_id"),
                    "tool_api_deployed": installed is not None, "tool_contract_output": safe(contract) if contract is not None else None,
                    "actual_retrieval_files": hits, **checks,
                }
            except Exception as error:  # record a real failure without exposing credentials
                result = {
                    "test_id": case["id"], "category": case["category"], "input": case["input"],
                    "actual_output": "", "tool_id": case.get("tool_id"), "actual_retrieval_files": [],
                    "citations_correct": False, "answer_correct": False, "issues_found": [clean(error, 700)],
                    "improvement_suggestions": ["先修复执行环境或接口错误；未经用户批准，不实施配置优化。"], "passed": False,
                }
            results.append(result)
            print(f"{case['id']}: {'通过' if result['passed'] else '未通过'}")
    report = {
        "verification": "issue-25-system-evaluation", "phase": args.phase,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "model": str(model.get("id", args.model)), "assistant_id": args.assistant_id,
        "assistant_api_present": assistant_exists, "knowledge_name": KNOWLEDGE_NAME,
        "knowledge_id": knowledge_id, "parameters": {"top_k": rag.TOP_K, "relevance_threshold": rag.RELEVANCE_THRESHOLD},
        "case_config": str(CASES_PATH.relative_to(ROOT)), "case_count": len(results),
        "passed": all(item["passed"] for item in results), "results": results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(safe(report), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.phase == "baseline":
        proposal_path = ROOT / "docs/system-evaluation/optimization-proposal.md"
        proposal_path.write_text(proposal(results, args.phase), encoding="utf-8")
        print(f"wrote: {proposal_path}")
    print(f"wrote: {output}")


if __name__ == "__main__":
    main()
