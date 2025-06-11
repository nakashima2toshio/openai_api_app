# streamlit run a1_03_audio_speeches.py --server.port=8507
# [Menu] ---------------------------------
# ① Text to Speech:音声生成API
# ② Speech to Text
# ③ 音声翻訳API（Translation）
# ④ RealtimeAPIで音声⇄音声（低遅延対話）
# ⑤「Chained」型 VoiceAgent（制御＋ログ重視）
# --------------------------------------
# ① Text to Speech:音声生成API
# --------------------------------------
# （1）APIの仕様、役割、特徴
# URL: POST https://api.openai.com/v1/audio/speech
# 役割: テキストから音声を生成する（Text to Speech）
# 特徴:
# ・最大4096文字までのテキストを音声化。
# ・対応モデル：tts-1, tts-1-hd, gpt-4o-mini-tts
# ・音声の種類（voice）：alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse
# ・音声速度や音声フォーマットの指定可能（mp3, opus, aac, flac, wav, pcm）。
# ・オプションで音声に詳細な指示（instructions）を与えることが可能（モデルに制約あり）
# --------------------------------------
# ② Speech to Text
# --------------------------------------
#
# --------------------------------------
# ③ 音声翻訳API（Translation）
# --------------------------------------
# （1）APIの仕様、役割、特徴
# URL: POST https://api.openai.com/v1/audio/translations
# 役割: 入力した音声を英語に翻訳し、テキストに変換（Speech Translation）
# --------------------------------------
# 特徴
# --------------------------------------
# ・対応モデル：whisper-1（Whisper V2をベースにしたモデル）
# ・音声ファイルフォーマット：flac, mp3, mp4, mpeg, mpg, m4a, ogg, wav, webm
# ・応答形式の指定可能（json, text, srt, verbose_json, vtt）
# ・promptにより翻訳スタイルを誘導可能
# ・温度（temperature）で翻訳結果のランダム性調整可能
# --------------------------------------
# ④ RealtimeAPIで音声⇄音声（低遅延対話）
# --------------------------------------
# ポイント
# ・トークン を取得 →client.beta.realtime.transcription_sessions.create()
# ・WebSocket へ接続し JSON イベントを送受信
# ・PCM16kHz/24kHz の Base64 チャンクを input_audio_buffer.append で送る
# 最小構成例（送信のみ）:
# --------------------------------------
# ⑤「Chained」型 VoiceAgent（制御＋ログ重視）
# --------------------------------------
# ・マイク → transcribe
# ・テキストを GPT‑4o へプロンプト
# ・応答テキストを TTS で音声化
# ・スピーカーへ
# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
import os
import sys
import asyncio
import base64
import json
from io import BytesIO
from pathlib import Path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
from a0_common_helper.helper import (
    init_page,
    init_messages,
    select_model,
    sanitize_key,
    get_default_messages,
    extract_text_from_response, append_user_message,
    select_speech_model, select_whisper_model,
    parse_translation_response,
)
from openai import OpenAI, AsyncOpenAI
from openai.types.responses import (
    EasyInputMessageParam,      # 基本の入力メッセージ
    ResponseInputTextParam,     # 入力テキスト
    ResponseInputImageParam,    # 入力画像
    ResponseFormatTextJSONSchemaConfigParam,  # Structured output 用
    ResponseTextConfigParam,    # Structured output 用
    FunctionToolParam,          # 関数呼び出しツール
    FileSearchToolParam,        # ファイル検索ツール
    WebSearchToolParam,         # Web 検索ツール
    ComputerToolParam,          #
    Response
)
# --- インポート直後に１度だけ実行する ---
import streamlit as st
st.set_page_config(
    page_title="ChatGPT API",
    page_icon="2025-5 Nakashima"
)
# ------------------------------------------------------------------
client = OpenAI()                       # 同期クライアント
asyn_client = AsyncOpenAI()             # 非同期クライアント（Realtime 用）

BASE_DIR = Path(__file__).resolve().parent.parent      # resolve() で実体パス
DATA_DIR = BASE_DIR / "data"
init_page("Audio & Speech Demo")

