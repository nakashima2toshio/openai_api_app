# tests/test_basic.py
# 最優先で実行する基本動作確認テスト
# 直接Python実行（最も簡単）
# python tests/test_basic.py

import sys
import os
import pytest
from pathlib import Path

# パス設定
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestEnvironment:
    """環境確認テスト"""

    def test_python_version(self):
        """Python バージョン確認"""
        assert sys.version_info >= (3, 8), f"Python 3.8以上が必要です。現在: {sys.version}"
        print(f"✅ Python バージョン: {sys.version}")

    def test_project_structure(self):
        """プロジェクト構造確認"""
        required_files = [
            "a10_00_openai_skeleton.py",
            "helper.py",
            "config.yaml"
        ]

        for file in required_files:
            file_path = PROJECT_ROOT / file
            assert file_path.exists(), f"必須ファイルが見つかりません: {file}"
            print(f"✅ ファイル存在確認: {file}")

    def test_dependencies(self):
        """基本依存関係確認"""
        required_modules = [
            "streamlit",
            "openai",
            "tiktoken",
            "yaml"
        ]

        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ モジュール確認: {module}")
            except ImportError:
                missing_modules.append(module)

        if missing_modules:
            pytest.fail(f"必要なモジュールが不足: {missing_modules}")


class TestBasicImports:
    """基本インポートテスト"""

    def test_import_helper(self):
        """helper.py インポートテスト"""
        try:
            import helper

            # 主要クラスの存在確認
            required_classes = [
                'ConfigManager',
                'MessageManager',
                'TokenManager',
                'UIHelper',
                'ResponseProcessor',
                'DemoBase'
            ]

            for class_name in required_classes:
                assert hasattr(helper, class_name), f"クラスが見つかりません: {class_name}"
                print(f"✅ クラス確認: {class_name}")

        except Exception as e:
            pytest.fail(f"helper.py インポート失敗: {e}")

    def test_import_skeleton(self):
        """skeleton.py インポートテスト"""
        try:
            import a10_00_openai_skeleton as skeleton

            # 主要クラスの存在確認
            required_classes = [
                'SimpleChatDemo',
                'StructuredOutputDemo',
                'TokenCounterDemo',
                'DemoManager',
                'OpenAISkeletonApp'
            ]

            for class_name in required_classes:
                assert hasattr(skeleton, class_name), f"クラスが見つかりません: {class_name}"
                print(f"✅ クラス確認: {class_name}")

        except Exception as e:
            pytest.fail(f"skeleton.py インポート失敗: {e}")


class TestBasicFunctionality:
    """基本機能テスト"""

    def test_config_loading(self):
        """設定ファイル読み込みテスト"""
        from helper import ConfigManager

        # 設定ファイル読み込み
        config = ConfigManager("config.yaml")

        # 基本設定の確認
        default_model = config.get("models.default")
        assert default_model is not None, "デフォルトモデルが設定されていません"
        print(f"✅ デフォルトモデル: {default_model}")

        # デフォルト値テスト
        non_existent = config.get("non.existent.key", "default_value")
        assert non_existent == "default_value", "デフォルト値が正しく動作していません"
        print("✅ デフォルト値機能: OK")

    def test_token_counting(self):
        """トークンカウント基本テスト"""
        from helper import TokenManager

        # 基本的なトークンカウント
        test_text = "これはテストです。"
        token_count = TokenManager.count_tokens(test_text, "gpt-4o-mini")

        assert isinstance(token_count, int), "トークン数が整数で返されていません"
        assert token_count > 0, "トークン数が0以下です"
        print(f"✅ トークンカウント: {test_text} → {token_count} tokens")

        # 空文字テスト
        empty_count = TokenManager.count_tokens("", "gpt-4o-mini")
        assert empty_count >= 0, "空文字のトークン数が負の値です"
        print(f"✅ 空文字トークンカウント: {empty_count} tokens")

    def test_demo_class_creation(self):
        """デモクラス作成テスト"""
        from a10_00_openai_skeleton import SimpleChatDemo, StructuredOutputDemo, TokenCounterDemo

        # SimpleChatDemo
        chat_demo = SimpleChatDemo("test_chat", "テストチャット")
        assert chat_demo.demo_name == "test_chat"
        assert chat_demo.title == "テストチャット"
        assert hasattr(chat_demo, 'run'), "runメソッドが存在しません"
        print("✅ SimpleChatDemo作成: OK")

        # StructuredOutputDemo
        struct_demo = StructuredOutputDemo("test_struct", "テスト構造化")
        assert struct_demo.demo_name == "test_struct"
        assert hasattr(struct_demo, 'run'), "runメソッドが存在しません"
        print("✅ StructuredOutputDemo作成: OK")

        # TokenCounterDemo
        token_demo = TokenCounterDemo("test_token", "テストトークン")
        assert token_demo.demo_name == "test_token"
        assert hasattr(token_demo, 'run'), "runメソッドが存在しません"
        print("✅ TokenCounterDemo作成: OK")


class TestIntegration:
    """統合動作テスト"""

    def test_demo_manager_creation(self):
        """DemoManager作成・統合テスト"""
        from a10_00_openai_skeleton import DemoManager

        manager = DemoManager()

        # 基本属性確認
        assert hasattr(manager, 'demos'), "demosアトリビュートが存在しません"
        assert hasattr(manager, 'run_demo'), "run_demoメソッドが存在しません"

        # 基本デモの存在確認
        expected_demos = ['simple_chat', 'structured_output', 'token_counter']
        for demo_name in expected_demos:
            assert demo_name in manager.demos, f"デモが登録されていません: {demo_name}"
            print(f"✅ デモ登録確認: {demo_name}")

    def test_main_app_creation(self):
        """メインアプリ作成テスト"""
        from a10_00_openai_skeleton import OpenAISkeletonApp

        # アプリ作成（Streamlitコンポーネントを使わない範囲で）
        app = OpenAISkeletonApp()

        assert hasattr(app, 'demo_manager'), "demo_managerが存在しません"
        assert hasattr(app, 'run'), "runメソッドが存在しません"
        print("✅ OpenAISkeletonApp作成: OK")


# ==================================================
# 実行時の動作確認
# ==================================================

if __name__ == "__main__":
    """スタンドアローン実行時の動作確認"""
    print("🧪 基本動作確認テスト開始")
    print("=" * 50)

    # 各テストクラスを手動実行
    test_classes = [
        TestEnvironment(),
        TestBasicImports(),
        TestBasicFunctionality(),
        TestIntegration()
    ]

    total_tests = 0
    passed_tests = 0

    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n📋 {class_name} 実行中...")

        # クラス内のテストメソッドを実行
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]

        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_class, method_name)
                method()
                passed_tests += 1
                print(f"  ✅ {method_name}: PASSED")
            except Exception as e:
                print(f"  ❌ {method_name}: FAILED - {e}")

    print("\n" + "=" * 50)
    print(f"🎯 テスト結果: {passed_tests}/{total_tests} PASSED")

    if passed_tests == total_tests:
        print("🎉 全ての基本テストが成功しました！")
        exit(0)
    else:
        print("⚠️ 一部のテストが失敗しました。")
        exit(1)
