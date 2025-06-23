# helper_old.py
import re
import time
import streamlit as st
from openai import OpenAI

# -----------------------------------
# Responses API で利用する型 (openai-python v1)
# -----------------------------------
from openai.types.responses import EasyInputMessageParam, ResponseInputTextParam, ResponseInputImageParam, \
    ResponseTextConfigParam, ResponseFormatTextJSONSchemaConfigParam, FunctionToolParam, FileSearchToolParam, \
    ComputerToolParam

# -----------------------------------------------
# chat completions用　2025-06-11 将来的に非推奨
# -----------------------------------------------
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
    # ChatCompletionMessageParam,
    Response
)
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,  # ← union 型
)
chat_completions_system_text = 'You are a helpful Japanese voice assistant.'
def build_user_messages(user_text: str) -> list[ChatCompletionMessageParam]:
    return [
        ChatCompletionSystemMessageParam(
            role="system",
            content=chat_completions_system_text
        ),
        ChatCompletionUserMessageParam(
            role="user",
            content=user_text
        ),
    ]

# --------------------------------------------------
# デフォルトプロンプト　responses-API（例）ソフトウェア開発用
# --------------------------------------------------
developer_text = (
    "You are a strong developer and good at teaching software developer professionals "
    "please provide an up-to-date, informed overview of the API by function, then show "
    "cookbook programs for each, and explain the API options."
    "あなたは強力な開発者でありソフトウェア開発者の専門家に教えるのが得意です。"
    "OpenAIのAPIを機能別に最新かつ詳細に説明してください。"
    "それぞれのAPIのサンプルプログラムを示しAPIのオプションについて説明してください。"
)
user_text = (
    "Organize and identify the problem and list the issues. "
    "Then, provide a solution procedure for the issues you have organized and identified, "
    "and solve the problems/issues according to the solution procedures."
    "不具合、問題を特定し、整理して箇条書きで列挙・説明してください。"
    "次に、整理・特定した問題点の解決手順を示しなさい。"
    "次に、解決手順に従って問題・課題を解決してください。"
)
assistant_text = "OpenAIのAPIを使用するには、公式openaiライブラリが便利です。回答は日本語で"


def get_default_messages() -> list[EasyInputMessageParam]:

    return [
    EasyInputMessageParam(role="developer", content=developer_text),
    EasyInputMessageParam(role="user",      content=user_text),
    EasyInputMessageParam(role="assistant", content=assistant_text),
]

def append_user_message(append_text, image_url=None):
    return [
    EasyInputMessageParam(role="developer", content=developer_text),
    EasyInputMessageParam(role="user",      content=user_text),
    EasyInputMessageParam(role="assistant", content=assistant_text),
    EasyInputMessageParam(role="user", content=append_text),
]

def append_developer_message(append_text):
    return [
    EasyInputMessageParam(role="developer", content=developer_text),
    EasyInputMessageParam(role="user",      content=user_text),
    EasyInputMessageParam(role="assistant", content=assistant_text),
    EasyInputMessageParam(role="developer", content=append_text),
]

def append_assistant_message(append_text):
    return [
        EasyInputMessageParam(role="developer", content=developer_text),
        EasyInputMessageParam(role="user", content=user_text),
        EasyInputMessageParam(role="assistant", content=assistant_text),
        EasyInputMessageParam(role="assistant", content=append_text),
    ]

# ------------------------------------------
# https://github.com/openai/tiktoken/blob/main/README.md
# !pip install tiktoken  # Byte pair encoding
# pip install --upgrade tiktoken
# ------------------------------------------
# OpenAI APIで使える各モデルの「コンテキストウィンドウ」
# （入力＋出力トークン合計の上限）はモデルにより大きく異なります。
# トークン数を誤ると 400 エラー／高コストにつながるため、
# 公式トークナイザ tiktoken で事前に文字列を計測・切り詰める実装が実務では必須です。
# ------------------------------------------
# 最新モデルのトークン上限（2025-06 時点）
# モデル名	                        コンテキスト上限
# GPT-4.1 / 4.1-mini / 4.1-nano	    1 000 000 tokens
# reuters.com
# GPT-4o （テキスト・マルチモーダル）	128 000 tokens
# ------------------------------------------
import tiktoken
from typing import List

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    # ------------------------------------------
    # Return the number of tokens `text` occupies for the specified OpenAI model.
    # ------------------------------------------
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def tail_from_tokens(text: str, max_tokens: int, model: str = "gpt-4o") -> str:
    # ------------------------------------------
    # Return the last `max_tokens` tokens of `text` as a decoded string.
    # If the text is shorter, the original text is returned unchanged.
    # ------------------------------------------
    enc = tiktoken.encoding_for_model(model)
    tokens: List[int] = enc.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return enc.decode(tokens[-max_tokens:])

