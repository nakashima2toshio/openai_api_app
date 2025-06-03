はじめに　・・・　色々と整理する

#### テキスト生成：　 response-API と　chat completions の比較：
   （結論） → Responses-APIを利用する!

ChatGPTのイメージのAIは、Question & Answerである。
OpenAIには、Responses-APIとchat completions-APIの２種類ある。
下記の表は両者の比較表である。


| 番号 | 比較項目                   | **Responses API**                                                                                                                                                                                                                          | **Chat Completions API**                                                                                                                                                                   |
| :--: | :------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  1  | **概要・位置付け**         | 最新のコア API かつエージェント API のプリミティブ。<br>新規ユーザーやツール連携を必要とするエージェント的なアプリケーションに推奨。<br>イベント駆動型アーキテクチャで、マルチステップの会話や推論を簡単に実装可能。                       | 業界標準のチャット API。<br>永続的にサポートされる予定。<br>ツールを必要としない一般的なチャット・テキスト生成に適しており、既に広く利用されている。                                       |
|  2  | **主な機能・対応分野**     | - テキスト生成<br>- 近日実装のオーディオ・コードインタープリター<br>- ビジョン (将来的に拡張の可能性)<br>- 構造化出力<br>- 関数呼び出し<br>- Web検索、ファイル検索、コンピュータ使用などの内蔵ツールに対応（エージェントワークフロー向き） | - テキスト生成<br>- 既存のチャット機能全般<br>- 構造化出力（responses_format ではなく text.format など別形状）<br>- 関数呼び出し（形状は異なる）<br>- オーディオ・ビジョン対応はまだ限定的 |
|  3  | **レスポンスの構造**     | -`response.output` フィールドを中心に返される<br>- 返却されるオブジェクトは `type: "message"`, `role: "assistant"`, `content` などの形式<br>- `output_text` ヘルパーがあり、簡単にテキストを取得可能                                       | -`choices` 配列を返す<br>- 各 `choice` に `message` オブジェクト（`role`, `content`）を含む<br>- SDK 側で `output_text` に相当する簡易ヘルパーは用意されていない                           |
|  4  | **会話の状態管理**         | - ステートフルなイベントを明確に扱える<br>- `previous_response_id` を使うことで複数ターンの会話を容易に継続可能<br>- 各イベントの差分（追加テキストなど）がセマンティックに扱われる                                                        | -`messages` 配列全体を都度送る必要がある<br>- トークン生成中に `content` が連続的に追加されるため、状態を手動で追跡する必要がある<br>- 会話の長期的な継続はユーザー側で工夫が必要          |
|  5  | **ツール連携**             | - ウェブ検索、ファイル検索、コンピュータ操作などのエージェント向け機能が組み込みで利用可能<br>- アプリケーションからエージェントワークフローを構築・統合しやすい                                                                           | - 組み込みツールは非対応<br>- 外部ツールとの連携はユーザーがカスタムで実装する必要がある                                                                                                   |
|  6  | **保存のデフォルト設定**   | -**新規アカウントではデフォルトで保存**<br>- 保存を無効にする場合は `store: false` を設定                                                                                                                                                  | - 新規アカウントの場合、現在はデフォルトで保存されるように変更済み（以前はデフォルト非保存だった）<br>- 保存を無効にする場合は同様に `store: false` を設定                                 |
|  7  | **関数呼び出しの扱い**     | - 関数呼び出しリクエストや応答の形式が独自（構造が異なる）<br>- 関数呼び出しガイドにて詳細が記載                                                                                                                                           | - 関数呼び出しの設定・応答の形式が別途用意されている<br>- Responses API に比べると形状が簡潔だが、ツール統合を想定した機能は限定的                                                         |
|  8  | **構造化出力**             | -`response_format` ではなく `text.format` のような形状を使用<br>- 出力内容に応じてセマンティックイベントが発行され、構造化データを扱いやすい                                                                                               | - 従来の`ChatCompletion` 形式に準拠<br>- choices の `message.content` を解析して構造化データを取り出すか、関数呼び出し形式で受け取る必要がある                                             |
|  9  | **推論オプション**         | -`reasoning.effort` を使用                                                                                                                                                                                                                 | -`reasoning_effort` を使用                                                                                                                                                                 |
|  10  | **新しいモデルのサポート** | - 可能な限り Chat Completions API と同等に新モデルを提供<br>- 組み込みツールを使うモデル（例: computer usage モデル）などは Responses API 専用になる場合がある                                                                             | - 業界標準として継続的に新モデルが追加される<br>- エージェント系ツールが不要なモデル（主に会話用途）は Chat Completions API にも追加                                                       |
|  11  | **ユースケースの推奨**     | - エージェントワークフローや複数モデルの連携が必要なアプリに最適<br>- 状態管理やイベントドリブンの処理を簡単にしたい場合に有効<br>- 新規ユーザーに推奨                                                                                     | - 一般的なチャットボットやシンプルなテキスト生成用途に適している<br>- 既に広く導入されており、プロダクション実績が多い                                                                     |
|  12  | **今後の展開**             | - OpenAI が今後エージェント構築の基盤として推進<br>- Assistant API の機能を取り込みながら、2026 年前半を目標に統合・完全移行を目指す<br>- 「コードインタープリター」などの機能も順次追加予定                                               | - 今後も無期限でサポートされる<br>- 新しいモデル・機能（ツール連携以外）は引き続き対応していく<br>- 業界標準 API として位置づけられている                                                  |

