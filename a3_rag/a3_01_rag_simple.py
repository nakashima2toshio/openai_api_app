# a3_01_rag_simple.py
# 下記コードは、ノイズが大きい。 ---> 09_01_rag_
# --------------------------------------------------
# ① カスタマーサポート・FAQデータセット   推奨データセット： Amazon_Polarity
# ② 一般知識・トリビアQAデータセット      推奨データセット： trivia_qa
# ③ 医療質問回答データセット             推奨データセット： FreedomIntelligence/medical-o1-reasoning-SFT
# ④ 科学・技術QAデータセット             推奨データセット： sciq
# ⑤ 法律・判例QAデータセット             推奨データセット： nguha/legalbench
# --------------------------------------------------
# 1. いま得られている結果をどう評価するか？
# --------------------------------------------------
# 観点	            評価
# 検索自体のヒット	    上位 0.746 のチャンク内に「返品ポリシーを教えてください。」
#                   →30 日以内で全額返金という正しい回答が含まれており、リコール（再現率）は OK。
# 精度 (Precision)	返ってきたチャンクが “Q/A を 10 問以上まとめて 1 塊” になっているため、
#                   ノイズが多く余計な QA も一緒に返っている。
# スコア分布	        0.746 → 0.676 → 0.636 ときれいに降下しており、ベクトル検索自体は機能している。
# 次の課題	        ・チャンクが大き過ぎる
#                   ・回答文だけ抽出してユーザーに返すロジックが無い
# --------------------------------------------------
from openai import OpenAI
from pathlib import Path
from datasets import load_dataset
import pandas as pd, tempfile, textwrap


datasets_to_download = [
    {
        "name": "customer_support_faq",
        "hfpath": "MakTek/Customer_support_faqs_dataset",
        "config": None,
        "split": "train",
    },
    {
        "name": "trivia_qa",
        "hfpath": "trivia_qa",
        "config": "rc",
        "split": "train",
    },
    {
        "name": "medical_qa",
        "hfpath": "FreedomIntelligence/medical-o1-reasoning-SFT",
        "config": "en",
        "split": "train",
    },
    {
        "name": "sciq_qa",
        "hfpath": "sciq",
        "config": None,
        "split": "train",
    },
    {
        "name": "legal_qa",
        "hfpath": "nguha/legalbench",
        "config": "consumer_contracts_qa",  # ★必須
        "split": "train",
    },
]


def download_dataset():
    DATA_DIR = Path("datasets")
    DATA_DIR.mkdir(exist_ok=True)

    for d in datasets_to_download:
        print(f"▼ downloading {d['name']} …")
        ds = load_dataset(
            path=d["hfpath"],
            name=d["config"],
            split=d["split"],
        )

        # # Arrow 形式 → data/<name>
        # arrow_path = DATA_DIR / d["name"]
        # ds.save_to_disk(arrow_path)
        # print(f"  saved dataset ➜ {arrow_path}")

        # CSV 形式 → data/<name>.csv
        csv_path = DATA_DIR / f"{d['name']}.csv"
        ds.to_pandas().to_csv(csv_path, index=False)
        print(f"  saved CSV     ➜ {csv_path}")

    print("\n[OK] All datasets downloaded & saved.")


def set_dataset(csv_path):
    client = OpenAI()
    CSV_PATH = "data/customer_support_faq_jp.csv"

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
    return tmp_txt.name

def create_vector_store_and_upload(name, tmp_txt_path):
    # 3-1 Vector Store 作成
    client = OpenAI()
    vs = client.vector_stores.create(name=name)
    VS_ID = vs.id

    # 3-2) ファイルを作成済み Vector Store に添付
    file_obj = client.files.create(file=open(tmp_txt_path, "rb"), purpose="assistants")
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
    print("vs_id=:", vs_id)
    query = "返品ポリシーを教えてください。"  # "返品は何日以内？"
    client = OpenAI()
    # max_num_results が正式な引数名
    results = client.vector_stores.search(
        vector_store_id = VS_ID,
        query = query,
        max_num_results = 3,  # 1~50
    )
    for r in results.data:
        print(f"{r.score:.3f}", r.content[0].text.strip())  # [:60], "...")

def main():
    # download_dataset()
    # csv_path = "data/customer_support_faq_jp.csv"
    # tmp_text = set_dataset(csv_path)
    # name = "customer_support_faq_jp"
    # vs_id = create_vector_store_and_upload(name, tmp_text)
    vs_id = 'vs_68345a403a548191817b3da8404e2d82'
    standalone_search(vs_id)

if __name__ == "__main__":
    main()
