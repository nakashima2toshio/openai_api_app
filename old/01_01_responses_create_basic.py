# streamlit run 01_01_responses_create_basic.py --server.port 8501
# port Check: lsof -i :5678
# OpenAI API: https://platform.openai.com/docs/api-reference/introduction
# API: https://docs.streamlit.io/develop/api-reference
# [Menu] -------------------------------
# OpenAI - APIサンプルプログラム（学習用に作成）
# 01_01 テキスト入力と出力(One Shot)
# 01_011 テキスト入出力（with memory)
# 01_02 画像入力
# 01_03 構造化された出力
# 01_04 関数呼び出し
# 01_05 会話状態
# 01_06 ツールを使ってモデルを拡張する
# ----------------------------------------

from openai import OpenAI
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import streamlit as st
import requests
import json

# --- インポート直後に１度だけ、実行する ---
st.set_page_config(
    page_title="ChatGPT API",
    page_icon="2025-5 Nakashima"
)

# -----------------------------------
# Responses API を利用する場合にセットすべきパラメータ一覧：
# -----------------------------------
from openai.types.responses import (
    EasyInputMessageParam,                      # 基本のopenaiのAPI
    ResponseInputTextParam,                     # 入力テキストパラメータ
    ResponseInputImageParam,                    # 入力画像パラメータ
    ResponseFormatTextJSONSchemaConfigParam,
    ResponseTextConfigParam,
    FunctionToolParam,                          # 関数呼び出しツールを定義する
    FileSearchToolParam,                        # ファイル検索ツールを定義する
    WebSearchToolParam,                         # ウェブ検索ツールを定義する
    Response,
)

# default
developer_text = "You are a strong developer and good at teaching software developer professionals; please provide an up-to-date, informed overview of the API by function, then show cookbook programs for each, and explain the API options."
user_text = "Organize and identify the problem and list the issues.Then, provide a solution procedure for the issues you have organized and identified, andSolve the problems/issues according to the solution procedures."
assistant_text = '回答は日本語で'
image_path_sample = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

def make_input_messages(dev_txt, user_txt, assistant_txt):
    """ EasyInputMessageParamを使った入力メッセージリスト生成 """
    return [
        EasyInputMessageParam(role="developer", content=dev_txt),
        EasyInputMessageParam(role="user", content=user_txt),
        EasyInputMessageParam(role="assistant", content=assistant_txt)
    ]

def init_page():
    st.header("ChatGPT Responses")
    st.sidebar.title("メニュー")

def init_messages():
    # 初期メッセージ履歴をEasyInputMessageParamで保存
    input_messages = [
        EasyInputMessageParam(role="developer", content=developer_text),
        EasyInputMessageParam(role="user", content=user_text),
        EasyInputMessageParam(role="assistant", content=assistant_text)
    ]
    if st.sidebar.button("会話履歴のクリア", key="clear") or "message_history" not in st.session_state:
        st.session_state.message_history = input_messages

def config_model(demo_name="設定"):
    models = ["gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-4o-mini", "o3-mini", "o4-mini", "o1-mini", "o4", "o3", "o1"]
    selected_model = st.sidebar.radio("Choose a model:", models)
    return selected_model

def create_responses_api(model, input_messages) -> Response:
    client = OpenAI()
    response = client.responses.create(
        model=model,
        input=input_messages
    )
    return response

def extract_text_from_response(response):
    """Responseオブジェクトから 'output_text' を抽出"""
    texts = []
    for item in response.output:
        if item.type == "message":
            for content_obj in item.content:
                if getattr(content_obj, "type", None) == "output_text":
                    texts.append(content_obj.text)
    return texts

