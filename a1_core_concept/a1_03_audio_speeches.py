# streamlit run a1_03_audio_speeches.py --server.port=8507
# [Menu] ---------------------------------
# ① Text to Speech:音声生成API
# ② Speech to Text
# ③ 音声翻訳API（Translation）
# ④ RealtimeAPIで音声⇄音声（低遅延対話）
# ⑤「Chained」型 VoiceAgent（制御＋ログ重視）
# --------------------------------------

import os
import sys
import asyncio
import base64
from io import BytesIO
from pathlib import Path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from a0_common_helper.helper import (
    init_page,
    init_messages,
    sanitize_key,
    get_default_messages,
    select_speech_model, select_whisper_model,
)

from openai import OpenAI, AsyncOpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,  # ← union 型
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
    st.write("tts-1 or tts-1-hd or gpt-4o-mini-tts のいずれかを選んで")
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
from openai import InternalServerError
import time, random

def safe_transcribe(file_handle, model="whisper-1"):
    delay = 1
    for _ in range(4):          # 最大 4 回
        try:

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
# ④ Realtime API (β)  –  SDK v1.86.0 対応版
# ------------------------------------------------------------------
# ChatCompletionSystemMessageParamで返す。
def build_messages(user_text: str) -> list[ChatCompletionMessageParam]:
    """ChatCompletion 用のメッセージを生成（型安全版）"""
    return [
        ChatCompletionSystemMessageParam(
            role="system",
            content=(
                "You are a friendly Japanese voice assistant. "
                "Respond in concise Japanese (≤2 sentences)."
            ),
        ),
        ChatCompletionUserMessageParam(
            role="user",
            content=user_text,
        ),
    ]

def realtime_api(_: str | None = None) -> None:
    try:
        import pyaudio, simpleaudio  # noqa: F401
    except ImportError as e:
        st.error(f"{e}. `pip install pyaudio simpleaudio` が必要です")
        return

    async def run_realtime() -> None:
        async_client = AsyncOpenAI()

        # --- Realtime WebSocket 接続 ---------------------------------
        async with async_client.beta.realtime.connect(
            model="gpt-4o-realtime-preview",
            # extra_query={"intent": "conversation",
        ) as conn:

            # --- セッション初期化（VAD + Whisper モデル指定） ----------
            await conn.session.update(
                session={
                    "voice": "alloy",
                    "input_audio_format": "pcm16",
                    "input_audio_transcription": {"model": "gpt-4o-transcribe"},
                    "turn_detection": {"type": "server_vad"},
                }
            )

            # --- マイク設定 -------------------------------------------
            import pyaudio, simpleaudio
            pa = pyaudio.PyAudio()
            stream = pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16_000,
                input=True,
                frames_per_buffer=1024,
            )

            # --- 並列タスク -------------------------------------------
            async def sender():
                while True:
                    pcm = stream.read(1024, exception_on_overflow=False)
                    await conn.input_audio_buffer.append(
                        audio=base64.b64encode(pcm).decode()
                    )

            async def receiver():
                async for event in conn:
                    if event.type == "response.audio.delta":
                        wav = base64.b64decode(event.audio)
                        simpleaudio.play_buffer(wav, 1, 2, 24_000)
                    elif event.type == "response.done":
                        break  # 会話終了

            await asyncio.gather(sender(), receiver())

    st.write("▶ **Start conversation** (マイクが ON になります)")
    if st.button("Run Realtime Demo"):
        asyncio.run(run_realtime())

# =================================================================
# ⑤ 「Chained」VoiceAgent
# =================================================================
# 概要
# Streamlit ウィジェット st.file_uploader で最大 25 MB の WAV/MP3 を受け取り、
# 音声バイト列を voice_agent_chunk() に渡して処理結果（MP3 バイト列）を
# st.audio で再生する UI レイヤ です。ブラウザ側での可搬性と即時プレビューを実現します。
# ========================
# IPO
# 区分	        内容
# I (Input)	    ユーザー操作：st.file_uploader でアップロードされた WAV/MP3 ファイル（≤ 25 MB）
# P (Process)	1. UI 表示（タイトル等）
#               2. ファイル存在チェック（if not uploaded: return）
#               3. uploaded.read() でバイト列取得
#               4. voice_agent_chunk() 呼び出し
# O (Output)	ブラウザ出力：st.audio(resp_audio, format="audio/mp3") による音声プレーヤー埋め込み
# ========================

