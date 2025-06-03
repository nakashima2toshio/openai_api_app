##### 1-1 Text and prompting：[docs]

1-1-1 Text generation and prompting[テキスト生成とプロンプト]
1-1-2 Message roles and instruction following[メッセージの役割と指示のフォロー]
1-1-3 Instructions versus developer messages in multi-turn conversations[複数ターンの会話における指示と開発者メッセージ]
1-1-4 Choosing a model[モデルの選択]
1-1-5 Prompt engineering[迅速なエンジニアリング]

[API](https://platform.openai.com/docs/api-reference/responses/create)
1-1-10 Create a model response[モデルレスポンスを作成する]
1-1-11 Get a model response[模範的な回答を得る]
1-1-12 Delete a model response[モデル応答を削除する]
1-1-13 List input items[入力項目をリストする]
1-1-14 The response object[レスポンスオブジェクト]
1-1-15 The input item list[入力項目リスト]

##### 1-1 Text and prompting： [テキスト生成とプロンプト](https://platform.openai.com/docs/guides/text)モデルにテキストを生成するよう指示する方法を学びます。

[Docs]
1-1-1 Text generation and prompting[テキスト生成とプロンプト]

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-4o",
    input="Write a one-sentence bedtime story about a unicorn."
)
```

1-1-2 Message roles and instruction following[メッセージの役割と指示のフォロー]

```python
response = client.responses.create(
    model="gpt-4o",
    instructions="Talk like a pirate.",
    input="Are semicolons optional in JavaScript?",
)
```

1-1-3 Instructions versus developer messages in multi-turn conversations[複数ターンの会話における指示と開発者メッセージ]

```python
instructionsパラメータは現在のレスポンス生成リクエストにのみ適用されることに注意してください。
このパラメータを使用して会話状態を管理しprevious_response_idている場合、
instructions以前のターンで使用されたパラメータはコンテキストに存在しません。
同じモデル指示をターン間で保持したい場合は、developer代わりにメッセージを使用してください。
```

1-1-4 Choosing a model[モデルの選択]

```python

```

1-1-5 Prompt engineering[迅速なエンジニアリング]

```python

```


| ロール      | 説明                                                                                                                                                                                  |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| developer   | developerメッセージは、アプリケーション開発者によって提供される、userメッセージよりも優先される指示です。                                                                             |
| user        | userメッセージは、エンドユーザーによって提供される、developerメッセージの背後に重み付けされた指示です。                                                                               |
| assistant   | モデルによって生成されたメッセージにはassistant役割があります。                                                                                                                       |
| instruction | モデルが応答を生成する際の動作に関する高レベルの指示（トーン、目標、正しい応答例など）を与えます。このパラメータで与えられた指示は、inputパラメータ内のプロンプトよりも優先されます。 |

[API](https://platform.openai.com/docs/api-reference/responses/create)
1-1-10-1 Create a model response[モデルレスポンスを作成する]
Text Input

```python
response = client.responses.create(
  model="gpt-4o",
  input="Tell me a three sentence bedtime story about a unicorn."
)
```

1-1-10-2 Image Input

```python
response = client.responses.create(
    model="gpt-4o",
    input=[
        {
            "role": "user",
            "content": [
                { "type": "input_text", "text": "what is in this image?" },
                {
                    "type": "input_image",
                    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                }
            ]
        }
    ]
)
```

1-1-10-3 Web Search

```python
response = client.responses.create(
    model="gpt-4o",
    tools=[{ "type": "web_search_preview" }],
    input="What was a positive news story from today?",
)
```

1-1-10-4 File Search

```python
response = client.responses.create(
    model="gpt-4o",
    tools=[{
      "type": "file_search",
      "vector_store_ids": ["vs_1234567890"],
      "max_num_results": 20
    }],
    input="What are the attributes of an ancient brown dragon?",
)
```

1-1-10-5 Streaming

```python
response = client.responses.create(
  model="gpt-4o",
  instructions="You are a helpful assistant.",
  input="Hello!",
  stream=True
)

for event in response:
  print(event)
```

1-1-11 Get a model response[模範的な回答を得る]

指定された ID を持つモデル応答を取得します。

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.retrieve("resp_123")
print(response)
```

1-1-12 Delete a model response[モデル応答を削除する]

指定された ID のモデル応答を削除します。

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.del("resp_123")
print(response)
```

1-1-13 List input items[入力項目をリストする]

指定された応答の入力項目のリストを返します。

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.input_items.list("resp_123")
print(response.data)
```

1-1-14 The response object[レスポンスオブジェクト]

```python
{
  "id": "resp_67ccd3a9da748190baa7f1570fe91ac604becb25c45c1d41",
  "object": "response",
  "created_at": 1741476777,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd3acc8d48190a77525dc6de64b4104becb25c45c1d41",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "The image depicts a scenic landscape with a wooden boardwalk or pathway leading through lush, green grass under a blue sky with some clouds. The setting suggests a peaceful natural area, possibly a park or nature reserve. There are trees and shrubs in the background.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "generate_summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 328,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 52,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 380
  },
  "user": null,
  "metadata": {}
}

```

1-1-15 The input item list[入力項目リスト]

```python
{
  "object": "list",
  "data": [
    {
      "id": "msg_abc123",
      "type": "message",
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "Tell me a three sentence bedtime story about a unicorn."
        }
      ]
    }
  ],
  "first_id": "msg_abc123",
  "last_id": "msg_abc123",
  "has_more": false
}

```

