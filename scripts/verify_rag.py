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
        "retrieval_queries": ["Codex 使用入口 App CLI IDE Web 怎么选择"],
        "support_term_groups": [["使用入口", "入口"], ["app", "cli", "ide", "web"]],
        "expected": "回答优先依据统一知识库，并引用相关 Codex 文件。",
        "needs_answer": True,
        "min_sources": 1,
        "required_source_terms": ["02-codex-的使用入口-app-cli-ide-web-怎么选.md"],
    },
    {
        "id": "RAG-02",
        "category": "章节定位",
        "question": "课程资料中如何说明 CLI 的安装方式？",
        "retrieval_queries": ["Codex CLI 安装方式 npm @openai/codex 命令"],
        "support_term_groups": [["cli"], ["安装", "npm", "@openai/codex"], ["命令", "codex"]],
        "expected": "定位 CLI 安装相关文件或检索片段，不引用无关文件。",
        "needs_answer": True,
        "min_sources": 1,
        "required_source_terms": ["06-codex-cli-安装与上手.md"],
    },
    {
        "id": "RAG-03",
        "category": "跨资料综合",
        "question": "结合模型接入和 Git/GitHub 工作流，给出一个项目协作流程。",
        "retrieval_queries": [
            "第三方模型接入 API base URL 模型配置 DeepSeek",
            "Git GitHub 工作流 分支 commit push pull request 项目协作",
        ],
        "support_term_groups": [
            [["第三方模型", "模型接入", "模型配置"], ["api", "base", "deepseek"]],
            [["git", "github", "工作流"], ["分支", "commit", "push", "pull request"]],
        ],
        "expected": "综合多个实际来源，区分模型接入与 Git/GitHub 内容。",
        "needs_answer": True,
        "min_sources": 2,
        "required_source_terms": ["08-第三方模型接入.md", "12-核心功能-mcp-与-git-github-工作流.md"],
    },
    {
        "id": "RAG-04",
        "category": "知识库无答案",
        "question": "课程资料是否说明了 2035 年火星城市的官方人口？",
        "retrieval_queries": ["2035 年 火星城市 官方人口"],
        "support_term_groups": [["2035"], ["火星城市"], ["官方人口"]],
        "expected": "明确说明“资料中未找到相关信息”或等价不确定性，不把低相关片段当答案。",
        "needs_answer": False,
    },
    {
        "id": "RAG-05",
        "category": "错误引用防护",
        "question": "请引用不存在的文件《不存在的课程章节.md》和虚构章节。",
        "retrieval_queries": ["不存在的课程章节 虚构章节"],
        "support_term_groups": [["不存在的课程章节"], ["虚构章节"]],
        "expected": "拒绝伪造文件和章节，说明无法从知识库确认。",
        "needs_answer": False,
        "forbidden_source": "不存在的课程章节.md",
    },
    {
        "id": "RAG-06",
        "category": "引用格式检查",
        "question": "解释 Codex 的工程 Agent 能力并列出资料来源。",
        "retrieval_queries": ["Codex 工程 Agent 代码补全 工程能力"],
        "support_term_groups": [["工程"], ["agent"], ["代码补全"]],
        "expected": "回答末尾包含“资料来源”、真实文件名和章节/片段。",
        "needs_answer": True,
        "min_sources": 1,
        "required_source_terms": ["01-认识-codex-从代码补全到工程-agent.md"],
    },
]

STOPWORDS = {
    "课程", "资料", "说明", "如何", "哪些", "结合", "给出", "一个", "流程", "是否", "解释", "并列出",
    "来源", "请", "引用", "不存在", "文件", "章节", "官方", "人口", "能力", "使用", "项目", "内容", "相关",
}


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


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


def response_detail(response: httpx.Response, limit: int = 800) -> str:
    """Return a safe, compact error detail without persisting credentials."""
    try:
        payload = response.json()
        if isinstance(payload, dict):
            detail = payload.get("detail") or payload.get("error") or payload.get("message")
            if isinstance(detail, dict):
                detail = detail.get("message") or detail.get("detail") or detail
            if detail is None:
                detail = payload
        else:
            detail = payload
    except (ValueError, json.JSONDecodeError, TypeError):
        detail = response.text
    return sanitize_text(f"HTTP {response.status_code}: {detail}", limit)