# [Menu]--------------------------------------------------------------
# 基本：
# パイプライン	モデル	                理由
# 01 音声入力	    whisper-turbo	        0.3 秒以内の低遅延·低コスト
# 02 会話生成	    GPT-4o mini(stream)     十分高精度・革命的コスパ
# 03 音声出力	    tts-1(chunk_size≈150字)	最短 TTFB；発熱の少ない M-series Mac でも安定
# 04 ターン検出	    server-VAD Silence      自動判定で自然な割り込み体験
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# ① Text → Speech
# gpt-4o-mini-tts: GPT-4o miniを搭載したテキスト読み上げモデル
# tts-1:    速度に最適化されたテキスト読み上げモデル
# tts-1-hd: 品質に最適化されたテキスト読み上げモデル
# ------------------------------------------------------------------
def text_to_speech(_: str | None = None) -> None:
    from pathlib import Path

    # --- ① txt ファイル一覧を取得 -------------------------------------
    txt_files = sorted(DATA_DIR.glob("*.txt"))  # → Path のリスト
    if not txt_files:  # 見つからない場合
        st.error(f"{DATA_DIR} に .txt がありません")
        st.stop()

    # --- ② セレクトボックスでファイル名を選択 ---------------------------
    txt_name = st.selectbox(
        "テキストファイルを選択してください",
        [f.name for f in txt_files]  # ラベル = ファイル名
    )  # docs: st.selectbox :contentReference[oaicite:0]{index=0}

    txt_file = DATA_DIR / txt_name  # ← これが選択結果
    text = txt_file.read_text(encoding="utf-8")  # 以降は従来ロジック

    # UI
    model = select_speech_model()
    voice  = st.selectbox("Voice", ["alloy", "nova", "echo", "onyx", "shimmer"])
    stream = st.checkbox("ストリーミング (chunk 転送)")
    st.write("model = ", model)

    # ボタン押下で TTS --------------------------------------
    if st.button("変換する（text → speech）"):
        with st.spinner("音声生成中..."):
            # ベース名 = 拡張子を除いた txt_file 名
            base       = Path(txt_name).stem  # pathlib で拡張子除去 :contentReference[oaicite:1]{index=1}
            speech_path = (DATA_DIR / f"{base}_stream.mp3"
                           if stream else DATA_DIR / f"{base}.mp3")

            # Streaming API で MP3 出力
            with client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=text,
            ) as resp:
                resp.stream_to_file(speech_path)  # 保存先を上記パスに

        st.success("完了")
        st.audio(str(speech_path), format="audio/mp3")

# ------------------------------------------------------------------
# ② Speech → Text
# [Model]
# ------------------------------------------------------------------
def speech_to_text(_: str | None = None) -> None:
    mp3_files = sorted(DATA_DIR.glob("*.mp3"))
    if not mp3_files:
        st.error("MP3 がありません"); st.stop()

    # print([f.name for f in mp3_files])
    mp3_name = st.selectbox("MP3ファイル", [f.name for f in mp3_files])
    mp3_file = DATA_DIR / mp3_name
    model    = select_whisper_model()

    # セッション保存キー
    key_tx = f"tx_{mp3_name}"

    if st.button("文字起こし・開始"):
        with mp3_file.open("rb") as f, st.spinner("文字起こし中..."):
            st.session_state[key_tx] = client.audio.transcriptions.create(
                model=model, file=f, response_format="text"
            )

    # 結果がセッションにあれば表示
    if key_tx in st.session_state:
        st.write(st.session_state[key_tx], language="markdown")

# ------------------------------------------------------------------
# ③ Speech → 英語 Text  ★ボタン押下で進行版
# ------------------------------------------------------------------
from openai import APITimeoutError, InternalServerError
import time, random
from openai import OpenAI, AsyncOpenAI

def safe_transcribe(file_handle, model="whisper-1"):
    delay = 1
    for _ in range(4):          # 最大 4 回
        try:
            client = OpenAI()
            return client.audio.transcriptions.create(
                model=model, file=file_handle, response_format="text"
            )
        except InternalServerError:
            time.sleep(delay)
            delay *= 2 + random.random()
    raise
