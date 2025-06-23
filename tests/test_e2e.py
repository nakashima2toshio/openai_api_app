# tests/test_e2e.py
"""E2Eテスト（Seleniumを使用）"""

import pytest
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


@pytest.mark.e2e
def test_app_startup():
    """アプリ起動テスト"""
    # Streamlitアプリを別プロセスで起動
    process = subprocess.Popen([
        "streamlit", "run", "a10_00_openai_skeleton.py",
        "--server.port=8502", "--server.headless=true"
    ])

    time.sleep(5)  # 起動待機

    try:
        # ブラウザ設定
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        # アプリにアクセス
        driver.get("http://localhost:8502")
        time.sleep(3)

        # タイトル確認
        title = driver.find_element(By.TAG_NAME, "h1").text
        assert "OpenAI" in title

        driver.quit()
    finally:
        process.terminate()
