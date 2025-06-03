#### OpenAI API Master Project by Toshio Nakashima ・・・　編集中!!
- 利用するモデルの選択
  - プログラムの確認は、o1-miniで、プログラム確認後は、o1を使います。
###### (nakashima2toshio@gmail.com)
- OpenAIのAPIのほぼ全部（100個くらい）の動作する・サンプルコードです。
  - 各、paython_program.pyのmainを実行、試してください。
  - アプリ仕立ては、HuggingFaceのGradioを利用しています。IPO(Input,Process,Output)の設定でOKなので。
- embedding, fine-tuningではデータの作り方(データ抽出)と実行例を示しています。
- OpenAIのAPI、ドキュメントの更新は頻繁なので、更新あり次第、対応する（つもり）です。

#### 構成・ディレクトリーの説明
- openai_api_sample_code ディレクトリー
  - サンプルプログラム（code_XXで始まるもの）です。
- openai_api_docs_sumup ディレクトリー
- サンプルデータ（*.txt)、抽出データ、抽出プログラムです。
  - paragraph_*.json: 参考資料をparagraph(段落)で分割、知識化したデータです。
  - code_*.json: 参考資料から[python-code]を抜き出し、タイトルとサブタイトルをつけたデータです。

## プログラム一覧：　[ラップ・プログラム名　API]
#### chat completions: テキスト生成
- code_1_0_chat_completions.py 
- 基本のQAを実行する。
  - (1)Default：デフォルト 	  [API]client.chat.completions.create
  - (2)Image input：イメージ入力   [API]client.chat.completions.create
  - (3)Streaming：ストリーミング     [API]client.chat.completions.create
  - (4)Functions：ファンクションズ     [API]client.chat.completions.create
    - 詳細はtools, messagesで設定する。
  - (5)Logprobs：ログ・プロッブズ      [API]client.chat.completions.create
#### Audio: 音声
- code_1_2_text_to_speech.py
  - (1) 入力テキストからオーディオを生成します。 [API]create_audio_speech(input_text, speech_file_path)
    - [model="tts-1"]
  - (2) デフォルト: 音声を入力言語に書き起こします。 [API]create_audio_transcriptions(speech_mp3, speech_file_path)
  - (3) 単語のタイムスタンプ: 音声を入力言語に書き起こします。[API]create_audio_transcription_word_timestamps(speech_mp3)
    - タイムスタンプの粒度は、response_format or verbose_jsonで設定します。
  - (4) セグメント・タイムスタンプ。 [API]create_audio_transcriptions_segment_timestamps(speech_mp3)
    - タイムスタンプの粒度を使用するには、[API]response_format or verbose_jsonを設定する必要があります
  - (5) 音声を英語に翻訳します。 [API]create_audio_transcription(speech_file_mp3)
- code_1_3_speech_to_text.py
  - (1) 文字起こし。 [API]create_audio_transcriptions(input_file_path):
    - 音声ファイルをテキストに変換する。
- code_1_4_function_calling.py　
  - 関数呼び出しで、モデルを外部ツールやシステムに接続できますgpt-4o。[API]client.chat.completions.create(model,messages,tools)
  - messages
  - tools （※超重要）
  - AI アシスタントに機能を追加したり、アプリケーションとモデル間の緊密な統合を構築したりするなど、
  - さまざまなことに役立ちます。
- code_1_5_number_of_tokens.py
  - token数：code_1_5_number_of_tokens：string, fileのtoken数をカウントする・・・料金の目安に利用する。
### Structured Outputs　・・・　超便利！ 現状は、まだ、まだだけど、大事。
- code_1_10_structured_outputs.py
  - Structured Outputsの利点は:
  - 信頼性のある型安全性: 不適切な形式の応答を検証したり再試行したりする必要がありません。
  - 明確な拒否: セキュリティに基づくモデルの拒否がプログラム的に検出可能になります。
  - 簡素化されたプロンプト: 一貫したフォーマットを達成するために強い言葉のプロンプトを使用する必要がありません。

- Structured Outputsは、
- モデルが常に指定されたJSONスキーマに従った応答を生成することを保証する機能です。
- これにより、モデルが必要なキーを省略したり、不正な列挙値を生成したりする心配がなくなります。

#### Structured Outputsの利点：
- 信頼性のある型安全性: 不適切な形式の応答を検証したり再試行したりする必要がありません。
- 明確な拒否: セキュリティに基づくモデルの拒否がプログラム的に検出可能になります。
- 簡素化されたプロンプト: 一貫したフォーマットを達成するために強い言葉のプロンプトを使用する必要がありません。
- ** Example **
- [Chain of thought]
  - モデルに対して、解決策に導くために、
  - 構造化されたステップバイステップの方法で回答を出力するように指示することができます。
- [Structured data extraction]
  - 研究論文のような非構造化データから抽出するための構造化フィールドを定義することができます。
