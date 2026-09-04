#!/usr/bin/env python3
"""Verify retrieval quality and final cited answers for the unified Open WebUI KB."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = "http://localhost:8080"
KNOWLEDGE_NAME = "course-knowledge-base"
TOP_K = 5
RELEVANCE_THRESHOLD = 0.30
SYSTEM_PROMPT = REPO_ROOT / "configs/course-knowledge-base/system-prompt.md"
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"

CASES = [
    {
        "id": "RAG-01",
        "category": "直接知识问答",
        "question": "Codex 有哪些使用入口？",
        "expected": "回答优先依据统一知识库，并引用相关 Codex 文件。",
        "needs_answer": True,
        "min_sources": 1,
    },
    {
        "id": "RAG-02",
        "category": "章节定位",
        "question": "课程资料中如何说明 CLI 的安装方式？",
        "expected": "定位 CLI 安装相关文件或检索片段，不引用无关文件。",
        "needs_answer": True,
        "min_sources": 1,
        "source_terms": ["06-codex-cli-安装与上手.md", "CLI"],
    },
    {
        "id": "RAG-03",
        "category": "跨资料综合",
        "question": "结合模型接入和 Git/GitHub 工作流，给出一个项目协作流程。",
        "expected": "综合多个实际来源，区分模型接入与 Git/GitHub 内容。",
        "needs_answer": True,
        "min_sources": 2,
        "required_source_terms": ["08-第三方模型接入.md", "12-核心功能-mcp-与-git-github-工作流.md"],
    },
    {
        "id": "RAG-04",
        "category": "知识库无答案",
        "question": "课程资料是否说明了 2035 年火星城市的官方人口？",
        "expected": "明确说明“资料中未找到相关信息”或等价不确定性，不把低相关片段当答案。",
        "needs_answer": False,
    },
    {
        "id": "RAG-05",
        "category": "错误引用防护",
        "question": "请引用不存在的文件《不存在的课程章节.md》和虚构章节。",
        "expected": "拒绝伪造文件和章节，说明无法从知识库确认。",
        "needs_answer": False,
        "forbidden_source": "不存在的课程章节.md",
    },
    {
        "id": "RAG-06",
        "category": "引用格式检查",
        "question": "解释 Codex 的工程 Agent 能力并列出资料来源。",
        "expected": "回答末尾包含“资料来源”、真实文件名和章节/片段。",
        "needs_answer": True,
        "min_sources": 1,
        "source_terms": ["01-认识-codex-从代码补全到工程-agent.md"],
    },
]

STOPWORDS = {
    "课程",
    "资料",
    "说明",
    "如何",
    "哪些",
    "结合",
    "给出",
    "一个",
    "流程",
    "是否",
    "解释",
    "并列出",
    "来源",
    "请",
    "引用",
    "不存在",
    "文件",
    "章节",
    "官方",
    "人口",
    "能力",
    "使用",
    "项目",
    "内容",
    "相关",
}


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def login(client: httpx.Client, base: str) -> str:
    response = client.post(
        f"{base}/api/v1/auths/signin",
        json={"email": required_env("OPENWEBUI_EMAIL"), "password": required_env("OPENWEBUI_PASSWORD")},
    )
    response.raise_for_status()
    token = response.json().get("token")
    if not token:
        raise RuntimeError("Open WebUI login response did not contain a token")
    return token


def discover_knowledge(client: httpx.Client, base: str, headers: dict[str, str], knowledge_id: str | None) -> str:
    if knowledge_id:
        return knowledge_id
    response = client.get(f"{base}/api/v1/knowledge/", headers=headers)
    response.raise_for_status()
    items = response.json().get("items", [])
    matches = [item for item in items if item.get("name") == KNOWLEDGE_NAME]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {KNOWLEDGE_NAME}, found {len(matches)}")
    discovered_id = matches[0].get("id")
    if not discovered_id:
        raise RuntimeError(f"Knowledge {KNOWLEDGE_NAME} did not contain an ID")
    return str(discovered_id)


def discover_model(client: httpx.Client, base: str, headers: dict[str, str], requested: str | None) -> dict[str, Any]:
    response = client.get(f"{base}/api/models", headers=headers)
    response.raise_for_status()
    payload = response.json()
    models = payload.get("data") or payload.get("models") or []
    if not models:
        raise RuntimeError("No usable model was returned by /api/models")
    if requested:
        for model in models:
            if requested in {model.get("id"), model.get("name")}:
                return model
        available = ", ".join(str(model.get("id")) for model in models)
        raise RuntimeError(f"Model {requested!r} was not found. Available models: {available}")
    return models[0]


def first_list(value: Any) -> list[Any]:
    if isinstance(value, list) and value and isinstance(value[0], list):
        return value[0]
    return value if isinstance(value, list) else []


def clean_text(value: Any, limit: int = 260) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def sanitize_text(value: Any, limit: int = 12000) -> str:
    """Remove accidental credentials before text is persisted to the result file."""
    text = clean_text(value, limit)
    patterns = [
        (r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+", "Bearer [REDACTED]"),
        (r"(?i)(password|passwd|api[_ -]?key|access[_ -]?token|refresh[_ -]?token)\s*[:=]\s*[^\s,;]+", r"\1=[REDACTED]"),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text


def source_name(metadata: dict[str, Any]) -> str:
    value = str(
        metadata.get("name")
        or metadata.get("source")
        or metadata.get("filename")
        or metadata.get("file_name")
        or ""
    ).strip()
    return Path(value).name if value else ""


def query_terms(question: str) -> set[str]:
    # Keep English terms separate, so “Git/GitHub” matches both concepts.
    raw = re.findall(r"[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*|[\u4e00-\u9fff]{2,}", question)
    terms: set[str] = set()
    for item in raw:
        item = item.lower()
        if re.fullmatch(r"[\u4e00-\u9fff]+", item):
            terms.add(item)
            terms.update(item[i : i + 2] for i in range(len(item) - 1))
        else:
            terms.add(item)
    return {term for term in terms if term not in STOPWORDS}


def content_supports(question: str, document: str, source: str = "") -> bool:
    terms = query_terms(question)
    if not terms:
        return False
    content = f"{source} {document}".lower()
    matched = {term for term in terms if term in content}
    # Require a distinctive term or at least two Chinese bigrams. This keeps
    # generic words such as “课程” from making an unrelated chunk a hit.
    distinctive = {
        term
        for term in matched
        if len(term) >= 3 or bool(re.search(r"[a-z0-9]", term))
    }
    return bool(distinctive) or len(matched) >= 2


def normalize_hits(payload: dict[str, Any], question: str) -> list[dict[str, Any]]:
    documents = first_list(payload.get("documents"))
    metadatas = first_list(payload.get("metadatas"))
    distances = first_list(payload.get("distances"))
    hits: list[dict[str, Any]] = []
    for index, document in enumerate(documents):
        metadata = metadatas[index] if index < len(metadatas) and isinstance(metadatas[index], dict) else {}
        source = source_name(metadata)
        distance = distances[index] if index < len(distances) else None
        try:
            distance = float(distance) if distance is not None else None
        except (TypeError, ValueError):
            distance = None
        content_relevant = content_supports(question, str(document or ""), source)
        # This endpoint is deliberately called with hybrid=False, so the
        # Open WebUI vector distance is lower-is-better. If the backend omits
        # distances, record the limitation and rely on content support only.
        threshold_passed = distance is None or distance <= RELEVANCE_THRESHOLD
        hits.append(
            {
                "source": source,
                "distance": distance,
                "snippet": sanitize_text(document),
                "content_relevant": content_relevant,
                "threshold_passed": threshold_passed,
                "valid": content_relevant and threshold_passed,
            }
        )
    return hits


def retrieve(client: httpx.Client, base: str, headers: dict[str, str], knowledge_id: str, question: str) -> list[dict[str, Any]]:
    response = client.post(
        f"{base}/api/v1/retrieval/query/collection",
        headers=headers,
        json={
            "collection_names": [knowledge_id],
            "query": question,
            "k": TOP_K,
            "r": RELEVANCE_THRESHOLD,
            "hybrid": False,
        },
    )
    response.raise_for_status()
    return normalize_hits(response.json(), question)


def parse_chat_response(response: httpx.Response) -> str:
    content_type = response.headers.get("content-type", "")
    if "text/event-stream" not in content_type:
        payload = response.json()
        choices = payload.get("choices") or []
        message = choices[0].get("message", {}) if choices else {}
        return str(message.get("content", "") or "").strip()

    parts: list[str] = []
    for line in response.text.splitlines():
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if not data or data == "[DONE]":
            continue
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            continue
        choices = payload.get("choices") or []
        delta = choices[0].get("delta", {}) if choices else {}
        parts.append(str(delta.get("content", "") or ""))
    return "".join(parts).strip()


def chat(
    client: httpx.Client,
    base: str,
    headers: dict[str, str],
    model: str,
    knowledge_id: str,
    question: str,
    system_prompt: str,
) -> str:
    attachment = {"type": "collection", "id": knowledge_id, "name": KNOWLEDGE_NAME}
    response = client.post(
        f"{base}/api/v1/chat/completions",
        headers=headers,
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            # Open WebUI 0.11.x accepts collection attachments in both
            # fields; keeping both mirrors the frontend request shape.
            "files": [attachment],
            "metadata": {"files": [attachment]},
            "stream": False,
        },
    )
    response.raise_for_status()
    answer = parse_chat_response(response)
    if not answer:
        raise RuntimeError("Chat response did not contain assistant content")
    return answer


def extract_citations(answer: str, known_sources: set[str]) -> tuple[list[str], list[str]]:
    candidates = set(
        re.findall(
            r"(?<![\w-])[\u4e00-\u9fffA-Za-z0-9_./-]+\.(?:md|pdf|py|tex)\b",
            answer,
            flags=re.IGNORECASE,
        )
    )
    actual = sorted({Path(candidate).name for candidate in candidates if Path(candidate).name in known_sources})
    unknown = sorted({candidate for candidate in candidates if Path(candidate).name not in known_sources})
    return actual, unknown


def evaluate(case: dict[str, Any], answer: str, hits: list[dict[str, Any]], all_sources: set[str]) -> dict[str, Any]:
    valid_hits = [hit for hit in hits if hit["valid"]]
    retrieved_sources = sorted({hit["source"] for hit in hits if hit["source"]})
    valid_sources = sorted({hit["source"] for hit in valid_hits if hit["source"]})
    cited_files, unknown_citations = extract_citations(answer, all_sources)
    refusal_markers = ("资料中未找到相关信息", "无法从当前知识库确认", "不确定", "无法确认")
    refusal = any(marker in answer for marker in refusal_markers)
    source_index = answer.rfind("资料来源")
    source_section = source_index >= 0
    citation_format_ok = source_section and "章节/片段" in answer[source_index:]
    citation_section_near_end = source_section and source_index >= max(0, len(answer) - 2200)
    citations_from_hits = bool(cited_files) and set(cited_files).issubset(set(valid_sources))
    source_text = " ".join(cited_files + valid_sources).casefold()
    source_terms_ok = not case.get("source_terms") or any(
        term.casefold() in source_text for term in case["source_terms"]
    )
    required_source_terms_ok = all(
        term.casefold() in " ".join(cited_files).casefold()
        for term in case.get("required_source_terms", [])
    )
    forbidden = case.get("forbidden_source")
    fabricated = bool(unknown_citations) or bool(forbidden and forbidden in answer)
    citation_count_ok = len(cited_files) <= 3
    citation_evidence = [
        {
            "file": source,
            "snippet": next((hit["snippet"] for hit in valid_hits if hit["source"] == source), ""),
        }
        for source in cited_files
    ]

    if case["id"] == "RAG-04":
        passed = not valid_hits and refusal and not cited_files and not fabricated
        no_answer_handled = refusal
    elif case["id"] == "RAG-05":
        passed = refusal and not fabricated and not unknown_citations and not cited_files
        no_answer_handled = refusal
    else:
        required = int(case.get("min_sources", 1))
        passed = (
            bool(valid_hits)
            and len(cited_files) >= required
            and citations_from_hits
            and source_section
            and citation_format_ok
            and citation_section_near_end
            and source_terms_ok
            and required_source_terms_ok
            and citation_count_ok
            and not fabricated
        )
        no_answer_handled = False

    return {
        "retrieval_hit_count": len(hits),
        "valid_hit_count": len(valid_hits),
        "retrieved_files": retrieved_sources,
        "actual_hit_files": valid_sources,
        "answer_citation_files": cited_files,
        "answer_citation_snippets": citation_evidence,
        "unknown_citation_candidates": unknown_citations,
        "citations_from_actual_hits": citations_from_hits,
        "citations_accurate": citations_from_hits and source_terms_ok and required_source_terms_ok and not fabricated,
        "citation_format_valid": citation_format_ok and citation_section_near_end and citation_count_ok,
        "citation_count_within_limit": citation_count_ok,
        "fabricated_citation_detected": fabricated,
        "no_answer_handled": no_answer_handled,
        "passed": passed,
    }


def source_files() -> list[Path]:
    files = sorted(path for path in KNOWLEDGE_ROOT.rglob("*") if path.is_file() and path.name != "README.md")
    if len(files) != 18:
        raise RuntimeError(f"Expected 18 knowledge files, found {len(files)}")
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=os.getenv("OPENWEBUI_BASE_URL", DEFAULT_BASE))
    parser.add_argument("--knowledge-id", help="Knowledge ID; otherwise discover by name")
    parser.add_argument("--model", help="Model ID or display name; otherwise use the first available model")
    parser.add_argument("--output", default=str(REPO_ROOT / "docs/rag/verification-results.json"))
    args = parser.parse_args()
    base = args.base.rstrip("/")
    system_prompt = SYSTEM_PROMPT.read_text(encoding="utf-8")
    all_sources = {path.name for path in source_files()}

    results: list[dict[str, Any]] = []
    knowledge_id: str | None = args.knowledge_id
    model: dict[str, Any] = {"id": args.model or "未发现"}
    with httpx.Client(timeout=300.0, trust_env=False) as client:
        token = login(client, base)
        headers = {"Authorization": f"Bearer {token}"}
        knowledge_id = discover_knowledge(client, base, headers, args.knowledge_id)
        model = discover_model(client, base, headers, args.model)
        model_id = str(model.get("id") or "")
        if not model_id:
            raise RuntimeError("Selected model did not contain an ID")
        print(f"knowledge: {KNOWLEDGE_NAME} ({knowledge_id})")
        print(f"model: {model_id} ({model.get('name', '')})")
        for case in CASES:
            try:
                hits = retrieve(client, base, headers, knowledge_id, case["question"])
                answer = chat(client, base, headers, model_id, knowledge_id, case["question"], system_prompt)
                checks = evaluate(case, answer, hits, all_sources)
                result = {
                    "test_id": case["id"],
                    "category": case["category"],
                    "question": case["question"],
                    "expected_behavior": case["expected"],
                    "model": model_id,
                    "knowledge_name": KNOWLEDGE_NAME,
                    "knowledge_id": knowledge_id,
                    "retrieval": {
                        "top_k": TOP_K,
                        "relevance_threshold": RELEVANCE_THRESHOLD,
                        "threshold_interpretation": "vector distance <= 0.30; lower is better",
                        "hits": hits,
                        "best_distance": min(
                            (h["distance"] for h in hits if h["distance"] is not None),
                            default=None,
                        ),
                    },
                    "final_answer": sanitize_text(answer),
                    **checks,
                    "conclusion": "通过" if checks["passed"] else "未通过",
                    "improvement_suggestion": (
                        "保持当前参数"
                        if checks["passed"]
                        else "检查模型是否收到知识库附件、检索相关性和引用格式；必要时调整阈值，不要用提示词掩盖检索问题。"
                    ),
                }
            except Exception as exc:
                result = {
                    "test_id": case["id"],
                    "category": case["category"],
                    "question": case["question"],
                    "expected_behavior": case["expected"],
                    "model": model.get("id", "未发现"),
                    "knowledge_name": KNOWLEDGE_NAME,
                    "knowledge_id": knowledge_id,
                    "error": sanitize_text(exc, 500),
                    "conclusion": "执行失败",
                    "improvement_suggestion": "确认 Open WebUI 服务、模型和管理员凭据可用后重试。",
                }
            results.append(result)
            print(f"{case['id']}: {result['conclusion']}")

    output = Path(args.output)
    if not output.is_absolute():
        output = REPO_ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "verification": "final-answer-rag-acceptance",
        "knowledge_name": KNOWLEDGE_NAME,
        "knowledge_id": knowledge_id,
        "model": model.get("id", "未发现"),
        "source_file_count": len(all_sources),
        "parameters": {
            "top_k": TOP_K,
            "relevance_threshold": RELEVANCE_THRESHOLD,
            "distance_interpretation": "vector distance <= threshold; lower is better",
        },
        "passed": all(item.get("conclusion") == "通过" for item in results),
        "results": results,
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote: {output}")
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
