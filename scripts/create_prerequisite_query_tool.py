#!/usr/bin/env python3
"""Create or update the knowledge prerequisite query tool in Open WebUI."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

import httpx

DEFAULT_BASE = "http://localhost:8080"
DEFAULT_TOOL_ID = "knowledge_prerequisite_query"
DEFAULT_NAME = "知识点先修关系查询工具"
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/knowledge_prerequisite_query.py"
CATALOG = ROOT / "data/course-catalog.json"
GRAPH = ROOT / "data/knowledge-prerequisites.json"
CATALOG_PLACEHOLDER = re.compile(r"json\.dumps\(\{\"courses\": \[\]\}\).*# PLACEHOLDER_COURSE_CATALOG")
GRAPH_PLACEHOLDER = re.compile(r"json\.dumps\(\{\"knowledge_points\": \[\], \"relations\": \[\]\}\).*# PLACEHOLDER_PREREQUISITE_GRAPH")


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"缺少环境变量 {name}。请在本机设置管理员凭据。")
    return value


def response_detail(response: httpx.Response) -> str:
    try:
        body = response.json()
        value = body.get("detail") or body.get("error") or body.get("message") if isinstance(body, dict) else body
    except (ValueError, json.JSONDecodeError):
        value = response.text
    text = str(value)[:500]
    for secret_name in ("OPENWEBUI_PASSWORD", "OPENAI_API_KEY"):
        secret = os.getenv(secret_name, "")
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return f"HTTP {response.status_code}: {text}"


def request_json(response: httpx.Response) -> Any:
    if not response.is_success:
        raise RuntimeError(response_detail(response))
    return response.json() if response.content else {}


def login(client: httpx.Client, base: str) -> str:
    response = client.post(
        f"{base}/api/v1/auths/signin",
        json={"email": required_env("OPENWEBUI_EMAIL"), "password": required_env("OPENWEBUI_PASSWORD")},
    )
    token = request_json(response).get("token")
    if not token:
        raise RuntimeError("登录响应未包含 token")
    return token


def load_and_validate() -> tuple[dict[str, Any], dict[str, Any]]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    chapter_ids = {chapter["id"] for course in catalog.get("courses", []) for chapter in course.get("chapters", [])}
    nodes = graph.get("knowledge_points") or []
    relations = graph.get("relations") or []
    if len(nodes) < 8 or len(relations) < 4:
        raise RuntimeError("先修关系数据不足：至少需要 8 个知识点和 4 条关系")
    node_ids = {node.get("id") for node in nodes}
    if len(node_ids) != len(nodes) or None in node_ids:
        raise RuntimeError("知识点 ID 必须存在且唯一")
    for node in nodes:
        required = {"id", "name", "aliases", "course", "chapter_id"}
        missing = required - set(node)
        if missing or node["chapter_id"] not in chapter_ids:
            raise RuntimeError(f"知识点 {node.get('id', '?')} 缺少字段或引用未知章节")
    for relation in relations:
        if set(relation) != {"prerequisite", "dependent"}:
            raise RuntimeError("先修关系字段必须是 prerequisite 和 dependent")
        if relation["prerequisite"] not in node_ids or relation["dependent"] not in node_ids:
            raise RuntimeError("先修关系引用了未知知识点")
        if relation["prerequisite"] == relation["dependent"]:
            raise RuntimeError("知识点不能依赖自身")
    return catalog, graph


def build_content() -> str:
    catalog, graph = load_and_validate()
    text = SOURCE.read_text(encoding="utf-8")
    if "class Tools:" not in text or "def query_prerequisites(" not in text:
        raise RuntimeError("工具源码缺少 Tools.query_prerequisites 定义")
    forbidden = ("requests.", "httpx.", "sqlite3", "OPENAI_API_KEY", "password =", "subprocess")
    if any(item in text for item in forbidden):
        raise RuntimeError("工具源码包含不允许的网络、数据库或敏感配置依赖")
    catalog_inline = "COURSE_CATALOG_JSON = " + json.dumps(json.dumps(catalog, ensure_ascii=False), ensure_ascii=False)
    graph_inline = "PREREQUISITE_GRAPH_JSON = " + json.dumps(json.dumps(graph, ensure_ascii=False), ensure_ascii=False)
    content, catalog_count = CATALOG_PLACEHOLDER.subn(catalog_inline, text, count=1)
    content, graph_count = GRAPH_PLACEHOLDER.subn(graph_inline, content, count=1)
    if catalog_count != 1 or graph_count != 1:
        raise RuntimeError("工具源码缺少课程目录或先修关系占位符")
    return content


def payload(tool_id: str, name: str, content: str, point_count: int, relation_count: int) -> dict[str, Any]:
    return {
        "id": tool_id,
        "name": name,
        "content": content,
        "meta": {"description": f"查询结构化知识点先修与后续关系（{point_count} 个知识点、{relation_count} 条关系）"},
        "access_grants": [],
    }


def find_existing(client: httpx.Client, base: str, headers: dict[str, str], tool_id: str) -> bool:
    response = client.get(f"{base}/api/v1/tools/id/{tool_id}", headers=headers)
    if response.status_code == 404:
        return False
    request_json(response)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=os.getenv("OPENWEBUI_BASE_URL", DEFAULT_BASE))
    parser.add_argument("--tool-id", default=DEFAULT_TOOL_ID)
    parser.add_argument("--name", default=DEFAULT_NAME)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.tool_id.strip() or not args.name.strip():
        raise SystemExit("--tool-id 和 --name 不能为空")
    _catalog, graph = load_and_validate()
    content = build_content()
    point_count = len(graph["knowledge_points"])
    relation_count = len(graph["relations"])
    body = payload(args.tool_id, args.name, content, point_count, relation_count)
    if args.dry_run:
        print(json.dumps({"mode": "dry-run", "tool_id": args.tool_id, "name": args.name, "knowledge_point_count": point_count, "relation_count": relation_count, "source": SOURCE.name}, ensure_ascii=False))
        return
    base = args.base.rstrip("/")
    with httpx.Client(timeout=60, trust_env=False) as client:
        token = login(client, base)
        headers = {"Authorization": f"Bearer {token}"}
        if find_existing(client, base, headers, args.tool_id):
            request_json(client.post(f"{base}/api/v1/tools/id/{args.tool_id}/update", headers=headers, json=body))
            action = "updated"
        else:
            request_json(client.post(f"{base}/api/v1/tools/create", headers=headers, json=body))
            action = "created"
    print(f"{action}: {args.name} ({args.tool_id}), points={point_count}, relations={relation_count}")


if __name__ == "__main__":
    main()
