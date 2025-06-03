# python 00_simple_fixed.py
from openai import OpenAI
import pprint

from openai.types.responses import EasyInputMessageParam


def main():
    # OpenAIクライアント初期化
    client = OpenAI()

    # 会話コンテキスト
    developer_content = 'あなたはプロのソフトウェア開発者に教えるのがうまいメンターです。'
    user_content      = 'streamlitの概要を箇条書きで記述して。'
    assistant_content = '日本語で記述しなさい。'

    # EasyInputMessageParam のリストとして渡す
    input_content = [
        EasyInputMessageParam(role="developer", content=developer_content),
        EasyInputMessageParam(role="user",      content=user_content),
        EasyInputMessageParam(role="assistant", content=assistant_content),
    ]

    # モデル呼び出し
    res = client.responses.create(
        model="o4-mini",
        input=input_content
    )
    pprint.pprint(res)

    # レスポンスからテキストを抽出
    if hasattr(res, "output_text"):
        res_text = res.output_text
    else:
        # 生の構造をたどる場合
        res_text = res.output[0].content[0].text

    print("=== モデルからの応答 ===")
    print(res_text)

if __name__ == "__main__":
    main()
