# embeddings: streamlit run a3_00_rag_embeddings.py --server.port=8506
# [RAG] Menu(Embeddings) ----------------------------
# (1) Embedding 取得・基本動作確認
# (1-1) Embedding 取得・基本動作確認-B
# (2) 文章検索 (Similarity Search)
# (3) コード検索
# (4) レコメンデーションシステム
# (5) Embedding の次元削減・正規化
# (6) 質問応答 (QA) システムへの Embeddings 活用
# (7) 可視化 (t-SNEなど) とクラスタリング
# (8) 機械学習モデルでの回帰・分類タスク
# (9) ゼロショット分類
# --------------------------------------------
# ユースケース（Amazon の高級食品レビュー データセット）
# https://platform.openai.com/docs/guides/embeddings#use-cases
# ---------------------------------------------

from openai import OpenAI
import streamlit as st

import pandas as pd
import numpy as np

import tempfile
import json

from rag_helper import select_model, init_page
from utils.get_embedding import get_embedding
from utils.get_data_df import get_data_df

client = OpenAI()
# set_page_config は一度だけ最初に実行する必要あり（最上位で1回のみ実施）
init_page("OpenAI Embeddings App")

# -----------------------------------------------------------------
# (0) Embeddingの取得と表示の機能を追加
# -----------------------------------------------------------------
def embedding_demo(demo_name="Embedding Demo"):
    st.write(f"# {demo_name}")
    selected_model_value = select_model()
    st.write("選択したモデル:", selected_model_value)

    with st.form(key="embedding_form"):
        user_input = st.text_area("ここにテキストを入力してください:", height=75)
        submit_button = st.form_submit_button(label="Embeddingを取得")

    if submit_button and user_input:
        st.write("選択したモデル ＝ ", selected_model_value)
        st.write("入力内容:", user_input)

        # Embeddingを取得
        embedding = get_embedding(user_input, model=selected_model_value)
        st.write("Embedding:", embedding)

        # 次の入力：
        with st.form(key="embedding_next_form"):
            submit_ok_button = st.form_submit_button(label="次の入力")
        if submit_ok_button:
            user_input = ''
            st.rerun()

# -----------------------------------------------------------------
# (1) Embedding 取得・基本動作確認-B
# Embeddingを取得する関数: https://platform.openai.com/docs/models
# -----------------------------------------------------------------
def embedding_basic_01(demo_name="Amazon Food Reviews01"):
    selected_model = config_embedding_model()

    # セッションステートにuser_inputがなければ初期化
    if "user_input" not in st.session_state:
        st.session_state.user_input = ''

    with st.form(key="emb_form"):
        st.session_state.user_input = st.text_area(
            "ここにテキストを入力してください:",
            height=75,
            value=st.session_state.user_input,
            key="user_input_form"
        )
        submit_button = st.form_submit_button(label="送信")

    if submit_button and st.session_state.user_input.strip():
        embedding = get_embedding(st.session_state.user_input, selected_model)
        st.write(embedding)

# -----------------------------------------------------------------
# (1-1) Embedding 取得・基本動作確認-A
# -----------------------------------------------------------------
def config_embedding_model():
    emb_models = ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"]
    model_name = st.sidebar.radio("Embeddingモデルを選択:", emb_models, key="radio_emb_model_name")
    return model_name

def embedding_01_a(demo_name=None):
    # 1) モデル選択 & 案内
    model = config_embedding_model()
    st.write("■ 使用 embedding model:", model)
    st.write("OpenAI Agents SDK の最新情報(Web)をサンプルデータとして活用します。")

    # 2) JSON 読み込み → DataFrame
    data, df = get_data_df('utils/agents_docs.json')
    if df.empty:
        st.error("JSON ファイルが空です。パスや中身をご確認ください。")
        return

    st.write(f"JSON 内のキー数: {len(df)} 件を順に処理します。")

    # 3) 各キーごとに処理
    for idx, row in df.iterrows():
        key = row['key']
        raw_val = row['value']

        # 3-1) text 化
        text = raw_val if isinstance(raw_val, str) else json.dumps(raw_val, ensure_ascii=False)
        st.write(f"▶ ({idx+1}/{len(df)}) キー `{key}` を処理中…")
        st.code(text[:200] + ("…" if len(text) > 200 else ""), language='')

        # 3-2) Embedding 取得（動作確認）
        emb_vec = get_embedding(text, model=model)
        st.write(f"   • embedding vector length = {len(emb_vec)}")

        # 3-3) JSONL 相当の内容を .txt として一時ファイル化
        with tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.txt', encoding='utf-8'
        ) as tmp:
            record = {"id": key, "text": text}
            tmp.write(json.dumps(record, ensure_ascii=False) + "\n")
            tmp_path = tmp.name

        # 3-4) ファイルアップロード (purpose=user_data)
        with open(tmp_path, "rb") as f:
            file_obj = client.files.create(
                file=f,
                purpose="user_data"
            )
        st.write(f"   • File ID = {file_obj.id}")

        # 3-5) Vector Store を新規作成（まずファイルなしで）
        vs = client.vector_stores.create(name=key)
        st.write(f"   • Vector Store 作成 → ID: {vs.id}")

        # 3-6) 作成済ストアにファイルを添付
        vs_file = client.vector_stores.files.create(
            vector_store_id=vs.id,
            file_id=file_obj.id
        )
        st.write(f"   • Vector Store File 添付 → ID: {vs_file.id}, status: {vs_file.status}")

    st.success("✅ 全キー分の Vector Store を新規作成しました。")


