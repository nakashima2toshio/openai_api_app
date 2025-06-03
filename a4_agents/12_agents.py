# python 12_agents.py
# pip install openai-agents
from pathlib import Path
import pandas as pd

"""
ファイル名	内容の概要
01_hello_world_sync.py	同期実行：基本的なエージェント動作
02_hello_world_async.py	非同期実行：asyncio によるエージェント動作
"""
# ==================================
# (1) 概要（intro）を箇条書きにする
#  (1) 概要（箇条書き）
# OpenAI Agents SDK は、シンプルな構成でエージェント型AIアプリを構築する Python SDK。
# Swarm の後継として、実運用に耐える軽量かつ生産性の高い設計。
# 3つの主要構成要素：
# Agent（命令付きLLM）
# Handoff（他のAgentへの委譲）
# Guardrail（入力検証）
# Python の自然なコード表現で複雑なエージェント連携も可能。
# トレーシング機能により、フローの可視化・デバッグ・評価・ファインチューニングが容易。
# 主な特徴：エージェントループ / handoffs / guardrails / 関数ツール / トレーシング。
# --------------------------------
overview_intro = [
    "OpenAI Agents SDK は、シンプルな構成でエージェント型AIアプリを構築するPython SDK。",
    "Swarm の後継として、実運用に耐える軽量かつ生産性の高い設計。",
    "3つの主要構成要素：Agent（命令付きLLM）、Handoff（他のAgentへの委譲）、Guardrail（入力検証）。",
    "Python の自然なコード表現で複雑なエージェント連携も可能。",
    "トレーシング機能により、フローの可視化・デバッグ・評価・ファインチューニングが容易。",
    "主な特徴：エージェントループ / handoffs / guardrails / 関数ツール / トレーシング。"
]

# (2) 抜粋されたPythonプログラム（Hello world）
sync_code = '''\
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)
'''

# (3) 非同期版（asyncio.run を使った変換）
async_code = '''\
from agents import Agent, Runner
import asyncio

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

async def main():
    result = await Runner.run(agent, "Write a haiku about recursion in programming.")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
'''

# ファイル出力先ディレクトリ
output_dir = Path("openai_agents_sdk_intro")
output_dir.mkdir(exist_ok=True)

file_list = []

# 同期版コード
sync_path = output_dir / "01_hello_world_sync.py"
sync_path.write_text(sync_code)
file_list.append((sync_path.name, "同期実行：基本的なエージェント動作"))

# 非同期版コード
async_path = output_dir / "02_hello_world_async.py"
async_path.write_text(async_code)
file_list.append((async_path.name, "非同期実行：asyncio によるエージェント動作"))

# 出力結果の表示
df = pd.DataFrame(file_list, columns=["ファイル名", "内容の概要"])
import ace_tools as tools; tools.display_dataframe_to_user(name="出力されたファイル一覧", dataframe=df)

# 箇条書きの概要も返す
overview_intro

"""
ファイル名	内容の概要
01_quickstart_triage_with_guardrail.py	handoffs + guardrail + 非同期エージェント構成の統合実行
"""
# --------------------------------
# 概要
# プロジェクト作成と仮想環境（venv）をセットアップして開始。
# OpenAI Agents SDK を pip でインストール（pip install openai-agents）。
# APIキー（OPENAI_API_KEY）を環境変数で設定。
# Agent は name と instructions により簡単に定義可能。
# 複数エージェントを handoff 機能で連携させることができる。
# Guardrail（入力検証）を追加して、ユーザー入力を事前チェック可能。
# Guardrail + handoffs を統合して、triage agent が動的に処理をルーティング。
# 実行は非同期 (asyncio.run(...)) で行い、OpenAI の Trace Viewer でトレースが可能。
# (2) 概要（intro）を箇条書きにする
# --------------------------------
from pathlib import Path
import pandas as pd

# (1) 概要（quick-start）を箇条書きでまとめ
overview_quickstart = [
    "プロジェクト作成と仮想環境（venv）をセットアップして開始。",
    "OpenAI Agents SDK を pip でインストール（`pip install openai-agents`）。",
    "APIキー（`OPENAI_API_KEY`）を環境変数で設定。",
    "Agent は name と instructions で定義可能。",
    "複数の Agent を handoff（委譲）構成で組み合わせてオーケストレーション。",
    "ガードレール（guardrail）を使って入力を検証・制御可能。",
    "すべてを統合して、ガードレール付き triage agent でルーティング実行。",
    "非同期（`asyncio.run(...)`）で実行。トレースも OpenAI ダッシュボードで確認可能。"
]

# (2) Python コードの抜き出し（サンプル統合コード）
code_combined = '''\
from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from pydantic import BaseModel
import asyncio

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail),
    ],
)

async def main():
    result = await Runner.run(triage_agent, "who was the first president of the united states?")
    print(result.final_output)

    result = await Runner.run(triage_agent, "what is life")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
'''

# 出力先ディレクトリ
output_dir = Path("openai_agents_sdk_quickstart")
output_dir.mkdir(exist_ok=True)

# ファイル保存
filepath = output_dir / "01_quickstart_triage_with_guardrail.py"
filepath.write_text(code_combined)

# 出力リスト整形
file_list = [("01_quickstart_triage_with_guardrail.py", "handoffs + guardrail + 非同期エージェント構成の統合実行")]

df = pd.DataFrame(file_list, columns=["ファイル名", "内容の概要"])
import ace_tools as tools; tools.display_dataframe_to_user(name="出力されたファイル一覧", dataframe=df)

# 箇条書きの概要も返す
overview_quickstart

# --------------------------------
# 概要
# --------------------------------

