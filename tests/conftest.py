# tests/conftest.py
# tests/conftest.py
"""pytest共通設定とfixture定義"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# プロジェクトルートをパスに追加
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ==================================================
# セッションレベルfixture
# ==================================================

@pytest.fixture(scope="session")
def setup_test_environment():
    """テスト環境の初期セットアップ"""
    print("\n🔧 テスト環境セットアップ開始...")

    # 必要なディレクトリ作成
    os.makedirs("logs/test", exist_ok=True)
    os.makedirs("tests/fixtures", exist_ok=True)

    # テスト用環境変数設定
    original_env = {}
    test_env_vars = {
        "TEST_MODE"     : "true",
        "OPENAI_API_KEY": "sk-test-dummy-key",
        "PYTHONPATH"    : str(PROJECT_ROOT),
        "LOG_LEVEL"     : "DEBUG"
    }

    for key, value in test_env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    yield

    # クリーンアップ
    print("\n🧹 テスト環境クリーンアップ...")
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


# ==================================================
# 関数レベルfixture
# ==================================================

@pytest.fixture
def mock_streamlit():
    """Streamlitのモック"""
    # Streamlitの完全モック
    streamlit_mock = MagicMock()

    # session_stateの設定
    streamlit_mock.session_state = {}

    # よく使われる関数のモック
    streamlit_mock.chat_input.return_value = None
    streamlit_mock.button.return_value = False
    streamlit_mock.selectbox.return_value = "gpt-4o-mini"
    streamlit_mock.text_area.return_value = ""
    streamlit_mock.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]

    with patch.dict('sys.modules', {'streamlit': streamlit_mock}):
        yield streamlit_mock


@pytest.fixture
def mock_openai_client():
    """OpenAI APIクライアントのモック"""
    with patch('openai.OpenAI') as mock_openai:
        # クライアントインスタンスのモック
        client_mock = Mock()

        # レスポンスオブジェクトのモック
        response_mock = Mock()
        response_mock.id = "resp_test_123"
        response_mock.model = "gpt-4o-mini"
        response_mock.output = [
            Mock(
                type="message",
                content=[
                    Mock(type="output_text", text="テスト応答メッセージ")
                ]
            )
        ]
        response_mock.usage = Mock(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )

        # responses.create の戻り値設定
        client_mock.responses.create.return_value = response_mock
        mock_openai.return_value = client_mock

        yield client_mock


@pytest.fixture
def sample_config():
    """テスト用設定データ"""
    return {
        "models": {
            "default"  : "gpt-4o-mini",
            "available": ["gpt-4o-mini", "gpt-4o"]
        },
        "api"   : {
            "timeout"    : 30,
            "max_retries": 3
        },
        "ui"    : {
            "page_title": "Test OpenAI API Demo",
            "layout"    : "wide"
        }
    }


@pytest.fixture
def sample_texts():
    """テスト用テキストサンプル"""
    return {
        "empty"   : "",
        "short"   : "短いテキスト",
        "medium"  : "これは中程度の長さのテストテキストです。" * 5,
        "long"    : "これは長いテストテキストです。" * 50,
        "japanese": "これは日本語のテストです。",
        "english" : "This is an English test.",
        "mixed"   : "Mixed 混合 text with English and 日本語.",
        "special" : "特殊文字：!@#$%^&*()[]{}|;':\",./<>?",
        "unicode" : "🚀🤖🧪✅❌⚡📊🎯🔧"
    }


# ==================================================
# マーカー設定
# ==================================================

def pytest_configure(config):
    """pytestマーカーの設定"""
    config.addinivalue_line(
        "markers", "unit: 単体テスト"
    )
    config.addinivalue_line(
        "markers", "integration: 統合テスト"
    )
    config.addinivalue_line(
        "markers", "slow: 実行時間の長いテスト"
    )
    config.addinivalue_line(
        "markers", "api: API呼び出しテスト"
    )
