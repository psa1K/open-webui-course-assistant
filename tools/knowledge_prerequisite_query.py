"""Open WebUI Workspace Tool: query structured knowledge-point prerequisites.

The installer embeds the course catalog and repository-maintained prerequisite
graph, so the Workspace Tool needs no filesystem, network, or database access.
Relations describe recommended learning dependencies; source fields identify
the course material that introduces each knowledge point.
"""
from __future__ import annotations

import json
from collections import deque
from typing import Any

COURSE_CATALOG_JSON = json.dumps({"courses": []})  # PLACEHOLDER_COURSE_CATALOG
PREREQUISITE_GRAPH_JSON = json.dumps({"knowledge_points": [], "relations": []})  # PLACEHOLDER_PREREQUISITE_GRAPH
COURSES = ("codex", "math-modeling")


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _normalized(value: Any) -> str:
    return _text(value).casefold()


class Tools:
    """Return direct and optional transitive prerequisite relationships."""

    def query_prerequisites(
        self,
        knowledge_point: str,
        course: str | None = None,
        include_indirect: bool = False,
    ) -> dict[str, Any]:
        knowledge_point = _text(knowledge_point)
        course = self._course(course)
        if not knowledge_point:
            return self._error("knowledge_point 不能为空。", knowledge_point, course, include_indirect)
        if course is False:
            return self._error("course 只能是 codex、math-modeling 或不填。", knowledge_point, course, include_indirect)
        if not isinstance(include_indirect, bool):
            return self._error("include_indirect 只能是 true 或 false。", knowledge_point, course, include_indirect)

        catalog, graph = self._load_data()
        nodes = {node["id"]: node for node in graph["knowledge_points"]}
        matches = self._matches(nodes.values(), knowledge_point, course)
        if not matches:
            return {
                "status": "ok",
                "mode": "knowledge_prerequisite_query",
                "query": {"knowledge_point": knowledge_point, "course": course, "include_indirect": include_indirect},
                "matched_count": 0,
                "knowledge_points": [],
                "message": "资料中未找到相关信息：结构化先修关系中没有匹配的知识点。",
            }

        by_id = self._chapter_index(catalog)
        incoming, outgoing = self._adjacency(graph["relations"])
        results = []
        for node in matches:
            node_id = node["id"]
            result = self._node_payload(node, by_id)
            result["prerequisites"] = [self._node_payload(nodes[item], by_id) for item in incoming.get(node_id, [])]
            result["successors"] = [self._node_payload(nodes[item], by_id) for item in outgoing.get(node_id, [])]
            if include_indirect:
                result["all_prerequisites"] = [
                    self._node_payload(nodes[item], by_id)
                    for item in self._walk(node_id, incoming)
                ]
                result["all_successors"] = [
                    self._node_payload(nodes[item], by_id)
                    for item in self._walk(node_id, outgoing)
                ]
            results.append(result)
        return {
            "status": "ok",
            "mode": "knowledge_prerequisite_query",
            "relation_scope": graph.get("relation_scope", "recommended learning dependencies"),
            "query": {"knowledge_point": knowledge_point, "course": course, "include_indirect": include_indirect},
            "matched_count": len(results),
            "knowledge_points": results,
        }

    @staticmethod
    def _error(message: str, knowledge_point: str, course: str | None | bool, include_indirect: Any) -> dict[str, Any]:
        return {
            "status": "error",
            "error_code": "INVALID_INPUT",
            "message": message,
            "query": {
                "knowledge_point": knowledge_point,
                "course": course if isinstance(course, str) or course is None else None,
                "include_indirect": include_indirect,
            },
        }

    @staticmethod
    def _course(value: str | None) -> str | None | bool:
        if value is None or not _text(value):
            return None
        normalized = _normalized(value)
        return normalized if normalized in COURSES else False

    @staticmethod
    def _load_data() -> tuple[dict[str, Any], dict[str, Any]]:
        catalog = json.loads(COURSE_CATALOG_JSON)
        graph = json.loads(PREREQUISITE_GRAPH_JSON)
        if not catalog.get("courses") or not graph.get("knowledge_points"):
            raise ValueError("结构化课程目录或先修关系为空，请检查工具是否完整安装")
        return catalog, graph

    @staticmethod
    def _matches(nodes: Any, query: str, course: str | None) -> list[dict[str, Any]]:
        needle = _normalized(query)
        ranked = []
        for node in nodes:
            if course and node["course"] != course:
                continue
            name = _normalized(node["name"])
            aliases = [_normalized(item) for item in node.get("aliases", [])]
            if needle == name:
                rank = 4
            elif needle in aliases:
                rank = 3
            elif needle in name or any(needle in item for item in aliases):
                rank = 2
            elif any(item in needle for item in [name, *aliases] if item):
                rank = 1
            else:
                continue
            ranked.append((rank, node))
        ranked.sort(key=lambda item: (-item[0], item[1]["name"]))
        return [node for _rank, node in ranked]

    @staticmethod
    def _chapter_index(catalog: dict[str, Any]) -> dict[str, tuple[dict[str, Any], dict[str, Any]]]:
        return {
            chapter["id"]: (course, chapter)
            for course in catalog["courses"]
            for chapter in course["chapters"]
        }

    @staticmethod
    def _adjacency(relations: list[dict[str, str]]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
        incoming: dict[str, list[str]] = {}
        outgoing: dict[str, list[str]] = {}
        for relation in relations:
            prerequisite = relation["prerequisite"]
            dependent = relation["dependent"]
            incoming.setdefault(dependent, []).append(prerequisite)
            outgoing.setdefault(prerequisite, []).append(dependent)
        return incoming, outgoing

    @staticmethod
    def _walk(start: str, adjacency: dict[str, list[str]]) -> list[str]:
        seen = {start}
        queue = deque(adjacency.get(start, []))
        found = []
        while queue:
            current = queue.popleft()
            if current in seen:
                continue
            seen.add(current)
            found.append(current)
            queue.extend(adjacency.get(current, []))
        return found

    @staticmethod
    def _node_payload(node: dict[str, Any], chapters: dict[str, tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
        course, chapter = chapters[node["chapter_id"]]
        return {
            "id": node["id"],
            "name": node["name"],
            "course": course["id"],
            "course_name": course["name"],
            "chapter": {
                "id": chapter["id"],
                "title": chapter["title"],
                "source": dict(chapter["source"]),
            },
        }
