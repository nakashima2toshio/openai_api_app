# api_responses.py
""" 情報：
[Cookbook ] https://cookbook.openai.com/
[API      ]  https://github.com/openai/openai-python
[Agent SDK] https://github.com/openai/openai-agents-python
--- --------------
[Model] https://platform.openai.com/docs/pricing
"""
from openai import OpenAI
from openai.types.responses import EasyInputMessageParam

def api_responses(developer_txt, user_txt, assistant_txt, model_name="o4-mini"):
    model_name = model_name
    input_messages = [
        EasyInputMessageParam(role="developer", content=developer_txt),
        EasyInputMessageParam(role="user",      content=user_txt),
        EasyInputMessageParam(role="assistant", content=assistant_txt),
    ]

    # Responses API 呼び出し
    client = OpenAI()
    response = client.responses.create(
        model=model_name,
        input=input_messages,
    )
    # テキストも読み取って返す。
    # output[1] が存在すれば第一メッセージ（実際の応答）を取得して表示
    if hasattr(response, "output") and len(response.output) > 1:
        # output[1] の生オブジェクト
        second_item = response.output[1]
        output_1_content = None
        # content があれば中のテキストのみループで出力
        if hasattr(second_item, "content"):
            # st.write("■ output[1] のテキスト:")
            for content_obj in second_item.content:
                output_1_content = output_1_content + content_obj
                # st.write(content_obj.text)
        else:
            output_1_content = None
            # st.warning("output[1] に content フィールドがありません")
    else:
        output_1_content = None
        # st.warning("output の 2 番目の要素が見つかりませんでした")

    return response, output_1_content

