# [ usage ] streamlit run a1_10_get_submenu_url.py --server.port 8501
# port Check: lsof -i :5678
from openai import OpenAI
from openai.types.responses import Response
from openai.types.responses import EasyInputMessageParam

import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from urllib.parse import urljoin

doc_txt="""Agents
Agents are the core building block in your apps. An agent is a large language model (LLM), configured with instructions and tools.

Basic configuration
The most common properties of an agent you'll configure are:

instructions: also known as a developer message or system prompt.
model: which LLM to use, and optional model_settings to configure model tuning parameters like temperature, top_p, etc.
tools: Tools that the agent can use to achieve its tasks.

from agents import Agent, ModelSettings, function_tool

@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny"

agent = Agent(
    name="Haiku agent",
    instructions="Always respond in haiku form",
    model="o3-mini",
    tools=[get_weather],
)
Context
Agents are generic on their context type. Context is a dependency-injection tool: it's an object you create and pass to Runner.run(), that is passed to every agent, tool, handoff etc, and it serves as a grab bag of dependencies and state for the agent run. You can provide any Python object as the context.


@dataclass
class UserContext:
    uid: str
    is_pro_user: bool

    async def fetch_purchases() -> list[Purchase]:
        return ...

agent = Agent[UserContext](
    ...,
)
Output types
By default, agents produce plain text (i.e. str) outputs. If you want the agent to produce a particular type of output, you can use the output_type parameter. A common choice is to use Pydantic objects, but we support any type that can be wrapped in a Pydantic TypeAdapter - dataclasses, lists, TypedDict, etc.


from pydantic import BaseModel
from agents import Agent


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

agent = Agent(
    name="Calendar extractor",
    instructions="Extract calendar events from text",
    output_type=CalendarEvent,
)
Note

When you pass an output_type, that tells the model to use structured outputs instead of regular plain text responses.

Handoffs
Handoffs are sub-agents that the agent can delegate to. You provide a list of handoffs, and the agent can choose to delegate to them if relevant. This is a powerful pattern that allows orchestrating modular, specialized agents that excel at a single task. Read more in the handoffs documentation.


from agents import Agent

booking_agent = Agent(...)
refund_agent = Agent(...)

triage_agent = Agent(
    name="Triage agent",
    instructions=(
        "Help the user with their questions."
        "If they ask about booking, handoff to the booking agent."
        "If they ask about refunds, handoff to the refund agent."
    ),
    handoffs=[booking_agent, refund_agent],
)
Dynamic instructions
In most cases, you can provide instructions when you create the agent. However, you can also provide dynamic instructions via a function. The function will receive the agent and context, and must return the prompt. Both regular and async functions are accepted.


def dynamic_instructions(
    context: RunContextWrapper[UserContext], agent: Agent[UserContext]
) -> str:
    return f"The user's name is {context.context.name}. Help them with their questions."


agent = Agent[UserContext](
    name="Triage agent",
    instructions=dynamic_instructions,
)
Lifecycle events (hooks)
Sometimes, you want to observe the lifecycle of an agent. For example, you may want to log events, or pre-fetch data when certain events occur. You can hook into the agent lifecycle with the hooks property. Subclass the AgentHooks class, and override the methods you're interested in.

Guardrails
Guardrails allow you to run checks/validations on user input, in parallel to the agent running. For example, you could screen the user's input for relevance. Read more in the guardrails documentation.

Cloning/copying agents
By using the clone() method on an agent, you can duplicate an Agent, and optionally change any properties you like.


pirate_agent = Agent(
    name="Pirate",
    instructions="Write like a pirate",
    model="o3-mini",
)

robot_agent = pirate_agent.clone(
    name="Robot",
    instructions="Write like a robot",
)
Forcing tool use
Supplying a list of tools doesn't always mean the LLM will use a tool. You can force tool use by setting ModelSettings.tool_choice. Valid values are:

auto, which allows the LLM to decide whether or not to use a tool.
required, which requires the LLM to use a tool (but it can intelligently decide which tool).
none, which requires the LLM to not use a tool.
Setting a specific string e.g. my_tool, which requires the LLM to use that specific tool.
Note

To prevent infinite loops, the framework automatically resets tool_choice to "auto" after a tool call. This behavior is configurable via agent.reset_tool_choice. The infinite loop is because tool results are sent to the LLM, which then generates another tool call because of tool_choice, ad infinitum.

If you want the Agent to completely stop after a tool call (rather than continuing with auto mode), you can set [Agent.tool_use_behavior="stop_on_first_tool"] which will directly use the tool output as the final response without further LLM processing.
"""

