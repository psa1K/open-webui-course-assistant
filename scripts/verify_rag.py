#!/usr/bin/env python3
"""Run retrieval-only smoke tests against the unified Open WebUI knowledge base."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import httpx

DEFAULT_BASE = "http://localhost:8080"
KNOWLEDGE_NAME = "course-knowledge-base"
CASES = [
    ("RAG-01", "Codex 有哪些使用入口？"),
    ("RAG-02", "课程资料中如何说明 CLI 的安装方式？"),
    ("RAG-03", "结合模型接入和 Git/GitHub 工作流，给出一个项目协作流程。"),
    ("RAG-04", "课程资料是否说明了 2035 年火星城市的官方人口？"),
    ("RAG-05", "请引用不存在的文件《不存在的课程章节.md》和虚构章节。"),
    ("RAG-06", "解释 Codex 的工程 Agent 能力并列出资料来源。"),
]


def env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=os.getenv("OPENWEBUI_BASE_URL", DEFAULT_BASE))
    parser.add_argument("--knowledge-id", help="Knowledge ID; otherwise discover by name")
    parser.add_argument("--output", default="docs/rag/verification-results.json")
    args = parser.parse_args()
    base = args.base.rstrip("/")

    with httpx.Client(timeout=120.0) as client:
        response = client.post(f"{base}/api/v1/auths/signin", json={"email": env("OPENWEBUI_EMAIL"), "password": env("OPENWEBUI_PASSWORD")})
        response.raise_for_status()
        headers = {"Authorization": f"Bearer {response.json()['token']}"}
        knowledge_id = args.knowledge_id
        if not knowledge_id:
            response = client.get(f"{base}/api/v1/knowledge/", headers=headers)
            response.raise_for_status()
            matches = [item for item in response.json().get("items", []) if item.get("name") == KNOWLEDGE_NAME]
            if len(matches) != 1:
                raise RuntimeError(f"Expected exactly one {KNOWLEDGE_NAME}, found {len(matches)}")
            knowledge_id = matches[0]["id"]

        results = []
        for case_id, question in CASES:
            response = client.post(
                f"{base}/api/v1/retrieval/query/collection",
                headers=headers,
                json={"collection_names": [knowledge_id], "query": question, "k": 5, "r": 0.30, "hybrid": False},
            )
            response.raise_for_status()
            payload = response.json()
            metadatas = payload.get("metadatas", [[]])
            documents = payload.get("documents", [[]])
            results.append({"id": case_id, "question": question, "metadatas": metadatas, "documents": documents})
            print(f"{case_id}: {len(documents[0]) if documents and documents[0] else 0} hits")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"knowledge": KNOWLEDGE_NAME, "knowledge_id": knowledge_id, "results": results}, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote: {output}")


if __name__ == "__main__":
    main()
