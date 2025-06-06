### サンプルプログラム一覧

以下の6つのデモを Streamlit 上で切り替えながら実行できる形にしました。

1. **イベント情報抽出デモ**
2. **数学的思考ステップデモ**
3. **UIコンポーネント生成デモ**
4. **エンティティ抽出デモ**
5. **条件分岐スキーマデモ**
6. **モデレーション＆拒否処理デモ**

---

### 各デモの実装フロー

1. **機能概要・利用API**
2. **入力情報**
3. **処理の説明**
   - JSON Schema を伴う Responses API の呼び出し
4. **出力の説明**
   - 生成された構造化 JSON の表示

---

### OpenAI API の Structured Outputs 機能まとめ

#### 1. 目的

`Structured Outputs` は、OpenAI モデルの出力が常に指定した JSON Schema に準拠するよう保証し、以下を実現します。

- **一貫性・信頼性**：必須フィールドの欠落や不正な enum 値を防ぐ
- **型安全性**：追加のバリデーションや再試行が不要
- **明示的な拒否**：安全性に基づくモデルの拒否をプログラムで検知可能
- **簡易プロンプト**：強調的な整形プロンプト不要

#### 2. 機能の説明

- **関数呼び出し（function calling）経由**
  システム内のツールやデータと連携する際に利用。
- **`text.format`（response_format）経由**
  ユーザーへのレスポンスを所定の構造で提供する際に利用。

---

#### 3. 利用例と詳細説明

##### 3.1 思考の連鎖（Chain of Thought）

- **利用目的**
  モデルの思考プロセスをステップバイステップで明示。
- **詳細説明**
  各ステップに「説明」と「出力」を含む配列を生成し、最後に `final_answer` を返却。
- **ユースケース**
  教育アプリ、数学チューター など

##### 3.2 構造化データ抽出（Structured Data Extraction）

- **利用目的**
  自然言語から特定データを抽出し、JSON 形式に整理。
- **詳細説明**
  イベント情報（名称、日時、参加者など）を抽出し、明示的なフィールドに詰める。
- **ユースケース**
  イベントスケジューラ、CRM、情報解析サービス など

##### 3.3 UI生成（UI Generation）

- **利用目的**
  モデルの出力を動的な UI コンポーネント構造として利用。
- **詳細説明**
  再帰的な JSON スキーマで UI ツリーを定義し、クライアント側でそのまま描画可能。
- **ユースケース**
  ノーコードツール、動的フォーム生成、ダッシュボード構築 など

##### 3.4 節度（Moderation）

- **利用目的**
  不適切リクエストをモデルが拒否し、その理由をプログラムで検知。
- **詳細説明**
  拒否時に `refusal` フィールドを含むオブジェクトを返し、エラー処理を容易に。
- **ユースケース**
  チャットボット、コンテンツ管理、コンプライアンス対応 など

---

#### 4. 利用方法の選択

##### 4.1 関数呼び出し経由での使用

- ツール／データベースとの連携が主目的
- API 呼び出しや外部システム操作を伴う場合に最適

##### 4.2 `text.format` 経由での使用

- ユーザー向けに構造化されたレスポンスを返す場合
- UI 表示やクライアント側の後処理でスキーマを活用したい場合に最適

---

#### 5. 試してみる

- Playground や API でスキーマ定義をその場で編集・検証可能
- 構造化レスポンスのメリットをハンズオンで体感

---

#### 6. 推奨されるモデル

- `gpt-4o-mini`
- `gpt-4o-2024-08-06`
- `gpt-4.5-preview-2025-02-27` 以降
- `o3-mini-2025-1-31` 以降

---

#### 7. Structured Outputs vs JSON mode

| 項目                | Structured Outputs       | JSON mode                 |
| ------------------- | ------------------------ | ------------------------- |
| 有効な JSON 出力    | 〇                       | 〇                        |
| スキーマ準拠        | 〇                       | ×                         |
| 対応モデル          | gpt-4o-mini, gpt-4o-*…   | gpt-3.5-turbo, gpt-4-*…   |
| 有効化              | `format: json_schema`    | `format: json_object`     |

Structured Outputs は JSON mode の進化版としてスキーマ準拠を保証するため、可能な限りこちらを推奨します。
