#!/usr/bin/env python3
"""Create or update the reproducible Open WebUI course assistant model."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import httpx

DEFAULT_BASE = "http://localhost:8080"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_NAME = "课程 AI 助教"
DEFAULT_ID = "course-ai-assistant"
KNOWLEDGE_NAME = "course-knowledge-base"
CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs/course-assistant"


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"缺少环境变量 {name}。请在本机设置管理员凭据。")
    return value


def detail(response: httpx.Response) -> str:
    try:
        data = response.json()
        if isinstance(data, dict):
            value = data.get("detail") or data.get("error") or data.get("message") or data
        else:
            value = data
    except (ValueError, json.JSONDecodeError):
        value = response.text
    text = str(value)[:500]
    for secret in (os.getenv("OPENWEBUI_PASSWORD", ""), os.getenv("OPENAI_API_KEY", "")):
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return f"HTTP {response.status_code}: {text}"


def request_ok(response: httpx.Response) -> Any:
    if not response.is_success:
        raise RuntimeError(detail(response))
    return response.json() if response.content else {}


def login(client: httpx.Client, base: str) -> str:
    response = client.post(f"{base}/api/v1/auths/signin", json={"email": required_env("OPENWEBUI_EMAIL"), "password": required_env("OPENWEBUI_PASSWORD")})
    data = request_ok(response)
    token = data.get("token")
    if not token:
        raise RuntimeError("登录响应未包含 token")
    return token


def discover_knowledge(client: httpx.Client, base: str, headers: dict[str, str], requested: str | None) -> dict[str, str]:
    if requested:
        response = client.get(f"{base}/api/v1/knowledge/{requested}", headers=headers)
        data = request_ok(response)
        if data.get("name") != KNOWLEDGE_NAME:
            raise RuntimeError(f"Knowledge ID {requested} 不是 {KNOWLEDGE_NAME}")
        return {"id": requested, "name": data["name"]}
    data = request_ok(client.get(f"{base}/api/v1/knowledge/", headers=headers))
    matches = [x for x in data.get("items", []) if x.get("name") == KNOWLEDGE_NAME]
    if len(matches) != 1:
        raise RuntimeError(f"期望唯一 Knowledge {KNOWLEDGE_NAME}，实际找到 {len(matches)} 个")
    return {"id": str(matches[0]["id"]), "name": KNOWLEDGE_NAME}


def discover_model(client: httpx.Client, base: str, headers: dict[str, str], model: str) -> None:
    data = request_ok(client.get(f"{base}/api/models", headers=headers))
    items = data.get("data", data.get("items", [])) if isinstance(data, dict) else data
    ids = {str(x.get("id")) for x in items if isinstance(x, dict)}
    if model not in ids:
        raise RuntimeError(f"模型 {model} 不在当前 Open WebUI 模型列表中")


def payload(model: str, name: str, knowledge: dict[str, str]) -> dict[str, Any]:
    prompt = (CONFIG_PATH / "system-prompt.md").read_text(encoding="utf-8")
    return {"id": DEFAULT_ID, "base_model_id": model, "name": name, "meta": {"description": "Codex 实战课程与数学建模课程 AI 助教", "knowledge": [{"type": "collection", "id": knowledge["id"], "name": knowledge["name"]}], "tags": ["课程助教", "RAG"]}, "params": {"system": prompt}, "is_active": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=os.getenv("OPENWEBUI_BASE_URL", DEFAULT_BASE))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--knowledge-id")
    parser.add_argument("--name", default=DEFAULT_NAME)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    base = args.base.rstrip("/")
    config = {"assistant_id": DEFAULT_ID, "name": args.name, "model": args.model, "knowledge_name": KNOWLEDGE_NAME}
    with httpx.Client(timeout=60, trust_env=False) as client:
        token = login(client, base)
        headers = {"Authorization": f"Bearer {token}"}
        knowledge = discover_knowledge(client, base, headers, args.knowledge_id)
        discover_model(client, base, headers, args.model)
        body = payload(args.model, args.name, knowledge)
        if args.dry_run:
            print(json.dumps({**config, "knowledge_id": knowledge["id"], "mode": "dry-run"}, ensure_ascii=False, indent=2))
            return
        existing = client.get(f"{base}/api/v1/models/model", params={"id": DEFAULT_ID}, headers=headers)
        if existing.status_code == 404:
            response = client.post(f"{base}/api/v1/models/create", headers=headers, json=body)
            action = "created"
        elif existing.is_success:
            response = client.post(f"{base}/api/v1/models/model/update", headers=headers, json=body)
            action = "updated"
        else:
            raise RuntimeError(detail(existing))
        request_ok(response)
        print(f"{action}: {args.name} ({DEFAULT_ID}), model={args.model}, knowledge={KNOWLEDGE_NAME} ({knowledge['id']})")


if __name__ == "__main__":
    main()