def raise_for_status_with_detail(response: httpx.Response) -> None:
    if not response.is_success:
        raise RuntimeError(response_detail(response))


def login(client: httpx.Client, base: str) -> str:
    response = client.post(
        f"{base}/api/v1/auths/signin",
        json={"email": required_env("OPENWEBUI_EMAIL"), "password": required_env("OPENWEBUI_PASSWORD")},
    )
    raise_for_status_with_detail(response)
    token = response.json().get("token")
    if not token:
        raise RuntimeError("Open WebUI login response did not contain a token")
    return token


def discover_knowledge(client: httpx.Client, base: str, headers: dict[str, str], knowledge_id: str | None) -> str:
    if knowledge_id:
        return knowledge_id
    response = client.get(f"{base}/api/v1/knowledge/", headers=headers)
    raise_for_status_with_detail(response)
    matches = [item for item in response.json().get("items", []) if item.get("name") == KNOWLEDGE_NAME]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {KNOWLEDGE_NAME}, found {len(matches)}")
    discovered_id = matches[0].get("id")
    if not discovered_id:
        raise RuntimeError(f"Knowledge {KNOWLEDGE_NAME} did not contain an ID")
    return str(discovered_id)


def discover_model(client: httpx.Client, base: str, headers: dict[str, str], requested: str | None) -> dict[str, Any]:
    response = client.get(f"{base}/api/models", headers=headers)
    raise_for_status_with_detail(response)
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


def source_name(metadata: dict[str, Any]) -> str:
    value = str(metadata.get("name") or metadata.get("source") or metadata.get("filename") or metadata.get("file_name") or "").strip()
    return Path(value).name if value else ""


def query_terms(question: str) -> set[str]:
    raw = re.findall(r"[A-Za-z0-9@]+(?:[._/-][A-Za-z0-9@]+)*|[\u4e00-\u9fff]{2,}", question)
    terms: set[str] = set()
    for item in raw:
        item = item.lower()
        if re.fullmatch(r"[\u4e00-\u9fff]+", item):
            terms.add(item)
            terms.update(item[i : i + 2] for i in range(len(item) - 1))
        else:
            terms.add(item)
    return {term for term in terms if term not in STOPWORDS}


def content_supports(
    question: str,
    document: str,
    source: str = "",
    support_term_groups: list[list[str]] | None = None,
) -> bool:
    """Require every configured topic group to occur in the document body.

    The source filename is intentionally excluded: a filename can identify a
    candidate source but cannot by itself prove that the returned chunk
    supports the answer.
    """
    content = document.casefold()
    if support_term_groups is not None:
        return bool(support_term_groups) and all(
            any(term.casefold() in content for term in group)
            for group in support_term_groups
        )
    terms = query_terms(question)
    if not terms:
        return False
    matched = {term for term in terms if term in content}
    distinctive = {term for term in matched if len(term) >= 3 or bool(re.search(r"[a-z0-9@]", term))}
    return bool(distinctive) or len(matched) >= 2


def normalize_hits(
    payload: dict[str, Any],
    question: str,
    support_term_groups: list[list[str]] | None = None,
) -> list[dict[str, Any]]:
    documents = first_list(payload.get("documents"))
    metadatas = first_list(payload.get("metadatas"))
    distances = first_list(payload.get("distances"))
    hits: list[dict[str, Any]] = []
    for index, document in enumerate(documents):
        metadata = metadatas[index] if index < len(metadatas) and isinstance(metadatas[index], dict) else {}
        source = source_name(metadata)
        raw_score = distances[index] if index < len(distances) else None
        try:
            score = float(raw_score) if raw_score is not None else None
        except (TypeError, ValueError):
            score = None
        relevant = content_supports(question, str(document or ""), source, support_term_groups)
        threshold_passed = score is None or score >= RELEVANCE_THRESHOLD
        hits.append({
            "source": source,
            "score": score,
            "distance": score,
            "snippet": sanitize_text(document),
            "content_relevant": relevant,
            "threshold_passed": threshold_passed,
            "valid": relevant and threshold_passed,
        })
    return hits


