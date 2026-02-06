from app.utils.text import clean_text


def test_clean_text_normalizes_spaces_and_punctuation():
    raw = "  明天  上午9点，开会：讨论方案。  "
    assert clean_text(raw) == "明天 上午9点,开会:讨论方案."