# ---------------------------------------------
# 01_01 テキスト入力と出力
# [Spec] https://platform.openai.com/docs/api-reference/responses
# [for Python] https://github.com/openai/openai-python/tree/main/tests/api_resources
# [CookBook] https://cookbook.openai.com/examples/responses_api/responses_example
#--------------------------------------------
def qa_sample(demo_name="Q & A Demo（One Shot）"):
    init_messages()
    st.write(f"# {demo_name}")
    selected_model_value = config_model()
    st.write("選択したモデル:", selected_model_value)

    with st.form(key="qa_form"):
        user_input = st.text_area("ここにテキストを入力してください:", height=75)
        submit_button = st.form_submit_button(label="送信")

    if submit_button and user_input:
        st.write("選択したモデル ＝ ", selected_model_value)
        st.write("入力内容:", user_input)

        # --- EasyInputMessageParam を利用 ---
        input_messages = make_input_messages(
            developer_text,
            user_input,       # ここだけユーザー入力内容で差し替え
            assistant_text
        )

        response = create_responses_api(model=selected_model_value, input_messages=input_messages)
        extracted_text_list = extract_text_from_response(response)
        for i, t in enumerate(extracted_text_list, 1):
            st.code(t)

        # 次の質問
        with st.form(key="qa_next_form"):
            submit_ok_button = st.form_submit_button(label="次の質問")
        if submit_ok_button:
            st.rerun()
    return True

