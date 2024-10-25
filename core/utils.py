import tiktoken
import base64

MAX_TOKENS = 256
encoder = tiktoken.encoding_for_model("gpt-4o-mini")


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def count_tokens(text):
    tokens = encoder.encode(text)
    return len(tokens)


def split_text(text: str, max_tokens: int = MAX_TOKENS):
    tokens = encoder.encode(text)
    chunks = [tokens[i : i + max_tokens] for i in range(0, len(tokens), max_tokens)]
    chunked_texts = [encoder.decode(chunk) for chunk in chunks]
    return chunked_texts


def truncate_text(text, max_tokens=MAX_TOKENS):
    tokens = encoder.encode(text)
    if len(tokens) > max_tokens:
        return encoder.decode(tokens[:max_tokens])
    return text


def main():
    text = "This is a test sentence. This is another test sentence. This is a third test sentence."
    print(split_text(text, 5))


if __name__ == "__main__":
    main()
