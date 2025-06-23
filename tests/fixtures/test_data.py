# tests/fixtures/test_data.py
# テスト用データ定義

# テキストサンプル
TEXT_SAMPLES = {
    "empty": "",
    "short": "短い",
    "medium": "これは中程度の長さのテストテキストです。" * 5,
    "long": "これは長いテストテキストです。" * 50,
    "japanese": "これは日本語のテストです。OpenAI APIを使用しています。",
    "english": "This is an English test. We are using OpenAI API.",
    "mixed": "This is 混合 text with English and 日本語.",
    "special_chars": "特殊文字：!@#$%^&*()[]{}|;':\",./<>?",
    "unicode": "🚀🤖🧪✅❌⚡📊🎯🔧"
}

# メッセージサンプル
MESSAGE_SAMPLES = [
    {"role": "user", "content": "こんにちは"},
    {"role": "assistant", "content": "こんにちは！どのようにお手伝いできますか？"},
    {"role": "user", "content": "天気を教えて"},
    {"role": "assistant", "content": "申し訳ございませんが、リアルタイムの天気情報は提供できません。"}
]

# 構造化出力テストケース
STRUCTURED_OUTPUT_CASES = [
    {
        "task": "商品レビューの分析",
        "input": "この商品は素晴らしいです。品質が高く、使いやすいです。ただし、価格がもう少し安ければと思います。",
        "expected_keys": ["評価", "良い点", "改善点"]
    },
    {
        "task": "テキストの要約",
        "input": "人工知能（AI）は、人間の知能を模倣する技術です。機械学習、深層学習、自然言語処理などの分野があります。近年、ChatGPTなどの大規模言語モデルが注目されています。",
        "expected_keys": ["タイトル", "要点", "結論"]
    },
    {
        "task": "感情分析",
        "input": "今日はとても楽しい一日でした！友達と会って美味しい食事をして、映画も見ました。",
        "expected_keys": ["感情", "強度", "理由"]
    }
]