# --------------------------------------------------
# ユーティリティ : Streamlit key 用に安全な文字列へ変換
# 英数・アンダースコア以外を "_" へ置換
# --------------------------------------------------
def sanitize_key(name: str) -> str:
    return re.sub(r'[^0-9a-zA-Z_]', '_', name).lower()

# --------------------------------------------------
# Streamlit: 共通ヘルパ
# --------------------------------------------------
def init_page(init_text) -> None:
    # ページ共通ヘッダ
    st.header(init_text)
    st.sidebar.title("メニュー: Tools")

# --------------------------------------------------
# ページ固有の「会話履歴クリア」ボタンと初期履歴設定
def init_messages(demo_name: str = "") -> None:
    safe = sanitize_key(demo_name)
    button_key = f"clear_{safe}"

    messages = get_default_messages()
    if st.sidebar.button("会話履歴のクリア", key=button_key) or "message_history" not in st.session_state:
        st.session_state.message_history = messages

# --------------------------------------------------
def select_model(demo_name: str = "設定") -> str:
    safe = sanitize_key(demo_name)
    models = [
        "gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-4o-mini",
        "gpt-4o-audio-preview", "gpt-4o-mini-audio-preview",
        "o3-mini", "o4-mini", "o1-mini", "o4", "o3", "o1",
    ]
    return st.sidebar.radio("Choose a model:", models, key=f"model_{safe}")

# --------------------------------------------------
def select_speech_model(demo_name: str = "speech_model") -> str:
    safe = sanitize_key(demo_name)
    models = [
        "gpt-4o-mini-tts", "tts-1", "tts-1-hd",
        "gpt-4o-audio-preview", "gpt-4o-mini-audio-preview",
        "o3-mini", "o4-mini",
    ]
    return st.sidebar.radio("Choose a model:", models, key=f"model_{safe}")

# helper_old.py -----------------------------------------------------------
def select_whisper_model(key: str = "whisper_model") -> str:
    # Whisper / Transcribe / Translate で使えるモデルだけ
    models = ["whisper-1", "gpt-4o-transcribe", "gpt-4o-mini-transcribe"]
    return st.sidebar.radio("STT/翻訳モデル", models, key=key)

# --------------------------------------------------
def select_realtime_model(demo_name: str = "設定") -> str:
    safe = sanitize_key(demo_name)
    models = [
        "gpt-4o-mini-realtime-preview", "gpt-4o-realtime-preview",
    ]
    return st.sidebar.radio("Choose a model:", models, key=f"model_{safe}")

# --------------------------------------------------
# Response.output から output_text を抽出
def extract_text_from_response(response: Response) -> list[str]:
    texts: list[str] = []
    for item in response.output:
        if item.type == "message":
            for content_obj in item.content:
                if getattr(content_obj, "type", None) == "output_text":
                    texts.append(content_obj.text)
    return texts

# --------------------------------------------------
# Responses オブジェクトからプロパティを安全に取得。
# - "output_text" の場合は output 配列を走査してテキストを連結。
# - それ以外は getattr() で取得（存在しなければ default）。
# --------------------------------------------------
def get_property(response: Response, property_name: str, default=None):
    if property_name == "output_text":
        texts = []
        for item in response.output:
            if item.type == "message":
                for content in item.content:
                    if content.type == "output_text":
                        texts.append(content.text)
        return "\n".join(texts) if texts else default
    else:
        return getattr(response, property_name, default)


