import json
import re
from bs4 import BeautifulSoup


def remove_emojis(text):

    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # geometric shapes extended
        "\U0001F800-\U0001F8FF"  # supplemental arrows
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA00-\U0001FA6F"  # chess, etc.
        "\U0001FA70-\U0001FAFF"  # extended symbols
        "\U00002700-\U000027BF"  # dingbats
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text)


def clean_text(text):
    if not text:
        return ""

    # 1. Remove HTML tags
    text = BeautifulSoup(text, "html.parser").get_text()

    # 2. Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "[URL]", text, flags=re.MULTILINE)

    # 3. Remove emojis
    text = remove_emojis(text)

    # 4. Remove escape characters
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")

    # 5. Remove non-ASCII symbols (optional but keeps dataset clean)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # 6. Normalize spacing
    text = re.sub(r"\s+", " ", text).strip()

    return text


def process_memory():
    input_path = "memory.json"
    output_path = "clean_memory.json"

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = []
    for email in data:
        email["body"] = clean_text(email.get("body", ""))
        cleaned_data.append(email)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)

    print(f"Cleaned {len(cleaned_data)} emails. Ready for AI.")


if __name__ == "__main__":
    process_memory()
