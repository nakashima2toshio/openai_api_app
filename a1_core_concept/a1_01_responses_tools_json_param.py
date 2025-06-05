# streamlit run a1_01_responses_tools_json_param.py --server.port=8501
# --------------------------------------------------
# [Menu] toolsパラメータの使い方 by schema
# --------------------------------------------------
# tools param 概要・一覧
# | 関数                             | 目的・概要                                      |
# | ------------------------------- | ---------------------------------------------- |
# | `web_search_tool_param`         | インターネット検索を実行し、取得記事をモデルに渡して最新情報を回答に反映させる。       |
# | `function_tool_param_by_schema` | モデルが外部API（為替レート取得）を安全に自動呼び出しし、結果を回答へ組み込む。      |
# | `file_search_tool_param`        | 自前ベクトルストアを意味検索し、関連文書を引用して回答する（RAG機能）。          |
# | `computer_use_tool_param`       | 仮想PC/ブラウザ環境をAIが操作するRPA機能。操作結果やスクリーンショットを取得できる。 |
# | `structured_output_by_schema`   | モデル出力をユーザ定義JSONスキーマへ厳密整形し、機械可読な構造化データとして取得。    |
# | `image_param`                   | Vision機能。画像＋質問を送り、画像内容を理解・回答させるサンプル。           |
# 宿題：computer_use_tool_param()　未実装
# --------------------------------------------------
# デフォルトプロンプト
# --------------------------------------------------
import os
import sys

import json
import base64
import glob
import requests
import pandas as pd

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from openai import OpenAI
from openai.types.responses.web_search_tool_param import UserLocation, WebSearchToolParam
from openai.types.responses import EasyInputMessageParam, ResponseInputTextParam, ResponseInputImageParam, \
    ResponseTextConfigParam, ResponseFormatTextJSONSchemaConfigParam, FunctionToolParam, FileSearchToolParam, \
    ComputerToolParam

from pydantic import BaseModel, ValidationError
from a0_common_helper.helper import (
    init_page,
    init_messages,
    select_model,
    sanitize_key,
    get_default_messages,
    extract_text_from_response,
)

import streamlit as st
# --- インポート直後に１度だけ実行する ---
st.set_page_config(
    page_title="ChatGPT Responses API",
    page_icon="2025-5 Nakashima"
)

# サンプル画像 URL
image_url = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/"
    "Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-"
    "Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
)

# --------------------------------------------------
# tools: web_search_tool_param
# --------------------------------------------------
def web_search_tool_param() -> None:
    ws_tool = WebSearchToolParam(
        type="web_search_preview",
        search_context_size="high"
    )

    client = OpenAI()
    messages = get_default_messages()
    add_text  = "週末の東京の天気とおすすめの屋内アクティビティは？"

    messages.append(  # ← 戻り値は None
        EasyInputMessageParam(
            role="user",
            content=[
                ResponseInputTextParam(type="input_text", text=add_text),
                ResponseInputImageParam(type="input_image", image_url=image_url, detail="auto"),
            ],
        )
    )
    resp = client.responses.create(
        model="gpt-4,1",
        tools=[ws_tool],
        input=messages,
    )
    print(resp.output_text)

# --------------------------------------------------
# tools: Function Calling by schema
# --------------------------------------------------
# !pip install forex-python  # 為替レートのライブラリー
import requests
import os

def get_exchange_rate(base: str, quote: str) -> float:
    api_key = os.getenv("EXCHANGERATE_API_KEY")
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base.upper()}/{quote.upper()}"
    response = requests.get(url)
    data = response.json()
    if data['result'] == 'success':
        return data['conversion_rate']
    else:
        raise ValueError(f"API Error: {data}")

def function_tool_param_by_schema():
    rate_tool: FunctionToolParam = {
        "name": "get_exchange_rate",
        "description": "指定した通貨ペアの為替レートを返す",
        "parameters": {
            "type": "object",
            "properties": {
                "base": {"type": "string", "description": "Base currency (e.g. USD)"},
                "quote": {"type": "string", "description": "Quote currency (e.g. JPY)"}
            },
            "required": ["base", "quote"],
            "additionalProperties": False  # 追加
        },
        "strict": True,
        "type": "function"
    }

    client = OpenAI()
    resp = client.responses.create(
        model="gpt-4.1",
        tools=[rate_tool],
        input="今の USD-JPY レートは？",
        tool_choice="auto"                     # 省略も可。自動で関数を呼ぶ
    )

    # 関数呼び出し結果の確認例
    import pprint
    if resp.tools and resp.tools[0].type == "function":
        tool = resp.tools[0]
        print(f"モデルが関数を呼び出しました: {tool.name}")
        print("\n▼関数情報")
        print(f"  name        : {tool.name}")
        print(f"  description : {tool.description}")
        print(f"  strict      : {tool.strict}")
        print(f"  type        : {tool.type}")
        print(f"  parameters  :")
        pprint.pprint(tool.parameters, indent=4, width=80)
    else:
        print(resp.output_text)

