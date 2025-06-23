# [Usage] streamlit run a0_openai_skeleton.py --server.port 8501
# ----------------------------------------
# サンプルプログラム作成用のスケルトン
# !!![OpenAi-APIは、messages に厳密型を要求することに起因します]
# ----------------------------------------
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
THIS_DIR = Path(__file__).resolve().parent
DATASETS_DIR = os.path.join(BASE_DIR, 'datasets')
HELPER_DIR = os.path.join(BASE_DIR, 'a0_common_helper')

from a0_common_helper.helper import (
    init_page,
    init_messages,
    select_model,
    sanitize_key,
    get_default_messages,
    extract_text_from_response, append_user_message,
)

from openai import OpenAI
from openai.types.responses import EasyInputMessageParam
# --- インポート直後に１度だけ実行する ---
import streamlit as st
st.set_page_config(
    page_title="ChatGPT API",
    page_icon="2025-6 Nakashima"
)
# -----------------------------------------------
# テキスト入出力 (One Shot):responses.create
# -----------------------------------------------
def responses_create_sample(demo_name: str = "responses_create_sample"):
    init_messages(demo_name)
    st.write(f"# {demo_name}")
    model = select_model(demo_name)
    st.write("選択したモデル:", model)

    safe = sanitize_key(demo_name)
    st.write("(Q-例)OpenAI-APIのresponses.parseの引数：toolsの説明をしなさい。")
    with st.form(key=f"responses_form_{safe}"):
        user_input = st.text_area("ここにテキストを入力してください:", height=75)
        submitted = st.form_submit_button("送信")

    if submitted and user_input:
        st.write("入力内容:", user_input)
        # デフォルトのプロンプト：messages に追加：
        messages = get_default_messages()
        messages.append(
            EasyInputMessageParam(role="user", content=user_input)
        )
        client = OpenAI()
        response = client.responses.create(model=model, input=messages)
        for i, txt in enumerate(extract_text_from_response(response), 1):
            st.code(txt)

        with st.form(key=f"responses_next_{safe}"):
            if st.form_submit_button("次の質問"):
                st.rerun()

# ==================================================
# sample2
# ==================================================
def sample2(demo_name: str = "sample2"):
    pass

# ==================================================
# メインルーティン
# ==================================================
def main() -> None:
    # init_page("skeleton")
    # page_funcs = {
    #     "OpenAI-API Responses(One Shot)": responses_create_sample,
    #     "sample2": sample2,
    # }
    # demo_name = st.sidebar.radio("デモを選択", list(page_funcs.keys()))
    # st.session_state.current_demo = demo_name
    # page_funcs[demo_name](demo_name)
    print('---------------')
    print(BASE_DIR)
    print(DATASETS_DIR)
    print(HELPER_DIR)

if __name__ == "__main__":
    main()
