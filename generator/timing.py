import re

from .config import (
    OPENING_MIN,
    OPENING_MAX,
    MIDDLE_MIN,
    MIDDLE_MAX,
    ENDING_MIN,
    ENDING_MAX,
)

DRAMATIC_LINES = {
    "split.",
    "shattered.",
    "silence.",
    "alone.",
    "gone.",
    "scum.",
    "good.",
    "bad.",
    "me.",
    "murder.",
}


def get_text(lines):
    return " ".join(
        line
        for line in lines
        if line.strip()
    )


def calculate_base_duration(lines):
    text = get_text(lines)

    if not text:
        return MIDDLE_MIN

    words = re.findall(r"\S+", text)
    word_count = len(words)

    if word_count <= 3:
        seconds = 1.7
    elif word_count <= 8:
        seconds = 2.2
    elif word_count <= 15:
        seconds = 2.8
    elif word_count <= 25:
        seconds = 3.5
    else:
        seconds = 4.2

    punctuation_count = len(
        re.findall(r"[,.!?;:]", text)
    )

    seconds += punctuation_count * 0.12

    lower_text = text.lower().strip()

    if lower_text in DRAMATIC_LINES:
        seconds = max(seconds, 2.3)

    return max(
        MIDDLE_MIN,
        min(seconds, MIDDLE_MAX)
    )


def calculate_slide_duration(
    lines,
    slide_index,
    total_slides
):
    duration = calculate_base_duration(lines)

    if slide_index < 3:
        duration = max(
            OPENING_MIN,
            min(duration, OPENING_MAX)
        )

    if (
        total_slides > 0
        and slide_index == total_slides - 1
    ):
        duration = max(
            ENDING_MIN,
            min(duration, ENDING_MAX)
        )

    return duration
