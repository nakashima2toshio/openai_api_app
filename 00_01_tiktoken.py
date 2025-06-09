# https://github.com/openai/tiktoken/blob/main/README.md
# !pip install tiktoken  # Byte pair encoding
# pip install --upgrade tiktoken
import tiktoken
from typing import List

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    # ------------------------------------------
    # Return the number of tokens `text` occupies for the specified OpenAI model.
    # ------------------------------------------
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def tail_from_tokens(text: str, max_tokens: int, model: str = "gpt-4o") -> str:
    # ------------------------------------------
    # Return the last `max_tokens` tokens of `text` as a decoded string.
    # If the text is shorter, the original text is returned unchanged.
    # ------------------------------------------
    enc = tiktoken.encoding_for_model(model)
    tokens: List[int] = enc.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return enc.decode(tokens[-max_tokens:])

# --- 使い方例 ----------------------------
if __name__ == "__main__":
    sample_text = "OpenAI の GPT-4.1 はコンテキスト長が 1M トークンに拡大しました。"
    total = count_tokens(sample_text, model="gpt-4o")
    print(f"トークン数: {total}")
    trimmed = tail_from_tokens(sample_text, max_tokens=10, model="gpt-4o")
    print(f"末尾10トークン: {trimmed}")

