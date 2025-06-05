１．`responses.create` と `responses.parse` の主な違い

1. 目的
   ・create：API へリクエストを投げて、OpenAI から返ってくる「生のレスポンスオブジェクト」をそのまま受け取る
   ・parse ：まずは同様に API へリクエストを投げるが、その後ライブラリが自動で JSON→Python 型（文字列／dict／Pydanticモデル等）に変換して返す

2. 戻り値の型
   ・create：OpenAIObject（ライブラリ内部のラップオブジェクト）、あるいは stream を使えばジェネレータ
   ・parse ：ユーザー指定の型（デフォルトは「choices[].message.content の文字列連結」）

3. 利用シーン
   ・create：
     – すべてのフィールド（usage, finish_reason, logprobs…）を細かく扱いたい
     – streaming で部分部分のチャンクを手元で細かく制御したい
   ・parse：
     – とにかく「返ってきたテキスト」だけほしい
     – 関数呼び出し機能で返ってくる JSON ペイロードを一発で dict や pydantic にマッピングしたい

4. エラー検出／例外
   ・create：HTTP ステータスや OpenAI のエラーコードは例外として上がるが、結果の JSON パースエラーは起きにくい
   ・parse：生成された JSON が期待したスキーマ（文字列／JSONオブジェクト）に合わないと、ライブラリ側で「パースエラー例外」が上がる

5. 実装負荷
   ・create：戻り値から `.choices[0].message.content` を自分で取り出すなど手作業が増える
   ・parse：単一メソッド呼び出し → すぐ Python 型になるのでサンプル・プロトタイピングが楽

###### -------------------------------------------------------------
■ 1. responses.create のサンプル

　# サンプル①: APIにリクエストを投げ、応答を生成する例
```python
　try:
	    # APIクライアントの初期化
	    client = OpenAI(api_key="your_api_key")
	    model = "gpt-4"  # 例：使用するモデルの指定
	    messages = [
	        {"role": "system", "content": "あなたはフレンドリーなアシスタントです。"},
	        {"role": "user", "content": "今日の天気は？"}
	    ]

	    # 実際にAPIを呼び出して応答を生成
	    res = client.responses.create(model=model, input=messages)

	    # レスポンスの生データを表示
	    print("API Response (raw):")
	    print(res)

	except Exception as e:
	    print("API呼び出し中にエラーが発生しました:", e)
```
■ 2. responses.parse のサンプル

　# サンプル②: 既に取得済みのAPI応答データから、主要な情報を抽出する例
```python
　try:
	    # ここでは仮にAPIから取得済みのレスポンスデータを用意
	    # ※通常はresponses.createの返却結果をそのまま使用することが多い
	    raw_response = {
	        "id": "response-123",
	        "object": "chat.completion",
	        "choices": [
	            {"message": {"role": "assistant", "content": "今日は晴れです。"}}
	        ],
	        "usage": {"prompt_tokens": 10, "completion_tokens": 12}
	    }

	    model = "gpt-4"

	    # レスポンスパーサーを使用して必要な情報を整形
	    parsed_response = client.responses.parse(model=model, input=raw_response)

	    # 整形済みの情報を表示
	    print("Parsed Response:")
	    print(parsed_response)

	except Exception as e:
	    print("レスポンス解析中にエラーが発生しました:", e)
```
###### ----------------------------------------------


## 2. **サンプルコード**
すべて共通で下記を前提とします。

```python
from openai import OpenAI
client = OpenAI()
messages = [
    {"role": "system", "content": "You are assistant."},
    {"role": "user",   "content": "Tell me a joke."}
]
```

### (1) `responses.create` を使う例

```python
res = client.responses.create(
    model="gpt-4",
    input=messages,
    temperature=0.7,
    max_tokens=150
)
# 生データの扱い
print(res)                                # OpenAIObject
print(res.usage)                          # トークン数
print(res.choices[0].message.content)     # 応答テキスト
```

(2) responses.parse を使う例（デフォルト：文字列抽出）
```python
text = client.responses.parse(
    model="gpt-4",
    input=messages,
    temperature=0.7,
    max_tokens=150
)
print(text)
```
(3) parse + 関数呼び出し結果を Pydantic にマッピング
```python
from pydantic import BaseModel

class FuncArgs(BaseModel):
    city: str

result: FuncArgs = client.responses.parse(
    model="gpt-4-0613",
    input=messages,
    functions=[{
        "name": "get_weather",
        "description": "Get weather by city",
        "parameters": {
            "type": "object",
            "properties": { "city": {"type": "string"} },
            "required": ["city"]
        }
    }],
    function_call={"name": "get_weather"},
    parse_return=FuncArgs
)
print(result.city)  # => "Tokyo"
```
4. まとめ
詳細情報やストリーミングが必要 → responses.create
テキストだけ欲しい／関数呼び出しをモデル化したい → responses.parse
