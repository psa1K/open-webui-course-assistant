#!/usr/bin/env python3
"""Upload every file under knowledge/ into one Open WebUI knowledge base."""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import httpx

DEFAULT_BASE = "http://localhost:8080"
KNOWLEDGE_NAME = "course-knowledge-base"


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
    return response.json()["token"]


def ensure_knowledge(client: httpx.Client, base: str, headers: dict[str, str], reset: bool) -> str:
    response = client.get(f"{base}/api/v1/knowledge/", headers=headers)
    response.raise_for_status()
    for item in response.json().get("items", []):
        if item.get("name") == KNOWLEDGE_NAME:
            if not reset:
                return item["id"]
            delete = client.delete(f"{base}/api/v1/knowledge/{item['id']}/delete", headers=headers)
            delete.raise_for_status()
            break

    response = client.post(
        f"{base}/api/v1/knowledge/create",
        headers=headers,
        json={
            "name": KNOWLEDGE_NAME,
            "description": "Unified knowledge base for the Codex practical course and mathematical modeling materials.",
        },
    )
    response.raise_for_status()
    return response.json()["id"]


def wait_for_processing(client: httpx.Client, base: str, headers: dict[str, str], file_id: str, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = client.get(f"{base}/api/v1/files/{file_id}/process/status", headers=headers)
        response.raise_for_status()
        status = response.json().get("status")
        if status == "completed":
            return
        if status == "failed":
            raise RuntimeError(f"File processing failed for {file_id}: {response.text[:300]}")
        time.sleep(2)
    raise TimeoutError(f"File processing timed out for {file_id}")


def source_files(root: Path) -> list[Path]:
    files = sorted(path for path in (root / "knowledge").rglob("*") if path.is_file() and path.name != "README.md")
    if not files:
        raise RuntimeError(f"No knowledge files found under {root / 'knowledge'}")
    return files


def upload_and_add(client: httpx.Client, base: str, headers: dict[str, str], knowledge_id: str, path: Path, timeout: float) -> None:
    with path.open("rb") as file_handle:
        response = client.post(
            f"{base}/api/v1/files/",
            headers=headers,
            files={"file": (path.name, file_handle)},
        )
    response.raise_for_status()
    file_id = response.json()["id"]
    wait_for_processing(client, base, headers, file_id, timeout)
    response = client.post(
        f"{base}/api/v1/knowledge/{knowledge_id}/file/add",
        headers=headers,
        json={"file_id": file_id},
    )
    response.raise_for_status()
    print(f"uploaded: {path.relative_to(path.parents[1])}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=os.getenv("OPENWEBUI_BASE_URL", DEFAULT_BASE))
    parser.add_argument("--root", default=".")
    parser.add_argument("--reset", action="store_true", help="Delete and recreate the unified knowledge base")
    parser.add_argument("--timeout", type=float, default=300.0, help="Per-file processing timeout in seconds")
    args = parser.parse_args()
    base = args.base.rstrip("/")
    root = Path(args.root).resolve()
    files = source_files(root)

    with httpx.Client(timeout=60.0, trust_env=False) as client:
        token = login(client, base)
        headers = {"Authorization": f"Bearer {token}"}
        knowledge_id = ensure_knowledge(client, base, headers, args.reset)
        print(f"knowledge: {KNOWLEDGE_NAME} ({knowledge_id})")
        print(f"files: {len(files)}")
        for path in files:
            upload_and_add(client, base, headers, knowledge_id, path, args.timeout)


if __name__ == "__main__":
    main()