def get_default_speech_text_message() -> list[EasyInputMessageParam]:
    # 双方向（音声⇄テキスト）会話用のデフォルトプロンプト。
    # - system: 音声アシスタント全体方針
    # - developer: フォーマット／デバッグ指示
    # - user:    テスト用ユーザ発話
    # - assistant: 期待される応答例

    system_txt = (
        "You are ChatGPT, a warm and engaging Japanese voice assistant. "
        "Respond in natural, concise Japanese within 15–20 seconds (≤2 sentences) unless asked to elaborate. "
        "If the user's intent is unclear, ask a clarifying question. "
        "Avoid disclosing private or sensitive data; remind users not to share secrets. "
        "Comply with OpenAI content policy at all times."
    )
    developer_txt = (
        "### 開発者向け指示 ###\n"
        "1. 返答は次の 3 段構成で: ①核心回答 ②要約 ③確認質問。\n"
        "2. 返答末尾に ```json {\"voice\":\"alloy\",\"temperature\":0.6}``` の形式で "
        "TTS オプションを echo してデバッグに利用。\n"
        "3. 長い説明が必要な場合は 20 秒区切りで『続けても良いですか？』と尋ねる。\n"
    )
    user_txt = (
        "マイクテストです。あなたの自己紹介を 15 秒以内でお願いします。"
    )
    assistant_txt = (
        "こんにちは、あなたの AI アシスタントです。日々の疑問や学習をお手伝いします！\n"
        "```json {\"voice\":\"alloy\",\"temperature\":0.6}```"
    )

    return [
        EasyInputMessageParam(role="system",   content=system_txt),
        EasyInputMessageParam(role="developer", content=developer_txt),
        EasyInputMessageParam(role="user",      content=user_txt),
        EasyInputMessageParam(role="assistant", content=assistant_txt),
    ]

# --------------------------------------
# client.responses.parse 出力の解析
# --------------------------------------
# print(response.output_text)

import json

# -------------------------------------------------
def parse_translation_response(resp):
    # 多態対応: Whisper Translation は
    #   ① resp.text 属性 (Translation オブジェクト)
    #   ② resp が str 型 (response_format="text")
    # ChatResponses API なら resp.output を解析
    # --- Whisper Translation ---------------------------------------
    if hasattr(resp, "text"):
        raw = resp.text
        return {"model": getattr(resp, "model", "whisper-1"),
                "usage": getattr(resp, "usage", {}),
                "raw_text": raw,
                "parsed": json.loads(raw) if _maybe_json(raw) else {}}

    if isinstance(resp, str):
        return {"model": "whisper-1",
                "usage": {},
                "raw_text": resp,
                "parsed": json.loads(resp) if _maybe_json(resp) else {}}

    # --- Chat Responses (fallback) ---------------------------------
    if hasattr(resp, "output"):
        msg = next((o for o in resp.output if o.get("type") == "message"), None)
        if msg:
            c = next((c for c in msg["content"] if c.get("type") == "output_text"), {})
            return {"model": resp.model,
                    "usage": resp.usage,
                    "raw_text": c.get("text", ""),
                    "parsed": c.get("parsed", {})}
    return None


def _maybe_json(text: str) -> bool:
    return text.strip().startswith("{") and text.strip().endswith("}")

# -------------------------------------------------
# Vector Store: File Search
# -------------------------------------------------
def create_vector_store_and_upload(txt_path: str, upload_name: str) -> str:
    # -----
    # txt_path で指定されたテキストファイルを指定 Vector Store にアップロードし、
    # インデックス完了を待って VS_ID を返す。
    # -----
    client = OpenAI()
    vs = client.vector_stores.create(name=upload_name)
    VS_ID = vs.id

    # 一時ファイルを添付
    with open(txt_path, "rb") as f:
        file_obj = client.files.create(file=f, purpose="assistants")
    client.vector_stores.files.create(vector_store_id=VS_ID, file_id=file_obj.id)

    # ❹ インデックス完了をポーリング
    while client.vector_stores.retrieve(VS_ID).status != "completed":
        time.sleep(2)
    print("Vector Store ready:", VS_ID)
    return VS_ID

def standalone_search(vs_id, query):
    VS_ID = vs_id
    # query = "返品は何日以内？"
    client = OpenAI()
    results = client.vector_stores.search(vector_store_id=VS_ID, query=query)
    for r in results.data:
        print(f"{r.score:.3f}", r.content[0].text.strip()[:60], "...")

