#!/usr/bin/env python3
"""Create or update the study-plan generator in Open WebUI."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

import httpx

DEFAULT_BASE = "http://localhost:8080"
DEFAULT_TOOL_ID = "study_plan_generator"
DEFAULT_NAME = "学习计划生成工具"
SOURCE = Path(__file__).resolve().parents[1] / "tools/study_plan_generator.py"
CATALOG = Path(__file__).resolve().parents[1] / "data/course-catalog.json"
PLACEHOLDER = re.compile(r"^COURSE_CATALOG_JSON = .*# PLACEHOLDER_COURSE_CATALOG$", re.MULTILINE)


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
    response = client.post(f"{base}/api/v1/auths/signin", json={"email": required_env("OPENWEBUI_EMAIL"), "password": required_env("OPENWEBUI_PASSWORD")})
    token = request_json(response).get("token")
    if not token:
        raise RuntimeError("登录响应未包含 token")
    return token


def build_content() -> str:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    if len(catalog.get("courses", [])) < 2 or sum(len(c.get("chapters", [])) for c in catalog.get("courses", [])) < 8:
        raise RuntimeError("课程目录不足：至少需要两门课程和 8 个章节")
    text = SOURCE.read_text(encoding="utf-8")
    if "class Tools:" not in text or "def generate_study_plan(" not in text:
        raise RuntimeError("工具源码缺少 Tools.generate_study_plan 定义")
    if any(item in text for item in ("requests.", "httpx.", "sqlite3", "OPENAI_API_KEY", "password =", "subprocess")):
        raise RuntimeError("工具源码包含不允许的网络、数据库或敏感配置依赖")
    inline = "COURSE_CATALOG_JSON = " + json.dumps(json.dumps(catalog, ensure_ascii=False), ensure_ascii=False)
    content, replaced = PLACEHOLDER.subn(inline, text, count=1)
    if replaced != 1:
        raise RuntimeError("工具源码缺少目录占位符")
    return content


def payload(tool_id: str, name: str, content: str, chapter_count: int) -> dict[str, Any]:
    return {"id": tool_id, "name": name, "content": content, "meta": {"description": f"根据结构化课程目录生成分阶段学习计划（覆盖 {chapter_count} 个章节）"}, "access_grants": []}


def find_existing(client, base, headers, tool_id):
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
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    chapter_count = sum(len(c.get("chapters", [])) for c in catalog.get("courses", []))
    content = build_content()
    body = payload(args.tool_id, args.name, content, chapter_count)
    if args.dry_run:
        print(json.dumps({"mode": "dry-run", "tool_id": args.tool_id, "name": args.name, "chapter_count": chapter_count, "source": SOURCE.name}, ensure_ascii=False))
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
    print(f"{action}: {args.name} ({args.tool_id}), chapters={chapter_count}")


if __name__ == "__main__":
    main()
