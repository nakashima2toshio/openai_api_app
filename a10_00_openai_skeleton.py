# streamlit run a10_00_openai_skeleton.py --server.port=8501
# ==================================================
# OpenAI API 学習用スケルトンプログラム
# ==================================================
# [Usage] streamlit run a10_00_openai_skeleton.py --server.port 8501
# このプログラムは、OpenAI APIの各種機能を学習するための
# 基本構造（スケルトン）を提供します。
# 新しいデモ機能を追加する際は、BaseDemoクラスを継承して実装してください。
# ==================================================
import sys
import streamlit as st
from typing import Dict, List, Optional
from pathlib import Path
import importlib

# ヘルパーモジュールのインポート
from helper import (
    ConfigManager, MessageManager, TokenManager, UIHelper,
    ResponseProcessor, DemoBase, timer, error_handler,
    sanitize_key, config
)

# OpenAI関連のインポート
from openai import OpenAI

# ==================================================
# デモ実装例(1)
# ==================================================
class SimpleChatDemo(DemoBase):
    # シンプルチャットのデモ

    def run(self):
        self.setup_ui()

        # チャット入力
        user_input = st.chat_input("メッセージを入力してください", key=f"chat_input_{self.key_prefix}")

        if user_input:
            # メッセージ追加
            self.add_user_message(user_input)

            # API呼び出し
            messages = self.message_manager.get_messages()
            # response = client.responses.create(**params)
            response = self.call_api(messages)

            # レスポンス処理
            texts = ResponseProcessor.extract_text(response)
            if texts:
                self.add_assistant_message(texts[0])

            st.rerun()

        # メッセージ表示
        self.display_messages()

# ==================================================
# デモ実装例(2)
# ==================================================
class StructuredOutputDemo(DemoBase):
    # 構造化出力のデモ

    def run(self):
        self.setup_ui()

        st.info("構造化出力のデモ - JSON形式での応答を取得します")

        # 入力フォーム
        with st.form(f"structured_form_{self.key_prefix}"):
            task = st.selectbox(
                "タスクを選択",
                ["商品レビューの分析", "テキストの要約", "感情分析"]
            )
            text = st.text_area("テキストを入力", height=100)
            submitted = st.form_submit_button("実行")

        if submitted and text:
            # プロンプトの構築
            prompts = {
                "商品レビューの分析": "以下のレビューを分析し、評価(1-5)、良い点、改善点をJSON形式で返してください。",
                "テキストの要約"    : "以下のテキストを要約し、タイトル、要点3つ、結論をJSON形式で返してください。",
                "感情分析"          : "以下のテキストの感情を分析し、感情タイプ、強度(0-1)、理由をJSON形式で返してください。"
            }

            prompt = f"{prompts[task]}\n\nテキスト: {text}"
            self.add_user_message(prompt)

            # API呼び出し（response_formatを指定）
            messages = self.message_manager.get_messages()
            # response = client.responses.create(**params)
            response = self.call_api(
                messages,
                response_format={"type": "json_object"}
            )

            # レスポンス処理
            texts = ResponseProcessor.extract_text(response)
            if texts:
                self.add_assistant_message(texts[0])

                # JSON表示
                try:
                    import json
                    result = json.loads(texts[0])
                    st.json(result)
                except:
                    pass

        # メッセージ表示
        self.display_messages()

# ==================================================
# デモ実装例(3)
# ==================================================
# class StructuredOutputDemo(DemoBase):


# ==================================================
# デモ実装例(4)
# ==================================================
class TokenCounterDemo(DemoBase):
    # トークンカウンターのデモ

    def run(self):
        self.setup_ui()

        st.info("テキストのトークン数を計算し、API使用コストを推定します")

        # テキスト入力
        text = st.text_area(
            "テキストを入力",
            height=200,
            key=f"token_text_{self.key_prefix}"
        )

        if text:
            # トークン数計算
            token_count = TokenManager.count_tokens(text, self.model)

            # コスト推定
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("トークン数", f"{token_count:,}")

            with col2:
                # 出力トークン数の推定（入力の50%と仮定）
                output_tokens = token_count // 2
                total_tokens = token_count + output_tokens
                st.metric("推定合計トークン", f"{total_tokens:,}")

            with col3:
                cost = TokenManager.estimate_cost(token_count, output_tokens, self.model)
                st.metric("推定コスト", f"${cost:.6f}")

            # モデル制限情報
            limits = TokenManager.get_model_limits(self.model)

            # プログレスバー
            usage_percent = (token_count / limits['max_tokens']) * 100
            st.progress(min(usage_percent / 100, 1.0))
            st.caption(f"使用率: {usage_percent:.1f}% / 最大: {limits['max_tokens']:,} tokens")

            # テキスト切り詰め機能
            st.subheader("テキスト切り詰め")
            max_tokens = st.number_input(
                "最大トークン数",
                min_value=1,
                max_value=limits['max_tokens'],
                value=min(1000, limits['max_tokens']),
                key=f"max_tokens_{self.key_prefix}"
            )

            if st.button("切り詰め実行", key=f"truncate_{self.key_prefix}"):
                truncated = TokenManager.truncate_text(text, max_tokens, self.model)
                truncated_tokens = TokenManager.count_tokens(truncated, self.model)

                st.text_area(
                    f"切り詰め後のテキスト ({truncated_tokens} tokens)",
                    value=truncated,
                    height=200,
                    key=f"truncated_text_{self.key_prefix}"
                )


