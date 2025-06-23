# tests/test_logic_only.py
"""Streamlit以外のロジック部分のテスト"""


def test_helper_functions():
    """helper.pyの関数テスト（Streamlit非依存）"""
    from helper import TokenManager, ConfigManager

    # TokenManagerのテスト
    token_count = TokenManager.count_tokens("テストテキスト", "gpt-4o-mini")
    assert isinstance(token_count, int)
    assert token_count > 0

    # ConfigManagerのテスト
    config = ConfigManager("config.yaml")
    default_model = config.get("models.default", "gpt-4o-mini")
    assert isinstance(default_model, str)
