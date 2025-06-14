### Audio & Speeches
| 関数名                   | API                     | 推奨モデル名 |
|--------------------------|-------------------------|--------------|
| text_to_speech           | audio.speech            | tts-1, tts-1-hd, gpt-4o-mini-tts |
| speech_to_text           | audio.transcriptions    | whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe |
| speech_to_transcription  | audio.transcriptions    | whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe |
| realtime_api             | beta.realtime           | gpt-4o-realtime-preview, gpt-4o-mini-realtime-preview |
| voice_agent_chunk        | audio.transcriptions    | whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe |
| voice_agent_chunk        | chat.completions        | gpt-4o-mini, gpt-4o |
| voice_agent_chunk        | audio.speech            | tts-1, tts-1-hd, gpt-4o-mini-tts |
## ① Text-to-Speech（audio.speech API）

### 概要
テキスト（≤ 4 096 文字）を音声ファイル（MP3 ほか）に変換するエンドポイント。高速な **`tts-1`**、高品質の **`tts-1-hd`**、バランス型 **`gpt-4o-mini-tts`** が推奨モデル。:contentReference[oaicite:0]{index=0}

### INPUT
- テキスト文字列
- パラメータ: `model`, `voice`, `format`, `speed` ほか:contentReference[oaicite:1]{index=1}

### Process
1. `client.audio.speech.with_streaming_response.create()` でリクエスト送信
2. バイトストリームを受信し、MP3 ファイルへ保存
3. Streamlit で進捗を表示しつつ UI に音声プレーヤーを埋め込み

### OUTPUT
- 出力音声ファイル（例 `*.mp3`）
- 成功メッセージ＋ブラウザでの再生プレーヤー

---

## ② Speech-to-Text（audio.transcriptions API）

### 概要
アップロードされた音声を文字起こし。高精度 **`whisper-1`**、多言語対応 **`gpt-4o-transcribe`**、低コスト **`gpt-4o-mini-transcribe`** が推奨。:contentReference[oaicite:2]{index=2}

### INPUT
- 音声ファイル（flac / mp3 / wav…，≤ 25 MB）
- パラメータ: `model`, `response_format` (`text`, `json` など)

### Process
1. `client.audio.transcriptions.create()` で音声→テキスト
2. エラー時は指数バックオフで再試行（`safe_transcribe`）
3. 結果を Streamlit セッションに保存し UI へ表示

### OUTPUT
- 文字列 or JSON（文字起こし結果）をブラウザ出力

---

## ③ 音声翻訳（audio.translations API）

### 概要
音声→英語翻訳専用エンドポイント。現在の公開モデルは **`whisper-1`**；今後 GPT-4o 系翻訳モデルが追加予定。:contentReference[oaicite:3]{index=3}

### INPUT
- 非英語音声ファイル（≤ 25 MB）
- パラメータ: `model`, `prompt`, `temperature` など

### Process
1. `client.audio.translations.create()` を呼び出し
2. Whisper が逐語訳→英訳テキストを生成
3. 必要に応じ post-processing（句読点補正、フォーマット変換）

### OUTPUT
- 英訳テキスト（`text` / `srt` / `vtt` / `json`）

---

## ④ Realtime 音声⇄音声（beta.realtime WebSocket）

### 概要
音声ストリームを WebSocket で送信し、サーバ VAD＋GPT-4o で即応答を返す低遅延対話 API。推奨モデルは **`gpt-4o-realtime-preview`** と **`gpt-4o-mini-realtime-preview`**。:contentReference[oaicite:4]{index=4}

### INPUT
- リアルタイム PCM16/24 kHz チャンク（Base64）
- `session.update()` 用パラメータ（`voice`, `turn_detection` など）

### Process
1. `async_client.beta.realtime.connect()` でソケット確立
2. `input_audio_buffer.append()` で音声送信
3. `response.audio.delta`／`response.done` イベントを受信し再生
4. VAD (`server_vad`) がターンを自動分離

### OUTPUT
- ストリーミング音声応答（PCM→再生 API へ）
- `response.text.delta/done` で文字起こしも取得可能

---

## ⑤ Chained VoiceAgent

### 概要
アップロード音声を **STT → ChatGPT → TTS** の 3 段パイプラインで処理し、応答音声を返す統合エージェント。会話生成モデルに **`gpt-4o-mini`** を使い、TTS は **`tts-1`**。:contentReference[oaicite:5]{index=5}

### INPUT
- `binary_wav: bytes`（ユーザー音声）

### Process
1. **STT**: `audio.transcriptions.create()` → `user_text` 生成
2. **Prompt 構築**: system / user メッセージを整形
3. **Chat**: `chat.completions.create(model="gpt-4o-mini")` で回答取得:contentReference[oaicite:6]{index=6}
4. **TTS**: `audio.speech.create(model="tts-1")` で音声合成
5. ブラウザへ MP3 ストリームを返却

### OUTPUT
- MP3 バイト列（Streamlit `st.audio` で再生）

---

## 補足・指摘事項

* **モデル指定の一元管理**
  環境変数や設定ファイルにモデル名をまとめ、将来のモデル置換（例：`gpt-4.1-mini`🡒`gpt-4o-mini`）を容易にすべき。:contentReference[oaicite:7]{index=7}
* **25 MB 制限**
  `audio.*` 系 API はファイル上限 25 MB。長時間音声はクライアント側で分割が必要。:contentReference[oaicite:8]{index=8}
* **リアルタイム権限**
  Realtime API は招待制ベータ。API キーにアクセス権が無い場合 401 エラーとなるので注意。
* **データ取り扱い**
  API に送ったデータは既定で学習に使用されないが、ポリシー変更に備えプライバシー告知を行うと良い。:contentReference[oaicite:10]{index=10}
* **コスト最適化**
  音声生成は `tts-1` が高速・低コスト、`tts-1-hd` はリッチ品質。ユースケースで使い分ける。:contentReference[oaicite:11]{index=11}
