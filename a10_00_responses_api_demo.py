# streamlit run a10_00_responses_api_demo.py --server.port=8501
# --------------------------------------------------
# OpenAI Responses API デモアプリケーション
# Streamlitを使用したインタラクティブなAPIテストツール
# --------------------------------------------------
import os
import sys
import json
import base64
import glob
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Literal
from pathlib import Path

import streamlit as st
import pandas as pd
import requests
from pydantic import BaseModel, ValidationError
from openai import OpenAI
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputTextParam,
    ResponseInputImageParam,
    ResponseFormatTextJSONSchemaConfigParam,
    ResponseTextConfigParam,
    FileSearchToolParam,
    WebSearchToolParam,
    ComputerToolParam,
)
from openai.types.responses.web_search_tool_param import UserLocation

# プロジェクトディレクトリの設定
BASE_DIR = Path(__file__).resolve().parent.parent
THIS_DIR = Path(__file__).resolve().parent

# PYTHONPATHに親ディレクトリを追加
sys.path.insert(0, str(BASE_DIR))

# 改良版ヘルパーのインポート
try:
    from helper import (
        ConfigManager,
        MessageManager,
        TokenManager,
        UIHelper,
        ResponseProcessor,
        error_handler,
        timer,
        sanitize_key,
    )
except ModuleNotFoundError:
    st.error("helper.py が見つかりません。ファイルの配置を確認してください。")
    st.stop()

# ページ設定（一度だけ実行）
config = ConfigManager()
st.set_page_config(
    page_title=config.get("ui.page_title", "ChatGPT Responses API Demo"),
    page_icon=config.get("ui.page_icon", "🤖"),
    layout=config.get("ui.layout", "wide")
)


# ==================================================
# 基底クラス
# ==================================================
class BaseDemo(ABC):
    # デモ機能の基底クラス

    def __init__(self, demo_name: str):
        self.demo_name = demo_name
        self.config = ConfigManager()
        self.client = OpenAI()
        self.safe_key = sanitize_key(demo_name)
        self.message_manager = MessageManager(f"messages_{self.safe_key}")

    def initialize(self):
        # 共通の初期化処理
        st.write(f"# {self.demo_name}")

    def select_model(self) -> str:
        # モデル選択UI
        return UIHelper.select_model(f"model_{self.safe_key}")

    def handle_error(self, e: Exception):
        # エラーハンドリング
        error_msg = self.config.get("error_messages.network_error", "エラーが発生しました")
        st.error(f"{error_msg}: {str(e)}")
        if st.checkbox("詳細を表示", key=f"error_detail_{self.safe_key}"):
            st.exception(e)

    @abstractmethod
    def run(self):
        # 各デモの実行処理
        pass


# ==================================================
# テキスト応答デモ
# ==================================================
class TextResponseDemo(BaseDemo):
    # 基本的なテキスト応答のデモ

    @error_handler
    def run(self):
        self.initialize()
        model = self.select_model()
        st.write("選択したモデル:", model)

        example_query = self.config.get("samples.responses_query",
                                        "OpenAIのAPIで、responses.createを説明しなさい。")
        st.write(f"例: {example_query}")

        with st.form(key=f"text_form_{self.safe_key}"):
            user_input = st.text_area(
                "質問を入力してください:",
                height=self.config.get("ui.text_area_height", 75)
            )
            submitted = st.form_submit_button("送信")

        if submitted and user_input:
            self._process_query(model, user_input)

    @timer
    def _process_query(self, model: str, user_input: str):
        # クエリの処理
        try:
            # トークン情報の表示
            UIHelper.show_token_info(user_input, model)

            messages = self.message_manager.get_default_messages()
            messages.append(
                EasyInputMessageParam(role="user", content=user_input)
            )

            with st.spinner("処理中..."):
                response = self.client.responses.create(
                    model=model,
                    input=messages
                )

            st.success("応答を取得しました")
            ResponseProcessor.display_response(response)

        except Exception as e:
            self.handle_error(e)


