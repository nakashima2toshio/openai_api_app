# tests/test_debug.py
"""デバッグ用テスト"""


def test_debug_environment():
    """環境デバッグ情報"""
    import sys
    import os
    from pathlib import Path

    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Environment variables:")
    for key, value in os.environ.items():
        if 'PYTHON' in key or 'PATH' in key:
            print(f"  {key}: {value}")

    # ファイル存在確認
    files_to_check = [
        "a10_00_openai_skeleton.py",
        "helper.py",
        "config.yaml"
    ]

    for file in files_to_check:
        path = Path(file)
        print(f"File {file}: {'EXISTS' if path.exists() else 'NOT FOUND'}")
        if path.exists():
            print(f"  Size: {path.stat().st_size} bytes")


def test_debug_imports():
    """インポートデバッグ"""
    modules_to_test = [
        "streamlit",
        "openai",
        "tiktoken",
        "yaml",
        "pytest"
    ]

    for module_name in modules_to_test:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'Unknown')
            print(f"✅ {module_name}: {version}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