# --- st.set_page_config() はインポート直後に実行する ---
st.set_page_config(
    page_title="ChatGPT Chat Completions",
    page_icon="NT"
)

developer_content = (
    "You are a strong developer and good at teaching software developer professionals; "
    "please provide an up-to-date, informed overview of the API by function, then show cookbook programs for each, "
    "and explain the API options."
)
user_content = (
    "Organize and identify the problem and list the issues. Then, provide a solution procedure for the issues you have "
    "organized and identified, and Solve the problems/issues according to the solution procedures."
)
assistant_content = '回答は日本語で'

role_message = [
    {"role": "developer", "content": developer_content},
    {"role": "user", "content": user_content},
    {"role": "assistant", "content": assistant_content},
]

# --- format_message() の定義を追加 ---
def format_message(msg):
    return msg

def init_page():
    st.header("最新Web情報からRAGデータを作成する。")
    st.sidebar.title("Rag - 処理手順")

def init_messages():
    if st.sidebar.button("会話履歴のクリア", key="clear") or "message_history" not in st.session_state:
        st.session_state.message_history = role_message

def config_model(demo_name="設定"):
    models = ["gpt-4o", "gpt-4o-mini", "o3-mini", "o3", "o4-mini", "o4"]
    return st.sidebar.radio("Choose a model:", models)

def create_responses_api(model, user_input) -> Response:
    client = OpenAI()
    return client.responses.create(model=model, input=user_input)

def extract_text_from_response(response):
    texts = []
    for item in getattr(response, 'output', []):
        if getattr(item, 'type', None) == "message":
            for content_obj in getattr(item, 'content', []):
                if getattr(content_obj, 'type', None) == "output_text":
                    texts.append(getattr(content_obj, 'text', ''))
    return texts