# ==================================================
# メモリ応答デモ
# ==================================================
class MemoryResponseDemo(BaseDemo):
    # 会話履歴を保持するデモ

    @error_handler
    def run(self):
        self.initialize()
        model = self.select_model()
        st.write("選択したモデル:", model)

        # 履歴表示
        UIHelper.display_messages(self.message_manager.get_messages())

        # 入力フォーム
        with st.form(key=f"memory_form_{self.safe_key}"):
            user_input = st.text_area(
                "質問を入力してください:",
                height=self.config.get("ui.text_area_height", 75)
            )
            submitted = st.form_submit_button("送信")

        if submitted and user_input:
            self._process_input(user_input, model)

        # 履歴クリアボタン
        if st.sidebar.button("会話履歴クリア", key=f"clear_{self.safe_key}"):
            self.message_manager.clear_messages()
            st.rerun()

    @timer
    def _process_input(self, user_input: str, model: str):
        # ユーザー入力の処理
        try:
            # トークン情報の表示
            UIHelper.show_token_info(user_input, model)

            self.message_manager.add_message("user", user_input)

            with st.spinner("処理中..."):
                response = self.client.responses.create(
                    model=model,
                    input=self.message_manager.get_messages()
                )

            texts = ResponseProcessor.extract_text(response)
            for text in texts:
                self.message_manager.add_message("assistant", text)

            st.rerun()

        except Exception as e:
            self.handle_error(e)


# ==================================================
# 画像応答デモ
# ==================================================
class ImageResponseDemo(BaseDemo):
    # 画像入力のデモ（URL/Base64）

    def __init__(self, demo_name: str, use_base64: bool = False):
        super().__init__(demo_name)
        self.use_base64 = use_base64

    @error_handler
    def run(self):
        self.initialize()
        model = self.select_model()
        st.write("選択したモデル:", model)

        if self.use_base64:
            self._run_base64_demo(model)
        else:
            self._run_url_demo(model)

    def _run_url_demo(self, model: str):
        # URL画像のデモ
        st.write("例: このイメージを説明しなさい。")

        default_url = self.config.get("samples.image_url", "")
        image_url = st.text_input(
            "画像URLを入力してください",
            value=default_url,
            key=f"img_url_{self.safe_key}"
        )

        if image_url:
            st.image(image_url, caption="入力画像", use_container_width=True)

        with st.form(key=f"img_form_{self.safe_key}"):
            question = st.text_input("質問", value="このイメージを説明しなさい。")
            submitted = st.form_submit_button("画像で質問")

        if submitted:
            self._process_image_question(model, question, image_url)

    def _run_base64_demo(self, model: str):
        # Base64画像のデモ
        images_dir = self.config.get("paths.images_dir", "images")
        files = self._get_image_files(images_dir)

        if not files:
            st.warning(f"{images_dir} に画像ファイルがありません")
            return

        file_path = st.selectbox("画像ファイルを選択", files, key=f"img_select_{self.safe_key}")

        with st.form(key=f"img_b64_form_{self.safe_key}"):
            submitted = st.form_submit_button("選択画像で実行")

        if submitted:
            self._process_base64_image(model, file_path)

    def _get_image_files(self, images_dir: str) -> List[str]:
        # 画像ファイルのリストを取得
        patterns = ["*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif"]
        files = []
        for pattern in patterns:
            files.extend(glob.glob(f"{images_dir}/{pattern}"))
        return sorted(files)

    def _encode_image(self, path: str) -> str:
        # 画像をBase64エンコード
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    @timer
    def _process_image_question(self, model: str, question: str, image_url: str):
        # 画像質問の処理
        try:
            messages = self.message_manager.get_default_messages()
            messages.append(
                EasyInputMessageParam(
                    role="user",
                    content=[
                        ResponseInputTextParam(type="input_text", text=question),
                        ResponseInputImageParam(
                            type="input_image",
                            image_url=image_url,
                            detail="auto"
                        ),
                    ],
                )
            )

            with st.spinner("処理中..."):
                response = self.client.responses.create(model=model, input=messages)

            st.subheader("回答:")
            ResponseProcessor.display_response(response)

        except Exception as e:
            self.handle_error(e)

    @timer
    def _process_base64_image(self, model: str, file_path: str):
        # Base64画像の処理
        try:
            b64 = self._encode_image(file_path)
            st.image(file_path, caption="選択画像", width=320)

            messages = self.message_manager.get_default_messages()
            messages.append(
                EasyInputMessageParam(
                    role="user",
                    content=[
                        ResponseInputTextParam(
                            type="input_text",
                            text="What's in this image?"
                        ),
                        ResponseInputImageParam(
                            type="input_image",
                            image_url=f"data:image/jpeg;base64,{b64}",
                            detail="auto"
                        ),
                    ],
                )
            )

            with st.spinner("処理中..."):
                response = self.client.responses.create(model=model, input=messages)

            st.subheader("出力テキスト:")
            ResponseProcessor.display_response(response)

        except Exception as e:
            self.handle_error(e)


