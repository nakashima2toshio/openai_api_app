### （1）関数 × 主なパラメータ

| 関数                              | 主なパラメータ                                                                                                                                |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `web_search_tool_param`         | `WebSearchToolParam`（`type="web_search_preview"`, `search_context_size="high"`）<br>`ResponseInputTextParam`, `ResponseInputImageParam` |
| `function_tool_param_by_schema` | `FunctionToolParam`（`name="get_exchange_rate"`, JSON‑Schema `parameters`, `strict=True`）                                               |
| `file_search_tool_param`        | `FileSearchToolParam`（`type="file_search"`, `vector_store_ids=[...]`, `max_num_results`）                                               |
| `computer_use_tool_param`       | `ComputerToolParam`（`type="computer_use_preview"`, `display_width`, `display_height`, `environment`）                                   |
| `structured_output_by_schema`   | `ResponseTextConfigParam` + `ResponseFormatTextJSONSchemaConfigParam`（`name`, `schema`, `strict=True`）                                 |
| `image_param`                   | `ResponseInputImageParam`（`image_url`, `detail="high"`）<br>`ResponseInputTextParam`                                                    |

---

### （2）関数 × 目的・概要

| 関数                              | 目的・概要                                          |
| ------------------------------- | ---------------------------------------------- |
| `web_search_tool_param`         | インターネット検索を実行し、取得記事をモデルに渡して最新情報を回答に反映させる。       |
| `function_tool_param_by_schema` | モデルが外部API（為替レート取得）を安全に自動呼び出しし、結果を回答へ組み込む。      |
| `file_search_tool_param`        | 自前ベクトルストアを意味検索し、関連文書を引用して回答する（RAG機能）。          |
| `computer_use_tool_param`       | 仮想PC/ブラウザ環境をAIが操作するRPA機能。操作結果やスクリーンショットを取得できる。 |
| `structured_output_by_schema`   | モデル出力をユーザ定義JSONスキーマへ厳密整形し、機械可読な構造化データとして取得。    |
| `image_param`                   | Vision機能。画像＋質問を送り、画像内容を理解・回答させるサンプル。           |