def embedding_01_b(demo_name=None):
    model = config_embedding_model()
    st.write('embedding model=:', model)

# -----------------------------------------------------------------
# (2)
# -----------------------------------------------------------------
def embedding_02(demo_name=None):
    pass

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def similarity_search(df, query, n=3):
    query_emb = get_embedding(query)
    # 各文書とクエリの類似度を計算
    df["similarity"] = df["embedding"].apply(lambda x: cosine_similarity(query_emb, x))
    return df.sort_values("similarity", ascending=False).head(n)

# -----------------------------------------------------------------
# (3) コード検索
# -----------------------------------------------------------------
def embedding_03(demo_name=None):
    pass

# -----------------------------------------------------------------
# (4) レコメンデーションシステム
# -----------------------------------------------------------------
def embedding_04(demo_name=None):
    pass

# -----------------------------------------------------------------
# (5) Embedding の次元削減・正規化
# -----------------------------------------------------------------
def embedding_05(demo_name=None):
    pass

# -----------------------------------------------------------------
# (6) 質問応答 (QA) システムへの Embeddings 活用
# -----------------------------------------------------------------
def embedding_06(demo_name=None):
    pass

# -----------------------------------------------------------------
# (7) 可視化 (t-SNEなど) とクラスタリング
# -----------------------------------------------------------------
def embedding_07(demo_name=None):
    pass

# -----------------------------------------------------------------
# (8) 機械学習モデルでの回帰・分類タスク
# -----------------------------------------------------------------
def embedding_08(demo_name=None):
    pass

# -----------------------------------------------------------------
# (9) ゼロショット分類
# -----------------------------------------------------------------
def embedding_09(demo_name=None):
    pass


def main():
    init_messages()
    demos = {
        "(demo)embedding_demo": embedding_demo,
        "(1)Embedding取得-基本動作確認": embedding_basic_01,
        "　1-a データ特定": embedding_01_a,
        "　1-b　データベクトル化": embedding_01_b,
        "(2)文章検索(Similarity Search)": embedding_02,
        "(3)コード検索": embedding_03,
        "(4)レコメンデーション": embedding_04,
        "(5)Embeddingの次元削減・正規化": embedding_05,
        "(6)質問応答のEmbeddings活用": embedding_06,
        "(7)可視化(t-SNE)とクラスタリング": embedding_07,
        "(8)機械学習モデルでの回帰・分類タスク": embedding_08,
        "(9)ゼロショット分類": embedding_09
    }

    demo_name = st.sidebar.radio("デモを選択してください", list(demos.keys()))
    demos[demo_name](demo_name)

def main_2():
    data = [
        {"text": "おいしいコーヒーのお店です。", "embedding": None},
        {"text": "格安で犬の餌を買えるサイト。", "embedding": None},
        {"text": "最新のAI技術を解説する記事です。", "embedding": None},
    ]
    df = pd.DataFrame(data)
    # 埋め込みを取得してDataFrameに格納
    df["embedding"] = df["text"].apply(lambda x: get_embedding(x))

    query = "AI技術に関する情報を探しています"
    results = similarity_search(df, query)
    print(results)

# ====================================
def sample_01(demo_name="Amazon Food Reviews"):
    """
    OpenAI API を用いてテキスト（レビュー）を埋め込みベクトルに変換し、CSVに出力する
    """
    st.write("sample_01 - Amazon Food Reviews")
    # 元の Reviews.csv ファイルを読み込み
    df_original = pd.read_csv("data/Reviews.csv")
    st.write("元のデータ（先頭20件）:")
    st.dataframe(df_original.head(20))

    # 1,000件に絞る（インデックス 0～999）
    df_limited = df_original.iloc[:1000]

    # 必要なカラムのみ抽出
    columns_to_keep = ["Time", "ProductId", "UserId", "Score", "Summary", "Text"]
    df_filtered = df_limited[columns_to_keep].copy()

    # Text 列のレビューを OpenAI API を用いて埋め込みベクトルに変換し、新規カラム "embedding" に格納する
    # st.write("レビューの埋め込みベクトルを計算中です。しばらくお待ちください...")
    # with st.spinner("Embedding を計算中..."):
    #     df_filtered["embedding"] = df_filtered["Text"].apply(lambda x: get_embedding(x))

    st.write("レビューの埋め込みベクトルを計算中です。しばらくお待ちください...")
    with st.spinner("Embedding を計算中..."):
        # DataFrame の Text 列からテキストリストを作成し、改行文字を削除
        texts = [text.replace("\n", " ") for text in df_filtered["Text"].tolist()]
        # OpenAI クライアントを初期化して、バッチ処理で全レビューに対する埋め込みを取得
        client = OpenAI()
        response = client.embeddings.create(input=texts, model="text-embedding-3-small")
        # 各テキストに対する埋め込みベクトルを抽出して DataFrame に格納
        embeddings = [result.embedding for result in response.data]
        df_filtered["embedding"] = embeddings


    st.write("抽出および埋め込み変換後のデータ（先頭10件）:")
    st.dataframe(df_filtered.head(10))

    # 結果を CSV ファイルに保存
    output_path = "data/reviews_1k.csv"
    df_filtered.to_csv(output_path, index=False)
    st.success(f"処理済みデータを {output_path} に保存しました。")


if __name__ == "__main__":
    main()