# ==================================================
# 構造化出力デモ
# ==================================================
class StructuredOutputDemo(BaseDemo):
    # 構造化出力のデモ

    class Event(BaseModel):
        # イベント情報のPydanticモデル
        name: str
        date: str
        participants: List[str]

    def __init__(self, demo_name: str, use_parse: bool = False):
        super().__init__(demo_name)
        self.use_parse = use_parse

    @error_handler
    def run(self):
        self.initialize()
        st.header("構造化出力: イベント情報抽出デモ")

        available_models = self.config.get("models.available", ["gpt-4o", "gpt-4o-mini"])
        model = st.selectbox(
            "モデルを選択",
            available_models,
            key=f"struct_model_{self.safe_key}"
        )

        default_event = self.config.get("samples.event_example",
                                        "台湾フェス2025 ～あつまれ！究極の台湾グルメ～")
        text = st.text_input(
            "イベント詳細を入力",
            value=default_event,
            key=f"struct_input_{self.safe_key}"
        )

        if st.button("実行：イベント抽出", key=f"struct_btn_{self.safe_key}"):
            if self.use_parse:
                self._run_with_parse(model, text)
            else:
                self._run_with_create(model, text)

    @timer
    def _run_with_create(self, model: str, text: str):
        # responses.createを使用した実行
        try:
            schema = {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "date": {"type": "string"},
                    "participants": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name", "date", "participants"],
                "additionalProperties": False,
            }

            messages = [
                EasyInputMessageParam(
                    role="developer",
                    content="Extract event details from the text."
                ),
                EasyInputMessageParam(
                    role="user",
                    content=[ResponseInputTextParam(type="input_text", text=text)]
                ),
            ]

            text_cfg = ResponseTextConfigParam(
                format=ResponseFormatTextJSONSchemaConfigParam(
                    name="event_extraction",
                    type="json_schema",
                    schema=schema,
                    strict=True,
                )
            )

            with st.spinner("処理中..."):
                response = self.client.responses.create(
                    model=model,
                    input=messages,
                    text=text_cfg
                )

            event = self.Event.model_validate_json(response.output_text)
            st.subheader("抽出結果 (Pydantic)")
            st.json(event.model_dump())
            st.code(repr(event), language="python")

        except (ValidationError, json.JSONDecodeError) as e:
            st.error(self.config.get("error_messages.parse_error", "解析エラー"))
            st.exception(e)
        except Exception as e:
            self.handle_error(e)

    @timer
    def _run_with_parse(self, model: str, text: str):
        # responses.parseを使用した実行
        try:
            messages = [
                EasyInputMessageParam(
                    role="developer",
                    content="Extract event details from the text."
                ),
                EasyInputMessageParam(
                    role="user",
                    content=[ResponseInputTextParam(type="input_text", text=text)]
                ),
            ]

            with st.spinner("処理中..."):
                response = self.client.responses.parse(
                    model=model,
                    input=messages,
                    text_format=self.Event,
                )

            event = response.output_parsed
            st.subheader("抽出結果 (Pydantic)")
            st.json(event.model_dump())
            st.code(repr(event), language="python")

        except Exception as e:
            self.handle_error(e)


