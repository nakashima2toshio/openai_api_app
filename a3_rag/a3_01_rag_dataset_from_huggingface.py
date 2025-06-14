# python a3_01_rag_dataset_from_huggingface.py
# 下記コードは、ノイズが大きい。 ---> 09_01_rag_
# --------------------------------------------------
# ① カスタマーサポート・FAQデータセット   推奨データセット： Amazon_Polarity
# ② 一般知識・トリビアQAデータセット      推奨データセット： trivia_qa
# ③ 医療質問回答データセット             推奨データセット： FreedomIntelligence/medical-o1-reasoning-SFT
# ④ 科学・技術QAデータセット             推奨データセット： sciq
# ⑤ 法律・判例QAデータセット             推奨データセット： nguha/legalbench
# --------------------------------------------------
# 1. いま得られている結果をどう評価するか？
# - 多くの RAG ワークフローでは 要点抽出または除外 が推奨です。
#    CoT を保持しておきたい場合は “raw_cot” を別フィールドとしてストレージに保存し、
#    検索ヒット後に参照すると良いでしょう。
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

# ----------------------------------------------------
# 1. Customer Support FAQs/ FAQ型のデータ：
#    前処理：「Q: … A: …」形式へ変換
# ----------------------------------------------------
def set_dataset_to_qa(csv_path):
    # 「Q: … A: …」形式へ変換し一時ファイルに書き出し
    df = pd.read_csv(csv_path)

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
    # 1) Vector Store 作成
    client = OpenAI()
    vs = client.vector_stores.create(name=name)

    # 2) ファイルを作成済み Vector Store に添付
    file_obj = client.files.create(file=open(tmp_txt_path, "rb"), purpose="assistants")
    client.vector_stores.files.create(vector_store_id=vs.id, file_id=file_obj.id)

    # 3) （任意）インデックス完了をポーリング
    import time
    while True:
        status = client.vector_stores.retrieve(vs.id).status
        if status == "completed": break
        time.sleep(2)
    print("Vector Store ready:", vs.id)
    return vs.id

def standalone_search(vs_id):
    print("vs_id=:", vs_id)
    query = "What is your return policy? "
    client = OpenAI()
    # max_num_results が正式な引数名
    results = client.vector_stores.search(
        vector_store_id = vs_id,
        query = query,
        max_num_results = 3,  # 1~50
    )
    for r in results.data:
        print(f"{r.score:.3f}", r.content[0].text.strip())  # [:60], "...")

# ----------------------------------------------------
# 2. Legal QA — *consumer_contracts_qa
#    前処理：
# ----------------------------------------------------
def set_dataset_02(csv_path):
    pass

# ----------------------------------------------------
# 3. Medical QA — *medical-o1-reasoning-SFT
#    前処理：
# ----------------------------------------------------
def set_dataset_03(csv_path):
    pass

# ----------------------------------------------------
# 4. SciQ — Science MCQ
#    前処理：
# ----------------------------------------------------
def set_dataset_04(csv_path):
    pass

# ----------------------------------------------------
# 5. Trivia QA — *rc*（Reading Comprehension）
#    前処理：
# ----------------------------------------------------
def set_dataset_05(csv_path):
    pass

# ----------------------------------------------------
def main():
    # download_dataset()
    # ----------------------------------------------------
    # 1. Customer Support FAQs/ FAQ型のデータ：
    # ----------------------------------------------------
    csv_path = "datasets/customer_support_faq.csv"
    tmp_text = set_dataset_to_qa(csv_path)
    name = "customer_support_faq"
    vs_id = create_vector_store_and_upload(name, tmp_text)
    print(vs_id)
    # vs_id = 'vs_68345a403a548191817b3da8404e2d82'
    # standalone_search(vs_id)

if __name__ == "__main__":
    main()
