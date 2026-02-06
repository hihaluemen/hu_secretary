import re


def clean_text(text: str) -> str:
    normalized = re.sub(r"\s+", " ", (text or "").strip())
    normalized = (
        normalized.replace("：", ":")
        .replace("，", ",")
        .replace("。", ".")
        .replace("？", "?")
    )
    return normalized

