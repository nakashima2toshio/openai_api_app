### OpenAI SDK ― `client.responses.create()` と `client.responses.parse()` 徹底比較
### 前提知識
- client.chat.completions（プリミィティブ）
- client.responses（こちらの利用を推奨）

##### まとめ
- チャット＋ツール＋履歴管理: responses.create()
- テキスト → 構造化データ:   responses.parse()

#### 1. サマリ表

| 観点 | `responses.create()` | `responses.parse()` |
|------|---------------------|---------------------|
| **主な役割** | マルチターン *エージェント API*  (従来の ChatCompletion + Assistants を統合) | 単発 *構造化パース API*  (Pydantic / JSON スキーマへ直結) |
| **入出力** | 1 + メッセージ配列・ツール呼び出し・履歴管理 / `Response` オブジェクト | 1 turn 文字列入力 / 戻り値は **任意の Python 型** |
| **ツール呼び出し** | 内蔵 (`file_search` など) または独自関数を自動実行 | なし |
| **履歴保存** | `store=True` でクラウド側に会話履歴保持 | なし（毎回独立） |
| **ストリーミング** | `stream=True` 安定動作 | `stream=True` はプレビュー段階 |
| **バリデーション** | JSON スキーマ強制可 (`response_format`) だが検証は手動 | SDK が自動パース & 検証 (失敗時は自動リトライ) |
| **想定シーン** | FAQ/RAG、検索・操作エージェント、マルチターンチャット | エンティティ抽出、テキスト→JSON 変換、ゴールドデータ生成 |
| **制約・注意** | コストはツール実行分増加 | マルチターン不可、`system`/`developer` メッセージ不可 |


#### 2. `responses.create()` ― 代表的なコード例

```python
from openai import OpenAI
client = OpenAI()

resp = client.responses.create(
    model="gpt-4o",
    input=[
        {"role": "user", "content": "顧客は何日以内に返品できますか？"}
    ],
    instructions="あなたは優秀なカスタマーサポート担当者です。丁寧に回答してください。",
    tools=[{"type": "file_search"}],
    store=True               # ← 会話履歴をクラウド保存
)

print(resp.output_text)      # => 「30日以内です」など
print(resp.tool_calls)       # file_search 呼び出しの詳細
next_id = resp.id            # 次回 previous_response_id で継続可能
```
##### ポイント
- 推論 ➜ ツール呼び出し ➜ 応答 が 1 回の API で完結。
- store=True により長い履歴を毎回送らずに済む。
- Assistants の run/step が不要なぶんコードがシンプル。

#### 3. responses.parse() ― 代表的なコード例
```python
from openai import OpenAI
from pydantic import BaseModel

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

client = OpenAI()
event = client.responses.parse(
    model="gpt-4o",
    input="Alice と Bob は来週金曜日に Science Fair に参加します。",
    text_format=CalendarEvent      # ← 戻り値は CalendarEvent 型
)

print(event)
# CalendarEvent(name='Science Fair', date='Fri 2025-06-13', participants=['Alice','Bob'])
```
##### ポイント
- “プロンプト＋スキーマ” を渡すと Python オブジェクト が返る。
- JSON → dict → 型変換が不要。
- 失敗時は SDK が自動で再試行 (max_retries 指定可)。
- 単発処理に特化。マルチターンやツール実行が必要なら create() を使う。

#### 4. 使い分けガイドライン
やりたいこと	                                        推奨 API
FAQ ボット / RAG / Web・ファイル検索を含む エージェント系	responses.create()
名刺 OCR → JSON、議事録 → TODO など 構造化抽出	        responses.parse()
JSON 生成しつつ複数ターン会話	                        responses.create() + response_format
単発抽出で コードを最小化	                            responses.parse()
