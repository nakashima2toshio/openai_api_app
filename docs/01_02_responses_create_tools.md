# OpenAI Responses API ツール利用例集

> **対象 SDK**: *Python SDK v1.12+ で動作確認*

このドキュメントは、Responses API で使える主な組み込みツールと JSON Schema ベースの Function Tool、構造化出力オプションのサンプルを **Markdown ソース** 形式でまとめたものです。各スニペットはコピペしてそのまま試せるように書かれています。

---

## 1. Built‑in ツール早見表

| ツール                    | `type` 文字列             | 主な用途                        | 代表的パラメータ                               |
| ---------------------- | ---------------------- | --------------------------- | -------------------------------------- |
| File Search            | `"file_search"`        | アップロード済みベクトルストアを検索しテキスト取得   | `vector_store_ids`, `max_num_results`  |
| Web Search (preview)   | `"web_search_preview"` | その場で Web 検索を実行し、結果をコンテキスト注入 | `user_location`, `search_context_size` |
| Computer Use (preview) | `"computer_use"`       | 画面を読み取りクリックや入力を自動実行         | (現状 `type` のみ)                         |

> **include オプション**: `include=["<tool>_call.results"]` を追加すると、ツール実行結果（検索ヒット全文など）をメッセージとは別に取得できます。

---

## 2. Web Search ToolParam の実装例

```python
from openai.types.responses import WebSearchToolParam

ws_tool = WebSearchToolParam(
    type="web_search_preview",
    user_location="Tokyo, JP",
    search_context_size="large"   # small / medium / large
)

resp = client.responses.create(
    model="gpt-4o-mini",
    tools=[ws_tool],
    input="週末の東京の天気とおすすめの屋内アクティビティは？",
    include=["web_search_call.results"]  # 検索ヒット全文が欲しい場合
)
```

検索結果は `resp.choices[0].message.tool_calls[0].results` に JSON 配列で格納されます。

---

## 3. Function ToolParam（独自関数呼び出し）

```python
from openai.types.responses import FunctionToolParam

rate_tool = FunctionToolParam(
    name="get_exchange_rate",
    description="指定した通貨ペアの為替レートを返す",
    parameters={
        "type": "object",
        "properties": {
            "base":  {"type": "string", "description": "Base currency (e.g. USD)"},
            "quote": {"type": "string", "description": "Quote currency (e.g. JPY)"}
        },
        "required": ["base", "quote"]
    }
)

resp = client.responses.create(
    model="gpt-4o",
    tools=[rate_tool],
    input="今の USDJPY レートは？",
    tool_choice="auto"  # 'get_exchange_rate' と明示も可
)
```

モデルが `function_call` を出力したら、実際の Python 関数を実行して応答に注入します。

---

## 4. File Search ToolParam（おさらい）

```python
from openai.types.responses import FileSearchToolParam

fs_tool = FileSearchToolParam(
    type="file_search",
    vector_store_ids=[vector_store_id],
    max_num_results=20
)

resp = client.responses.create(
    model="gpt-4o-mini",
    tools=[fs_tool],
    input="請求書の支払い期限は？",
    include=["file_search_call.results"]
)
```

---

## 5. Computer Use ToolParam（画面操作を任せる）

```python
from openai.types.responses import ComputerUseToolParam

cu_tool = ComputerUseToolParam(type="computer_use")

resp = client.responses.create(
    model="gpt-4o",
    tools=[cu_tool],
    input="ブラウザで https://news.ycombinator.com を開いて、トップ記事のタイトルをコピーしてメモ帳に貼り付けて"
)
```

> **備考**: Computer Use は現在プレビュー版。GUI 操作用のエージェント実行環境が必要です。

---

## 6. Structured Outputs  — `ResponseFormatTextJSONSchemaConfigParam`

```python
from openai.types.responses import ResponseFormatTextJSONSchemaConfigParam

weather_schema = {
    "type": "object",
    "properties": {
        "city":     {"type": "string"},
        "date":     {"type": "string", "format": "date"},
        "forecast": {"type": "string"}
    },
    "required": ["city", "date", "forecast"]
}

resp = client.responses.create(
    model="gpt-4o",
    input="5月30日の東京の天気を教えて。JSON で返して。",
    response_format=ResponseFormatTextJSONSchemaConfigParam(
        type="json_schema",
        json_schema=weather_schema,
        strict=True  # スキーマ違反ならエラー
    )
)
```

`strict=True` で 100 % スキーマ準拠を保証します。

---

## 7. Text 向けフォーマッタ — `ResponseTextConfigParam`

`ResponseTextConfigParam` を使うと、区切り記号や文体などテキスト出力を細かく制御できます。ただし現行 SDK では **シンタックスシュガー** 的位置づけであり、将来非推奨になる可能性があります。

---

## 8. 画像入力パラメータ例

```python
from openai.types.responses import (
    ResponseInputTextParam, ResponseInputImageParam
)

resp = client.responses.create(
    model="gpt-4o",
    input=[
        ResponseInputTextParam(
            type="input_text",
            text="この画像に写っている建造物の名前は？"
        ),
        ResponseInputImageParam(
            type="input_image",
            image_url=image_url,
            detail="high"  # low / high / auto
        )
    ]
)
```

画像は PNG/JPEG/WebP のみ、最大 20 MB まで。Vision 対応モデルが必要です。

---

## 9. まとめ

* **File / Web / Computer** の 3 つは `type` 文字列を指定するだけで利用可能。
* **FunctionToolParam** で独自 JSON Schema を宣言し、`tool_choice` で呼び出し方法を制御。
* **構造化出力** は `response_format` に JSON Schema を渡して実現。
* `include` パラメータでツールの **生データ** をメッセージ外に取得可能。

---

以上で、Responses API ツール利用の主要パターンを Markdown ソース形式で再構築しました。
