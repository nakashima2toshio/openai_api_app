### docs for Responses (すべてResponses-APIで利用される。)
https://github.com/openai/openai-python/blob/main/src/openai/types/responses
- Paramクラス情報：
  | Param名                       | 説明概要                                                                                            | source                                                                                                                                                                                          |
  | ----------------------------- | --------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | EasyInputMessageParam         | モデルへのメッセージ入力を表す TypedDict。テキスト／画像／音声などの入力コンテンツを指定            | [easy_input_message_param.py](https://github.com/openai/openai-python/blob/main/src/openai/types/responses/easy_input_message_param.py) :contentReference[oaicite:0]{index=0}                   |
  | ResponseInputTextParam        | モデルへのテキスト入力アイテムを表す TypedDict。テキスト入力本体を指定                              | [response_input_text_param.py](https://github.com/openai/openai-python/blob/main/src/openai/types/responses/response_input_text_param.py) :contentReference[oaicite:1]{index=1}                 |
  | ResponseInputImageParam       | モデルへの画像入力アイテムを表す TypedDict。画像の詳細度、ファイルID、URLなどを指定                 | [response_input_image_param.py](https://github.com/openai/openai-python/blob/main/src/openai/types/responses/response_input_image_param.py) :contentReference[oaicite:2]{index=2}               |
  | ResponseFormatTextConfigParam | テキスト出力フォーマットを指定する Union 型。プレーンテキスト／JSONスキーマ／JSONオブジェクトを設定 | [response_format_text_config_param.py](https://github.com/openai/openai-python/blob/main/src/openai/types/responses/response_format_text_config_param.py) :contentReference[oaicite:3]{index=3} |
  | FunctionToolParam             | 関数呼び出しツールを定義する TypedDict。関数名、パラメータ、型チェック設定を指定                    | [function_tool_param.py](https://github.com/openai/openai-python/blob/main/src/openai/types/responses/function_tool_param.py) :contentReference[oaicite:4]{index=4}                             |
  | FileSearchToolParam           | ファイル検索ツールを定義する TypedDict。ベクトルストアID、フィルタ、取得件数などを指定              | [file_search_tool_param.py](https://github.com/openai/openai-python/blob/main/src/openai/types/responses/file_search_tool_param.py) :contentReference[oaicite:5]{index=5}                       |
  | WebSearchToolParam            | ウェブ検索ツールを定義する TypedDict。検索プレビュータイプ、コンテキスト量、ユーザー位置情報        | [web_search_tool_param.py](https://github.com/openai/openai-python/blob/main/src/openai/types/responses/web_search_tool_param.py) :contentReference[oaicite:6]{index=6}                         |
- Paramの型：


  | Param クラス名                | 説明                                                                                                  | フィールド                                                                                                                                                                                                                                                                                                                                 |
  | ----------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
  | EasyInputMessageParam         | モデルへのメッセージ入力を表す TypedDict。                                                            | -**content** Required Union\[str, ResponseInputMessageContentListParam] … テキスト／画像／音声などの入力コンテンツ<br>- **role** Required Literal\["user","assistant","system","developer"\] … メッセージのロール<br>- **type** Literal\["message"\] … 常に `"message"`                                                                 |
  | ResponseInputTextParam        | モデルへのテキスト入力アイテムを表す TypedDict。                                                      | -**text** Required str … テキスト入力本体<br>- **type** Required Literal\["input_text"\] … 常に `"input_text"`                                                                                                                                                                                                                           |
  | ResponseInputImageParam       | モデルへの画像入力アイテムを表す TypedDict。                                                          | -**detail** Required Literal\["high","low","auto"\] … 画像の詳細度。デフォルト `auto`<br>- **type** Required Literal\["input_image"\] … 常に `"input_image"`<br>- **file_id** Optional str … 事前にアップロードしたファイルのID<br>- **image_url** Optional str … 画像の URL または base64 データ URL                                  |
  | ResponseFormatTextConfigParam | テキスト出力フォーマットを指定する Union 型。プレーンテキスト／JSONスキーマ／JSONオブジェクトを設定。 | TypeAlias = Union\<ResponseFormatText, ResponseFormatTextJSONSchemaConfigParam, ResponseFormatJSONObject\> … 出力のフォーマット設定                                                                                                                                                                                                       |
  | FileSearchToolParam           | ファイル検索ツールを定義する TypedDict。                                                              | -**type** Required Literal\["file_search"\] … 常に `"file_search"`<br>- **vector_store_ids** Required List\[str\] … 検索対象のベクトルストア ID リスト<br>- **filters** Filters … ComparisonFilter または CompoundFilter<br>- **max_num_results** int … 最大取得件数 (1–50)<br>- **ranking_options** RankingOptions … ランキング設定 |
  | WebSearchToolParam            | ウェブ検索ツールを定義する TypedDict。                                                                | -**type** Required Literal\["web_search_preview","web_search_preview20250311"\] … 検索ツールタイプ<br>- **search_context_size** Literal\["low","medium","high"\] … 検索時のコンテキスト量（デフォルト `medium`）<br>- **user_location** Optional UserLocation … ユーザー位置情報                                                        |

### 使い方例：cookbook
| Param（パラメータ名）                           | 利用例が掲載されているCookbookのリンク                                                                                                                |                                                                                                                |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| EasyInputMessageParam                   | [Web Search and States with Responses API](https://cookbook.openai.com/examples/responses_api/responses_example)                       |                                                                                                                |
| ResponseInputTextParam                  | [Web Search and States with Responses API](https://cookbook.openai.com/examples/responses_api/responses_example)                       |                                                                                                                |
| ResponseInputImageParam                 | [Web Search and States with Responses API](https://cookbook.openai.com/examples/responses_api/responses_example)                       |                                                                                                                |
| ResponseFormatTextJSONSchemaConfigParam | [Introduction to Structured Outputs](https://cookbook.openai.com/examples/structured_outputs_intro)                                    |                                                                                                                |
| ResponseTextConfigParam                 | [Introduction to Structured Outputs](https://cookbook.openai.com/examples/structured_outputs_intro)                                    |                                                                                                                |
| FunctionToolParam                       | [Function calling with an OpenAPI specification](https://cookbook.openai.com/examples/function_calling_with_an_openapi_spec)           |                                                                                                                |
| FileSearchToolParam                     | [Doing RAG on PDFs using File Search in the Responses API](https://cookbook.openai.com/examples/file_search_responses)                 |                                                                                                                |
| WebSearchToolParam                      | [Web Search and States with Responses API](https://cookbook.openai.com/examples/responses_api/responses_example)                       |                                                                                                                |
| Response                                | [Better performance from reasoning models using the Responses API](https://cookbook.openai.com/examples/responses_api/reasoning_items) | ([OpenAI Cookbook][1], [OpenAI Cookbook][2], [OpenAI Cookbook][3], [OpenAI Cookbook][4], [OpenAI Cookbook][5]) |

[1]: https://cookbook.openai.com/examples/responses_api/responses_example?utm_source=chatgpt.com "Web Search and States with Responses API - OpenAI Cookbook"
[2]: https://cookbook.openai.com/examples/structured_outputs_intro?utm_source=chatgpt.com "Introduction to Structured Outputs | OpenAI Cookbook"
[3]: https://cookbook.openai.com/examples/function_calling_with_an_openapi_spec?utm_source=chatgpt.com "Function calling with an OpenAPI specification | OpenAI Cookbook"
[4]: https://cookbook.openai.com/?utm_source=chatgpt.com "OpenAI Cookbook"
[5]: https://cookbook.openai.com/examples/responses_api/reasoning_items?utm_source=chatgpt.com "Better performance from reasoning models using the Responses API"

## 1. EasyInputMessageParam

モデルへのメッセージ履歴（チャットコンテキスト）を組み立てるときに使います。

```python
from openai import OpenAI
from openai.types.responses import EasyInputMessageParam

client = OpenAI()

messages = [
    EasyInputMessageParam(content="おはようございます", role="user", type="message"),
    EasyInputMessageParam(content="こんにちは！今日は何をお手伝いしましょう？", role="assistant", type="message"),
]

res = client.responses.create(
    model="o4-mini",
    input=messages
)

print(res)
```

### 2. ResponseInputTextParam

単一のテキスト入力アイテムを渡すときに使います。

```python
from openai import OpenAI
from openai.types.responses import ResponseInputTextParam

client = OpenAI()

text_item = ResponseInputTextParam(
    text="東京都の今日の天気を教えてください。",
    type="input_text"
)

res = client.responses.create(
    model="o4-mini",
    input=[text_item]
)

print(res)
```

### 3. ResponseInputImageParam

画像を入力として渡すときに使います。file_id または image_url のいずれかを指定します。

```python
from openai import OpenAI
from openai.types.responses import ResponseInputImageParam

client = OpenAI()

# 事前にアップロードした file_id を使う場合
image_item = ResponseInputImageParam(
    file_id="file-abc123xyz",
    detail="auto",
    type="input_image"
)

# または URL／base64 データURL を直接渡す場合
# image_item = ResponseInputImageParam(
#     image_url="https://example.com/cat.png",
#     detail="high",
#     type="input_image"
# )

res = client.responses.create(
    model="o4-mini",
    input=[image_item]
)

print(res)
```

### 4. ResponseFormatTextConfigParam

モデルの出力フォーマット（プレーンテキスト／JSON スキーマ／JSON オブジェクト）を指定します。
以下は JSON スキーマでレスポンスを制約する例です。

```python
from openai import OpenAI
from openai.types.responses import (
ResponseFormatTextJSONSchemaConfigParam,
ResponseInputTextParam
)

client = OpenAI()

json_schema = ResponseFormatTextJSONSchemaConfigParam(
type="json_schema",
schema={
"type": "object",
"properties": {
"temperature": {"type": "number"},
"condition":   {"type": "string"}
},
"required": ["temperature", "condition"]
}
)

res = client.responses.create(
model="o4-mini",
input=[ResponseInputTextParam(text="今日の東京の天気は？", type="input_text")],
response_format=json_schema
)

print(res)
```


補足

プレーンテキストは ResponseFormatText、JSON オブジェクトは ResponseFormatJSONObject を使います。

### 5. FunctionToolParam
Function Calling 用のツール定義です。事前に functions=[...] で関数仕様を渡し、実行時に呼び出します。

```python
from openai import OpenAI
from openai.types.responses import (
    EasyInputMessageParam,
    FunctionToolParam
)

client = OpenAI()

weather_tool = FunctionToolParam(
    name="get_current_weather",
    parameters={"city": "Tokyo", "unit": "metric"},
    strict=True,
    type="function",
    description="指定都市の現在の天気を取得します"
)

res = client.responses.create(
    model="o4-mini",
    input=[EasyInputMessageParam(content="東京の天気を教えて。", role="user", type="message")],
    tools=[weather_tool]
)

print(res)
```

補足

functions=[{...}] に対応する JSON スキーマ定義をあらかじめ渡しておく必要があります。

### 6. FileSearchToolParam
ベクトルストア内のドキュメント検索を行うときのツール定義です。

```python
from openai import OpenAI
from openai.types.responses import FileSearchToolParam

client = OpenAI()

file_search = FileSearchToolParam(
    type="file_search",
    vector_store_ids=["vs-12345", "vs-67890"],
    filters=None,                   # ComparisonFilter／CompoundFilter を指定する場合は import してここに渡す
    max_num_results=5,
    ranking_options={"ranker": "relevance", "score_threshold": 0.7}
)

res = client.responses.create(
    model="o4-mini",
    input=[EasyInputMessageParam(content="過去の会議記録から「プロジェクトX」の議事録を探して。", role="user", type="message")],
    tools=[file_search]
)

print(res)
```

filters には ComparisonFilter や CompoundFilter を組み合わせて渡せます。

ranking_options の詳細は RankingOptions 型 (ranker, score_threshold) を参照してください。

### 7. WebSearchToolParam
ウェブ検索プレビューを行うときのツール定義例です。

```python
from openai import OpenAI
from openai.types.responses import WebSearchToolParam

client = OpenAI()

web_search = WebSearchToolParam(
    type="web_search_preview",       # または "web_search_preview20250311"
    search_context_size="medium",    # "low" | "medium" | "high"
    user_location={                  # UserLocation 型
        "type":     "coordinates",
        "city":     "Tokyo",
        "country":  "Japan",
        "region":   "Kanto",
        "timezone": "Asia/Tokyo"
    }
)

res = client.responses.create(
    model="o4-mini",
    input=[EasyInputMessageParam(content="最新のAI関連ニュースを教えて", role="user", type="message")],
    tools=[web_search]
)

print(res)
```

補足

user_location は必要に応じて UserLocation 型で詳細を渡してください。

##### -----------
# OpenAI Responses API: FileSearch と WebSearch の活用ガイド

---

## 1. 位置付けと目的

| ツール            | 主な目的                                                                                | 想定シナリオ                              |
| -------------- | ----------------------------------------------------------------------------------- | ----------------------------------- |
| **FileSearch** | **自前でアップロードしたファイル**（PDF／MD／DOCX など）を対象に、ベクトル検索 + キーワード検索を行い、モデル回答の根拠となるテキストや引用を取り出す | *社内マニュアルや研究論文の Q\&A、FAQ ボット、RAG 構築* |
| **WebSearch**  | **インターネット上の最新情報**を取得し、モデルの知識をリアルタイムで拡張する                                            | *ニュースの要約、最新統計の取得、競合リサーチ、株価・スポーツ速報*  |

---

## 2. FileSearch の機能

* **ベクトルストア連携**: 事前に `vector_store` を作成し、`files.upload()` で文書を追加→自動埋め込み。
* **意味検索 + キーワード検索**: GPT‑4o がクエリを生成→ストアを検索→最適なチャンクを取得。
* **ファイル引用**: モデル出力に `file_citation` アノテーションを付与し、根拠箇所を示す。
* **検索結果取得**: `include=["file_search_call.results"]` を指定すると、検索結果メタデータ（スコア・抜粋テキスト）を JSON で受け取れる。
* **メタデータフィルタ**: アップロード時に付与した属性（例: `{"type":"pdf"}`）で絞り込み可能。

### 最小コード例

```python
from openai import OpenAI
from openai.types.responses import FileSearchToolParam
client = OpenAI()

fs_tool = FileSearchToolParam(
    type="file_search",
    vector_store_ids=["vs_abc123"],
    max_num_results=3,
)

resp = client.responses.create(
    model="gpt-4o-mini",
    input="What is deep research by OpenAI?",
    tools=[fs_tool],
    include=["file_search_call.results"],
)
print(resp.output_text)
print(resp.file_search_call.results)
```

---

## 3. WebSearch の機能

* **外部検索エンジン**: モデルが裏側で Bing / DuckDuckGo API などを使用してクエリを発行。
* **検索文脈サイズ**: `search_context_size`（"small" / "medium" / "large"）で取得記事数と抜粋長を調整。
* **要約 + 引用**: モデルは取得したページの要約と URL 引用を含めた回答を生成。

### 最小コード例

```python
from openai import OpenAI
from openai.types.responses import WebSearchToolParam
client = OpenAI()

ws_tool = WebSearchToolParam(
    type="web_search_preview",
    search_context_size="medium",
)

resp = client.responses.create(
    model="gpt-4o",
    input="今年の Apple WWDC の開催日は?",
    tools=[ws_tool]
)
print(resp.output_text)
```

---

## 4. 使い分けの指針

| 状況                            | 推奨ツール                                               |
| ----------------------------- | --------------------------------------------------- |
| **自社ナレッジ・内部文書**               | FileSearch                                          |
| **日本語 PDF マニュアルを引用付きで回答させたい** | FileSearch + `include=["file_search_call.results"]` |
| **公開ニュースの速報性が重要**             | WebSearch                                           |
| **モデル生成文中にネット記事の URL 引用が欲しい** | WebSearch (search\_context\_size="large")           |

---

## 5. Tips

1. **両方同時に渡す**ことも可能 (例: `tools=[fs_tool, ws_tool]`)。モデルは必要に応じて片方 / 両方を呼び分ける。
2. **コスト最適化**: FileSearch は取得チャンク長、WebSearch は context サイズを控えめに設定するとトークン削減。
3. **ストリーミング**レスポンス時は検索結果 JSON が後から届くため、UI 側でハンドリングが必要。
4. **ファイル更新**したら必ず `vector_store.file_batches.upload_and_poll()` を再実行して再埋め込みを行う。

---

## 6. よくあるエラー

| エラー                           | 原因と対処                                |
| ----------------------------- | ------------------------------------ |
| `vector_store_ids=[]` で検索結果が空 | ストア ID が誤り / ファイル未アップロード。ダッシュボードで確認。 |
| `Unauthorized`                | API キーに Retrieval 権限が無い (Tier 要件)。   |
| WebSearch がタイムアウト             | ネットワーク制限のある環境、複雑なクエリ。簡潔に書き直す。        |

---

**参考:** [OpenAI Retrieval Guide](https://platform.openai.com/docs/guides/retrieval) ・ SDK Docs `client.responses.create()` / `FileSearchToolParam` / `WebSearchToolParam` 各項目。

