"""Personal Brain 連携用 Memory Provider。

会話サーバホスト上で動作する Personal Brain REST API（localhost:28080）に
会話履歴の保存と検索を委譲する。
"""

import asyncio
import json
import traceback
from typing import Optional

import requests

from ..base import MemoryProviderBase, logger

TAG = __name__


class MemoryProvider(MemoryProviderBase):
    def __init__(self, config: dict, summary_memory: Optional[str] = None):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://127.0.0.1:28080").rstrip("/")
        self.timeout = config.get("timeout", 5)
        self.role_id = config.get("role_id", "default")

        logger.bind(tag=TAG).info(f"PersonalBrain memory provider initialized: {self.base_url}")
        self._check_connection()

    def _check_connection(self):
        try:
            r = self._get("/health")
            r.raise_for_status()
            data = r.json()
            logger.bind(tag=TAG).info(
                f"Personal Brain health check OK: conversations={data.get('counts', {}).get('conversations', '?')}, "
                f"memories={data.get('counts', {}).get('memories', '?')}"
            )
        except Exception as e:
            logger.bind(tag=TAG).warning(
                f"Personal Brain is not reachable at {self.base_url}: {e}. "
                "Conversations will not be saved until the API is started."
            )

    def _post(self, path: str, payload: dict):
        url = f"{self.base_url}{path}"
        return requests.post(url, json=payload, timeout=self.timeout)

    def _get(self, path: str, params: dict = None):
        url = f"{self.base_url}{path}"
        return requests.get(url, params=params, timeout=self.timeout)

    @staticmethod
    def _message_to_content(message) -> Optional[str]:
        """Message オブジェクトから保存用テキストを抽出する。"""
        content = message.content
        if not content:
            return None
        # ASR 結果が {"content": "..."} 形式の場合がある
        try:
            if content.strip().startswith("{") and content.strip().endswith("}"):
                data = json.loads(content)
                if isinstance(data, dict) and "content" in data:
                    content = data["content"]
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        return content.strip() if content else None

    async def save_memory(self, msgs, session_id=None):
        """会話終了時に呼ばれる。各ターンを Personal Brain に保存する。"""
        if not session_id:
            logger.bind(tag=TAG).warning("session_id is empty, skipping save_memory")
            return

        try:
            for msg in msgs:
                # system / tool / 一時メッセージは保存対象外
                if msg.role in ("system", "tool") or getattr(msg, "is_temporary", False):
                    continue

                content = self._message_to_content(msg)
                if not content:
                    continue

                payload = {
                    "session_id": session_id,
                    "role": msg.role,
                    "content": content,
                    "metadata_json": json.dumps({
                        "role_id": self.role_id,
                        "source": "xiaozhi-esp32-server",
                    }),
                }
                await asyncio.to_thread(self._post, "/conversations/append", payload)

            logger.bind(tag=TAG).info(
                f"Saved {len(msgs)} messages to Personal Brain for session {session_id}"
            )
        except Exception as e:
            logger.bind(tag=TAG).error(f"Failed to save memory: {e}")
            logger.bind(tag=TAG).debug(f"Detailed error: {traceback.format_exc()}")

    async def query_memory(self, query: str) -> str:
        """LLM 応答前に呼ばれる。関連する記憶を検索してプロンプトに挿入する。"""
        try:
            response = await asyncio.to_thread(
                self._post, "/memories/search", {"query": query, "top_k": 5}
            )
            response.raise_for_status()
            items = response.json()
            if not items:
                return ""

            lines = []
            for item in items:
                doc = item.get("document", "")
                meta = item.get("metadata", {})
                mtype = meta.get("memory_type", "memory")
                if doc:
                    lines.append(f"- [{mtype}] {doc}")

            return "\n".join(lines)
        except Exception as e:
            logger.bind(tag=TAG).error(f"Failed to query memory: {e}")
            return ""