# ==================================================
# デモマネージャー
# ==================================================
class DemoManager:
    # デモアプリケーションの管理

    def __init__(self):
        self.demos = self._load_demos(self)

    @staticmethod
    def _load_demos(self) -> Dict[str, DemoBase]:
        # デモの読み込み
        demos = {
            "simple_chat"      : SimpleChatDemo("simple_chat", "シンプルチャット"),
            "structured_output": StructuredOutputDemo("structured_output", "構造化出力"),
            "token_counter"    : TokenCounterDemo("token_counter", "トークンカウンター"),
        }

        # 外部デモの動的読み込み（拡張用）
        demos_dir = Path("demos")
        if demos_dir.exists():
            for demo_file in demos_dir.glob("*.py"):
                if demo_file.stem.startswith("demo_"):
                    try:
                        module_name = f"demos.{demo_file.stem}"
                        module = importlib.import_module(module_name)

                        # DemoBaseを継承したクラスを探す
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and
                                    issubclass(attr, DemoBase) and
                                    attr != DemoBase):
                                demo_name = attr_name.lower().replace("demo", "")
                                demos[demo_name] = attr(demo_name)
                    except Exception as e:
                        st.error(f"デモの読み込みエラー ({demo_file}): {e}")

        return demos

    def get_demo_categories(self) -> List[Dict[str, List[str]]]:
        # デモのカテゴリを取得
        categories = config.get("app.demo_categories", [])

        # 利用可能なデモのみをフィルタリング
        filtered_categories = []
        for category in categories:
            available_demos = [
                demo for demo in category.get("demos", [])
                if demo in self.demos
            ]
            if available_demos:
                filtered_categories.append({
                    "name" : category["name"],
                    "demos": available_demos
                })

        return filtered_categories

    def run_demo(self, demo_name: str):
        # デモの実行
        if demo_name in self.demos:
            demo = self.demos[demo_name]
            demo.run()
        else:
            st.error(f"デモが見つかりません: {demo_name}")


# ==================================================
# メインアプリケーション
# ==================================================
class OpenAISkeletonApp:
    # メインアプリケーションクラス

    def __init__(self):
        self.demo_manager = DemoManager()
        self._init_session_state(self)

    @staticmethod
    def _init_session_state(self):
        # セッションステートの初期化
        if 'selected_demo' not in st.session_state:
            st.session_state.selected_demo = None

    def run(self):
        # アプリケーションの実行
        # ページ設定
        UIHelper.init_page()

        # サイドバーメニュー
        self._create_sidebar_menu()

        # メインコンテンツ
        if st.session_state.selected_demo:
            self.demo_manager.run_demo(st.session_state.selected_demo)
        else:
            self._show_welcome_page()

        # フッター
        self._show_footer(self)

    def _create_sidebar_menu(self):
        # サイドバーメニューの作成
        st.sidebar.header("デモ選択")

        # カテゴリ別にデモを表示
        categories = self.demo_manager.get_demo_categories()

        for category in categories:
            st.sidebar.subheader(category["name"])

            for demo_name in category["demos"]:
                demo_title = config.get(f"app.demo_titles.{demo_name}", demo_name)

                if st.sidebar.button(
                        demo_title,
                        key=f"select_{demo_name}",
                        use_container_width=True
                ):
                    st.session_state.selected_demo = demo_name
                    st.rerun()

        # セパレーター
        st.sidebar.divider()

        # リセットボタン
        if st.sidebar.button("🏠 ホームに戻る", use_container_width=True):
            st.session_state.selected_demo = None
            st.rerun()

    def _show_welcome_page(self):
        # ウェルカムページの表示
        st.title("🤖 OpenAI Responses API デモ")

        st.markdown("""
        このアプリケーションでは、OpenAI Responses APIの様々な機能をデモンストレーションします。

        ### 利用可能なデモ
        """)

        # デモカテゴリの表示
        categories = self.demo_manager.get_demo_categories()

        for category in categories:
            st.subheader(f"📁 {category['name']}")

            cols = st.columns(3)
            for i, demo_name in enumerate(category["demos"]):
                demo_title = config.get(f"app.demo_titles.{demo_name}", demo_name)

                with cols[i % 3]:
                    if st.button(
                            demo_title,
                            key=f"welcome_{demo_name}",
                            use_container_width=True
                    ):
                        st.session_state.selected_demo = demo_name
                        st.rerun()

        # 使い方
        with st.expander("📖 使い方"):
            st.markdown("""
            1. サイドバーからデモを選択します
            2. 各デモの指示に従って操作します
            3. APIキーは環境変数 `OPENAI_API_KEY` に設定してください

            ##### 設定のカスタマイズ
            - `config.yaml` でアプリケーションの設定を変更できます
            - 新しいデモは `demos/` ディレクトリに追加できます
            """)

    @staticmethod
    def _show_footer(self):
        # フッターの表示
        st.sidebar.divider()

        # バージョン情報
        st.sidebar.caption("OpenAI Responses API Demo v1.0")

        # デバッグモード
        if config.get("experimental.debug_mode", False):
            with st.sidebar.expander("🐛 デバッグ情報"):
                st.write("セッションステート:", st.session_state)

                if 'performance_metrics' in st.session_state:
                    st.write("パフォーマンス:", st.session_state.performance_metrics[-5:])


# ==================================================
# エントリーポイント
# ==================================================
@error_handler
def main():
    # メイン関数
    app = OpenAISkeletonApp()
    app.run()


if __name__ == "__main__":
    main()

# streamlit run a10_00_openai_skeleton.py --server.port=8501
