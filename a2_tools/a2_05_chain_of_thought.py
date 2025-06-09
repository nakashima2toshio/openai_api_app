# streamlit run chain_of_thought.py --server.port=8505
#
# ─ ５種の代表的 CoT パターン
# [Menu] ------------------------------------
# 1. Step-by-Step（逐次展開型）
# 2. Hypothesis-Test（仮説検証型）
# 3. Tree-of-Thought（分岐探索型）
# 4. Pros-Cons-Decision（賛否比較型）
# 5. Plan-Execute-Reflect（反復改良型）
# ------------------------------------------
# 題名（日本語）	            題名（英語）	URL
# ------------------------------------------
# 信頼性を向上させるテクニック	                Techniques to improve reliability	https://cookbook.openai.com/articles/techniques_to_improve_reliability
# GPT-4.1 プロンプト活用ガイド	G               PT-4.1 Prompting Guide	https://cookbook.openai.com/examples/gpt4-1_prompting_guide
# Reasoningモデルでのファンクションコールの扱い方	Handling Function Calls with Reasoning Models	https://cookbook.openai.com/examples/reasoning_function_calls
# o3/o4-mini 関数呼び出しガイド	            o3/o4-mini Function Calling Guide	https://cookbook.openai.com/examples/o-series/o3o4-mini_prompting_guide
# Responses-APIを用いたReasoningモデルの性能向上	Better performance from reasoning models using the Responses API	https://cookbook.openai.com/examples/responses_api/reasoning_items
# 大規模言語モデルの活用方法	                How to work with large language models	https://cookbook.openai.com/articles/how_to_work_with_large_language_models
# 検索APIとリランキングによる質問応答	        Question answering using a search API and re-ranking	https://cookbook.openai.com/examples/question_answering_using_a_search_api
# LangChainでツール利用エージェントを構築する方法	How to build a tool-using agent with LangChain	https://cookbook.openai.com/examples/how_to_build_a_tool-using_agent_with_langchain
# Web 上の関連リソースまとめ	                Related resources from around the web	https://cookbook.openai.com/articles/related_resources
# Reasoning を活用したルーチン生成	            Using reasoning for routine generation	https://cookbook.openai.com/examples/o1/using_reasoning_for_routine_generation
# ------------------------------------------
import os
import sys

from a0_common_helper.helper import append_user_message
from a1_core_concept.a1_20__moderations import get_default_messages

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
from typing import List
from pydantic import BaseModel
from openai import OpenAI

# ------------------------------------------
# 1. Step-by-Step（逐次展開型）
#    用途: 算数・アルゴリズム・レシピ等の手順型タスク
# ------------------------------------------
class StepByStep(BaseModel):
    question: str
    steps: List[str]
    answer: str

# ------------------------------------------
# 2. Hypothesis-Test（仮説検証型）
#    用途: バグ解析・科学実験・A/B テスト
# ------------------------------------------
class HypothesisTest(BaseModel):
    problem: str
    hypothesis: str
    evidence: List[str] | None = None
    evaluation: str | None = None
    conclusion: str

# ------------------------------------------
# 3. Tree-of-Thought（分岐探索型）
#    用途: パズル・最適化・プランニング・ゲーム AI
# ------------------------------------------
class Branch(BaseModel):
    state: str
    action: str
    score: float | None = None

class TreeOfThought(BaseModel):
    goal: str
    branches: List[Branch]
    best_path: List[int] | None = None
    result: str

# ------------------------------------------
# 4. Pros-Cons-Decision（賛否比較型）
#    用途: 技術選定・意思決定ドキュメント・企画提案
# ------------------------------------------
class ProsConsDecision(BaseModel):
    topic: str
    pros: List[str] | None = None
    cons: List[str] | None = None
    decision: str
    rationale: str | None = None

# ------------------------------------------
# 5. Plan-Execute-Reflect（反復改良型）
#    用途: 自律エージェント・長期プロジェクト管理
# ------------------------------------------
class PlanExecuteReflect(BaseModel):
    objective: str
    plan: List[str]
    execution_log: List[str] | None = None
    reflect: str
    next_plan: List[str] | None = None

# ------------------------------------------
# OpenAI helper & 共通呼び出し関数
# ------------------------------------------
client = OpenAI()  # OPENAI_API_KEY を環境変数に設定

model_map = {
    "step:Step-by-Step（逐次展開型）": StepByStep,
    "hypo:Hypothesis-Test（仮説検証型）": HypothesisTest,
    "treeTree-of-Thought（分岐探索型）": TreeOfThought,
    "pros:Pros-Cons-Decision（賛否比較型）": ProsConsDecision,
    "plan:Plan-Execute-Reflect（反復改良型）": PlanExecuteReflect,
}

def request_cot(prompt: str, pattern: str, append_developer_message=None):
    # pattern: "step", "hypo", "tree", "pros", "plan"
    schema = model_map[pattern]

    message = get_default_messages()
    user_text = (
                    "You are an expert reasoning engine. "
                    "Return ONLY valid JSON conforming to the given schema."
                )
    message = append_developer_message(user_text)
    response = client.responses.parse(
        model="gpt-4.1",
        input=message,
        text_format=schema,  # Pydantic モデルを直接指定
    )
    return response.output_parsed  # → Pydantic インスタンス

# ------------------------------------------
# CLI テスト（逐次展開型の例）
# ------------------------------------------
if __name__ == "__main__":
    result = request_cot("2 と 5 を足してください。", pattern="step")
    print(result)
