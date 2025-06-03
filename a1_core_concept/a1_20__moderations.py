# a1_20__moderations.py
from typing import Optional

from pydantic import BaseModel, Field

from openai import OpenAI
# from  openai.lib._tools import pydantic_function_tool
from openai import pydantic_function_tool

import streamlit as st

# -----------------------------------
# Responses API で利用する型 (openai-python v1)
# -----------------------------------
from openai.types.responses import (
    EasyInputMessageParam,      # 基本の入力メッセージ
    ResponseInputTextParam,     # 入力テキスト
    ResponseInputImageParam,    # 入力画像
    ResponseFormatTextJSONSchemaConfigParam,  # Structured output 用
    ResponseTextConfigParam,    # Structured output 用
    FunctionToolParam,          # 関数呼び出しツール
    FileSearchToolParam,        # ファイル検索ツール
    WebSearchToolParam,         # Web 検索ツール
    ComputerToolParam,          # AIが操作するRPA機能
    Response
)
# --------------------------------------------------
# デフォルトプロンプト
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

# role="user"の append messageの追加
def append_message(user_input_text):
    messages = get_default_messages()
    messages.append(
        EasyInputMessageParam(role="user", content=user_input_text)
    )
    return messages

# ------------------------------------------------------
from openai.types.responses import EasyInputMessageParam           # ← ここがポイント

# ページ設定
st.set_page_config(page_title="Structured Outputs Samples", page_icon="🗂️")

# --------------------------- 06. Moderation & Refusal Demo ------------------
class ModerationResult(BaseModel):
    refusal: str = Field(..., description="拒否する場合は理由、問題なければ空文字")
    content: Optional[str] = Field(None, description="許可された場合の応答コンテンツ")

    model_config = {"extra": "forbid"}

def parse_moderation(model: str, text: str) -> dict:
    prompt = (
        "You are a strict content moderator. "
        "If the input violates policy (hate, sexual, violence, self-harm, etc.), "
        "set 'refusal' to a short reason and leave 'content' null. "
        "Otherwise set 'refusal' to an empty string and echo the safe content in 'content'.\n\n"
        f"INPUT:\n{text}"
    )
    client = OpenAI()
    resp = client.responses.parse(model=model, input=prompt, text_format=ModerationResult)
    return resp.output_parsed.model_dump()

def demo_moderation() -> None:
    st.header("6. モデレーション＆拒否処理デモ")
    model = st.selectbox("モデルを選択",
                         ["o4-mini", "gpt-4o-2024-08-06", "gpt-4o-mini"],
                         key="mod_model")
    text = st.text_input("入力テキスト (不適切例: ...)", "Sensitive request example")
    if st.button("実行：モデレーションチェック"):
        st.json(parse_moderation(model, text))
