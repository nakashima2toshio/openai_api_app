# helper.py
# a2_helper.py
import re
import streamlit as st

# -----------------------------------
# Responses API で利用する型 (openai-python v1)
# -----------------------------------
from openai.types.responses import EasyInputMessageParam, ResponseInputTextParam, ResponseInputImageParam, \
    ResponseTextConfigParam, ResponseFormatTextJSONSchemaConfigParam, FunctionToolParam, FileSearchToolParam, \
    ComputerToolParam

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

# --------------------------------------------------
# デフォルトプロンプト　（例）ソフトウェア開発用
# --------------------------------------------------
def get_default_messages() -> list[EasyInputMessageParam]:
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

    return [
    EasyInputMessageParam(role="developer", content=developer_text),
    EasyInputMessageParam(role="user",      content=user_text),
    EasyInputMessageParam(role="assistant", content=assistant_text),
]

def append_user_message(append_text):
    messages = get_default_messages()
    messages = messages.append(
        EasyInputMessageParam(
            role="user",
            content=[
                ResponseInputTextParam(type="input_text", text=append_text),
            ],
        )
    )
    return messages

def append_developer_message(append_text):
    messages = get_default_messages()
    messages = messages.append(
        EasyInputMessageParam(
            role="developer",
            content=[
                ResponseInputTextParam(type="input_text", text=append_text),
            ]
        )
    )
    return messages

def append_assistant_message(append_text):
    messages = get_default_messages()
    messages = messages.append(
        EasyInputMessageParam(
            role="assistant",
            content=[
                ResponseInputTextParam(type="input_text", text=append_text),
            ]
        )
    )
    return messages

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
        "gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-4o-mini",
    ]
    return st.sidebar.radio("Choose a model:", models, key=f"model_{safe}")
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

# --------------------------------------
# client.responses.parse 出力の解析
# --------------------------------------
# import pprint
#
# print(response.output_text)
# print('----------------------------------\n')
#
# pprint.pprint(response.model_dump())