# --------------------------
# (1) CRAWL: SubMenuとそのURL情報
# --------------------------
def extract_sidebar_links(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    sidebar = soup.find('nav', class_='md-nav md-nav--primary')
    if not sidebar:
        st.error("メニューが見つかりませんでした。(クラス名が正しくありません)")
        return None
    links = sidebar.find_all('a', class_='md-nav__link')
    data = []
    for link in links:
        text = link.get_text(strip=True).replace('/', '_').replace(' ', '_')
        full_url = urljoin(url, link.get('href'))
        data.append([text, full_url])
    return pd.DataFrame(data, columns=['タイトル_サブタイトル', 'URL'])

# --------------------------
# (1) submenuとURL取得とCSV出力
# --------------------------
def submenu_urls(demo_name=None):
    st.write("・指定URLのWeb画面の左メニューのメニュー：リンクからRAGデータを作成する。")
    st.write("・デフォルト（例）はOpenAIのOpenAI Agents SDKのWebページです。")
    st.write("")
    url = st.text_input(
        "対象のURLを入力してください:",
        value="https://openai.github.io/openai-agents-python/"
    )
    if st.button("CSVデータ生成"):
        df = extract_sidebar_links(url)
        if df is not None:
            st.write("取得したデータ:")
            st.dataframe(df)

            # data フォルダ作成
            data_dir = Path("data")
            data_dir.mkdir(parents=True, exist_ok=True)
            file_path = data_dir / "menu_links.csv"

            # CSV 保存
            df.to_csv(file_path, index=False, encoding="utf-8-sig")
            st.success(f"CSV を保存しました: `{file_path}`")

# --------------------------
# (2) submenuのコンテンツを表示、データ分解
# --------------------------
def submenu_content(demo_name=None):
    # カスタムプロンプト（必要に応じて本文の最後に付与）
    developer_cnt = (
        "あなたは強力な開発者であり、ソフトウェア開発者の専門家を教えるのが得意です。"
        "機能別にAPIの概要を最新かつ詳細に説明し、それぞれのサンプルプログラムを示し、"
        "そしてAPIのオプションについて説明してください。"
    )
    user_cnt = (
        "・提供されたテキストの概要を作成せよ。・内容を箇条書きにまとめ、説明せよ。"
    )
    # モデル選択 UI
    selected_model = config_model()

    st.write("サブメニューのコンテンツを表示する。")

    # CSV 読み込み
    data_dir = Path("data")
    file_path = data_dir / "menu_links.csv"
    if not file_path.exists():
        st.error("`data/menu_links.csv` が見つかりません。先に URL 取得デモで CSV を生成してください。")
        return
    df = pd.read_csv(file_path)

    # カラムチェック
    if 'タイトル_サブタイトル' not in df.columns or 'URL' not in df.columns:
        st.error("CSV のカラムが 'タイトル_サブタイトル' と 'URL' で構成されていません。")
        return

    # サブメニュー選択
    options = df['タイトル_サブタイトル'].tolist()
    selected = st.selectbox("サブメニューを選択してください", options)

    # 実行ボタン
    if st.button("表示を実行"):
        url = df.loc[df['タイトル_サブタイトル'] == selected, 'URL'].values[0]
        st.write(f"選択された URL: {url}")

        # ページをクロールして本文テキストを抽出
        try:
            page_resp = requests.get(url)
            page_resp.raise_for_status()
            soup = BeautifulSoup(page_resp.text, 'html.parser')
            paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
            url_text = "\n\n".join(paragraphs)
        except Exception as e:
            st.error(f"ページ取得または本文抽出に失敗しました: {e}")
            return

        # 必要であればプロンプトを追加
        url_text = url_text + "\n\n" + developer_cnt + "\n\n" + user_cnt

        # Responses API 呼び出し
        client = OpenAI()
        res = client.responses.create(model=selected_model, input=url_text)

        # output[1] が存在すれば第一メッセージ（実際の応答）を取得して表示
        if hasattr(res, "output") and len(res.output) > 1:
            second_item = res.output[1]
            st.write("■ output[1] の生オブジェクト:")
            st.write(second_item)

            # content があれば中のテキストのみループで出力
            if hasattr(second_item, "content"):
                st.write("■ output[1] のテキスト:")
                for content_obj in second_item.content:
                    st.write(content_obj.text)
            else:
                st.warning("output[1] に content フィールドがありません")
        else:
            st.warning("output の 2 番目の要素が見つかりませんでした")

# --------------------------
# SubMenu Get Programming-Code
# --------------------------
def submenu_get_pg(demo_name=None):
    # カスタムプロンプト（必要に応じて本文の最後に付与）
    developer_cnt2 = (
        "あなたは強力な開発者であり、ソフトウェア開発者の専門家を教えるのが得意です。"
        "機能別にAPIの概要を最新かつ詳細に説明し、それぞれのサンプルプログラムを示し、"
        "そしてAPIのオプションについて説明してください。"
    )
    user_cnt2 = (
        "・提供されたテキストの概要を作成せよ。・内容を箇条書きにまとめ、説明せよ。"
    )
    assistant_cnt2 = '回答は日本語で'

    user_txt = user_cnt2 + doc_txt
    # ← ここを dict から EasyInputMessageParam に置き換え
    input_messages = [
        EasyInputMessageParam(role="developer", content=developer_cnt2),
        EasyInputMessageParam(role="user",      content=user_txt),
        EasyInputMessageParam(role="assistant", content=assistant_cnt2),
    ]

    # モデル選択 UI
    selected_model = config_model()

    # Responses API 呼び出し
    client = OpenAI()
    res = client.responses.create(
        model=selected_model,
        input=input_messages  # ← 正しい型のリスト
    )
    # output[1] が存在すれば第一メッセージ（実際の応答）を取得して表示
    if hasattr(res, "output") and len(res.output) > 1:
        second_item = res.output[1]
        st.write("■ output[1] の生オブジェクト:")
        st.write(second_item)

        # content があれば中のテキストのみループで出力
        if hasattr(second_item, "content"):
            st.write("■ output[1] のテキスト:")
            for content_obj in second_item.content:
                st.write(content_obj.text)
        else:
            st.warning("output[1] に content フィールドがありません")
    else:
        st.warning("output の 2 番目の要素が見つかりませんでした")

# --------------------------
# Submenu Embedding
# --------------------------
def submenu_embedding(demo_name=None):
    pass

# --------------------------
# QAサンプル
# --------------------------
def qa_sample(demo_name=None):
    st.write(f"# {demo_name}")
    selected_model = config_model()
    st.write("選択したモデル:", selected_model)

    with st.form(key="qa_form"):
        user_input = st.text_area("ここにテキストを入力してください:", height=75)
        submit_button = st.form_submit_button(label="送信")
    if submit_button and user_input:
        response = create_responses_api(model=selected_model, user_input=user_input)
        for text in extract_text_from_response(response):
            st.write(text)
        with st.form(key="qa_next_form"):
            if st.form_submit_button(label="次の質問"):
                st.rerun()

# --------------------------
# メイン
# --------------------------
def main():
    init_page()
    init_messages()
    demos = {
        "(1)submenuのurl取得しCSV化": submenu_urls,
        "(2)submenuのコンテンツ解析": submenu_content,
        "(3)submenuのプログラム抽出": submenu_get_pg,
        "(4)submenuのembedding": submenu_embedding,
        "QAサンプル(One Shot)": qa_sample,
    }
    choice = st.sidebar.radio("Choose a demo", list(demos.keys()))
    demos[choice](choice)

if __name__ == "__main__":
    main()

