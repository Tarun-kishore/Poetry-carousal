import re

HOOK_WORDS = {
    "but",
    "then",
    "until",
    "suddenly",
    "realized",
    "realise",
    "thought",
    "wrong",
    "never",
    "alone",
    "dead",
    "death",
    "inside",
    "outside",
    "dark",
    "nothing",
    "someone",
    "something",
    "why",
    "how",
}


def get_slide_text(slide):
    return " ".join(
        line
        for line in slide
        if line.strip()
    )


def analyze_poem(title, slides):
    if not slides:
        return

    first_text = get_slide_text(slides[0])

    full_text = " ".join(
        get_slide_text(slide)
        for slide in slides
    )

    words = re.findall(r"\S+", full_text)
    word_count = len(words)

    hook_matches = 0

    for word in re.findall(
        r"[A-Za-z']+",
        first_text.lower()
    ):
        if word in HOOK_WORDS:
            hook_matches += 1

    last_text = get_slide_text(slides[-1])

    print()
    print("==============================")
    print("        REEL ANALYSIS")
    print("==============================")
    print()

    print(f"Slides:       {len(slides)}")
    print(f"Word count:   {word_count}")
    print(f"Opening:      {first_text}")
    print(f"Ending:       {last_text}")

    if hook_matches > 0:
        print("Opening hook: DETECTED")
    else:
        print("Opening hook: SUBTLE")

    if len(last_text.split()) <= 10:
        print(
            "Final payoff: SHORT / "
            "good candidate for a pause"
        )
    else:
        print("Final payoff: LONG")

    print()