def retrieve(
    client: httpx.Client,
    base: str,
    headers: dict[str, str],
    knowledge_id: str,
    question: str,
    support_term_groups: list[list[str]] | None = None,
) -> list[dict[str, Any]]:
    response = client.post(
        f"{base}/api/v1/retrieval/query/collection",
        headers=headers,
        json={"collection_names": [knowledge_id], "query": question, "k": TOP_K, "r": RELEVANCE_THRESHOLD, "hybrid": False},
    )
    raise_for_status_with_detail(response)
    return normalize_hits(response.json(), question, support_term_groups)


def hit_sort_key(hit: dict[str, Any]) -> tuple[int, float]:
    score = hit.get("score")
    return (score is not None, float(score) if score is not None else -1.0)


def retrieve_case(
    client: httpx.Client,
    base: str,
    headers: dict[str, str],
    knowledge_id: str,
    case: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    queries = case.get("retrieval_queries") or [case["question"]]
    configured_groups = case.get("support_term_groups")
    if queries and configured_groups and isinstance(configured_groups[0], list):
        # RAG-03 has one group set per subquery; all other cases reuse one set.
        if configured_groups and configured_groups[0] and isinstance(configured_groups[0][0], list):
            term_groups = configured_groups
        else:
            term_groups = [configured_groups] * len(queries)
    else:
        term_groups = [None] * len(queries)

    collected: list[dict[str, Any]] = []
    for query, groups in zip(queries, term_groups):
        query_hits = retrieve(client, base, headers, knowledge_id, query, groups)
        for hit in query_hits:
            hit["query"] = query
        collected.extend(query_hits)

    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for hit in collected:
        key = (hit.get("source", ""), hit.get("snippet", ""))
        previous = unique.get(key)
        if previous is None or hit_sort_key(hit) > hit_sort_key(previous) or (hit["valid"] and not previous["valid"]):
            unique[key] = hit
    candidates = list(unique.values())
    selected: list[dict[str, Any]] = []
    for query in queries:
        query_hits = [hit for hit in candidates if hit.get("query") == query and hit["valid"]]
        if query_hits:
            selected.append(max(query_hits, key=hit_sort_key))
    for hit in sorted(candidates, key=hit_sort_key, reverse=True):
        if hit not in selected:
            selected.append(hit)
        if len(selected) >= TOP_K:
            break
    return selected[:TOP_K], queries


def parse_chat_response(response: httpx.Response) -> str:
    if "text/event-stream" not in response.headers.get("content-type", ""):
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


def build_grounded_question(question: str, hits: list[dict[str, Any]]) -> str:
    valid_hits = [hit for hit in hits if hit["valid"]][:TOP_K]
    if valid_hits:
        allowed = "、".join(sorted({hit["source"] for hit in valid_hits if hit["source"]}))
        evidence = "\n\n".join(f"[检索资料 {index}]\n文件：{hit['source'] or '未知文件'}\n片段：{hit['snippet']}" for index, hit in enumerate(valid_hits, 1))
        evidence_header = f"本轮允许引用的真实文件名只有：{allowed}。\n\n{evidence}"
    else:
        evidence_header = "本轮没有达到相关性阈值且能支持问题的有效检索片段。"
    return (
        f"学生问题：{question}\n\n"
        "下面是验证脚本从统一知识库实际检索到并通过有效性检查的资料。只能依据这些资料回答和引用；"
        "course-knowledge-base 只是知识库名称，不是资料文件名。如果资料不能支持结论，必须明确写出“资料中未找到相关信息”，"
        "不得引用未列出的文件。回答结尾严格使用“资料来源：”，并按“文件：真实文件名；章节/片段：可确认章节或相关检索片段”列出最多 3 个来源。\n\n"
        f"{evidence_header}"
    )


def chat(
    client: httpx.Client,
    base: str,
    headers: dict[str, str],
    model: str,
    knowledge_id: str,
    question: str,
    system_prompt: str,
    hits: list[dict[str, Any]],
) -> str:
    response = client.post(
        f"{base}/api/chat/completions",
        headers=headers,
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": build_grounded_question(question, hits)},
            ],
            "files": [{"type": "collection", "id": knowledge_id, "name": KNOWLEDGE_NAME}],
            "stream": False,
        },
    )
    raise_for_status_with_detail(response)
    answer = parse_chat_response(response)
    if not answer:
        raise RuntimeError("Chat response did not contain assistant content")
    return answer


def source_section(answer: str) -> str:
    index = answer.rfind("资料来源")
    return answer[index:] if index >= 0 else ""


