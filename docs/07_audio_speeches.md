#### 07_audio_speeches.md
#### (1) タスク別表
| タスク | Python 呼び出し例 (`openai‑python v1`) | 典型　モデル | ストリーミング | 主な用途 |
| --- | --- | --- | --- | --- |
| **Text → Speech** | `client.audio.speech.create(...)`<br>`client.audio.speech.with_streaming_response.create(...)` | `gpt‑4o‑mini‑tts`, `tts‑1`, `tts‑1‑hd` | **出力のみ**（chunk 転送） | ナレーション、読み上げ、チャット応答の音声化 |
| **Speech → Text** | `client.audio.transcriptions.create(...)` | `gpt‑4o‑transcribe`, `gpt‑4o‑mini‑transcribe`, `whisper‑1` | **出力のみ** <br> `stream=True` で逐次取得（`whisper‑1` は非対応） | 音声メモ書き起こし、多言語議事録作成 |
| **Speech → 英語 Text** | `client.audio.translations.create(...)` | `whisper‑1` | なし | 多言語 → 英語の翻訳字幕 |
| **音声双方向（低遅延）** | `openai.beta.realtime.*` で WebSocket セッション | `gpt‑4o‑realtime‑preview`, `gpt‑4o‑mini‑realtime‑preview` | **入出力ともリアルタイム** | 音声対話エージェント、インタラクティブ検索 |
| **音声を含むチャット補完** | `client.chat.completions.create(modalities=["text", "audio"], ...)` | `gpt‑4o‑audio‑preview`, `gpt‑4o‑mini‑audio‑preview` | **出力のみ** | 既存チャット UI に音声入出力を追加 |

#### (2) Voice Agents の 2 方式 <!-- 3. Voice Agents の 2 方式 -->
| 方式 | 流れ | 強み | 向くユースケース |
| --- | --- | --- | --- |
| Speech‑to‑Speech（S2S） | Audio → **Realtime API** → Audio | 最小遅延・感情/抑揚まで直接理解 | 英会話チュータ、対話ボット、探索系検索 |
| Chained | Audio → STT → LLM → TTS | 台本・関数呼び出しを完全に制御、ログ取得容易 | コールセンター自動応答、FAQ、社内ボイス UI |

#### (3) Realtime API（双方向ストリーミング）
##### 特徴と用途
・WebSocketベースで音声データを双方向にストリーミング。
・マルチモーダル／音声⇄音声を１つのモデル呼び出しで完結（GPT‑4o Realtimeモデル）。
・低レイテンシかつ自然な対話感を重視したボイスエージェント向け。
・割り込み検知や関数呼び出しとも組み合わせ可能で、対話中の操作をリアルタイムに実行できる。

##### 利用シナリオ
・インタラクティブなカスタマーサポートや言語学習アプリ
・音声による命令から即座にアプリケーションを操作するユースケース
・既存のテキストエージェントにリアルタイム音声を組み込みたい場合

#### (4) Audio API vs. Realtime API ― 違いを一言で <!-- 4. Audio API vs. Realtime API ― 違いを一言で -->
| 観点 | Audio API（`/audio/`） | Realtime API |
| --- | --- | --- |
| 接続方式 | 単発 HTTP リクエスト | 持続的 WebSocket／WebRTC |
| モダリティ | 単機能（TTS / STT / 翻訳） | 多機能（音声⇄テキスト ± 視覚・関数） |
| 音声の流れ | 入力 or 出力いずれか片方向<br>（ストリームは出力のみ） | 入出力とも双方向ストリーム |
| レイテンシ | 数百 ms ～ 秒 | 数十 ms クラス |
| 実装難度 | 低（REST + ファイル/バイト列） | 中～高（ソケット管理・バッファリング） |
| 使い分け | 音声化・書き起こしなど **処理単発** | **会話主体** のインタラクティブ体験 |

#### (5) 選択ガイド <!-- 5. 選択ガイド -->
| ニーズ / 条件 | 推奨 API |
| --- | --- |
| リアルタイム会話が最優先 | **Realtime API**（Speech‑to‑Speech） |
| 既存テキスト中心アプリに音声 I/O を追加 | **Chat Completions** + `modalities=["text","audio"]`（audio‑preview モデル） |
| 書き起こしや TTS など 1 機能だけ必要 | **Audio API** の専用エンドポイント（`audio/speech`, `audio/transcriptions`, など） |
| 台本を完全に制御したいボイスボット | **Chained** アーキテクチャ（STT → LLM → TTS） |

