[![Banners](../images/banner1.png)](https://github.com/xinnan-tech/xiaozhi-esp32-server)

<h1 align="center">Xiaozhi バックエンドサービス xiaozhi-esp32-server</h1>

<p align="center">
人と機械の共生知能の理論と技術に基づき、知能端末のハード・ソフト体系を開発するプロジェクト<br/>オープンソースの知能ハードウェア
<a href="https://github.com/78/xiaozhi-esp32">xiaozhi-esp32</a> にバックエンドサービスを提供します<br/>
<a href="https://ccnphfhqs21z.feishu.cn/wiki/M0XiwldO9iJwHikpXD5cEx71nKh">小智通信プロトコル</a>に準拠し、Python / Java / Vue で実装<br/>
MQTT+UDP プロトコル、WebSocket プロトコル、MCP アクセスポイント、声紋認識、ナレッジベースに対応
</p>

<p align="center">
<a href="../FAQ.md">FAQ</a>
· <a href="https://github.com/xinnan-tech/xiaozhi-esp32-server/issues">問題報告</a>
· <a href="../../README.md#%E9%83%A8%E7%BD%B2%E6%96%87%E6%A1%A3">デプロイ文書</a>
· <a href="https://github.com/xinnan-tech/xiaozhi-esp32-server/releases">リリースノート</a>
</p>

<p align="center">
  <a href="../../README.md"><img alt="简体中文版自述文件" src="https://img.shields.io/badge/简体中文-DFE0E5"></a>
  <a href="./README_ja.md"><img alt="日本語版自述文件" src="https://img.shields.io/badge/日本語-DBEDFA"></a>
  <a href="./README_en.md"><img alt="README in English" src="https://img.shields.io/badge/English-DFE0E5"></a>
  <a href="./README_vi.md"><img alt="Tiếng Việt" src="https://img.shields.io/badge/Tiếng Việt-DFE0E5"></a>
  <a href="./README_de.md"><img alt="Deutsch" src="https://img.shields.io/badge/Deutsch-DFE0E5"></a>
  <a href="./README_pt_BR.md"><img alt="Português (Brasil)" src="https://img.shields.io/badge/Português (Brasil)-DFE0E5"></a>
  <a href="https://github.com/xinnan-tech/xiaozhi-esp32-server/releases">
    <img alt="GitHub Contributors" src="https://img.shields.io/github/v/release/xinnan-tech/xiaozhi-esp32-server?logo=docker" />
  </a>
  <a href="https://github.com/xinnan-tech/xiaozhi-esp32-server/blob/main/LICENSE">
    <img alt="GitHub pull requests" src="https://img.shields.io/badge/license-MIT-white?labelColor=black" />
  </a>
  <a href="https://github.com/xinnan-tech/xiaozhi-esp32-server">
    <img alt="stars" src="https://img.shields.io/github/stars/xinnan-tech/xiaozhi-esp32-server?color=ffcb47&labelColor=black" />
  </a>
</p>

<p align="center">
華南理工大学・劉思源教授チーム主導開発
</br>
刘思源教授团队主导研发（华南理工大学）
</br>
<img src="../images/hnlg.jpg" alt="華南理工大学" width="50%">
</p>

> 本ファイルは上流 `README_en.md` の日本語訳です。上流の更新に追従しない場合があります。
> 最新の詳細は上流の中国語版 `README.md` / 英語版 `README_en.md` を参照してください。

---

## このフォークの差分（Chronona 版）

上流 `xinnan-tech/xiaozhi-esp32-server` に対する日本向け・ローカルファーストのカスタマイズです。
ブランチ `custom/sakura-local` で管理しています。`main` は上流のミラー専用で、直接編集しません。

### 追加・変更ファイル

| ファイル | 内容 |
|---|---|
| `main/xiaozhi-server/core/providers/asr/openai.py`（変更） | `language` / `prompt` / `response_format` を config から透過。上流は `model` のみ送信 |
| `main/xiaozhi-server/core/providers/tts/voicevox.py`（新規） | VOICEVOX ENGINE の2段階 API（`/audio_query` → `/synthesis`）対応。`type: voicevox` で利用 |
| `main/xiaozhi-server/core/providers/vllm/sakura_ja.py`（新規） | 日本語指示で画像解説。上流 `openai.py` の中国語指示ハードコードを回避。`max_tokens` / `temperature` / `top_p` を実際にリクエストへ渡す（上流は属性に持つだけで未使用）。`save_images` で撮影画像の保存可 |
| `main/xiaozhi-server/render-config.ps1`（新規） | `data/.config.yaml.tmpl` の `__SAKURA_API_KEY__` に環境変数 `SAKURA_API_KEY` を注入して `.config.yaml` を生成 |
| `main/xiaozhi-server/run.ps1`（新規） | Windows + uv 用起動ラッパー。Opus DLL の PATH 追加と出力の UTF-8 強制を行う |

### 設定例（`.config.yaml` 抜粋）

```yaml
selected_module:
  ASR: SakuraASR        # または WhisperLocal（自前 faster-whisper）
  LLM: SakuraLLM
  VLLM: SakuraVLLM
  TTS: VoicevoxTTS      # リハーサル用。本番は SakuraTTS
  Memory: nomem
  Intent: function_call

ASR:
  SakuraASR:
    type: openai
    base_url: https://api.ai.sakura.ad.jp/v1/audio/transcriptions
    model_name: whisper-large-v3-turbo
    language: ja
    prompt: スタックちゃん、撮影、再撮影、写真、カメラ、画像、説明
    response_format: json

TTS:
  VoicevoxTTS:
    type: voicevox
    api_url: http://127.0.0.1:50021
    speaker: 3          # ずんだもん（ノーマル）

VLLM:
  SakuraVLLM:
    type: sakura_ja
    language: 日本語
    base_url: https://api.ai.sakura.ad.jp/v1
    model_name: preview/gemma-4-31B-it
    max_tokens: 200
```

### 運用ルール

* `main` には直接コミットしない。作業は `custom/sakura-local` で行う
* 上流の更新は週1回目安で `fetch upstream` → `custom` へマージ（リベース禁止）
* API キーはコミットしない。`.config.yaml` は生成物として扱い、テンプレート + 環境変数で運用する

---

## 対象ユーザー 👥

本プロジェクトは ESP32 ハードウェアデバイスと組み合わせて使います。ESP32 関連ハードウェアを購入し、配布済みのバックエンドサービスへの接続に成功したうえで、独自の `xiaozhi-esp32` バックエンドサービスを構築したい方に適しています。

動作イメージは以下の動画を参照してください 🎥

<table>
  <tr>
    <td>
      <a href="https://www.bilibili.com/video/BV1FMFyejExX" target="_blank">
        <picture>
          <img alt="応答速度の体感" src="docs/images/demo9.png" /></picture>
      </a>
    </td>
    <td>
      <a href="https://www.bilibili.com/video/BV1vchQzaEse" target="_blank">
        <picture>
          <img alt="速度最適化の秘訣" src="docs/images/demo6.png" /></picture>
      </a>
    </td>
    <td>
      <a href="https://www.bilibili.com/video/BV1WEcxzFEAT" target="_blank">
        <picture>
          <img alt="小智デジタルヒューマン・音声ウェイク対応" src="docs/images/demo8.png" /></picture>
      </a>
    </td>
    <td>
      <a href="https://www.bilibili.com/video/BV1CKVz6UEuB" target="_blank">
        <picture>
          <img alt="デバイス間通話" src="docs/images/demo0.png" /></picture>
      </a>
    </td>
    <td>
      <a href="https://www.bilibili.com/video/BV1C1tCzUEZh" target="_blank">
        <picture>
          <img alt="複雑な医療シーン" src="docs/images/demo1.png" /></picture>
      </a>
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://www.bilibili.com/video/BV1VC96Y5EMH" target="_blank">
        <picture>
          <img alt="音楽再生・天気・ニュース読み上げ" src="docs/images/demo7.png" /></picture>
      </a>
    </td>
    <td>
      <a href="https://www.bilibili.com/video/BV12J7WzBEaH" target="_blank">
        <picture>
          <img alt="リアルタイム割り込み" src="docs/images/demo10.png" /></picture>
      </a>
    </td>
    <td>
      <a href="https://www.bilibili.com/video/BV1Co76z7EvK" target="_blank">
        <picture>
          <img alt="撮影して物品を識別" src="docs/images/demo12.png" /></picture>
      </a>
    </td>
    <td>
      <a href="https://www.bilibili.com/video/BV1pNXWYGEx1" target="_blank">
        <picture>
          <img alt="家電のオンオフ制御" src="docs/images/demo5.png" /></picture>
      </a>
    </td>
    <td>
      <a href="https://www.bilibili.com/video/BV1TJ7WzzEo6" target="_blank">
        <picture>
          <img alt="複数指令タスク" src="docs/images/demo11.png" /></picture>
      </a>
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://www.bilibili.com/video/BV1ZQKUzYExM" target="_blank">
        <picture>
          <img alt="MCP アクセスポイント" src="docs/images/demo13.png" /></picture>
      </a>
    </td>
    <td>
      <a href="https://www.bilibili.com/video/BV1zUW5zJEkq" target="_blank">
        <picture>
          <img alt="MQTT 指令配信" src="docs/images/demo4.png" /></picture>
      </a>
    </td>
    <td>
      <a href="https://www.bilibili.com/video/BV1Exu3zqEDe" target="_blank">
        <picture>
          <img alt="声紋認識" src="docs/images/demo14.png" /></picture>
      </a>
    </td>
    <td>
      <a href="https://www.bilibili.com/video/BV1CDKWemEU6" target="_blank">
        <picture>
          <img alt="カスタム音色" src="docs/images/demo2.png" /></picture>
      </a>
    </td>
    <td>
      <a href="https://www.bilibili.com/video/BV12yA2egEaC" target="_blank">
        <picture>
          <img alt="広東語での会話" src="docs/images/demo3.png" /></picture>
      </a>
    </td>
  </tr>
</table>

---

## 注意 ⚠️

1. 本プロジェクトはオープンソースソフトウェアです。連携する第三者 API サービス事業者（音声認識、大規模言語モデル、音声合成などのプラットフォームを含みますがこれらに限りません）との商業提携はなく、サービス品質や資金の安全性について何ら保証しません。関連事業の許可を持つ事業者のサービスを優先し、利用規約とプライバシーポリシーをよく読んでください。本ソフトウェアはアカウントのキーを預からず、資金の流れに関与せず、チャージ資金の損失リスクを負いません。

2. 本プロジェクトの機能は未完成であり、ネットワークセキュリティ評価を通過していません。商用環境では使用しないでください。公衆網環境で学習目的にデプロイする場合は、必要な防御措置を必ず講じてください。

---

## デプロイ文書

![Banners](../images/banner2.png)

本プロジェクトは2種類のデプロイ方式を提供します。用途に応じて選択してください。

#### 🚀 デプロイ方式の選択
| デプロイ方式 | 特徴 | 適用場面 | デプロイ文書 | 構成要件 | 動画チュートリアル |
|---------|------|---------|---------|---------|---------|
| **簡易インストール** | 知能対話、単一エージェント管理 | 低スペック環境、データは設定ファイルに保存、データベース不要 | [①Docker版](../Deployment.md#%E6%96%B9%E5%BC%8F%E4%B8%80docker%E5%8F%AA%E8%BF%90%E8%A1%8Cserver) / [②ソースコードデプロイ](../Deployment.md#%E6%96%B9%E5%BC%8F%E4%BA%8C%E6%9C%AC%E5%9C%B0%E6%BA%90%E7%A0%81%E5%8F%AA%E8%BF%90%E8%A1%8Cserver)| `FunASR` 使用時は 2コア4GB、全API利用時は 2コア2GB | - |
| **全モジュールインストール** | 知能対話、マルチユーザー管理、マルチエージェント管理、知能コンソール操作 | 全機能体験、データはデータベースに保存 |[①Docker版](../Deployment_all.md#%E6%96%B9%E5%BC%8F%E4%B8%80docker%E8%BF%90%E8%A1%8C%E5%85%A8%E6%A8%A1%E5%9D%97) / [②ソースコードデプロイ](../Deployment_all.md#%E6%96%B9%E5%BC%8F%E4%BA%8C%E6%9C%AC%E5%9C%B0%E6%BA%90%E7%A0%81%E8%BF%90%E8%A1%8C%E5%85%A8%E6%A8%A1%E5%9D%97) / [③ソースコード自動更新チュートリアル](../dev-ops-integration.md) | `FunASR` 使用時は 4コア8GB、全API利用時は 2コア4GB| [ローカルソース起動動画チュートリアル](https://www.bilibili.com/video/BV1wBJhz4Ewe) |

よくある質問と関連チュートリアルは[こちら](../FAQ.md)を参照してください。

> 💡 注記: 以下は最新コードでデプロイしたテスト用プラットフォームです。必要に応じて焼き込み・テストに利用できます。同時接続 6、データは毎日クリアされます。

```
知能コンソールアドレス: https://2662r3426b.vicp.fun
知能コンソールアドレス (H5): https://2662r3426b.vicp.fun/h5/index.html

サービス試験ツール: https://2662r3426b.vicp.fun/test/
OTA インターフェースアドレス: https://2662r3426b.vicp.fun/xiaozhi/ota/
Websocket インターフェースアドレス: wss://2662r3426b.vicp.fun/xiaozhi/v1/
```

#### 🚩 設定の説明と推奨
> [!Note]
> 本プロジェクトは2種類の設定案を提供します:
>
> 1. `入門・無料設定`: 個人・家庭利用向け。全コンポーネントを無料案で構成し、追加費用は不要です。
>
> 2. `ストリーミング設定`: デモ、研修、同時接続2超などの場面向け。ストリーミング処理技術で応答速度が速く、体験が良好です。
>
> バージョン `0.5.2` 以降、ストリーミング設定に対応。旧バージョン比で応答速度が約 `2.5秒` 改善し、ユーザー体験が大きく向上します。

| モジュール名 | 入門・無料設定 | ストリーミング設定 |
|:---:|:---:|:---:|
| ASR（音声認識） | FunASR（ローカル） | 👍XunfeiStreamASR（訊飛ストリーミング） |
| LLM（大規模言語モデル） | glm-4-flash（智譜） | 👍qwen-flash（Alibaba Bailian） |
| VLLM（視覚言語モデル） | glm-4v-flash（智譜） | 👍qwen3.5-flash（Alibaba Bailian） |
| TTS（音声合成） | EdgeTTS（Microsoft） | 👍HuoshanDoubleStreamTTS（火山ストリーミング） |
| Intent（意図認識） | function_call（関数呼び出し） | function_call（関数呼び出し） |
| Memory（記憶機能） | mem_local_short（ローカル短期記憶） | mem_local_short（ローカル短期記憶） |

各コンポーネントのレイテンシが気になる場合は[小智コンポーネント性能テスト報告](https://github.com/xinnan-tech/xiaozhi-performance-research)を参照し、報告内の試験方法で自身の環境で実測してください。

#### 🔧 テストツール
本プロジェクトはシステム検証とモデル選定のため以下のテストツールを提供します。

| ツール名 | 場所 | 使用方法 | 機能説明 |
|:---:|:---|:---:|:---:|
| 音声インタラクションテストツール | main》digital-human》index.html | `main/digital-human` で `python start.py` を実行後 `http://127.0.0.1:8006/index.html` にアクセス | 音声再生・受信機能を試験し、Python 側の音声処理が正常か検証する |
| モデル応答テストツール | main》xiaozhi-server》performance_tester.py | `python performance_tester.py` を実行 | ASR（音声認識）、LLM（大規模言語モデル）、VLLM（視覚モデル）、TTS（音声合成）の応答速度を試験する |

> 💡 注記: モデル速度の試験時は、キーが設定済みのモデルのみ試験されます。

---

## 機能一覧 ✨
### 実装済み ✅
![全モジュール構成図](../images/deploy2.png)
| 機能モジュール | 説明 |
|:---:|:---|
| コアアーキテクチャ | [MQTT+UDP ゲートウェイ](https://github.com/xinnan-tech/xiaozhi-esp32-server/blob/main/docs/mqtt-gateway-integration.md)、WebSocket、HTTP サーバーを基盤とし、完全なコンソール管理と認証システムを提供する |
| 音声インタラクション | ストリーミング ASR（音声認識）、ストリーミング TTS（音声合成）、VAD（音声活動検出）に対応し、多言語認識と音声処理に対応する |
| 声紋認識 | 複数ユーザーの声紋登録・管理・認識に対応し、ASR と並列処理し、話者 identity をリアルタイム認識して LLM に渡しパーソナライズ応答する |
| 知能対話 | 複数の LLM（大規模言語モデル）に対応し、知能対話を実現する |
| 視覚認識 | 複数の VLLM（視覚大規模モデル）に対応し、マルチモーダルインタラクションを実現する |
| 意図認識 | 外付けの大規模モデル意図認識、大規模モデルの自律的関数呼び出しに対応し、プラグイン式の意図処理機構を提供する |
| 記憶システム | ローカル短期記憶、mem0ai インターフェース記憶、PowerMem 知能記憶に対応し、記憶要約機能を持つ |
| ナレッジベース | RAGFlow ナレッジベースに対応し、大規模モデルが必要性を判断してナレッジベースを参照したうえで回答する |
| ツール呼び出し | クライアント IOT プロトコル、クライアント MCP プロトコル、サーバー MCP プロトコル、MCP アクセスポイントプロトコル、カスタムツール関数に対応する |
| 指令配信 | MQTT プロトコルにより、知能コンソールから ESP32 デバイスへ MCP 指令を配信できる |
| 管理バックエンド | Web 管理画面を提供し、ユーザー管理、システム設定、デバイス管理に対応する。簡体字中国語・繁体字中国語・英語表示に対応する |
| テストツール | 性能テストツール、視覚モデルテストツール、音声インタラクションテストツールを提供する |
| デプロイ対応 | Docker デプロイとローカルデプロイに対応し、完全な設定ファイル管理を提供する |
| プラグインシステム | 機能プラグイン拡張、カスタムプラグイン開発、プラグインホットロードに対応する |

### 開発中 🚧

開発計画の進捗は[こちら](https://github.com/users/xinnan-tech/projects/3)を参照してください。よくある質問と関連チュートリアルは[こちら](../FAQ.md)を参照してください。

ソフトウェア開発者の方は[開発者への公開書簡](../contributor_open_letter.md)も参照してください。参加を歓迎します。

---

## 製品エコシステム 👬
小智はエコシステムです。本製品の利用時は、このエコシステム圏の他の[優良プロジェクト](https://github.com/78/xiaozhi-esp32/blob/main/README_zh.md#%E7%9B%B8%E5%85%B3%E5%BC%80%E6%BA%90%E9%A1%B9%E7%9B%AE)も参照してください。

---

## 対応プラットフォーム / コンポーネント一覧 📋
### LLM 言語モデル

| 使用方式 | 対応プラットフォーム | 無料プラットフォーム |
|:---:|:---:|:---:|
| OpenAI インターフェース呼び出し | Alibaba Bailian、火山引擎、DeepSeek、智譜、Gemini、科大訊飛 | 智譜、Gemini |
| Ollama インターフェース呼び出し | Ollama | - |
| Dify インターフェース呼び出し | Dify | - |
| FastGPT インターフェース呼び出し | FastGPT | - |
| Coze インターフェース呼び出し | Coze | - |
| Xinference インターフェース呼び出し | Xinference | - |
| HomeAssistant インターフェース呼び出し | HomeAssistant | - |

実際、OpenAI インターフェース呼び出しに対応する LLM はいずれも接続利用できます。

---

### VLLM 視覚モデル

| 使用方式 | 対応プラットフォーム | 無料プラットフォーム |
|:---:|:---:|:---:|
| OpenAI インターフェース呼び出し | Alibaba Bailian、智譜 ChatGLMVLLM | 智譜 ChatGLMVLLM |

実際、OpenAI インターフェース呼び出しに対応する VLLM はいずれも接続利用できます。

---

### TTS 音声合成

| 使用方式 | 対応プラットフォーム | 無料プラットフォーム |
|:---:|:---:|:---:|
| インターフェース呼び出し | EdgeTTS、科大訊飛、火山引擎、Tencent Cloud、Alibaba Cloud および Bailian、CosyVoiceSiliconflow、TTS302AI、CozeCnTTS、GizwitsTTS、ACGNTTS、OpenAITTS、灵犀ストリーミングTTS、MinimaxTTS | 灵犀ストリーミングTTS、EdgeTTS、CosyVoiceSiliconflow（一部） |
| ローカルサービス | FishSpeech、GPT_SOVITS_V2、GPT_SOVITS_V3、Index-TTS、PaddleSpeech | Index-TTS、PaddleSpeech、FishSpeech、GPT_SOVITS_V2、GPT_SOVITS_V3 |

---

### VAD 音声活動検出

| 種別 | プラットフォーム名 | 使用方式 | 課金形態 | 備考 |
|:---:|:---------:|:----:|:----:|:--:|
| VAD | SileroVAD | ローカル利用 | 無料 | |

---

### ASR 音声認識

| 使用方式 | 対応プラットフォーム | 無料プラットフォーム |
|:---:|:---:|:---:|
| ローカル利用 | FunASR、SherpaASR | FunASR、SherpaASR |
| インターフェース呼び出し | FunASRServer、火山引擎、科大訊飛、Tencent Cloud、Alibaba Cloud、Baidu Cloud、OpenAI ASR | FunASRServer |

---

### Voiceprint 声紋認識

| 使用方式 | 対応プラットフォーム | 無料プラットフォーム |
|:---:|:---:|:---:|
| ローカル利用 | 3D-Speaker | 3D-Speaker |

---

### Memory 記憶ストレージ

| 種別 | プラットフォーム名 | 使用方式 | 課金形態 | 備考 |
|:------:|:---------------:|:----:|:---------:|:--:|
| Memory | mem0ai | インターフェース呼び出し | 1000回/月枠 | |
| Memory | [powermem](../powermem-integration.md) | ローカル要約 | LLM と DB に依存 | OceanBase オープンソース、知能検索対応 |
| Memory | mem_local_short | ローカル要約 | 無料 | |
| Memory | nomem | 記憶なしモード | 無料 | |

---

### Intent 意図認識

| 種別 | プラットフォーム名 | 使用方式 | 課金形態 | 備考 |
|:------:|:-------------:|:----:|:-------:|:---------------------:|
| Intent | intent_llm | インターフェース呼び出し | LLM 課金に基づく | 大規模モデルで意図を認識し、汎用性が高い |
| Intent | function_call | インターフェース呼び出し | LLM 課金に基づく | 大規模モデルの関数呼び出しで意図を完結し、高速で効果が良い |
| Intent | nointent | 意図なしモード | 無料 | 意図認識を行わず、対話結果を直接返す |

---

### RAG 検索拡張生成

| 種別 | プラットフォーム名 | 使用方式 | 課金形態 | 備考 |
|:------:|:-------------:|:----:|:-------:|:---------------------:|
| Rag | ragflow | インターフェース呼び出し | スライス・分かち書き消費トークンに基づき課金 | RAGFlow の検索拡張生成機能により、より正確な対話応答を提供する |

---

## 謝辞 🙏

| ロゴ | プロジェクト/企業 | 説明 |
|:---:|:---:|:---|
| <img src="../images/logo_bailing.png" width="160"> | [百聆音声対話ロボット](https://github.com/wwbin2017/bailing) | 本プロジェクトは[百聆音声対話ロボット](https://github.com/wwbin2017/bailing)に着想を得て、その基礎の上に実装されています |
| <img src="../images/logo_tenclass.png" width="160"> | [十方融海](https://www.tenclass.com/) | [十方融海](https://www.tenclass.com/)が小智エコシステムの標準通信プロトコル、複数デバイス互換案、高並発場面の実践例を策定し、本プロジェクトに全連鎖の技術文書支援を提供したことに感謝します |
| <img src="../images/logo_xuanfeng.png" width="160"> | [玄鳳科技](https://github.com/Eric0308) | [玄鳳科技](https://github.com/Eric0308)が関数呼び出し枠組み、MCP通信プロトコル、プラグイン化呼び出し機構の実装コードを貢献しました。標準化された指令調度体系と動的拡張能力により、前端デバイス（IoT）の対話効率と機能拡張性を大きく向上させています |
| <img src="../images/logo_junsen.png" width="160"> | [huangjunsen](https://github.com/huangjunsen0406) | [huangjunsen](https://github.com/huangjunsen0406)が`知能コンソールモバイル`モジュールを貢献し、クロスプラットフォームのモバイルデバイスで高効率制御とリアルタイム対話を実現し、モバイル場面での操作利便性と管理効率を大きく向上させました |
| <img src="../images/logo_huiyuan.png" width="160"> | [匯遠設計](http://ui.kwd988.net/) | [匯遠設計](http://ui.kwd988.net/)が本プロジェクトに専門的ビジュアルソリューションを提供し、千社超の企業に奉仕する設計実戦経験で本プロジェクト製品のユーザー体験に力を与えたことに感謝します |
| <img src="../images/logo_qinren.png" width="160"> | [西安勤人信息科技](https://www.029app.com/) | [西安勤人信息科技](https://www.029app.com/)が本プロジェクトの視覚体系を深化させ、複数場面応用での全体設計様式の一致性と拡張性を確保したことに感謝します |
| <img src="../images/logo_contributors.png" width="160"> | [コード貢献者](https://github.com/xinnan-tech/xiaozhi-esp32-server/graphs/contributors) | [すべてのコード貢献者](https://github.com/xinnan-tech/xiaozhi-esp32-server/graphs/contributors)に感謝します。皆さんの尽力がプロジェクトをより堅牢で強力にしています。 |


<a href="https://star-history.com/#xinnan-tech/xiaozhi-esp32-server&Date">

  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=xinnan-tech/xiaozhi-esp32-server&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=xinnan-tech/xiaozhi-esp32-server&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=xinnan-tech/xiaozhi-esp32-server&type=Date" />
  </picture>
</a>