def chained_voice_agent(_: str | None = None) -> None:
    st.write("### 1 回発話→応答のデモ")
    uploaded = st.file_uploader("あなたの音声 (WAV/MP3 ≤25 MB)", type=["wav", "mp3"])
    if not uploaded:
        return

    resp_audio = voice_agent_chunk(uploaded.read())
    st.audio(resp_audio, format="audio/mp3")

# ========================
# 概要
# 1 本の音声バイト列を入力とし、Speech-to-Text → Chat Completion → Text-to-Speech を順に実行して MP3 バイト列を返します。主要コンポーネントは以下の通り。
#
# ステップ	API / モデル	主な役割
# ① STT	audio.transcriptions.create() + Whisper 系（whisper-1, gpt-4o-transcribe など）で日本語音声→テキスト化
# ② Chat	chat.completions.create() + gpt-4o-mini で対話応答生成
# ③ TTS	audio.speech.create() + tts-1 でテキスト→音声変換
# IPO
# 区分	        内容
# I (Input)	    binary_wav: bytes – WAV/MP3 の生バイト列（BytesIO で STT に渡す）
# P (Process)	1. 音声認識: client.audio.transcriptions.create(model=audio_model)
#　　　　　　　　　　　で Whisper 文字起こし
#               2. プロンプト生成: ChatCompletionSystemMessageParamと
#               　　ChatCompletionUserMessageParam でメッセージ配列構築
#               3. 対話生成: client.chat.completions.create(model="gpt-4o-mini") で応答テキスト取得
#               4. TTS: client.audio.speech.create(model="tts-1") で MP3 バイト列生成
# O (Output)	bytes – エンコーディング済み MP3（呼び出し元で st.audio 再生）

# voice_agent_chunk ---------------------------------------------------
def voice_agent_chunk(binary_wav: bytes) -> bytes:
    # ① 音声 → 文字起こし（Whisper 系モデル）
    audio_model = select_whisper_model()                      # whisper-1 / gpt-4o-transcribe 等
    res = client.audio.transcriptions.create(
        model=audio_model,
        file=BytesIO(binary_wav),
        response_format="text",
    )
    user_text = getattr(res, "output_text", str(res))

    # ② ChatCompletion 用メッセージを構築
    chat_messages: list[ChatCompletionMessageParam] = [
        ChatCompletionSystemMessageParam(
            role="system",
            content=(
                "You are a friendly Japanese voice assistant. "
                "Respond in concise Japanese (≤2 sentences)."
            ),
        ),
        ChatCompletionUserMessageParam(role="user", content=user_text),
    ]

    # ③ テキスト生成（Chat 用モデルを指定）
    chat_model = "gpt-4o-mini"                                # チャットモデル
    chat_resp = client.chat.completions.create(
        model=chat_model,
        messages=chat_messages,
    )
    assistant_text = chat_resp.choices[0].message.content

    # ④ TTS で音声化
    tts_resp = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=assistant_text,
    )
    return tts_resp.content

# ------------------------------------------------------------------ Streamlit menu
def main() -> None:
    init_messages("speech & text")
    demos = {
        "1_text_to_speech": text_to_speech,
        "2_speech_to_text": speech_to_text,
        "3_speech_to_transcription": speech_to_transcription,
        "4_realtime_api": realtime_api,
        "5_chained_voice_agent": chained_voice_agent,
    }
    choice = st.sidebar.radio("デモを選択してください", list(demos.keys()))
    demos[choice](choice)


if __name__ == "__main__":
    main()

# streamlit run a1_03_audio_speeches.py --server.port=8507