# (1) 概要

AI技術の習得のため、OpenAIのAPI仕様とAPIの使い方を学びたい。
作成したいサンプルプログラムは、フレームワークとして **streamlit** の環境を利用し、OpenAIのAPIの機能を確かめるためのPythonコードである。
主として参考にするのは、OpenAIのDocの資料である。([https://platform.openai.com/docs/overview](https://platform.openai.com/docs/overview))
このDocの左メニューの **Core concepts** の **Text and prompting** から資料を確認しつつ、これらの機能を理解するためにサンプルプログラムを作成する。
ここで利用するOpenAIのAPIは、 **API Reference** ([https://platform.openai.com/docs/api-reference/introduction](https://platform.openai.com/docs/api-reference/introduction)) の資料を参照する。

---

# (2) 確認技術・内容

OpenAIのDocの資料を参照。([https://platform.openai.com/docs/overview](https://platform.openai.com/docs/overview))

- 作成する資料の題目と作成関数の対応を以下に示す。
- 大項目は以下の9項目である。

  1. (2-1) Core Concept
  2. (2-2) Built-in Tools
  3. (2-3) Building agents
  4. (2-4) Realtime API
  5. (2-5) Specialized models
  6. (2-6) Specialized models
  7. (2-7) OpenAI Platform
  8. (2-8) Best practises
  9. (2-9) Assistants API
- 各大項目の詳細化: 以下はそれぞれの大項目の詳細化である。
- **各詳細項目** には以下の詳細項目を記述する。

  - （1）作成サンプル関数名
  - （2）利用するAPI
  - （3）作成サンプル関数の仕様（IPO: Input, Process, Output）
    - （入力）Input
    - （処理）Process
    - （出力）Output
  - （4）

---

## (2-1) Core Concept

Docの資料を参照（[https://platform.openai.com/docs/guides/text?api-mode=chat](https://platform.openai.com/docs/guides/text?api-mode=chat)）

### (2-1-1) Text and prompting

- （1）Text inputs and outputs
- （2）利用するAPI

  - `client.chat.completions.create`
  - response
- （3）作成サンプル関数の仕様

  - （入力）Input
  - （処理）Process
  - （出力）Output
- （4）

---

### (2-1-2) images and vision

・image input

---

### (2-1-3) Audio and speech

---

### (2-1-4) Structured Outputs

・structured outputs

---

### (2-1-5) Function calling

・function calling

---

### (2-1-6) Conversation state

・conversation state

---

### (2-1-7) Streaming

---

### (2-1-8) File inputs

---

### (2-1-9) Reasoning

---

## (2-2) Built-in Tools

Docの資料を参照（[https://platform.openai.com/docs/guides/tools?api-mode=chat](https://platform.openai.com/docs/guides/tools?api-mode=chat)）

### (2-2-1) Using built-in tools

・Extend the models with tools

---

### (2-2-2) Web search

---

### (2-2-3) File search

---

### (2-2-4) Computer use

---

## (2-3) Building agents

Docの資料を参照（[https://platform.openai.com/docs/guides/agents](https://platform.openai.com/docs/guides/agents)）

### (2-3-1) Building agents

---

### (2-3-2) Voice agents

---

### (2-3-3) Agents SDK

([https://openai.github.io/openai-agents-python/](https://openai.github.io/openai-agents-python/))

---

## (2-4) Realtime API

### (2-4-1) Using the Realtime API

---

### (2-4-2) Realtime conversations

---

### (2-4-3) Realtime transcription

---

### (2-4-4) Voice activity detection

---

## (2-5) Specialized models

---

## (2-6) Specialized models

---

## (2-7) OpenAI Platform

---

## (2-8) Best practises

---

## (2-9) Assistants API
