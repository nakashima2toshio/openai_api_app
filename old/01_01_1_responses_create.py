# streamlit run 01_01_1_responses_create.py  --server.port=8502
"""
[1] core concepts　＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
(1) QuickStart              : (Developer quickstart) https://platform.openai.com/docs/quickstart?api-mode=responses
    ・01_1 Developer quickstart           ：プロンプトからテキスト出力を生成
    ・Analyze image inputs           ：画像入力を分析する
    ・Extend the model with tools    ：ツールでモデルを拡張する
    ・Deliver blazing fast AI experiences　：超高速AIエクスペリエンスを提供
    ・Build agents                   ：エージェントを構築

(2) Responses(Text inputs and outputs) : (Text generation and prompting) https://platform.openai.com/docs/guides/text?api-mode=responses
    ・02_1: Text inputs and outputs
    ・02_2: Image inputs
    ・02_3: Structured Outputs
    ・02_4: Function calling
    ・02_5: Conversation state
    ・02_6 Extend the models with tools
(3) Images and vision
    ・Images and vision：url or base643
    ・Image input requirements and detail, spec., limitations and calculation costs
    ・Provide multiple image inputs

(Todo) ・入出力のtokenから利用料金を表示する。

EasyInputMessageParam           01_ QA                          モデルへのメッセージ入力を表す TypedDict
ResponseInputTextParam          02_1 Text inputs and outputs     モデルへのテキスト入力アイテムを表す TypedDict
ResponseInputImageParam         02_2 Image inputs               モデルへの画像入力アイテムを表す TypedDict
ResponseFormatTextConfigParam   02_3 Structured Outputs         テキスト出力フォーマットを指定する Union 型。プレーンテキスト／JSONスキーマ／JSONオブジェクトを設定
                                02_4 Function calling
                                02_5: Conversation state
                                02_6 Extend the models with tools
FileSearchToolParam             2-4. Built-in Tools (FileSearch / WebSearch)
                                     ファイル検索ツールを定義する TypedDict
WebSearchToolParam              2-4. Built-in Tools (FileSearch / WebSearch)
                                     ウェブ検索ツールを定義する TypedDict。
"""
# streamlit run 01_01_1_responses_create.py --server.port=8501
import streamlit as st
import base64
import json

from openai import OpenAI
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputTextParam,
    ResponseInputImageParam,
    # ResponseFormatTextJSONSchemaConfigParam,  # この型を使う
    FunctionToolParam,
    FileSearchToolParam,
    WebSearchToolParam, ResponseTextConfigParam,
)

from utils import util_00_st as st_utils
from utils import util_01_responses as responses_utils


# ────────────────────────────────────────────────────────────────
# ページ初期化
# ────────────────────────────────────────────────────────────────
st_utils.init_page("OpenAI Responses App")

# ────────────────────────────────────────────────────────────────
# 01_1. QA サンプル
# ────────────────────────────────────────────────────────────────
def qa_sample(demo_name="Q & A Sample"):
    model = st_utils.config_model()

    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    with st.form("qa_form"):
        st.session_state.user_input = st.text_area(
            "質問を入力してください :", height=75, value=st.session_state.user_input
        )
        submitted = st.form_submit_button("送信")

    if submitted and st.session_state.user_input:
        user_msg = EasyInputMessageParam(
            role="user",
            content=[
                ResponseInputTextParam(type="input_text", text=st.session_state.user_input)
            ],
        )

        resp = OpenAI().responses.create(model=model, input=[user_msg])
        out = responses_utils.get_property(resp, "output_text", "（回答なし）")
        st_utils.display_response(out)

        if st.button("次の質問"):
            st.session_state.user_input = ""
            st.rerun()


# ────────────────────────────────────────────────────────────────
# 2-1. Image 入力
# ────────────────────────────────────────────────────────────────
def image_inputs_02_01(demo_name=None):
    model = st_utils.config_model()
    url = st.text_input("画像 URL を入力", "")

    if st.button("送信（Image I/O）"):
        client = OpenAI()

        text_input = ResponseInputTextParam(
            type="input_text", text="この画像には何が写っていますか？"
        )
        image_input = ResponseInputImageParam(
            type="input_image", image_url=url, detail="auto"
        )
        easy_msg = EasyInputMessageParam(role="user", content=[text_input, image_input])

        resp = client.responses.create(model=model, input=[easy_msg])
        st_utils.display_response(resp.output_text)

def structured_outputs_02_02(demo_name=None):
    model = st_utils.config_model()

    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age":  {"type": "integer"},
        },
        "required": ["name", "age"],
    }

    prompt = st.text_area(
        "JSON 形式で name, age を返してください。",
        "Please provide your name and age in JSON.",
    )

    resp = ''
    if st.button("送信（Structured）"):
        client = OpenAI()

        # ResponseTextConfigParam
        response_text_config_param = {
            "format": {
                "type": "json_schema",
                "schema": schema
            }
        }

        resp = client.responses.create(
            model=model,
            instructions="Respond ONLY with JSON matching the schema",
            input=prompt,
            text=ResponseTextConfigParam(response_text_config_param),
        )

    st.markdown("**生の出力**")
    st.write(resp.output_text)

    try:
        st.markdown("**パース結果 (JSON)**")
        st.json(json.loads(resp.output_text))
    except json.JSONDecodeError:
        st.error("JSON パースに失敗しました。モデル出力を確認してください。")

