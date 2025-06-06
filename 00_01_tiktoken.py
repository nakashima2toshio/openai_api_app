# https://github.com/openai/tiktoken/blob/main/README.md
# !pip install tiktoken  # Byte pair encoding

import tiktoken
import pprint

def main():
    enc = tiktoken.get_encoding("o200k_base")
    assert enc.decode(enc.encode("hello world")) == "hello world"

    # To get the tokeniser corresponding to a specific model in the OpenAI API:
    enc = tiktoken.encoding_for_model("gpt-4o")
    pprint.pprint(enc)


if __name__ == '__main__':
    main()