# ==================================================
# 天気デモ
# ==================================================
class WeatherDemo(BaseDemo):
    # OpenWeatherMap APIを使用した天気デモ

    @error_handler
    def run(self):
        self.initialize()
        model = self.select_model()
        st.write("選択したモデル:", model)

        # 都市データの読み込み
        try:
            cities_csv = self.config.get("paths.cities_csv", "data/cities_list.csv")
            df_jp = self._load_japanese_cities(cities_csv)
            city, lat, lon = self._select_city(df_jp)

            # 天気情報の表示
            self._display_weather(lat, lon)

        except Exception as e:
            self.handle_error(e)

    def _load_japanese_cities(self, csv_path: str) -> pd.DataFrame:
        # 日本の都市データを読み込み
        df = pd.read_csv(csv_path)
        jp = df[df["country"] == "Japan"][["name", "lat", "lon"]].drop_duplicates()
        return jp.sort_values("name").reset_index(drop=True)

    def _select_city(self, df: pd.DataFrame) -> tuple:
        # 都市選択UI
        city = st.selectbox(
            "都市を選択してください",
            df["name"].tolist(),
            key=f"city_{self.safe_key}"
        )
        row = df[df["name"] == city].iloc[0]
        return city, row["lat"], row["lon"]

    def _display_weather(self, lat: float, lon: float):
        # 天気情報の表示
        try:
            # 現在の天気
            today = self._get_current_weather(lat, lon)
            st.write("----- 本日の天気 -----")
            st.write(f"都市 : {today['city']}")
            st.write(f"気温 : {today['temperature']}℃")
            st.write(f"説明 : {today['description']}")

            # 週間予報
            st.write("----- 5日間予報 （3時間毎を日別平均） -----")
            forecast = self._get_weekly_forecast(lat, lon)
            for day in forecast:
                st.write(f"{day['date']} : {day['temp_avg']}℃, {day['weather']}")

        except Exception as e:
            st.error(f"天気情報の取得に失敗しました: {str(e)}")

    @timer
    def _get_current_weather(self, lat: float, lon: float, unit: str = "metric") -> dict:
        # 現在の天気を取得
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            raise RuntimeError(self.config.get("error_messages.api_key_missing",
                                               "OPENWEATHER_API_KEY が設定されていません"))

        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": unit
        }

        response = requests.get(url, params=params,
                                timeout=self.config.get("api.timeout", 30))
        response.raise_for_status()
        data = response.json()

        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "coord": data["coord"],
        }

    @timer
    def _get_weekly_forecast(self, lat: float, lon: float, unit: str = "metric") -> List[dict]:
        # 週間予報を取得
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            raise RuntimeError(self.config.get("error_messages.api_key_missing",
                                               "OPENWEATHER_API_KEY が設定されていません"))

        url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "units": unit,
            "appid": api_key
        }

        response = requests.get(url, params=params,
                                timeout=self.config.get("api.timeout", 30))
        response.raise_for_status()
        data = response.json()

        # 日別に集計
        daily = {}
        for item in data["list"]:
            date = item["dt_txt"].split(" ")[0]
            temp = item["main"]["temp"]
            weather = item["weather"][0]["description"]

            if date not in daily:
                daily[date] = {"temps": [], "weather": weather}
            daily[date]["temps"].append(temp)

        # 平均気温を計算
        return [
            {
                "date": date,
                "temp_avg": round(sum(info["temps"]) / len(info["temps"]), 1),
                "weather": info["weather"]
            }
            for date, info in daily.items()
        ]


# ==================================================
# ツールデモ
# ==================================================
class ToolsDemo(BaseDemo):
    # FileSearch/WebSearchツールのデモ

    @error_handler
    def run(self):
        self.initialize()
        model = self.select_model()
        st.write("選択したモデル:", model)

        tool_choice = st.selectbox(
            "ツール選択",
            ["file_search", "web_search_preview"],
            key=f"tool_{self.safe_key}"
        )

        query = st.text_input("クエリを入力", "", key=f"query_{self.safe_key}")

        if tool_choice == "file_search":
            self._run_file_search(model, query)
        else:
            self._run_web_search(model, query)

    @timer
    def _run_file_search(self, model: str, query: str):
        # FileSearchの実行
        vector_store_id = st.text_input(
            "vector_store_id",
            "",
            key=f"vs_{self.safe_key}"
        )

        max_results = st.number_input(
            "最大取得数",
            1,
            self.config.get("ui.max_file_search_results", 20),
            5,
            key=f"max_{self.safe_key}"
        )

        if st.button("送信（FileSearch）", key=f"fs_btn_{self.safe_key}"):
            try:
                fs_tool = FileSearchToolParam(
                    type="file_search",
                    vector_store_ids=[vector_store_id] if vector_store_id else [],
                    max_num_results=int(max_results),
                )

                with st.spinner("検索中..."):
                    response = self.client.responses.create(
                        model=model,
                        tools=[fs_tool],
                        input=query,
                        include=["file_search_call.results"],
                    )

                st.subheader("モデル回答")
                ResponseProcessor.display_response(response)

                st.subheader("FileSearch 結果")
                if hasattr(response, "file_search_call") and response.file_search_call:
                    if hasattr(response.file_search_call, "results"):
                        st.json(response.file_search_call.results)
                    else:
                        st.info("検索結果が返されませんでした")

            except Exception as e:
                self.handle_error(e)

    @timer
    def _run_web_search(self, model: str, query: str):
        # WebSearchの実行
        if st.button("送信（WebSearch）", key=f"ws_btn_{self.safe_key}"):
            try:
                user_location = UserLocation(
                    type="approximate",
                    country="JP",
                    city="Tokyo",
                    region="Tokyo"
                )

                ws_tool = WebSearchToolParam(
                    type="web_search_preview",
                    user_location=user_location,
                    search_context_size="medium",
                )

                with st.spinner("検索中..."):
                    response = self.client.responses.create(
                        model=model,
                        tools=[ws_tool],
                        input=query
                    )

                st.subheader("モデル回答")
                ResponseProcessor.display_response(response)

            except Exception as e:
                self.handle_error(e)


