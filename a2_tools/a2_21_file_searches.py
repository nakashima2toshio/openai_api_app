# streamlit run a2_21_file_searches.py --server.port=8504
# !pip install openai pandas tqdm -q
# 応答を生成する前に、モデルがファイル内の関連情報を検索できるようにします。
# 現時点では、一度に検索できるベクター ストアは 1 つだけなので、
# ファイル検索ツールを呼び出すときに含めることができるベクター ストア ID は 1 つだけです。

import pandas as pd, tempfile, os, json, textwrap
from openai import OpenAI


def set_dataset():
    client = OpenAI()

    CSV_PATH = "dataset/customer_support_faq_jp.csv"

    # 「Q: … A: …」形式へ変換し一時ファイルに書き出し
    df = pd.read_csv(CSV_PATH)

    tmp_txt = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    with open(tmp_txt.name, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            f.write(textwrap.dedent(f"""\
                Q: {row['question']}
                A: {row['answer']}
            """))
    print("plain-text file:", tmp_txt.name)

def create_vector_store_and_upload():
    # 3-1 Vector Store 作成
    client = OpenAI()
    vs = client.vector_stores.create(name="faq_store_jp")
    VS_ID = vs.id

    # 3-2) ファイルを作成済み Vector Store に添付
    file_obj = client.files.create(file=open(tmp_txt.name, "rb"), purpose="assistants")
    client.vector_stores.files.create(vector_store_id=VS_ID, file_id=file_obj.id)

    # 3-3) （任意）インデックス完了をポーリング
    import time
    while True:
        status = client.vector_stores.retrieve(VS_ID).status
        if status == "completed": break
        time.sleep(2)
    print("Vector Store ready:", VS_ID)
    return VS_ID

def standalone_search(vs_id):
    VS_ID = vs_id
    query = "返品は何日以内？"
    client = OpenAI()
    results = client.vector_stores.search(vector_store_id=VS_ID, query=query, k=3)
    for r in results.data:
        print(f"{r.score:.3f}", r.content[0].text.strip()[:60], "...")

def file_searches():
    pass

def main():
    set_dataset()
    vs_id = create_vector_store_and_upload()
    standalone_search(vs_id)


if __name__ == "__main__":
    main()

