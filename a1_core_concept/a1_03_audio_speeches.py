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
import asyncio
import base64
import json
from pathlib import Path

import streamlit as st
from openai import OpenAI, AsyncOpenAI

# --------------------------------------------------------------------------------
# UI Utility – 既存 util が呼べない環境でも動くようフォールバック
try:
    from utils import util_00_st as st_utils           # ユーザ独自ユーティリティ
except ModuleNotFoundError:                            # fallback (簡易実装)
    class _Stub:
        @staticmethod
        def init_page(title: str): st.set_page_config(page_title=title)
        @staticmethod
        def init_messages(): pass
    st_utils = _Stub()

# ------------------------------------------------------------------
client = OpenAI()                     # 同期クライアント
a_client = AsyncOpenAI()              # 非同期クライアント（Realtime 用）
DATA_DIR = Path(__file__).parent / "data"
st_utils.init_page("Audio & Speech Demo")

# ------------------------------------------------------------------
# ① Text → Speech
# gpt-4o-mini-tts: GPT-4o miniを搭載したテキスト読み上げモデル
# tts-1:    速度に最適化されたテキスト読み上げモデル
# tts-1-hd: 品質に最適化されたテキスト読み上げモデル
# ------------------------------------------------------------------
def text_to_speech(_: str | None = None) -> None:
    # モデルとテキスト読み込み
    model = st_utils.config_speech_model()
    txt_file = DATA_DIR / "taketori_1.txt"
    if not txt_file.exists():
        st.error(f"{txt_file} が見つかりません")
        return
    text = txt_file.read_text(encoding="utf-8")

    # UI
    voice  = st.selectbox("Voice", ["alloy", "nova", "echo", "onyx", "shimmer"])
    stream = st.checkbox("ストリーミング (chunk 転送)")
    st.write("model = ", model)

    # ボタン押下時のみ音声生成
    if st.button("変換する（text to speech）"):
        st.write("")  # 空行
        with st.spinner("音声生成中..."):
            # 出力ファイル名を方式に応じて設定
            speech_path = DATA_DIR / ("speech_stream.mp3" if stream else "speech.mp3")

            # Streaming API を利用してファイルへ直接書き出し
            with client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=text,
            ) as resp:
                resp.stream_to_file(speech_path)

        # 完了表示とプレイヤー
        st.success("完了")
        st.audio(str(speech_path), format="audio/mp3")

# ------------------------------------------------------------------
# ② Speech → Text
# [Model]
# ------------------------------------------------------------------
def speech_to_text(_: str | None = None) -> None:
    audio_file = DATA_DIR / "speech_stream.mp3"
    # model = st_utils.config_speech_model()
    if not audio_file.exists():
        st.error(f"{audio_file} が見つかりません")
        return

    if st.button("文字起こし・開始 "):

        with audio_file.open("rb") as f:
            with st.spinner("文字起こし中..."):
                tx = client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=f,
                    response_format="text",
                )

    st.code(tx, language="markdown")

# ------------------------------------------------------------------
# ③ Speech → 英語 Text
#
# ------------------------------------------------------------------
def speech_to_transcription(_: str | None = None) -> None:
    audio_file = DATA_DIR / "taketori_1.mp3"
    if not audio_file.exists():
        st.error(f"{audio_file} が見つかりません")
        return

    with audio_file.open("rb") as f:
        with st.spinner("翻訳 (→English) 中..."):
            tx = client.audio.translations.create(
                model="whisper-1",
                file=f,
                response_format="text",
            )
    st.code(tx.text, language="markdown")


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
        sess = await a_client.beta.realtime.transcription_sessions.create(
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


def voice_agent_chunk(binary_wav: bytes) -> bytes:
    """1 round: user audio -> text -> GPT -> TTS -> audio (bytes)"""
    # 1) speech→text
    tx = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=binary_wav,
        response_format="text",
    )
    user_text: str = tx.text

    # 2) LLM 応答
    chat = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "developer", "content": "あなたは親切な旅行ガイドです"},
            {"role": "user", "content": user_text},
        ],
    )
    assistant_text: str = chat.choices[0].message.content

    # 3) text→speech
    voice = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=assistant_text,
    )
    return voice.audio  # bytes (mp3 デフォルト)


# ------------------------------------------------------------------ Streamlit menu
def main() -> None:
    st_utils.init_messages()
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
