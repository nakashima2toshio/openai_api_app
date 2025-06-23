# streamlit run a10_02_images_and_vision.py --server.port=8502
# [Menu]-------------------------------------------
#（1-1A）テキストから画像を作成する。
#（1-1B）入力画像（URL）からテキストを作成する。
# (1-2) 入力画像データ（Base64)からテキストデータを作成する。
# (2) テキスト（プロンプト）から画像イメージのジェネレート
# -------------------------------------------------
import os
import sys
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
import base64

from openai import OpenAI
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputTextParam,
    ResponseInputImageParam,
)

from helper import (
    init_page,
    init_messages,
    select_model,
    sanitize_key,
    get_default_messages,
    extract_text_from_response, append_user_message,
)

import streamlit as st
st.set_page_config(
    page_title="ChatGPT API Image and Vision",
    page_icon="2025-5 Nakashima"
)

# イメージ例
image_url = (
    'https://upload.wikimedia.org/wikipedia/commons/'
    'thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/'
    '2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg'
)

# -------------------------------------------------
#（1-1A）テキストから画像を作成する。
# -------------------------------------------------

# -------------------------------------------------
#（1-1B）入力画像（URL）からテキストを作成する。
# -------------------------------------------------
def url_image_to_text(demo_name):
    model = select_model()
    input_text = '日本語で回答しなさい。'
    client = OpenAI()

    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    with st.form(key="url_form"):
        st.session_state.user_input = st.text_area(
            "ここに画像のURLを入力してください:",
            height=75,
            value=image_url,
            key="user_input_form"
        )
        submit_button = st.form_submit_button(label="送信")

    if submit_button and st.session_state.user_input:
        messages = get_default_messages()
        messages = messages.append(
            EasyInputMessageParam(
                role="assistant",
                content=[
                    ResponseInputTextParam(type="input_text", text=append_text),
                    ResponseInputImageParam(type="input_text", text=append_text)
                ]
            )
        )
        res = client.responses.create(
            model=model,
            input=messages,
        )
        st.write(res)

# -------------------------------------------------
# (1-2) 入力画像データ（Base64)からテキストデータを作成する。
# -------------------------------------------------
def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def url_image_base64_to_text(demo_name):
    client = OpenAI()
    selected_model = select_model()

    # 画像フォルダー内のファイル列挙
    image_folder = "images"
    image_files = [
        f for f in os.listdir(image_folder)
        if f.lower().endswith(('png', 'jpg', 'jpeg', 'webp', 'gif'))
    ]

    if not image_files:
        st.error("画像フォルダに画像ファイルがありません。")
        return

    # 画像選択
    selected_image_file = st.selectbox(
        "(images/ ホルダー内の)画像ファイルを選択してください",
        image_files
    )

    # プロンプト入力（既定値付き）
    prompt_default = (
        "画像に何が写っているか説明してください。何人いますか？ 日本語で。"
    )
    user_prompt = st.text_area(
        "プロンプトを入力してください",
        value=prompt_default,
        height=75
    )

    # 解析ボタン
    if st.button("解析する"):
        image_path = os.path.join(image_folder, selected_image_file)
        image_base64 = encode_image_to_base64(image_path)

        # Pydantic モデルを用いて入力メッセージを構築
        message = EasyInputMessageParam(
            role="user",
            content=[
                ResponseInputTextParam(text=user_prompt),
                ResponseInputImageParam(
                    image_url=f"data:image/png;base64,{image_base64}"
                ),
            ],
        )

        response = client.responses.create(
            model=selected_model,
            input=[message],
        )

        # レスポンス表示
        if response and hasattr(response, "output_text"):
            st.write(response.output_text)
        else:
            st.error("APIから適切なレスポンスが得られませんでした。")

# -------------------------------------------------
# (2) テキスト（プロンプト）から画像イメージのジェネレート
# -------------------------------------------------
def prompt_to_image(demo_name):
    st.write("## 未実装（プロンプトから画像生成）")


def sample_04(demo_name):
    st.write("## サンプル04（未実装）")


def main():
    demos = {
        "入力画像(URL)→テキスト生成": url_image_to_text,
        "入力画像データ(Base64)→テキスト": url_image_base64_to_text,
        "プロンプト→画像イメージ": prompt_to_image,
        "サンプル04": sample_04
    }
    demo_name = st.sidebar.radio("デモを選択してください", list(demos.keys()))
    demos[demo_name](demo_name)


if __name__ == "__main__":
    main()
