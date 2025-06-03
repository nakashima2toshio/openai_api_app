# [Usage] streamlit run a0_openai_skeleton.py --server.port 8501
# port Check: lsof -i :5678
# ----------------------------------------
# [CookBook] https://github.com/openai/openai-cookbook
# ----------------------------------------
# サンプルプログラム作成用のスケルトン
# ----------------------------------------
from __future__ import annotations
import re
import streamlit as st
from openai import OpenAI

# --- インポート直後に１度だけ実行する ---
st.set_page_config(
    page_title="ChatGPT API",
    page_icon="2025-5 Nakashima"
)
# ====================================
# [I] Core Concept
# ====================================
# [Menu] Responses create APIの使い方
# a1_00_responses_create.py
# (01_01)  テキスト入力と出力(One Shot)
# (01_011) テキスト入出力（with memory)
# (01_02)  画像入力
# (01_03)  構造化された出力
# (01_04)  関数呼び出し
# (01_05)  会話状態
# (01_06)  ツールを使ってモデルを拡張する
# ====================================
# [II] Tools
# ====================================
# [Menu] toolsパラメータの使い方 by responses-create schema (プリミティブで理解する)
# a1_01_responses_tools_json_param.py
# ・web_search_tool_param()
# ・function_tool_param_by_schema()
# ・file_search_tool_param()
# ・computer_use_tool_param()        「指示の自動実行（RPA）」リクエストのみ。応答はAPIレスポンスオブジェクトそのもの。
# ・structured_output_by_schema()
# ・image_param()
# --------------------------------------
# [Menu] toolsパラメータの使い方 by responses-parse pydantic（利用はこちらをおすすめ）
# a2_02_responses_tools_pydantic_parse.py
# [サンプル01]
# (01_01) 基本的な function_call の structured output
# (01_02) 複数ツールの登録・複数関数呼び出し
# (01_03) ユーザー独自の複雑な構造体（入れ子あり）
# (01_04) Enum型や型安全なオプションパラメータ付き
# (01_05) text_format引数で自然文のstructured outputを生成
# -----------
# [サンプル02]
# (02_01) 基本パターン（シンプルな構造化データ抽出）
# (02_02) 複雑なクエリパターン（条件・ソートなど）
# (02_03) 列挙型・動的な値の利用パターン
# (02_04) Chain of thought(!!!) 階層化された出力構造
# (02_05) 会話履歴を持った連続した構造化出力の処理
#
# ====================================
# [III] Agents
# ====================================
# Building Agent
# Voice Agent
# Agent SDK !!!
#
# --------------------------------------
# [RAG] Menu(Embeddings)
# a3_00_rag_embeddings.py
# --------------------------------------
# (1) Embedding 取得・基本動作確認
# (2) 文章検索 (Similarity Search)
# (3) コード検索
# (4) レコメンデーションシステム
# (5) Embedding の次元削減・正規化
# (6) 質問応答 (QA) システムへの Embeddings 活用
# (7) 可視化 (t-SNEなど) とクラスタリング
# (8) 機械学習モデルでの回帰・分類タスク
# (9) ゼロショット分類
# --------------------------------------------

# --------------------------------------
# Responses API で利用する型 (openai-python v1)
# --------------------------------------
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
# ユーティリティ : Streamlit key 用に安全な文字列へ変換
# 英数・アンダースコア以外を "_" へ置換
# --------------------------------------------------
def sanitize_key(name: str) -> str:
    return re.sub(r'[^0-9a-zA-Z_]', '_', name).lower()

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

# サンプル画像 URL
image_path_sample = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/"
    "Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-"
    "Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
)

# --------------------------------------------------
# 共通ヘルパ
# --------------------------------------------------
def init_page() -> None:
    """ページ共通ヘッダ"""
    st.header("ChatGPT API Usage")
    st.sidebar.title("Skeleton-メニュー")

# --------------
# ページ固有の「会話履歴クリア」ボタンと初期履歴設定
def init_messages(demo_name: str = "") -> None:
    safe = sanitize_key(demo_name)
    button_key = f"clear_{safe}"

    if st.sidebar.button("会話履歴のクリア", key=button_key) or "message_history" not in st.session_state:
        messages = get_default_messages()
        st.session_state.message_history = messages

# --------------
def select_model(demo_name: str = "設定") -> str:
    safe = sanitize_key(demo_name)
    models = [
        "gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-4o-mini",
        "gpt-4o-audio-preview", "gpt-4o-mini-audio-preview",
        "o3-mini", "o4-mini", "o1-mini", "o4", "o3", "o1",
    ]
    return st.sidebar.radio("LLM-モデルの選択", models, key=f"model_{safe}")

# --------------
# Response.output から output_text を抽出
def extract_text_from_response(response: Response) -> list[str]:
    texts: list[str] = []
    for item in response.output:
        if item.type == "message":
            for content_obj in item.content:
                if getattr(content_obj, "type", None) == "output_text":
                    texts.append(content_obj.text)
    return texts

# -----------------------------------------------
# 01_01 テキスト入出力 (One Shot):responses.create
# -----------------------------------------------
def responses_create_sample(demo_name: str = "responses_create_sample"):
    init_messages(demo_name)
    st.write(f"# {demo_name}")
    model = select_model(demo_name)
    st.write("選択したモデル:", model)

    safe = sanitize_key(demo_name)
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
        res = client.responses.create(model=model, input=messages)
        for i, txt in enumerate(extract_text_from_response(res), 1):
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
    init_page()
    page_funcs = {
        "OpenAI-API-Responses(One Shot)": responses_create_sample,
        "sample2": sample2,
    }
    demo_name = st.sidebar.radio("デモを選択", list(page_funcs.keys()))
    st.session_state.current_demo = demo_name
    page_funcs[demo_name](demo_name)

if __name__ == "__main__":
    main()