# ==================================================
# FileSearchデモ（スタンドアロン）
# ==================================================
class FileSearchStandaloneDemo(BaseDemo):
    # FileSearch専用デモ

    @error_handler
    def run(self):
        self.initialize()
        model = self.select_model()
        st.write("選択したモデル:", model)

        # ハードコードされたvector_store_id
        vector_store_id = 'vs_68345a403a548191817b3da8404e2d82'
        st.info(f"Vector Store ID: {vector_store_id}")

        query = st.text_input("検索クエリ", value="請求書の支払い期限は？")

        if st.button("FileSearch実行", key=f"fs_exec_{self.safe_key}"):
            self._execute_file_search(model, vector_store_id, query)

    @timer
    def _execute_file_search(self, model: str, vector_store_id: str, query: str):
        # FileSearchの実行
        try:
            fs_tool = FileSearchToolParam(
                type="file_search",
                vector_store_ids=[vector_store_id],
                max_num_results=20
            )

            with st.spinner("検索中..."):
                response = self.client.responses.create(
                    model=model,
                    tools=[fs_tool],
                    input=query,
                    include=["file_search_call.results"]
                )

            st.subheader("検索結果")
            ResponseProcessor.display_response(response)

            # 詳細結果の表示
            if hasattr(response, "file_search_call") and response.file_search_call:
                with st.expander("FileSearch詳細結果"):
                    st.json(response.file_search_call.results)

        except Exception as e:
            self.handle_error(e)


# ==================================================
# WebSearchデモ（スタンドアロン）
# ==================================================
class WebSearchStandaloneDemo(BaseDemo):
    # WebSearch専用デモ

    @error_handler
    def run(self):
        self.initialize()
        model = self.select_model()
        st.write("選択したモデル:", model)

        default_query = self.config.get("samples.weather_query",
                                        "週末の東京の天気とおすすめの屋内アクティビティは？")
        query = st.text_input("検索クエリ", value=default_query)

        # Literal型の制約に対応
        context_size: Literal["low", "medium", "high"] = st.selectbox(
            "検索コンテキストサイズ",
            ["low", "medium", "high"],
            index=1,
            key=f"ws_context_{self.safe_key}"
        )

        if st.button("WebSearch実行", key=f"ws_exec_{self.safe_key}"):
            self._execute_web_search(model, query, context_size)

    @timer
    def _execute_web_search(self, model: str, query: str, context_size: Literal["low", "medium", "high"]):
        # WebSearchの実行
        try:
            user_location = UserLocation(
                type="approximate",
                country="JP",
                city="Tokyo",
                region="Tokyo"
            )

            ws_tool = WebSearchToolParam(
                type="web_search_preview",
                user_location=user_location,
                search_context_size=context_size
            )

            with st.spinner("検索中..."):
                response = self.client.responses.create(
                    model=model,
                    tools=[ws_tool],
                    input=query
                )

            st.subheader("検索結果")
            ResponseProcessor.display_response(response)

        except Exception as e:
            self.handle_error(e)


