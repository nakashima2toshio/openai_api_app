# tests/test_streamlit_mock.py
"""Streamlit要素のモックテスト"""

import pytest
from unittest.mock import Mock, patch
import sys

# Streamlitモックの設定
sys.modules['streamlit'] = Mock()


def test_demo_logic_with_mock():
    """デモロジックのモックテスト"""
    with patch('streamlit.selectbox') as mock_selectbox:
        mock_selectbox.return_value = "gpt-4o-mini"

        # テスト対象のインポート（モック後）
        from a10_00_openai_skeleton import SimpleChatDemo

        demo = SimpleChatDemo("test_chat", "テストチャット")
        assert demo.demo_name == "test_chat"