# ------------------------------------
# 01_011 テキスト入出力 - with memory
# ----------------------------------
def qa_memory_sample(demo_name="QAのサンプル（＋Memory）"):
    st.write(f"# {demo_name}")
    selected_model_value = config_model()
    st.write("選択したモデル:", selected_model_value)

    # --- 1. 履歴管理 ---
    if "qa_memory_history" not in st.session_state:
        # 初期化。最初にdeveloper→user→assistantの形でhistory作成（最初の「役割」付与のため）
        st.session_state.qa_memory_history = [
            EasyInputMessageParam(role="developer", content=developer_text),
            EasyInputMessageParam(role="user", content=user_text),
            EasyInputMessageParam(role="assistant", content=user_text),
        ]

    # --- 2. 全履歴の表示 ---
    for msg in st.session_state.qa_memory_history:
        if msg['role'] == 'user':  # msg.get("role", "default") = msg['role']
            st.markdown(f"**User:** {msg['content']}")
        elif msg['role'] == 'assistant':
            st.markdown(f"<span style='color:green'><b>Assistant:</b> {msg['content']}</span>", unsafe_allow_html=True)
        elif msg['role'] == 'developer':
            st.markdown(f"<span style='color:gray'><i>System:</i> {msg['content']}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"{msg['role'].capitalize()}: {msg['content']}")

    # --- 3. 入力フォーム ---
    with st.form(key="qam_form"):
        user_input = st.text_area("ここにテキストを入力してください:", height=75, key="memory_input")
        submit_button = st.form_submit_button(label="送信")

    if submit_button and user_input:
        # 3-1. 入力を履歴に追加
        st.session_state.qa_memory_history.append(
            EasyInputMessageParam(role="user", content=user_input)
        )

        # 3-2. APIに渡すmessages（developer + 全User/Assistant履歴）を作成
        input_messages = st.session_state.qa_memory_history.copy()
        # （ここでassistant_textをsystem用に必要なら追加）

        # 3-3. API呼び出し
        response = create_responses_api(model=selected_model_value, input_messages=input_messages)
        extracted_text_list = extract_text_from_response(response)
        # 複数outputが返る場合もあるのでforで追加
        for t in extracted_text_list:
            st.session_state.qa_memory_history.append(
                EasyInputMessageParam(role="assistant", content=t)
            )
        # 入力欄リセット（UI上は自動的にクリアされるが、再描画確定のため）
        st.rerun()

    # --- 4. 履歴リセット機能 ---
    if st.button("会話履歴クリア"):
        st.session_state.qa_memory_history = [
            EasyInputMessageParam(role="developer", content=developer_text),
        ]
        st.rerun()

# -------------------------------------------
# 01_02 画像入力 by URL
# -----------------------------------------------
# [Supported file types]
#   PNG (.png), JPEG (.jpeg and .jpg), WEBP (.webp), Non-animated GIF (.gif)
# [Size limits]
#   Up to 20MB per image
# [Low-resolution]: 512px x 512px
# [High-resolution]: 768px (short side) x 2000px (long side)
# -----------------------------------------
# -------------------------------------------
# 01_02 画像入力 by URL（改良版）
# -------------------------------------------
def qa_01_02_passing_url(demo_name=None):
    # モデル選択UI
    model = config_model()
    st.write("選択したモデル:", model)

    # 画像のURL入力、デフォルト画像URL
    image_path_default = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    image_url = st.text_input("画像URLを入力してください", value=image_path_default)

    # 質問テキスト（入力欄にしてもよいが今回は固定）
    question_text = "このイメージを説明しなさい。"

    # --- 実行ボタン付きフォーム ---
    with st.form(key="qa_img_form"):
        submit_button = st.form_submit_button(label="画像で質問")

    # ボタンが押されたときのみAPI実行
    if submit_button:
        client = OpenAI()

        # 実行条件：developer_text, assistant_textを会話履歴として追加
        developer_txt = "あなたは強力な開発者であり、ソフトウェア開発者の専門家に教えるのが得意です。機能別にAPIの最新情報を提供し、それぞれのサンプルプログラムを示し、APIオプションについて説明してください。"
        assistant_txt = '回答は日本語で'

        input_txt = [
            EasyInputMessageParam(role="developer", content=developer_txt),
            EasyInputMessageParam(role="assistant", content=assistant_txt),
            EasyInputMessageParam(
                role="user",
                content=[
                    ResponseInputTextParam(
                        type="input_text",
                        text=question_text
                    ),
                    ResponseInputImageParam(
                        type="input_image",
                        image_url=image_url,
                        detail="auto"
                    )
                ]
            )
        ]
        response = client.responses.create(
            model=model,
            input=input_txt
        )

        # 出力の整形
        # 通常はresponse.outputやoutput_textを確認
        if hasattr(response, "output_text"):
            st.write(response.output_text)
        else:
            # より柔軟に
            st.write(str(response))

 # -----------------------------------------
 # 01_021 画像入力 by base64
 # -----------------------------------------
import base64
import glob
import os
# from IPython.display import Image, display
# - display(Image(url=url, width=400))

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def qa_01_021_base64_image(demo_name=None):
    st.write(f"# {demo_name if demo_name else '画像入力 (base64)'}")
    model = config_model()
    st.write("選択したモデル:", model)
    client = OpenAI()

    # （1）画像選択：指定ディレクトリからselect
    image_dir = "images/"
    # jpg/png/webp/gif を自動リストアップ
    img_files = sorted(
        glob.glob(os.path.join(image_dir, "*.png")) +
        glob.glob(os.path.join(image_dir, "*.jpg")) +
        glob.glob(os.path.join(image_dir, "*.jpeg")) +
        glob.glob(os.path.join(image_dir, "*.webp")) +
        glob.glob(os.path.join(image_dir, "*.gif"))
    )
    if not img_files:
        st.warning(f"画像ディレクトリ {image_dir} に画像ファイルがありません")
        return
    image_path = st.selectbox("画像ファイルを選択してください", img_files)

    # （2）プロンプト追加
    developer_txt = "あなたは強力な開発者であり、ソフトウェア開発者の専門家に教えるのが得意です。機能別にAPIの最新情報を提供し、それぞれのサンプルプログラムを示し、APIオプションについて説明してください。"
    user_txt = '入力画像の説明を日本語で実施しなさい。'
    assistant_txt = '回答は日本語で'

    # --- 実行フォーム ---
    with st.form(key="img_base64_form"):
        submit_button = st.form_submit_button(label="選択画像で実行")
    if submit_button:
        # 画像base64変換
        base64_image = encode_image(image_path)
        # 画像プレビュー
        st.image(image_path, caption="選択画像", width=320)

        input_messages = [
            EasyInputMessageParam(role="developer", content=developer_txt),
            EasyInputMessageParam(role="user", content=user_txt),
            EasyInputMessageParam(role="assistant", content=assistant_txt),
            EasyInputMessageParam(
                role="user",
                content=[
                    ResponseInputTextParam(
                        type="input_text",
                        text="what's in this image?"
                    ),
                    ResponseInputImageParam(
                        type="input_image",
                        image_url=f"data:image/jpeg;base64,{base64_image}",
                        detail="auto"
                    )
                ]
            )
        ]
        response = client.responses.create(
            model=model,
            input=input_messages,
        )

        # 結果表示
        st.subheader("出力テキスト:")
        if hasattr(response, "output_text"):
            st.write(response.output_text)
        else:
            st.write(str(response))

# ------------------------------------
# qa_01_03_structured_output: 構造化された出力
# ------------------------------------
def create_structured_response(model, messages, schema_name, schema):
    # Structured Outputs 用 TypedDict を直接インスタンス化
    outputs = ResponseTextConfigParam(
        format=ResponseFormatTextJSONSchemaConfigParam(
            name=schema_name,
            schema=schema,
            type="json_schema",
            strict=True
        )
    )
    client = OpenAI()
    res = client.responses.create(
        model=model,
        input=messages,
        text=outputs
    )
    return json.loads(res.output_text)

def qa_01_03_structured_output(demo_name=None):
    st.header("1. structured_output: イベント情報抽出デモ")
    model = st.selectbox("モデルを選択", ["o4-mini", "gpt-4o-2024-08-06", "gpt-4o-mini"])
    text = st.text_input(
        "イベント詳細を入力",
        "(例)台湾フェス2025 ～あつまれ！究極の台湾グルメ～ in Kawasaki Spark"
    )
    st.write("(例)台湾フェス2025 ～あつまれ！究極の台湾グルメ～ in Kawasaki Spark")
    if st.button("実行：イベント抽出"):
        messages = [
            {"role": "developer", "content": "Extract event details from the text."},
            {"role": "user", "content": text}
        ]
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "date": {"type": "string"},
                "participants": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["name", "date", "participants"],
            "additionalProperties": False
        }
        result = create_structured_response(
            model, messages,
            "event_extraction", schema
        )
        st.json(result)


