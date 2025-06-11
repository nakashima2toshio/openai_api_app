#　utils/get_embedding.py
from openai import OpenAI

client = OpenAI()
def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    # selected_embedding_model = config_embedding_model()
    response = client.embeddings.create(
        model=model,
        input=[text],            # string or array
        encoding_format="float",  # float or base64
        dimensions = 1536
    )
    embedding = response.data[0].embedding  # response['data'][0]['embedding']
    return embedding
