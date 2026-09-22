"""VOICEVOX ENGINE 用 TTS provider.

配置先:
    <xiaozhi-server>/core/providers/tts/voicevox.py

`core/utils/tts.py` の `create_instance()` が
`core/providers/tts/{type}.py` を動的 import して `TTSProvider` を生成するため、
このファイルを置くだけで `type: voicevox` が使えるようになる。コア側の改変は不要。

なぜ CustomTTS で代用できないか:
    `custom.py` は `requests.post(url, json=params)` の単発リクエストしかできない。
    VOICEVOX は2段階:
        POST /audio_query?text=...&speaker=N  -> クエリJSON
        POST /synthesis?speaker=N   (上のJSON) -> WAV
    したがって専用の provider が要る。

出力は WAV 24kHz / モノラル / 16bit。さくらの音声合成と同じ形式なので、
リハーサル（VOICEVOX）と本番（さくら）で音声パイプラインの条件が揃う。
"""

import os
import uuid
import requests
from datetime import datetime

from config.logger import setup_logging
from core.providers.tts.base import TTSProviderBase

TAG = __name__
logger = setup_logging()


class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)

        self.api_url = config.get("api_url", "http://127.0.0.1:50021").rstrip("/")
        # ずんだもん（ノーマル）= 3。話者一覧は GET /speakers で取得できる
        self.speaker = int(config.get("speaker", 3))
        self.audio_file_type = config.get("format", "wav")
        self.output_file = config.get("output_dir", "tmp/")
        self.timeout = int(config.get("timeout", 30))

        # 話速・音高・抑揚。未指定なら VOICEVOX の既定値をそのまま使う
        self.speed_scale = self._opt_float(config, "speed_scale")
        self.pitch_scale = self._opt_float(config, "pitch_scale")
        self.intonation_scale = self._opt_float(config, "intonation_scale")

    @staticmethod
    def _opt_float(config, key):
        v = config.get(key)
        if v is None or v == "":
            return None
        return float(v)

    def generate_filename(self, extension=None):
        ext = extension or f".{self.audio_file_type}"
        return os.path.join(
            self.output_file,
            f"tts-{datetime.now().date()}@{uuid.uuid4().hex}{ext}",
        )

    async def text_to_speak(self, text, output_file):
        try:
            # 1段階目: 読み・アクセント句のクエリを作る
            query_resp = requests.post(
                f"{self.api_url}/audio_query",
                params={"text": text, "speaker": self.speaker},
                timeout=self.timeout,
            )
            if query_resp.status_code != 200:
                raise Exception(
                    f"audio_query 失敗: {query_resp.status_code} - {query_resp.text}"
                )
            query = query_resp.json()

            # クエリを書き換えてから合成する（VOICEVOX の作法）
            if self.speed_scale is not None:
                query["speedScale"] = self.speed_scale
            if self.pitch_scale is not None:
                query["pitchScale"] = self.pitch_scale
            if self.intonation_scale is not None:
                query["intonationScale"] = self.intonation_scale

            # 2段階目: 合成
            synth_resp = requests.post(
                f"{self.api_url}/synthesis",
                params={"speaker": self.speaker},
                json=query,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
            if synth_resp.status_code != 200:
                raise Exception(
                    f"synthesis 失敗: {synth_resp.status_code} - {synth_resp.text}"
                )

            if output_file:
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, "wb") as f:
                    f.write(synth_resp.content)
            else:
                return synth_resp.content

        except Exception as e:
            error_msg = f"VOICEVOX TTS请求失败: {e}"
            logger.bind(tag=TAG).error(error_msg)
            raise Exception(error_msg)