# a1_03_audio_speeches.py --------------------------------------------
def speech_to_transcription(_: str | None = None) -> None:
    st.code = "今は、whisper系だけ選択してください。"
    model      = select_whisper_model()
    st.write("model=", model)

    mp3_files = sorted(DATA_DIR.glob("*.mp3"))
    if not mp3_files:
        st.error("MP3 がありません")
        st.stop()

    st.write("speech_stream.mp3を選んでね。")
    mp3_name = st.selectbox("MP3ファイル", [f.name for f in mp3_files])
    mp3_file = DATA_DIR / mp3_name
    if not mp3_file.exists():
        st.error(f"{mp3_file} が見つかりません"); return

    key_tx = f"tx_{mp3_name}"

    if st.button("文字起こし・開始"):
        with mp3_file.open("rb") as f, st.spinner("文字起こし中..."):
            try:
                st.session_state[key_tx] = safe_transcribe(f, model)
            except Exception as e:
                st.error(f"API 失敗: {e}")
                st.stop()

    if key_tx in st.session_state:
        st.write(st.session_state[key_tx])  # ← 警告解消

# ------------------------------------------------------------------
# ④ Realtime API (β)
# ------------------------------------------------------------------
def realtime_api(_: str | None = None) -> None:
    try:
        import pyaudio, websockets  # noqa: F401
    except ImportError as e:
        st.error(f"{e}. `pip install pyaudio websockets` が必要です")
        return

    async def run_realtime() -> None:
        sess = await asyn_client.realtime.transcription_sessions.create(
            input_audio_format="pcm16",
            input_audio_transcription={"model": "gpt-4o-transcribe"},
        )
        token = sess.client_secret
        ws_url = (
            "wss://api.openai.com/v1/realtime"
            "?model=gpt-4o-realtime-preview&intent=conversation"
        )

        import pyaudio, websockets  # local scope
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024,
        )

        async with websockets.connect(
            ws_url,
            extra_headers={
                "Authorization": f"Bearer {token}",
                "OpenAI-Beta": "realtime=v1",
            },
        ) as ws:

            # handshake
            await ws.send(
                json.dumps(
                    {"type": "session.update", "session": {"turn_detection": {"type": "server_vad"}}}
                )
            )

            async def sender():
                while True:
                    data = stream.read(1024, exception_on_overflow=False)
                    await ws.send(
                        json.dumps(
                            {
                                "type": "input_audio_buffer.append",
                                "audio": base64.b64encode(data).decode(),
                            }
                        )
                    )

            async def receiver():
                import simpleaudio  # 任意再生ライブラリ
                async for msg in ws:
                    evt = json.loads(msg)
                    if evt.get("type") == "response.audio.delta":
                        wav = base64.b64decode(evt["audio"])
                        simpleaudio.play_buffer(wav, 1, 2, 24000)

            await asyncio.gather(sender(), receiver())

    st.write("▶ **Start conversation** (マイクが ON になります)")
    if st.button("Run Realtime Demo"):
        asyncio.run(run_realtime())

# ------------------------------------------------------------------
# ⑤ 「Chained」VoiceAgent
# ------------------------------------------------------------------
def chained_voice_agent(_: str | None = None) -> None:
    st.write("### 1 回発話→応答のデモ")
    uploaded = st.file_uploader("あなたの音声 (WAV/MP3 ≤25 MB)", type=["wav", "mp3"])
    if not uploaded:
        return

    resp_audio = voice_agent_chunk(uploaded.read())
    st.audio(resp_audio, format="audio/mp3")


# voice_agent_chunk ---------------------------------------------------
def voice_agent_chunk(binary_wav: bytes) -> bytes:
    audio_model = select_whisper_model()
    res = client.audio.transcriptions.create(
        model=audio_model,
        file=BytesIO(binary_wav),
        response_format="text",
    )
    user_text = getattr(res, "output_text", str(res))

    messages = get_default_messages()
    messages.append(
        EasyInputMessageParam(
            role="user",
            content=[
                ResponseInputTextParam(type="input_text", text=user_text),
            ],
        ),
    )
    chat = client.chat.completions.create(
        model=audio_model,
        messages=messages,
    )
    assistant_text = chat.choices[0].message.content

    tts = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=assistant_text,
    )
    return tts.content

# ------------------------------------------------------------------ Streamlit menu
def main() -> None:
    init_messages("speech & text")
    demos = {
        "1_text_to_speech": text_to_speech,
        "2_speech_to_text": speech_to_text,
        "3_speech_to_transcription": speech_to_transcription,
        "4_realtime_api": realtime_api,
        "5_voice_agent_chunk": chained_voice_agent,
    }
    choice = st.sidebar.radio("デモを選択してください", list(demos.keys()))
    demos[choice](choice)


if __name__ == "__main__":
    main()

# streamlit run a1_03_audio_speeches.py --server.port=8507
