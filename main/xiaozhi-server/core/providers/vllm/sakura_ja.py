# 日本語で画像を説明する VLLM プロバイダ。
#
# 上流の core/providers/vllm/openai.py は response() の中で
#     question = question + "(请使用中文回复)"
# と中国語指示をハードコードしており、config からは変えられない。
# 上流ファイルを書き換えると差分が残るため、type: sakura_ja として別実装を置く。
#
# 変更点は2つだけ。
#   1) 言語指示を config の language から組み立てる（既定: 日本語）
#   2) max_tokens / temperature / top_p を実際にリクエストへ渡す
#      （上流は属性に持つだけで create() に渡しておらず、効いていない）
#
# 使い方（data/.config.yaml）:
#   selected_module:
#     VLLM: SakuraVLLM
#   VLLM:
#     SakuraVLLM:
#       type: sakura_ja
#       url: https://api.ai.sakura.ad.jp/v1
#       model_name: preview/gemma-4-31B-it
#       language: 日本語
#       max_tokens: 200

import base64
import datetime
import os

import openai

from config.logger import setup_logging
from core.providers.vllm.base import VLLMProviderBase
from core.utils.util import check_model_key

TAG = __name__
logger = setup_logging()


class VLLMProvider(VLLMProviderBase):
    def __init__(self, config):
        self.model_name = config.get("model_name")
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url") or config.get("url")
        self.language = config.get("language") or "日本語"
        # モデル比較用に実際の撮影画像を残す。比較が終わったら false に戻す。
        self.save_images = bool(config.get("save_images", False))
        self.image_dir = config.get("image_dir") or "tmp"

        param_defaults = {
            "max_tokens": (500, int),
            "temperature": (0.7, lambda x: round(float(x), 1)),
            "top_p": (1.0, lambda x: round(float(x), 1)),
        }
        for param, (default, converter) in param_defaults.items():
            value = config.get(param)
            try:
                setattr(
                    self, param, converter(value) if value not in (None, "") else default
                )
            except (ValueError, TypeError):
                setattr(self, param, default)

        model_key_msg = check_model_key("VLLM", self.api_key)
        if model_key_msg:
            logger.bind(tag=TAG).error(model_key_msg)
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

    def _dump_image(self, base64_image):
        try:
            os.makedirs(self.image_dir, exist_ok=True)
            name = datetime.datetime.now().strftime("vision_%Y%m%d_%H%M%S_%f.jpg")
            path = os.path.join(self.image_dir, name)
            with open(path, "wb") as f:
                f.write(base64.b64decode(base64_image))
            logger.bind(tag=TAG).info(f"撮影画像を保存: {path}")
        except Exception as e:  # noqa: BLE001
            logger.bind(tag=TAG).error(f"画像の保存に失敗: {e}")

    def response(self, question, base64_image):
        if self.save_images:
            self._dump_image(base64_image)
        # 音声で読み上げられるため、箇条書きや記号は避けさせる
        directive = (
            f"\n\n必ず{self.language}で答えてください。"
            "音声で読み上げるため、2文以内・80文字以内で、箇条書きや記号は使わないでください。"
        )
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question + directive},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ]
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=False,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in response generation: {e}")
            raise