- [How to use Structured Outputs with response_format]
  - 新しいSDKヘルパーを使用して、モデルの出力を希望する形式に解析するために
  - Structured Outputsを利用することができます。
  - または、JSONスキーマを直接指定することも可能です。
  - [SDK-OBJECT]、[Manual schema]　手順は同じ。
    - Step 1: Define your object: 
    - Step 2: Supply your object in the API call
    - Step 3: Handle edge cases
    - Step 4: Use the generated structured data in a type-safe way
  - Refusals with Structured Outputs
  - JSON mode（----> structured outputs が発展系でこっちを使う）
  - Supported schemas

#### Embedding: 埋込み　・・・　RAGの限定盤的な。
- code_2_embedding.py　[API]client.embeddings.create(model, input, encoding_format="float")
  - 入力テキストを表す埋め込みベクトルを作成します。  (1)[API]client.embeddings.create
    - """                                     (2)[API]client.embeddings.create
    - データセットから埋め込みを取得する            (3)[API]client.embeddings.create(input = [text], model=model).data[0].embedding
### 超重要：ベクターデータをFaiss-DBにローカルに保存、利用する（例）
- code_2_0_embeddings.py:  （クラウド保存・利用例）data-> embeddings -> to openai-Storage 
- code_2_embeddings_data_into_faiss_db.py：（ローカル保存・利用例）data-> Vector -> ローカルのFaiss-DBに保存する例
  - ファイルを読み込み、段落とPythonコードブロックに分割する                       (1)split_into_paragraphs(file_path)
  - テキストのリストを受け取り、OpenAI APIを使用してそれぞれのベクトル表現を取得する  (2)get_embeddings(texts, model=model_vector)
  - 与えられたベクトル表現を使用してFaissインデックスを作成する                    (3)create_faiss_index(embeddings)
  - クエリを受け取り、Faissインデックスを使用して最も類似したk個のチャンクを検索する   (4)search_chunk(query, index, df_normalized, k=5)
  - テキストデータを読み込み、ベクトル化し、正規化してFaissインデックスを作成する      (5)process_data()
  - FaissインデックスとデータフレームをファイルとしてLOCALに保存する                (6)save_data(index, df_normalized)
  - (main処理): 
  
#### Fine-tuning: ファインチューニング
- code_3_fine_tuning.py
  - app_6_1_make_fine_tuning_data_from_paragraph_dict_simple.py
  - app_6_3_make_fine_tuning_data_from_python_dict_simple.py
- 03_01_tools_function_calling.txt
- 03_02_tools_file_search.txt
- Create fine-tuning job
- List fine-tuning jobs
- List fine-tuning events
- List fine-tuning checkpoints
- Retrieve fine-tuning job
- Cancel fine-tuning
- Training format for chat models
- Training format for completions models
- The fine-tuning job object
- The fine-tuning job event object
- The fine-tuning job checkpoint object
#### Batch: バッチ
- code_4_batch.py
- Create batch
- Retrieve batch
- Cancel batch
- List batch
- The batch object
- The request input object
- The request output object
#### Files: ファイルズ
- code_5_files.py
- Upload file 
- List files
- Retrieve file
- Delete file
- Retrieve file content
- The file object
#### Uploads: アップロード
- Create upload 
- Add upload part 
- Complete upload 
- Cancel upload 
- The upload object 
- The upload part object
#### Images: イメージ
- code_7_0_images.py
  - code_7_2_vision.py
- Create image 
- Create image edit
- Create image variation 
- The image object
#### Models: モデル
- code_8_models.py
#### Moderations: 節度を作る
- code_9_moderations.py
- Create moderation 
- The moderation object
## Assistant:　アシスタント
- code_10_0_assistants.py
  - code_10_1_assistant_code_interpriter_unstreaming.py
  - code_10_2_assistant_code_interpriter_streaming_unstreaming.py
  - code_10_3_assistant_file_search_unstreaming.py
  - code_10_4_assistant_file_search_streaming.py
  - code_10_5_assistant_function_calling_unstreaming.py
  - code_10_6_assistant_function_calling_streaming.py
  -  code_10_10_structured_outputs.py
  -  code_10_11_structured_outputs_pydantic_zod.py
  - code_10_12_json_mode.py
- 10_1_assistants_overview.txt
- 10_2_assistants_quick_start.txt
- 10_3_assistants_deep_dive.txt
- 10_4_assistant_tools.txt
- 10_5_structured_outputs.txt
#### Thread: スレッド
- code_11_thread.py
- Create thread
- Retrieve thread
- Modify thread
- Delete thread
- The thread object
#### Messages: メッセージ
- code_12_messages.py
- Create message
- List messages
- Retrieve message
- Modify message
- Delete message
- The message object
#### Runs: ラン
- code_13_runs.py
- Create run
- Create thread and run
- List runs
- Retrieve run
- Modify run
- Submit tool outputs to run
  - Runが「requires_action」のステータスを持ち、required_action.type が 
  - submit_tool_outputs である場合、
  - このエンドポイントを使用して、ツールコールからの出力がすべて完了した後に、それらの出力を提出できます。
  - すべての出力は1つのリクエストで提出する必要があります。
- Cancel a run
- The run object
#### Run Steps
- code_14_run_steps.py
- Represents the steps (model and tool calls) taken during the run.
- List run steps
- Retrieve run step
- The run step object
#### Vector Stores: ベクター・ストア
- code_15_vector_stores.py
- Create vector store　　（＊）OpenAIのVector Storeを使う他、Faissを使う応用は、app_XXXを参照のこと。
- List vector stores
- Retrieve vector store
- Modify vector store
- Delete vector store
- The vector store object
#### Vector Store Files: ベクター・ストア・ファイルズ
- code_16_vector_store_files.py
- Vector store files represent files inside a vector store. 
- Create vector store file
- List vector store files
- Retrieve vector store file
- Delete vector store file
- The vector store file object

##### Vector Store File Batches
- code_17_vector_store_file_batches.py
  - ベクトルストアのファイルバッチは、複数のファイルをベクトルストアに追加するための操作を表します。
- Create vector store file batch
- Retrieve vector store file batch
- Cancel vector store file batch
- List vector store files in a batch
- The vector store files batch object

##### 18_streaming.txt
- - code_18_streaming.py
  - toolの出力を送信した後、Runの実行またはRunの再開の結果をストリームします。
- The message delta object
  - メッセージデルタ、すなわちストリーミング中にメッセージで変更されたフィールドを表します。
  - デルタは差分。
- The run step delta object
  - ランステップのデルタ、つまりストリーミング中にランステップで変更されたフィールドを表します。
- Assistant stream events
  - i.e.
```Server-Sent Events (SSE) 
event: thread.created
data: {"id": "thread_123", "object": "thread", ...}
```
## documentationからの追加項目

#### Advanced Usage: 高度な使用法：　工夫の方法、考え方と言い訳
- OpenAI のテキスト生成モデル
- (生成的事前トレーニング済みトランスフォーマーまたは大規模言語モデルと呼ばれることが多い) は、
- 自然言語、コード、および画像を理解するようにトレーニングされています。
- モデルは、入力に応じてテキスト出力を提供します。
- これらのモデルへのテキスト入力は、「プロンプト」とも呼ばれます。
- プロンプトの設計は、基本的に、タスクを正常に完了する方法の指示または例を提供することによって、
- 大規模言語モデルを「プログラム」する方法です。
- Reproducible outputs: 再現可能な出力
  - チャット完了はデフォルトでは非決定論的です 
  - (つまり、モデル出力はリクエストごとに異なる場合があります)。
  - とはいえ、seedパラメータとsystem_fingerprint応答フィールドにアクセスできるようにすることで、
  - 決定論的な出力に対する制御を提供します。
- Managing tokens
  - 言語モデルは、トークンと呼ばれるチャンク単位でテキストを読み書きします。
  - 英語では、トークンは 1 文字ほど短い場合もあれば、1 単語ほど長い場合もあります (例:aまたはapple)。
  - 言語によっては、トークンが 1 文字よりも短い場合や、1 単語よりも長い場合もあります。
- Parameter details
  - Frequency and presence penalties: 頻度と存在のペナルティ
  - Token log probabilities: トークンログ確率
  - Other parameters: その他のパラメータ
##### 組織とプロジェクト
- 準備：組織情報、プロジェクト情報などが必要な場合はAdministratorAPIを参照してください。
- code_0_organizations_and_projects.py

 code_10_0_assistants.py
├── code_10_11_structured_outputs_pydantic_zod.py
├── code_10_12_json_mode.py
├── code_10_1_assistant_code_interpriter_unstreaming.py
├── code_10_2_assistant_code_interpriter_streaming_unstreaming.py
├── code_10_3_assistant_file_search_unstreaming.py
├── code_10_4_assistant_file_search_streaming.py
├── code_10_5_assistant_function_calling_unstreaming.py
├── code_10_6_assistant_function_calling_streaming.py


├── code_11_threads.py
├── code_12_messages.py
├── code_13_runs.py
├── code_14_run_steps.py
├── code_15_vector_stores.py
├── code_16_vector_store_files.py
├── code_17_vector_store_file_batches.py
├── code_18_streaming.py
├── code_1_0_chat_completions.py
├── code_1_10_structured_outputs.py
├── code_1_2_text_to_speech.py
├── code_1_3_speech_to_text.py
├── code_1_4_function_calling.py
├── code_1_5_number_of_tokens.py


├── code_3_fine_tuning.py
├── code_4_batch.py
├── code_5_files.py
├── code_7_0_images.py
├── code_7_2_vision.py
├── code_8_models.py
├── code_9_moderations.py