# -------------------------------------------
# 01_04 関数呼び出し function calling
# -----------------------------------------
import pandas as pd

# 1. FunctionToolParamの定義
function_tool_param: FunctionToolParam = {
    "name": "get_current_weather",
    "description": "指定都市の現在の天気を返す",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {"type": "string"},
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"]
            }
        },
        "required": ["location"],
    },
    "strict": True,
    "type": "function",
}

def load_japanese_cities(csv_path: str) -> pd.DataFrame:
    # CSVファイルを読み込み
    df = pd.read_csv(csv_path)
    # 日本の都市のみを抽出
    df_japan = df[df['country'] == 'Japan'][['name', 'lat', 'lon']].drop_duplicates()
    # 都市名でソート
    df_japan = df_japan.sort_values('name').reset_index(drop=True)
    return df_japan

def select_city(df_japan: pd.DataFrame):
    # 都市名のリストを作成
    city_names = df_japan['name'].tolist()
    # Streamlitのセレクトボックスで都市を選択
    selected_city = st.selectbox("都市を選択してください", city_names)
    # 選択された都市の緯度と経度を取得
    city_data = df_japan[df_japan['name'] == selected_city].iloc[0]
    return selected_city, city_data['lat'], city_data['lon']

def get_current_weather_by_coords(lat: float, lon: float, unit: str = "metric") -> dict:
    """
    指定した緯度・経度の現在の天気を取得し、coord(lat, lon) を含む dict を返す。
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("環境変数 OPENWEATHER_API_KEY が設定されていません。")

    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={api_key}&units={unit}"
    )
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()

    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "coord": data["coord"]
    }


def get_weekly_forecast(lat: float, lon: float, unit: str = "metric") -> list[dict]:
    # 【無料プラン対応版】--------------------------
    # ・緯度・経度を指定して「5日／3時間毎」の予報を取得し、
    # ・日付ごとに平均気温と代表的な天気を計算して返す。
    # Returns:
    #   [{"date": "YYYY-MM-DD", "temp_avg": float, "weather": str},  ... ]
    # ------------------------------------------
    # 🔍 APIでの都市指定方法
    # OpenWeatherMapのAPIでは、以下のパラメータを使用して都市を指定できます。
    # ・都市名で指定：http://api.openweathermap.org/data/2.5/weather?q=Tokyo,jp&appid=YOUR_API_KEY
    # ・都市IDで指定：http://api.openweathermap.org/data/2.5/weather?id=1850147&appid=YOUR_API_KEY
    # ・緯度・経度で指定：http://api.openweathermap.org/data/2.5/weather?lat=35.6895&lon=139.6917&appid=YOUR_API_KEY
    # ---------------------------------------------
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("環境変数 OPENWEATHER_API_KEY が設定されていません。")

    # 5day/3hour forecast
    url = (
        f"http://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}&lon={lon}"
        f"&units={unit}&appid={api_key}"
    )
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()

    if "list" not in data:
        err = data.get("message", f"HTTP {res.status_code}")
        raise RuntimeError(f"OpenWeather 5日予報エラー: {err}")

    # 日付ごとに分けて平均気温を計算
    daily = {}
    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]
        temp = item["main"]["temp"]
        weather = item["weather"][0]["description"]
        if date not in daily:
            daily[date] = {"temps": [], "weather": weather}
        daily[date]["temps"].append(temp)

    forecast = []
    for date, info in daily.items():
        avg_temp = sum(info["temps"]) / len(info["temps"])
        forecast.append({
            "date": date,
            "temp_avg": round(avg_temp, 1),
            "weather": info["weather"]
        })

    return forecast

def qa_01_04_function_calling(demo_name=None):
    model = config_model()
    st.write("選択したモデル:", model)

    # 日本の都市リストを読み込み
    csv_path = "data/cities_list.csv"
    df_japan = load_japanese_cities(csv_path)

    # 都市を選択
    selected_city, lat, lon = select_city(df_japan)

    # 本日の天気
    today = get_current_weather_by_coords(lat, lon)
    st.write("----- 本日の天気 -----")
    st.write(f"都市       : {today['city']}")
    st.write(f"気温       : {today['temperature']}℃")
    st.write(f"説明       : {today['description']}")

    # 5日予報
    week = get_weekly_forecast(lat, lon)
    st.write("----- 5日間予報 （3時間毎を日別平均） -----")
    for day in week:
        st.write(f"{day['date']} : {day['temp_avg']}℃, {day['weather']}")


# -------------------------------------------
# 01_05 会話状態
# -----------------------------------------
def qa_01_05_conversation(demo_name=None):
    model = config_model()
    st.write("選択したモデル:", model)

# -------------------------------------------
# 01_06 ツールを使ってモデルを拡張する
# -----------------------------------------
def qa_01_06_extend_model(demo_name=None):
    model = config_model()
    st.write("選択したモデル:", model)


# ----------------------------------------------
def main():
    init_page()
    init_messages()

    page_names_to_funcs = {
        "01_01  QAのサンプル(One Shot)": qa_sample,
        "01_011 QAのサンプル(Memory付き)": qa_memory_sample,
        "01_02  画像入力(URL)": qa_01_02_passing_url,
        "01_021 画像入力(base64)": qa_01_021_base64_image,
        "01_03  構造化出力": qa_01_03_structured_output,
        "01_04  関数 calling": qa_01_04_function_calling,
        "01_05  会話状態": qa_01_05_conversation,
        "01_06  ツールでモデルを拡張": qa_01_06_extend_model
    }

    demo_name = st.sidebar.radio("モデルの選択", list(page_names_to_funcs.keys()))
    st.session_state.current_demo = demo_name
    page_names_to_funcs[demo_name](demo_name)

if __name__ == "__main__":
    main()
