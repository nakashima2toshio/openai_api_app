# tests/fixtures/mock_responses.py
"""OpenAI API モックレスポンス定義"""

MOCK_CHAT_RESPONSE = {
    "id": "resp_test_123",
    "model": "gpt-4o-mini",
    "created_at": "2025-01-01T00:00:00Z",
    "output": [
        {
            "type": "message",
            "content": [
                {
                    "type": "output_text",
                    "text": "これはテスト用の応答メッセージです。"
                }
            ]
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 8,
        "total_tokens": 18
    }
}

MOCK_JSON_RESPONSE = {
    "id": "resp_test_456",
    "model": "gpt-4o-mini",
    "output": [
        {
            "type": "message",
            "content": [
                {
                    "type": "output_text",
                    "text": '{"評価": 5, "良い点": ["高品質", "使いやすい"], "改善点": ["価格"]}'
                }
            ]
        }
    ],
    "usage": {
        "prompt_tokens": 25,
        "completion_tokens": 15,
        "total_tokens": 40
    }
}

MOCK_ERROR_RESPONSE = {
    "error": {
        "type": "invalid_request_error",
        "message": "Invalid API key provided",
        "code": "invalid_api_key"
    }
}