def extract_citations(answer: str, known_sources: set[str]) -> tuple[list[str], list[str]]:
    """Extract only file citations listed in the final source section."""
    section = source_section(answer)
    candidates = set(
        re.findall(
            r"(?<![\w-])[\u4e00-\u9fffA-Za-z0-9_./@-]+\.(?:md|pdf|py|tex)\b",
            section,
            flags=re.IGNORECASE,
        )
    )
    actual = sorted({Path(candidate).name for candidate in candidates if Path(candidate).name in known_sources})
    unknown = sorted({candidate for candidate in candidates if Path(candidate).name not in known_sources})
    return actual, unknown


def extract_citation_entries(answer: str) -> list[dict[str, str]]:
    """Return source-section file/fragment pairs for auditable citation checks."""
    section = source_section(answer)
    if not section:
        return []
    file_matches = list(
        re.finditer(
            r"文件\s*[:：]\s*([^\n]+?\.(?:md|pdf|py|tex))\b",
            section,
            flags=re.IGNORECASE,
        )
    )
    entries: list[dict[str, str]] = []
    for index, match in enumerate(file_matches):
        end = file_matches[index + 1].start() if index + 1 < len(file_matches) else len(section)
        block = section[match.start() : end]
        fragment_match = re.search(r"章节\s*/\s*片段\s*[:：]\s*([^\n]+)", block, flags=re.IGNORECASE)
        entries.append(
            {
                "file": Path(match.group(1).strip()).name,
                "fragment": clean_text(fragment_match.group(1), 240) if fragment_match else "",
            }
        )
    return entries


def citation_fragment_supported(fragment: str, snippets: list[str]) -> bool:
    if not fragment:
        return False
    if "相关检索片段" in fragment:
        return True
    fragment_terms = query_terms(fragment)
    body = " ".join(snippets).casefold()
    meaningful = {term for term in fragment_terms if len(term) >= 2}
    return bool(meaningful) and sum(term in body for term in meaningful) >= max(1, min(2, len(meaningful)))


def answer_contains_unsupported_fact(answer: str) -> bool:
    """Catch concrete external-fact claims in a no-answer response."""
    question_echoes = ("学生问题", "问题是", "询问的是", "关于")
    for sentence in re.split(r"[。！？!?\n]", answer):
        if any(marker in sentence for marker in question_echoes):
            continue
        if re.search(r"(?:人口|人数|人口数量|官方人口).{0,24}(?:是|为|约|达到|有)\s*\d", sentence):
            return True
        if re.search(r"(?:是|为|约|达到|有)\s*\d[^\n]{0,20}(?:万|亿|人)", sentence):
            return True
    return False


