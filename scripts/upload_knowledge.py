#!/usr/bin/env python3
"""Upload knowledge/ materials into Open WebUI collections.

Usage:
    .venv/bin/python scripts/upload_knowledge.py [--base http://localhost:8080]
    Requires admin credentials via env: OPENWEBUI_EMAIL / OPENWEBUI_PASSWORD
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import httpx

BASE = "http://localhost:8080"
EMAIL = os.getenv("OPENWEBUI_EMAIL", "kei2332@qq.com")
PASSWORD = os.getenv("OPENWEBUI_PASSWORD", "")

COLLECTIONS = {
    "codex-course": [
        "knowledge/codex-course/*.md",
        "knowledge/codex-course/00-协作工具-环境准备.pdf",
        "knowledge/codex-course/courses_mcp01.py",
    ],
    "math-modeling": [
        "knowledge/math-modeling/Lecture1.pdf",
        "knowledge/math-modeling/Lecture1.tex",
    ],
}


def login(client: httpx.Client) -> str:
    r = client.post(
        f"{BASE}/api/v1/auths/signin",
        json={"email": EMAIL, "password": PASSWORD},
    )
    r.raise_for_status()
    return r.json()["token"]


def ensure_knowledge(client: httpx.Client, headers: dict, name: str, reset: bool = False) -> str:
    r = client.get(f"{BASE}/api/v1/knowledge/", headers=headers)
    r.raise_for_status()
    for item in r.json().get("items", []):
        if item["name"] == name:
            if reset:
                r = client.delete(f"{BASE}/api/v1/knowledge/{item['id']}/delete", headers=headers)
                r.raise_for_status()
                break
            return item["id"]
    r = client.post(
        f"{BASE}/api/v1/knowledge/create",
        headers=headers,
        json={"name": name, "description": f"Course knowledge base: {name}"},
    )
    r.raise_for_status()
    return r.json()["id"]


def wait_for_processing(client: httpx.Client, headers: dict, file_id: str, timeout: float = 120.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = client.get(f"{BASE}/api/v1/files/{file_id}/process/status", headers=headers)
        r.raise_for_status()
        status = r.json().get("status")
        if status == "completed":
            return
        if status == "failed":
            raise RuntimeError(f"file processing failed: {r.text[:200]}")
        time.sleep(2)
    raise TimeoutError(f"file processing timed out for {file_id}")


def upload_and_add(client: httpx.Client, headers: dict, kb_id: str, path: Path) -> None:
    with path.open("rb") as fh:
        r = client.post(
            f"{BASE}/api/v1/files/",
            headers=headers,
            files={"file": (path.name, fh)},
        )
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError:
            print(f"  ! upload failed {path.name}: {r.text[:300]}")
            raise
        file_id = r.json()["id"]
    wait_for_processing(client, headers, file_id)
    r = client.post(
        f"{BASE}/api/v1/knowledge/{kb_id}/file/add",
        headers=headers,
        json={"file_id": file_id},
    )
    try:
        r.raise_for_status()
    except httpx.HTTPStatusError:
        print(f"  ! add failed {path.name}: {r.text[:300]}")
        raise
    print(f"  + {path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=BASE)
    parser.add_argument("--root", default=".")
    parser.add_argument("--reset", action="store_true", help="recreate collections before upload")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    client = httpx.Client(timeout=60.0)
    token = login(client)
    headers = {"Authorization": f"Bearer {token}"}

    for name, patterns in COLLECTIONS.items():
        kb_id = ensure_knowledge(client, headers, name, reset=args.reset)
        print(f"[{name}] {kb_id}")
        files = []
        for pat in patterns:
            files.extend(sorted(root.glob(pat)))
        for path in files:
            if path.is_file():
                upload_and_add(client, headers, kb_id, path)


if __name__ == "__main__":
    main()