# --------------------------------------------------
# tools: File Search ToolParam
# --------------------------------------------------
def file_search_tool_param():
    # ------　data/customer_support_faq_jp.csv
    vector_store_id = 'vs_68345a403a548191817b3da8404e2d82'
    fs_tool = FileSearchToolParam(
        type="file_search",
        vector_store_ids=[vector_store_id],
        max_num_results=20
    )
    client = OpenAI()
    resp = client.responses.create(
        model="gpt-4.1",
        tools=[fs_tool],
        input="支払い情報は安全ですか？ また、請求書の支払い期限は？",
        include=["file_search_call.results"]
    )
    print(resp.output_text)

# --------------------------------------------------
# tools: ComputerUseToolParam（画面操作を任せる）Coming soon.
# --------------------------------------------------
def computer_use_tool_param():
    pass

# --------------------------------------------------
# tools: StructuredOutputs  — X ResponseFormatTextJSONSchemaConfigParam
#        ResponseTextConfigParam を利用すること。
# --------------------------------------------------
def structured_output_by_schema():
    from openai import OpenAI
    # ----------------------------
    # 1. JSON Schema 定義
    # ----------------------------
    weather_schema = {
        "type": "object",
        "properties": {
            "city": {"type": "string"},
            "date": {"type": "string", "format": "date"},
            "forecast": {"type": "string"},
        },
        "required": ["city", "date", "forecast"],
        "additionalProperties": False,   # ★ 追加
    }
    # ----------------------------
    # 2. メッセージ作成
    # ----------------------------
    messages = [
        EasyInputMessageParam(
            role="user",
            content=[
                ResponseInputTextParam(
                    type="input_text",
                    text="5月30日の東京の天気を教えて。JSON で返して。",
                )
            ],
        )
    ]

    # ----------------------------
    # 3. ResponseTextConfigParam を生成
    #    → name を必須で付与
    # ----------------------------
    text_cfg = ResponseTextConfigParam(
        format=ResponseFormatTextJSONSchemaConfigParam(
            name="weather_schema",          # ★ 追加: 必須キー
            type="json_schema",
            schema=weather_schema,
            strict=True,
        )
    )

    # ----------------------------
    # 4. API 呼び出し
    # ----------------------------
    client = OpenAI()
    resp = client.responses.create(
        model="gpt-4.1",
        input=messages,
        text=text_cfg,
    )

    print(resp.output_text)

# --------------------------------------------------
# tools: Text 向けフォーマッタ —: ResponseTextConfigParam
# --------------------------------------------------
# ResponseTextConfigParam を使うと、区切り記号や文体などテキスト出力を細かく制御できます。
# ただし現行 SDK では シンタックスシュガー 的位置づけであり、将来非推奨になる可能性があります。

# --------------------------------------------------
# tools: Image Parameter  ― 修正版
# --------------------------------------------------
def image_param():
    # 画像 + テキストを 1 つの user メッセージとして送信
    client = OpenAI()

    # 1. user メッセージを EasyInputMessageParam で包む
    messages = [
        EasyInputMessageParam(
            role="user",
            content=[
                ResponseInputTextParam(
                    type="input_text",
                    text="この画像に写っている建造物の名前は？",
                ),
                ResponseInputImageParam(
                    type="input_image",
                    image_url=image_url,
                    detail="high",  # low / high / auto
                ),
            ],
        )
    ]

    # 2. Responses API 呼び出し
    resp = client.responses.create(
        model="gpt-4o",
        input=messages,
    )

    print(resp.output_text)


def web_search_tool(demo_name=None):
    pass

def function_tool(demo_name=None):
    pass

def file_search_tool(demo_name=None):
    pass

def computer_use_tool(demo_name=None):
    pass

def structured_output(demo_name=None):
    pass

def image_vision(demo_name=None):
    pass

# ==================================================
# メインルーティン
# ==================================================
def main() -> None:
    init_page("core concept")
    page_funcs = {
        "01 web_search": web_search_tool,
        "02 function_tool": function_tool,
        "03  file_search": file_search_tool,
        "04 computer_use_tool": computer_use_tool,
        "05 構造化出力": structured_output,
        "06 image_vision": image_vision,
    }
    demo_name = st.sidebar.radio("デモを選択", list(page_funcs.keys()))
    st.session_state.current_demo = demo_name
    page_funcs[demo_name](demo_name)

if __name__ == "__main__":
    main()

