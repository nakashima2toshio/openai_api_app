##### Menu [Quick_start]

##### [Core_concepts]

##### 1-1 Text and prompting：
1-1-1 Text generation and prompting[テキスト生成とプロンプト]
1-1-2 Message roles and instruction following[メッセージの役割と指示のフォロー]
1-1-3 Instructions versus developer messages in multi-turn conversations[複数ターンの会話における指示と開発者メッセージ]
1-1-4 Choosing a model[モデルの選択]
1-1-5 Prompt engineering[迅速なエンジニアリング]

| ロール    | 説明                                                                                                      |
| --------- | --------------------------------------------------------------------------------------------------------- |
| developer | developerメッセージは、アプリケーション開発者によって提供される、userメッセージよりも優先される指示です。 |
| user      | userメッセージは、エンドユーザーによって提供される、developerメッセージの背後に重み付けされた指示です。   |
| assistant | モデルによって生成されたメッセージにはassistant役割があります。                                           |

[API:responses](https://platform.openai.com/docs/api-reference/responses)Responses
1-1-10 Create a model response[モデルレスポンスを作成する]
1-1-11 Get a model response[模範的な回答を得る]
1-1-12 Delete a model response[モデル応答を削除する]
1-1-13 List input items[入力項目をリストする]
1-1-14 The response object[レスポンスオブジェクト]
1-1-15 The input item list[入力項目リスト]


#### 1-2 images and vision：[画像とビジョン](https://platform.openai.com/docs/guides/images?api-mode=responses)　視覚機能を使用して画像を理解する方法を学びます。

[Docs](https://platform.openai.com/docs/guides/images?api-mode=responses)
1-2-1 ビジョンとは、画像をモデルへの入力プロンプトとして使用し、画像内のデータに基づいて応答を生成する機能です。
1-2-2 Passing a URL[URLを渡す]
1-2-3 Passing a Base64 encoded image[Base64を渡す]

- Image input requirements:[画像入力要件]
- Specify image input detail level[画像入力の詳細レベルを指定する]
  1-2-4 Provide multiple image inputs[複数の画像入力を提供する]

[API:images](https://platform.openai.com/docs/api-reference/images/create)

- Create image[画像を作成]プロンプトに応じて画像を作成します。
- Create image edit[画像編集を作成]元の画像とプロンプトを指定して、編集または拡張された画像を作成します。
- Create image variation[画像のバリエーションを作成する]指定された画像のバリエーションを作成します。
- The image object[画像オブジェクト]OpenAI API によって生成された画像の URL またはコンテンツを表します。
-

1-3 Audio and speech：[音声とスピーチ](https://platform.openai.com/docs/guides/audio)OpenAI API のオーディオと音声機能を調べます。
[Docs]オーディオのAPIは以下の4種類ある。＜適切に利用しよう＞


| API             | サポートされているモダリティ | ストリーミングサポート           |
| --------------- | ---------------------------- | -------------------------------- |
| リアルタイムAPI | オーディオとテキストの入出力 | オーディオストリーミングの入出力 |
| チャット完了API | オーディオとテキストの入出力 | オーディオストリーミング出力     |
| 文字起こしAPI   | オーディオ入力               | オーディオストリーミング出力     |
| 音声API         | テキスト入力と音声出力       | オーディオストリーミング出力     |

[API:audio](https://platform.openai.com/docs/api-reference/audio)
1-3-10 Create speech[音声生成API] *Text to Speech*
1-3-11 Create transcription[音声文字起こしAPI]
1-3-12 Create translation[音声翻訳API]
1-3-13 The transcription object (JSON)[]
1-3-14 The transcription object (Verbose JSON)[]
1-3-15 Stream Event (transcript.text.delta)[]
1-3-16 Stream Event (transcript.text.done)[]

##### --------------------------------------------------------------

1-4 Structured Outputs：[構造化された出力](https://platform.openai.com/docs/guides/structured-outputs)モデルがデータを取得してアクションを実行できるようにします。

##### --------------------------------------------------------------

1-5 Function calling：[関数呼び出し](https://platform.openai.com/docs/guides/function-calling?api-mode=responses)モデルがデータを取得してアクションを実行できるようにします。

##### --------------------------------------------------------------

1-6 Conversation state：[会話状態](https://platform.openai.com/docs/guides/conversation-state?api-mode=responses)モデルの対話中に会話の状態を管理する方法を学びます。

1-7 streaming：[ストリーミングAPIレスポンス](https://platform.openai.com/docs/guides/streaming-responses?api-mode=responses)サーバー送信イベントを使用して OpenAI API からモデル応答をストリーミングする方法を学習します。

1-8 File inputs：[ファイル入力](https://platform.openai.com/docs/guides/pdf-files?api-mode=responses)OpenAI API への入力として PDF ファイルを使用する方法を学びます。

1-9 Reasoning：[推論モデル](https://platform.openai.com/docs/guides/reasoning?api-mode=responses)高度な推論と問題解決モデルを探ります。

1-10 Evaluating model performance：[モデルのパフォーマンスの評価]()評価を通じてモデル出力をテストし、改善します。

#### 2 [Built-in_tools]

2-1 Using built-in tools：[組み込みツール](https://platform.openai.com/docs/guides/tools?api-mode=responses)Web 検索やファイル検索などの組み込みツールを使用して、モデルの機能を拡張します。

2-2 Web search：[ウェブ検索](https://platform.openai.com/docs/guides/tools-web-search?api-mode=responses)モデルが応答を生成する前に、Web で最新情報を検索できるようにします。

```python
client.responses.create(
    tools=[{"type": "web_search_preview"}]
```

2-3 File search：[ファイル検索](https://platform.openai.com/docs/guides/tools-file-search)応答を生成する前に、モデルがファイル内の関連情報を検索できるようにします。

2-4 computer use：[コンピュータの使用](https://platform.openai.com/docs/guides/tools-computer-use)あなたの代わりにタスクを実行できるコンピューター使用エージェントを構築します

#### 3[Agent]()

3-1 Building agents

3-2 Voice agents

3-3 Agents SDK

#### 4[Realtime_api]

4-1 Using the Realtime API

4-2 Realtime conversations

4-3 Realtime transcription

4-4 Voice activity detection

#### 5 Specialized models

5-1 Image generation --------------------------------------------------------------
[API:images]
5-1-1 Image generation[画像生成](https://platform.openai.com/docs/guides/image-generation?language=python) [API]client.images.generate

5-2-1 Text to speech[テキスト読み上げ](https://platform.openai.com/docs/guides/text-to-speech) [API]client.audio.speech.with_streaming_response.create

5-3-1 speech to text[音声テキスト変換](https://platform.openai.com/docs/guides/speech-to-text) [API]client.audio.transcriptions.create

#### 5-4 embeddings -----------------------------------------------
5-4-1 Embedding 取得・基本動作確認
5-4-2 文章検索 (Similarity Search)
5-4-3 コード検索
5-4-4 レコメンデーションシステム
5-4-5 Embedding の次元削減・正規化
5-4-6 質問応答 (QA) システムへの Embeddings 活用
5-4-7 可視化 (t-SNEなど) とクラスタリング
5-4-8 機械学習モデルでの回帰・分類タスク
5-4-9 ゼロショット分類

##### --------------------------------------------------------
5-5 Moderation
-----------------

##### --------------------------------------------------------
6 OpenAI Platform
-----------------

6-1 Fine-tuning

6-2 distillation

6-3 Retrieval

6-4 Evaluations

6-5 Batch

6-6 Prompt generation

=========================