# ==================================================
# Computer Useデモ
# ==================================================
class ComputerUseDemo(BaseDemo):
    # Computer Use Tool のデモ

    @error_handler
    def run(self):
        self.initialize()
        st.warning("Computer Use APIは実験的な機能です。実行には特別な権限が必要です。")

        model = "computer-use-preview"
        st.write("使用モデル:", model)

        instruction = st.text_area(
            "実行指示",
            value="ブラウザで https://news.ycombinator.com を開いて、"
                  "トップ記事のタイトルをコピーしてメモ帳に貼り付けて",
            height=100
        )

        # Literal型の制約に対応
        environment: Literal["browser", "mac", "windows", "ubuntu", "linux"] = st.selectbox(
            "実行環境",
            ["browser", "mac", "windows", "ubuntu"],
            key=f"cu_env_{self.safe_key}"
        )

        if st.button("Computer Use実行", key=f"cu_exec_{self.safe_key}"):
            self._execute_computer_use(model, instruction, environment)

    @timer
    def _execute_computer_use(self, model: str, instruction: str,
                             environment: Literal["windows", "mac", "linux", "ubuntu", "browser"]):
        # Computer Useの実行
        try:
            cu_tool = ComputerToolParam(
                type="computer_use_preview",
                display_width=1280,
                display_height=800,
                environment=environment,
            )

            messages = [
                EasyInputMessageParam(
                    role="user",
                    content=[
                        ResponseInputTextParam(
                            type="input_text",
                            text=instruction
                        )
                    ]
                )
            ]

            with st.spinner("実行中..."):
                response = self.client.responses.create(
                    model=model,
                    tools=[cu_tool],
                    input=messages,
                    truncation="auto",
                    stream=False,
                    include=["computer_call_output.output.image_url"]
                )

            st.subheader("実行結果")
            ResponseProcessor.display_response(response)

            # Computer Use特有の出力処理
            for output in response.output:
                if hasattr(output, 'type') and output.type == 'computer_call':
                    st.subheader("Computer Use アクション")
                    if hasattr(output, 'action'):
                        st.write('実行アクション:', output.action)
                    if hasattr(output, 'image_url'):
                        st.image(output.image_url, caption="スクリーンショット")

        except Exception as e:
            self.handle_error(e)