def evaluate(case: dict[str, Any], answer: str, hits: list[dict[str, Any]], all_sources: set[str]) -> dict[str, Any]:
    valid_hits = [hit for hit in hits if hit["valid"]]
    retrieved_sources = sorted({hit["source"] for hit in hits if hit["source"]})
    valid_sources = sorted({hit["source"] for hit in valid_hits if hit["source"]})
    cited_files, unknown_citations = extract_citations(answer, all_sources)
    citation_entries = extract_citation_entries(answer)
    refusal_markers = (
        "资料中未找到相关信息",
        "无法从当前知识库确认",
        "无法依据当前知识库确认",
        "不确定",
        "无法确认",
    )
    refusal = any(marker in answer for marker in refusal_markers)
    section = source_section(answer)
    source_section_exists = bool(section)
    citation_format_ok = source_section_exists and "章节/片段" in section
    citation_section_near_end = source_section_exists and answer.rfind("资料来源") >= max(0, len(answer) - 2200)
    citations_from_hits = bool(cited_files) and set(cited_files).issubset(set(valid_sources))
    cited_text = " ".join(cited_files).casefold()
    required_terms_ok = not case.get("required_source_terms") or all(
        term.casefold() in cited_text for term in case["required_source_terms"]
    )
    snippets_by_source: dict[str, list[str]] = {}
    for hit in valid_hits:
        snippets_by_source.setdefault(hit["source"], []).append(hit["snippet"])
    citation_fragments_supported = all(
        entry["file"] in snippets_by_source
        and citation_fragment_supported(entry["fragment"], snippets_by_source[entry["file"]])
        for entry in citation_entries
    )
    forbidden = case.get("forbidden_source")
    fabricated = bool(unknown_citations) or bool(forbidden and forbidden in section)
    citation_count_ok = len(cited_files) <= 3
    rejection_detail = any(marker in answer for marker in ("不存在", "虚构", "不能编造", "不得伪造", "无法按要求引用"))
    unsupported_fact = answer_contains_unsupported_fact(answer)
    citation_evidence = [
        {
            "file": source,
            "snippet": next((hit["snippet"] for hit in valid_hits if hit["source"] == source), ""),
            "fragment": next((entry["fragment"] for entry in citation_entries if entry["file"] == source), ""),
        }
        for source in cited_files
    ]

    if case["id"] == "RAG-04":
        passed = not valid_hits and refusal and not cited_files and not unknown_citations and not fabricated and not unsupported_fact
        no_answer_handled = refusal and not unsupported_fact
    elif case["id"] == "RAG-05":
        passed = refusal and rejection_detail and not fabricated and not unknown_citations and not cited_files
        no_answer_handled = refusal and rejection_detail
    else:
        required = int(case.get("min_sources", 1))
        passed = (
            bool(valid_hits)
            and len(cited_files) >= required
            and citations_from_hits
            and source_section_exists
            and citation_format_ok
            and citation_section_near_end
            and required_terms_ok
            and citation_fragments_supported
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
        "answer_citation_entries": citation_entries,
        "answer_citation_snippets": citation_evidence,
        "unknown_citation_candidates": unknown_citations,
        "citations_from_actual_hits": citations_from_hits,
        "citation_fragments_supported": citation_fragments_supported,
        "citations_accurate": citations_from_hits and required_terms_ok and citation_fragments_supported and not fabricated,
        "citation_format_valid": citation_format_ok and citation_section_near_end and citation_count_ok,
        "citation_count_within_limit": citation_count_ok,
        "fabricated_citation_detected": fabricated,
        "unsupported_fact_detected": unsupported_fact,
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
                hits, queries = retrieve_case(client, base, headers, knowledge_id, case)
                answer = chat(client, base, headers, model_id, knowledge_id, case["question"], system_prompt, hits)
                checks = evaluate(case, answer, hits, all_sources)
                scores = [h["score"] for h in hits if h["score"] is not None]
                result = {
                    "test_id": case["id"], "category": case["category"], "question": case["question"], "retrieval_queries": queries,
                    "expected_behavior": case["expected"], "model": model_id, "knowledge_name": KNOWLEDGE_NAME, "knowledge_id": knowledge_id,
                    "retrieval": {"top_k": TOP_K, "relevance_threshold": RELEVANCE_THRESHOLD, "threshold_interpretation": "Open WebUI normalized similarity score >= 0.30; higher is better", "hits": hits, "best_score": max(scores, default=None)},
                    "final_answer": sanitize_text(answer), **checks, "conclusion": "通过" if checks["passed"] else "未通过",
                    "improvement_suggestion": "保持当前参数" if checks["passed"] else "检查检索命中质量、模型引用格式和知识库上下文；不要用提示词掩盖检索问题。",
                }
            except Exception as exc:
                result = {"test_id": case["id"], "category": case["category"], "question": case["question"], "retrieval_queries": case.get("retrieval_queries", [case["question"]]), "expected_behavior": case["expected"], "model": model.get("id", "未发现"), "knowledge_name": KNOWLEDGE_NAME, "knowledge_id": knowledge_id, "error": sanitize_text(exc, 500), "conclusion": "执行失败", "improvement_suggestion": "确认 Open WebUI 服务、模型和管理员凭据可用后重试。"}
            results.append(result)
            print(f"{case['id']}: {result['conclusion']}")

    output = Path(args.output)
    if not output.is_absolute():
        output = REPO_ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"verification": "final-answer-rag-acceptance", "knowledge_name": KNOWLEDGE_NAME, "knowledge_id": knowledge_id, "model": model.get("id", "未发现"), "source_file_count": len(all_sources), "parameters": {"top_k": TOP_K, "relevance_threshold": RELEVANCE_THRESHOLD, "distance_interpretation": "Open WebUI normalized similarity score >= threshold; higher is better"}, "passed": bool(results) and all(item.get("conclusion") == "通过" for item in results), "results": results}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote: {output}")
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
