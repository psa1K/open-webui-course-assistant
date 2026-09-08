#!/usr/bin/env python3
"""Create or update the temporary practice generator in Open WebUI."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import httpx

DEFAULT_BASE = "http://localhost:8080"
DEFAULT_TOOL_ID = "course_practice_generator"
DEFAULT_NAME = "章节练习题生成器"
SOURCE = Path(__file__).resolve().parents[1] / "tools/course_practice_generator.py"


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


def source_content() -> str:
    text = SOURCE.read_text(encoding="utf-8")
    if "class Tools:" not in text or "def generate_practice_questions(" not in text:
        raise RuntimeError("工具源码缺少 Tools.generate_practice_questions 定义")
    forbidden = ("requests.", "httpx.", "sqlite3", "OPENAI_API_KEY", "password =")
    if any(item in text for item in forbidden):
        raise RuntimeError("工具源码包含不允许的网络、数据库或敏感配置依赖")
    return text


def payload(tool_id: str, name: str, content: str) -> dict[str, Any]:
    return {"id": tool_id, "name": name, "content": content, "meta": {"description": "根据统一课程知识库和用户约束临时生成章节练习题"}, "access_grants": []}


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
    content = source_content()
    body = payload(args.tool_id, args.name, content)
    if args.dry_run:
        print(json.dumps({"mode": "dry-run", "tool_id": args.tool_id, "name": args.name, "source": str(SOURCE.name)}, ensure_ascii=False))
        return
    base = args.base.rstrip("/")
    with httpx.Client(timeout=60, trust_env=False) as client:
        token = login(client, base)
        headers = {"Authorization": f"Bearer {token}"}
        if find_existing(client, base, headers, args.tool_id):
            response = client.post(f"{base}/api/v1/tools/id/{args.tool_id}/update", headers=headers, json=body)
            action = "updated"
        else:
            response = client.post(f"{base}/api/v1/tools/create", headers=headers, json=body)
            action = "created"
        request_json(response)
    print(f"{action}: {args.name} ({args.tool_id})")


if __name__ == "__main__":
    main()
