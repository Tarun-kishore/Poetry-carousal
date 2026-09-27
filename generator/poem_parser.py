from .config import POEM_FILE


def load_poem():
    if not POEM_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {POEM_FILE}."
        )

    text = POEM_FILE.read_text(encoding="utf-8")
    lines = text.splitlines()

    title = ""
    slides = []
    current_slide = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("TITLE:"):
            title = stripped[len("TITLE:"):].strip()
            continue

        if stripped.startswith("# "):
            title = stripped[2:].strip()
            continue

        # Kept for compatibility, but MOOD is now ignored.
        if stripped.upper().startswith("MOOD:"):
            continue

        if stripped == "---":
            if current_slide:
                slides.append(current_slide)
                current_slide = []
            continue

        if stripped == "":
            if current_slide:
                current_slide.append("")
            continue

        current_slide.append(line)

    if current_slide:
        slides.append(current_slide)

    return title, slides
