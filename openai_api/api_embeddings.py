# api_embeddings.py
"""
[Rag] https://cookbook.openai.com/examples/responses_api/responses_api_tool_orchestration
[Cookbook ] https://cookbook.openai.com/
[API      ]  https://github.com/openai/openai-python
[Agent SDK] https://github.com/openai/openai-agents-python
"""
from openai import OpenAI
from openai.types.responses import EasyInputMessageParam

def api_embeddings(developer_txt, user_txt, assistant_txt, model_name="o4-mini"):
    model_name = model_name
    input_messages = [
        EasyInputMessageParam(role="developer", content=developer_txt),
        EasyInputMessageParam(role="user",      content=user_txt),
        EasyInputMessageParam(role="assistant", content=assistant_txt),
    ]
    client = OpenAI()
    response = client.embeddings.create(
        model=model_name,
        input=input_messages,
    )
    return response
