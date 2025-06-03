#####

■ 全体概要・建て付け
このコードは、OpenAIのAPIをPythonから使って、Q&Aのやり取りをWeb画面上で実現するためのStreamlitアプリです。

Streamlit（ストリームリット）：Pythonで手軽にWebアプリ（フォーム・ダッシュボード）が作れるライブラリ。

OpenAI API：AIモデル（GPT-4oなど）に「メッセージ」を送信し、AIの返答（テキストや画像など）をもらうための仕組み。

全体の流れ
Webフォームで質問入力（Streamlit UI）

入力内容をOpenAI APIへ送信

AIの返答をWebに表示

■ 対象関数 qa_sample の説明
この関数は、「1問1答型Q&A」（One Shot）のサンプルです。

やっていること（ざっくり）
画面に「質問入力フォーム」を作る

ユーザーが入力→送信ボタンで、AIに質問を投げる

AIの回答をコード表示（st.code）で見せる

「次の質問」ボタンでリセットもできる

詳しく解説
1. モデル選択
```python
selected_model_value = config_model()
```
**AIモデル（gpt-4oなど）**をサイドバーで選べる。

2. 質問フォーム
```python
with st.form(key="qa_form"):
    user_input = st.text_area("ここにテキストを入力してください:", height=75)
    submit_button = st.form_submit_button(label="送信")
```
ここでユーザーの質問を入力し、「送信」でAPIリクエストへ進む。

3. OpenAI APIにリクエスト
```python

input_messages = make_input_messages(
    developer_text,    # 開発者プロンプト（ガイダンス）
    user_input,        # ユーザー入力
    assistant_text     # 「日本語で答えて」などの指定
)
response = create_responses_api(model=selected_model_value, input_messages=input_messages)
```

**AIへ渡す「メッセージ群」**を用意。
```bash
developer_text：AIに専門家として説明してほしい、という指示
user_input：ユーザーの実際の質問
assistant_text：「日本語で答えて」等の制御
```
client.responses.createでAPI呼び出しを実行。

4. 回答の表示
```python
extracted_text_list = extract_text_from_response(response)
for i, t in enumerate(extracted_text_list, 1):
    st.code(t)
```
APIの返答からテキスト部分を抽出し、きれいに表示。

■ 説明のポイント
1. client.responses.create の解説
```python
response = client.responses.create(
    model=model,
    input=input_messages
)
```
OpenAIの「Responses API」の基本形。
・model：どのAIモデルを使うか（例：gpt-4o）。
・input：AIに渡すメッセージのリスト（EasyInputMessageParam型など）。

2. メッセージのパラメータ構成
```python
[
    EasyInputMessageParam(role="developer", content=dev_txt),
    EasyInputMessageParam(role="user", content=user_txt),
    EasyInputMessageParam(role="assistant", content=assistant_txt)
]
```
```bash
role（役割）
"developer"：AIへシステムガイダンス
"user"：ユーザーの質問本文
"assistant"：AIに対する回答スタイル等の指示
```
```bash
content（内容）
それぞれ役割に応じたテキスト
```
この3段構えで、「どんなスタンスでどう答えるか」まで細かく指定できます。

■ まとめ：初級プログラマ向けアドバイス
OpenAI APIは、「メッセージ（役割＋内容）」をリスト形式で送るのが基本形

roleで「開発者」「ユーザー」「アシスタント」など立場を分けられる

contentで各メッセージの内容を指定

StreamlitでWebフォーム＋API連携が簡単

st.formでフォーム作成、st.text_areaで入力欄

入力内容をAPIへ→返答をst.code等で出力

APIレスポンスは一度「取り出し関数」で整形

構造化された出力（例：extract_text_from_response）

■ その他・応用のヒント
「会話履歴を持たせる」→qa_memory_sample参照

画像入力や構造化出力も同じAPIで可能（本サンプルに他例あり）

モデルを選べば、精度・速度の使い分けも可能

【サンプル全体の設計思想】
誰でも簡単にAIと会話できるWebアプリをPython＋Streamlitで構築

入力・出力・API呼び出しを関数で分離し、見通し良く・カスタムしやすくしてある

パラメータやプロンプト設計を変えるだけで、用途に合わせたAIアプリが作れるようになっている

公式ドキュメント・サンプル
OpenAI Responses API Spec

OpenAI Cookbook：responses_example