# ==================================================
# 会話状態デモ
# ==================================================
class ConversationStateDemo(BaseDemo):
    # 会話状態の管理デモ

    @error_handler
    def run(self):
        self.initialize()
        model = self.select_model()
        st.write("選択したモデル:", model)

        # 会話状態の表示
        st.subheader("会話状態の管理")

        # 現在の会話履歴
        messages = self.message_manager.get_messages()
        st.write(f"現在のメッセージ数: {len(messages)}")

        # 会話履歴の詳細表示
        if st.checkbox("会話履歴の詳細を表示", key=f"show_detail_{self.safe_key}"):
            for i, msg in enumerate(messages):
                with st.expander(f"メッセージ {i + 1} - {msg.get('role', 'unknown')}"):
                    st.json(msg)

        # トークン数の計算
        total_tokens = 0
        for msg in messages:
            if isinstance(msg.get('content'), str):
                tokens = TokenManager.count_tokens(msg['content'], model)
                total_tokens += tokens

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("総トークン数", total_tokens)
        with col2:
            estimated_cost = TokenManager.estimate_cost(total_tokens, total_tokens // 2, model)
            st.metric("推定コスト", f"${estimated_cost:.4f}")
        with col3:
            st.metric("メッセージ数", len(messages))

        # 会話のエクスポート/インポート
        st.subheader("会話の管理")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("会話をエクスポート", key=f"export_{self.safe_key}"):
                # EasyInputMessageParamを辞書に変換
                messages_dict = [dict(msg) for msg in messages]
                self._export_conversation(messages_dict)

        with col2:
            uploaded_file = st.file_uploader(
                "会話をインポート",
                type=['json'],
                key=f"import_{self.safe_key}"
            )
            if uploaded_file is not None:
                self._import_conversation(uploaded_file)

    def _export_conversation(self, messages: List[Dict[str, Any]]):
        # 会話履歴のエクスポート
        try:
            # メッセージを辞書形式に変換
            export_data = {
                "timestamp": str(pd.Timestamp.now()),
                "message_count": len(messages),
                "messages": messages
            }

            json_str = json.dumps(export_data, ensure_ascii=False, indent=2)

            st.download_button(
                label="JSONファイルをダウンロード",
                data=json_str,
                file_name=f"conversation_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

        except Exception as e:
            self.handle_error(e)

    def _import_conversation(self, uploaded_file):
        # 会話履歴のインポート
        try:
            content = uploaded_file.read()
            data = json.loads(content)

            if "messages" in data:
                # 既存の履歴をクリアして新しい履歴をセット
                self.message_manager.clear_messages()
                for msg in data["messages"]:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    # roleの検証
                    if role in ["user", "assistant", "system", "developer"]:
                        self.message_manager.add_message(role, content)

                st.success(f"{len(data['messages'])}件のメッセージをインポートしました")
                st.rerun()
            else:
                st.error("有効な会話データが見つかりません")

        except Exception as e:
            self.handle_error(e)


# ==================================================
# デモマネージャー
# ==================================================
class DemoManager:
    # デモの管理クラス

    def __init__(self):
        self.config = ConfigManager()
        self.demos = self._initialize_demos()

    def _initialize_demos(self) -> Dict[str, BaseDemo]:
        # デモインスタンスの初期化
        return {
            "01_01  Responsesサンプル(One Shot)": TextResponseDemo(
                "01_01_responses_One_Shot"
            ),
            "01_011 Responsesサンプル(Memory)": MemoryResponseDemo(
                "01_011_responses_memory"
            ),
            "01_02  画像入力(URL)": ImageResponseDemo(
                "01_02_Image_URL", use_base64=False
            ),
            "01_021 画像入力(base64)": ImageResponseDemo(
                "01_021_Image_Base64", use_base64=True
            ),
            "01_03  構造化出力-responses": StructuredOutputDemo(
                "01_03_Structured_Output", use_parse=False
            ),
            "01_031 構造化出力-parse": StructuredOutputDemo(
                "01_031_Structured_Parse", use_parse=True
            ),
            "01_04  関数 calling": WeatherDemo(
                "01_04_Function_Calling"
            ),
            "01_05  会話状態": ConversationStateDemo(
                "01_05_Conversation"
            ),
            "01_06  ツール:FileSearch, WebSearch": ToolsDemo(
                "01_06_Tools"
            ),
            "01_061 File Search": FileSearchStandaloneDemo(
                "01_061_FileSearch"
            ),
            "01_062 Web Search": WebSearchStandaloneDemo(
                "01_062_WebSearch"
            ),
            "01_07  Computer Use Tool Param": ComputerUseDemo(
                "01_07_Computer_Use"
            ),
        }

    def run(self):
        # アプリケーションの実行
        UIHelper.init_page()

        # デモ選択
        demo_name = st.sidebar.radio(
            "デモを選択",
            list(self.demos.keys()),
            key="demo_selection"
        )

        # セッション状態の更新
        if "current_demo" not in st.session_state:
            st.session_state.current_demo = demo_name
        elif st.session_state.current_demo != demo_name:
            st.session_state.current_demo = demo_name

        # 選択されたデモの実行
        demo = self.demos.get(demo_name)
        if demo:
            try:
                demo.run()
            except Exception as e:
                st.error(f"デモの実行中にエラーが発生しました: {str(e)}")
                if st.checkbox("詳細なエラー情報を表示"):
                    st.exception(e)
        else:
            st.error(f"デモ '{demo_name}' が見つかりません")

        # フッター情報
        self._display_footer()

    def _display_footer(self):
        # フッター情報の表示
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 情報")

        # 現在の設定情報
        with st.sidebar.expander("現在の設定"):
            st.json({
                "default_model": self.config.get("models.default"),
                "api_timeout": self.config.get("api.timeout"),
                "ui_layout": self.config.get("ui.layout"),
            })

        # バージョン情報
        st.sidebar.markdown("### バージョン")
        st.sidebar.markdown("- OpenAI Responses API Demo v2.0")
        st.sidebar.markdown("- Streamlit " + st.__version__)

        # リンク
        st.sidebar.markdown("### リンク")
        st.sidebar.markdown("[OpenAI API ドキュメント](https://platform.openai.com/docs)")
        st.sidebar.markdown("[Streamlit ドキュメント](https://docs.streamlit.io)")


# ==================================================
# メイン関数
# ==================================================
def main():
    # アプリケーションのエントリーポイント

    # ロギングの設定
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 環境変数のチェック
    if not os.getenv("OPENAI_API_KEY"):
        st.error("環境変数 OPENAI_API_KEY が設定されていません。")
        st.info("export OPENAI_API_KEY='your-api-key' を実行してください。")
        st.stop()

    # デモマネージャーの作成と実行
    try:
        manager = DemoManager()
        manager.run()
    except Exception as e:
        st.error(f"アプリケーションの起動に失敗しました: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()

# streamlit run a10_00_responses_api_demo.py --server.port=8501