# ────────────────────────────────────────────────────────────────
# 2-3. Function Calling
# ────────────────────────────────────────────────────────────────
def function_calling_02_03(demo_name=None):
    model = st_utils.config_model()

    weather_function_schema = {
        "name": "get_current_weather",
        "description": "指定都市の現在の天気を返す",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    }

    city = st.text_input("都市名を入力", "Tokyo, Japan")

    if st.button("送信（Function Call）"):
        client = OpenAI()

        func_tool = FunctionToolParam(
            name=weather_function_schema["name"],
            description=weather_function_schema["description"],
            parameters=weather_function_schema["parameters"],
            strict=True,
            type="function",
        )

        resp = client.responses.create(
            model=model,
            input=f"What is the weather in {city}?",
            tools=[func_tool],
            tool_choice="auto",
        )

        # モデルが関数を呼び出したか？
        if resp.tools and resp.tools[0].type == "function":
            args = resp.tools[0].arguments
            st.markdown(f"**モデルが {resp.tools[0].name} を呼び出しました**")
            st.json(args)

            # --- ダミーの関数実行結果 ---
            result = {
                "location": args["location"],
                "temperature": 23,
                "unit": args.get("unit", "celsius"),
            }
            st.markdown("**関数実行結果 (ダミー)**")
            st.json(result)

            # Follow-up メッセージ
            follow = client.responses.create(
                model=model,
                previous_response_id=resp.id,
                input=[
                    EasyInputMessageParam(
                        role="assistant",
                        content=[
                            ResponseInputTextParam(
                                type="input_text",
                                text=json.dumps(result),
                            )
                        ],
                    )
                ],
            )
            st.markdown("**最終応答**")
            st.write(follow.output_text)
        else:
            st_utils.display_response(resp.output_text)


# ────────────────────────────────────────────────────────────────
# 2-4. Built-in Tools (FileSearch / WebSearch)
# ────────────────────────────────────────────────────────────────
def extend_tools_02_04(demo_name=None):
    model = st_utils.config_model()
    tool = st.selectbox("ツール選択", ["file_search", "web_search_preview"])
    query = st.text_input("クエリを入力", "")

    if st.button("送信（Tools）"):
        client = OpenAI()

        if tool == "file_search":
            vs = st.text_input("vector_store_id", "")

            fs_tool = FileSearchToolParam(
                type="file_search",
                vector_store_ids=[vs] if vs else [],
                max_num_results=5,
            )

            resp = client.responses.create(model=model, tools=[fs_tool], input=query)
            st.json(resp.file_search_call.results)

        else:
            ws_tool = WebSearchToolParam(
                type="web_search_preview", search_context_size="medium"
            )
            resp = client.responses.create(model=model, tools=[ws_tool], input=query)
            st_utils.display_response(resp.output_text)


# ────────────────────────────────────────────────────────────────
# 3. Images & Vision
# ────────────────────────────────────────────────────────────────
def images_and_vision_03(demo_name=None):
    model = st_utils.config_model()

    url_text = st.text_area("画像 URL を改行区切りで入力")
    files = st.file_uploader(
        "画像アップロード",
        type=["png", "jpg", "jpeg", "webp", "gif"],
        accept_multiple_files=True,
    )
    detail = st.selectbox("Detail", ["auto", "low", "high"])

    if st.button("画像解析"):
        items: list = [
            ResponseInputTextParam(type="input_text", text="何が写っていますか？")
        ]

        # URL
        for u in filter(None, (u.strip() for u in url_text.splitlines())):
            items.append(
                ResponseInputImageParam(
                    type="input_image", image_url=u, detail=detail
                )
            )

        # アップロード画像 ⇒ base64
        for f in files or []:
            b64 = base64.b64encode(f.read()).decode()
            items.append(
                ResponseInputImageParam(
                    type="input_image",
                    image_url=f"data:{f.type};base64,{b64}",
                    detail=detail,
                )
            )

        easy_msg = EasyInputMessageParam(role="user", content=items)
        resp = OpenAI().responses.create(model=model, input=[easy_msg])
        st_utils.display_response(resp.output_text)


# ────────────────────────────────────────────────────────────────
# アプリ起動
# ────────────────────────────────────────────────────────────────
def main():
    st_utils.init_messages()

    demos = {
        "QA": qa_sample,
        "Image I/O": image_inputs_02_01,
        "Structured": structured_outputs_02_02,
        "Function": function_calling_02_03,
        "Tools": extend_tools_02_04,
        "Vision": images_and_vision_03,
    }

    choice = st.sidebar.radio("デモを選択", list(demos.keys()))
    demos[choice]()


if __name__ == "__main__":
    main()
