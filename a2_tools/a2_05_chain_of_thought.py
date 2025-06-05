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

# 処理のパターン：
# ------------------------------------------
# 1. Step-by-Step（逐次展開型）
# ------------------------------------------
# フィールド	型	説明
# question	str	問い／課題
# steps	list[str]	解決までのステップ列
# answer	str	結論
#
# 必須：すべて
# 用途：算数・アルゴリズム・レシピなど順序性が高いタスク
# ------------------------------------------
from openai import OpenAI
from a0_common_helper.helper import get_default_messages, Response

from pydantic import BaseModel
from typing import List
import responses  # 自作 or 任意のパーサ

class StepByStep(BaseModel):
    question: str
    steps: List[str]
    answer: str

# --- 受信後 ---
raw = chat_completion.choices[0].message.content  # JSON 文字列
cot = responses.parse(raw, StepByStep)            # または StepByStep.model_validate_json(raw)

# ------------------------------------------
# 2. Hypothesis-Test（仮説検証型）
# ------------------------------------------
# フィールド	型	説明
# problem	str	観測された問題
# hypothesis	str	立てた仮説
# evidence	list[str]	データ・根拠
# evaluation	str	仮説の検証結果
# conclusion	str	結論／次のアクション
#
# 必須：problem, hypothesis, conclusion
# 用途：バグ解析、科学実験、A/B テスト結果整理
# ------------------------------------------
class HypothesisTest(BaseModel):
    problem: str
    hypothesis: str
    evidence: List[str] | None = None
    evaluation: str | None = None
    conclusion: str

# ------------------------------------------
# 3. Tree-of-Thought（分岐探索型）
# ------------------------------------------
# フィールド	型	説明
# goal	str	目的
# branches	list[dict]	各分岐の記録
# 例：{"state": "...", "action": "...", "score": float}
# best_path	list[int]	最良経路の分岐 index 列
# result	str	得られた解
#
# 必須：goal, branches, result
# 用途：探索・最適化（パズル、プランニング、ゲーム AI など）
# ------------------------------------------
from typing import Dict, Any

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
# ------------------------------------------
# フィールド	型	説明
# topic	str	検討テーマ
# pros	list[str]	利点
# cons	list[str]	欠点
# decision	str	最終判断
# rationale	str	判断理由
#
# 必須：topic, decision
# 用途：技術選定、意思決定ドキュメント、企画提案
# ------------------------------------------
class ProsConsDecision(BaseModel):
    topic: str
    pros: List[str] | None = None
    cons: List[str] | None = None
    decision: str
    rationale: str | None = None

# ------------------------------------------
# 5. Plan-Execute-Reflect（反復改良型）
# ------------------------------------------
# フィールド	型	説明
# objective	str	長期目標
# plan	list[str]	今回の計画
# execution_log	list[str]	実行時ログ／結果
# reflect	str	振り返り
# next_plan	list[str]	次サイクル案
#
# 必須：objective, plan, reflect
# 用途：自律エージェントのループ、長期プロジェクト管理
# ------------------------------------------
class PlanExecuteReflect(BaseModel):
    objective: str
    plan: List[str]
    execution_log: List[str] | None = None
    reflect: str
    next_plan: List[str] | None = None

# ------------------------------------------
# 共通的な呼び出しフロー（疑似コード）
# ------------------------------------------
from openai import OpenAI
client = OpenAI()

model_map = {
    "step": StepByStep,
    "hypo": HypothesisTest,
    "tree": TreeOfThought,
    "pros": ProsConsDecision,
    "plan": PlanExecuteReflect,
}

def request_cot(prompt: str, pattern: str):
    schema = model_map[pattern]
    sys = "あなたは優秀な思考過程エンジンです。以下の JSON スキーマに従って回答してください。"
    user = prompt

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": sys},
                  {"role": "user", "content": user}]
    )

    raw_json = resp.choices[0].message.content
    cot_obj = responses.parse(raw_json, schema)  # または schema.model_validate_json(raw_json)
    return cot_obj


