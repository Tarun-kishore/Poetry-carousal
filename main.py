from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess
import imageio_ffmpeg
import re


# ============================================================
# SETTINGS
# ============================================================

WIDTH = 1080
HEIGHT = 1350

REEL_WIDTH = 1080
REEL_HEIGHT = 1920

FPS = 30

TITLE_FONT_SIZE = 90
BODY_FONT_SIZE = 58
PAGE_FONT_SIZE = 28

MIN_SLIDE_SECONDS = 2.5
MAX_SLIDE_SECONDS = 7.0

TITLE_DURATION = 3.0

FONT_PATH = Path("font.ttf")

POEM_FILE = Path("poem.txt")

OUTPUT_FOLDER = Path("output")


# ============================================================
# THEMES
# ============================================================

THEMES = {
    "1": {
        "name": "Midnight",
        "type": "solid",
        "background": "#080808",
        "text": "#E8E8E8",
        "page": "#666666",
    },

    "2": {
        "name": "Paper",
        "type": "solid",
        "background": "#F2EFE8",
        "text": "#171717",
        "page": "#88847C",
    },

    "3": {
        "name": "Dusk",
        "type": "gradient",
        "gradient_start": "#050817",
        "gradient_end": "#55356F",
        "text": "#EEEAF2",
        "page": "#81788A",
    },

    "4": {
        "name": "Ember",
        "type": "gradient",
        "gradient_start": "#050505",
        "gradient_end": "#64252D",
        "text": "#F0E8E8",
        "page": "#80696C",
    },
}


# ============================================================
# FONT
# ============================================================

def load_font(size):
    if not FONT_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {FONT_PATH}.\n"
            f"Put your .ttf font in the same folder as main.py "
            f"and rename it to font.ttf."
        )

    return ImageFont.truetype(
        str(FONT_PATH),
        size
    )


# ============================================================
# COLORS / BACKGROUND
# ============================================================

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i + 2], 16)
        for i in (0, 2, 4)
    )


def create_background(width, height, theme):

    if theme["type"] == "solid":

        return Image.new(
            "RGB",
            (width, height),
            hex_to_rgb(theme["background"])
        )

    start = hex_to_rgb(theme["gradient_start"])
    end = hex_to_rgb(theme["gradient_end"])

    image = Image.new(
        "RGB",
        (width, height)
    )

    draw = ImageDraw.Draw(image)

    max_distance = width + height - 2

    for y in range(height):

        for x in range(width):

            ratio = (x + y) / max_distance

            ratio = max(
                0,
                min(1, ratio)
            )

            r = int(
                start[0]
                + (end[0] - start[0]) * ratio
            )

            g = int(
                start[1]
                + (end[1] - start[1]) * ratio
            )

            b = int(
                start[2]
                + (end[2] - start[2]) * ratio
            )

            draw.point(
                (x, y),
                fill=(r, g, b)
            )

    return image


# ============================================================
# POEM PARSER
# ============================================================

def load_poem():

    if not POEM_FILE.exists():

        raise FileNotFoundError(
            f"Could not find {POEM_FILE}."
        )

    text = POEM_FILE.read_text(
        encoding="utf-8"
    )

    lines = text.splitlines()

    title = ""
    slides = []

    current_slide = []

    for line in lines:

        stripped = line.strip()

        # Title
        if stripped.startswith("TITLE:"):

            title = stripped[
                len("TITLE:"):
            ].strip()

            continue

        # Slide break
        if stripped == "---":

            if current_slide:

                slides.append(
                    current_slide
                )

                current_slide = []

            continue

        # Preserve blank lines
        if stripped == "":

            if current_slide:

                current_slide.append("")

            continue

        current_slide.append(line)

    # Last slide
    if current_slide:

        slides.append(
            current_slide
        )

    return title, slides


# ============================================================
# TEXT HELPERS
# ============================================================

def get_text_height(
    draw,
    text,
    font
):

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    return bbox[3] - bbox[1]


def get_line_height(
    draw,
    font
):

    bbox = draw.textbbox(
        (0, 0),
        "Ag",
        font=font
    )

    return bbox[3] - bbox[1]


def draw_centered_text(
    draw,
    text,
    y,
    width,
    font,
    fill
):

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    x = (
        width - text_width
    ) / 2

    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill
    )


# ============================================================
# POEM TEXT RENDERING
# ============================================================

def draw_poem_text(
    draw,
    lines,
    width,
    height,
    font_size,
    text_color
):

    font = load_font(font_size)

    line_height = get_line_height(
        draw,
        font
    )

    line_spacing = 20
    stanza_spacing = 45

    # Calculate total height
    total_height = 0

    for line in lines:

        if line == "":
            total_height += stanza_spacing

        else:
            total_height += (
                line_height
                + line_spacing
            )

    total_height -= line_spacing

    # Center vertically
    y = (
        height - total_height
    ) / 2

    for line in lines:

        if line == "":

            y += stanza_spacing

            continue

        draw_centered_text(
            draw,
            line,
            y,
            width,
            font,
            text_color
        )

        y += (
            line_height
            + line_spacing
        )


# ============================================================
# CAROUSEL
# ============================================================

def create_carousel_frame(
    lines,
    theme,
    page_number=None,
    total_pages=None
):

    image = create_background(
        WIDTH,
        HEIGHT,
        theme
    )

    draw = ImageDraw.Draw(image)

    draw_poem_text(
        draw,
        lines,
        WIDTH,
        HEIGHT,
        BODY_FONT_SIZE,
        hex_to_rgb(theme["text"])
    )

    # Page number
    if page_number is not None:

        page_font = load_font(
            PAGE_FONT_SIZE
        )

        page_text = str(page_number)

        bbox = draw.textbbox(
            (0, 0),
            page_text,
            font=page_font
        )

        text_width = (
            bbox[2] - bbox[0]
        )

        margin_right = 55
        margin_bottom = 40

        x = (
            WIDTH
            - text_width
            - margin_right
        )

        y = (
            HEIGHT
            - PAGE_FONT_SIZE
            - margin_bottom
        )

        draw.text(
            (x, y),
            page_text,
            font=page_font,
            fill=hex_to_rgb(
                theme["page"]
            )
        )

    return image


def create_carousel_title(
    title,
    theme
):

    image = create_background(
        WIDTH,
        HEIGHT,
        theme
    )

    draw = ImageDraw.Draw(image)

    font = load_font(
        TITLE_FONT_SIZE
    )

    bbox = draw.textbbox(
        (0, 0),
        title,
        font=font
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    x = (
        WIDTH - text_width
    ) / 2

    y = (
        HEIGHT - text_height
    ) / 2

    draw.text(
        (x, y),
        title,
        font=font,
        fill=hex_to_rgb(
            theme["text"]
        )
    )

    return image


def generate_carousel(
    title,
    slides,
    theme
):

    output_folder = (
        OUTPUT_FOLDER
        / theme["name"].lower()
        / "carousel"
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # Title
    if title:

        title_image = create_carousel_title(
            title,
            theme
        )

        title_image.save(
            output_folder / "01.png"
        )

        start_number = 2

    else:

        start_number = 1

    # Slides
    for index, slide in enumerate(
        slides,
        start=start_number
    ):

        image = create_carousel_frame(
            slide,
            theme,
            index - 1,
            len(slides)
        )

        image.save(
            output_folder
            / f"{index:02d}.png"
        )

    print(
        f"Created Carousel: {output_folder}"
    )


# ============================================================
# REEL TIMING
# ============================================================

def calculate_slide_duration(lines):

    text = " ".join(
        line
        for line in lines
        if line.strip()
    )

    if not text:
        return 1.5

    words = re.findall(
        r"\S+",
        text
    )

    word_count = len(words)

    # --------------------------------------------------------
    # Base timing
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Punctuation
    # --------------------------------------------------------

    punctuation_count = len(
        re.findall(
            r"[,.!?;:]",
            text
        )
    )

    seconds += (
        punctuation_count * 0.12
    )

    # --------------------------------------------------------
    # Dramatic short lines
    # --------------------------------------------------------

    dramatic_words = [
        "split.",
        "shattered.",
        "silence.",
        "alone.",
        "gone.",
        "scum.",
        "good.",
        "bad.",
        "me.",
    ]

    lower_text = text.lower().strip()

    if lower_text in dramatic_words:

        seconds = max(
            seconds,
            2.3
        )

    # --------------------------------------------------------
    # Final limits
    # --------------------------------------------------------

    seconds = max(
        seconds,
        1.7
    )

    seconds = min(
        seconds,
        5.0
    )

    return seconds

# ============================================================
# REEL FRAMES
# ============================================================

def create_reel_title_frame(
    title,
    theme
):

    image = create_background(
        REEL_WIDTH,
        REEL_HEIGHT,
        theme
    )

    draw = ImageDraw.Draw(image)

    font = load_font(
        TITLE_FONT_SIZE
    )

    bbox = draw.textbbox(
        (0, 0),
        title,
        font=font
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    x = (
        REEL_WIDTH - text_width
    ) / 2

    y = (
        REEL_HEIGHT - text_height
    ) / 2

    draw.text(
        (x, y),
        title,
        font=font,
        fill=hex_to_rgb(
            theme["text"]
        )
    )

    return image


def create_reel_frame(
    slide_lines,
    theme
):

    image = create_background(
        REEL_WIDTH,
        REEL_HEIGHT,
        theme
    )

    draw = ImageDraw.Draw(image)

    draw_poem_text(
        draw,
        slide_lines,
        REEL_WIDTH,
        REEL_HEIGHT,
        BODY_FONT_SIZE,
        hex_to_rgb(
            theme["text"]
        )
    )

    return image


# ============================================================
# REEL GENERATION
# ============================================================

def generate_reel(
    title,
    slides,
    theme
):

    output_folder = (
        OUTPUT_FOLDER
        / theme["name"].lower()
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_folder
        / "reel.mp4"
    )

    # Delete old Reel
    if output_file.exists():

        output_file.unlink()

    ffmpeg = (
        imageio_ffmpeg
        .get_ffmpeg_exe()
    )

    command = [
        ffmpeg,

        "-y",

        "-f",
        "rawvideo",

        "-pix_fmt",
        "rgb24",

        "-s",
        f"{REEL_WIDTH}x{REEL_HEIGHT}",

        "-r",
        str(FPS),

        "-i",
        "-",

        "-an",

        "-c:v",
        "libx264",

        "-pix_fmt",
        "yuv420p",

        "-preset",
        "medium",

        "-crf",
        "20",

        str(output_file)
    ]

    print()
    print("Generating Reel...")
    print()

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE
    )

    try:

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        if title:

            print(
                "Title: 3.0 seconds"
            )

            title_image = (
                create_reel_title_frame(
                    title,
                    theme
                )
                .convert("RGB")
            )

            title_bytes = (
                title_image.tobytes()
            )

            title_frames = int(
                TITLE_DURATION * FPS
            )

            # IMPORTANT:
            # The exact same frame is repeated.
            # No fade.
            # No regeneration.
            # No flickering.

            for _ in range(
                title_frames
            ):

                process.stdin.write(
                    title_bytes
                )

        # ----------------------------------------------------
        # POEM SLIDES
        # ----------------------------------------------------

        for index, slide in enumerate(
            slides
        ):

            duration = (
                calculate_slide_duration(
                    slide
                )
            )

            frame_count = int(
                duration * FPS
            )

            print(
                f"Slide {index + 1}: "
                f"{duration:.1f} seconds"
            )

            slide_image = (
                create_reel_frame(
                    slide,
                    theme
                )
                .convert("RGB")
            )

            slide_bytes = (
                slide_image.tobytes()
            )

            # Repeat identical frame.
            # This prevents flickering.

            for _ in range(
                frame_count
            ):

                process.stdin.write(
                    slide_bytes
                )

    except BrokenPipeError:

        print(
            "FFmpeg stopped unexpectedly."
        )

    finally:

        if process.stdin:

            process.stdin.close()

        process.wait()

    if process.returncode != 0:

        raise RuntimeError(
            "FFmpeg failed to create the Reel."
        )

    print()
    print(
        f"Created Reel: {output_file}"
    )


# ============================================================
# THEME SELECTION
# ============================================================

def choose_theme():

    print()
    print("==============================")
    print("        CHOOSE A THEME")
    print("==============================")
    print()

    for key, theme in THEMES.items():

        print(
            f"{key}. {theme['name']}"
        )

    print()

    while True:

        choice = input(
            "Enter 1-4: "
        ).strip()

        if choice in THEMES:

            return THEMES[choice]

        print(
            "Please enter 1, 2, 3, or 4."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("==============================")
    print("       POETRY GENERATOR")
    print("==============================")

    try:

        title, slides = load_poem()

    except Exception as error:

        print()
        print(
            f"ERROR: {error}"
        )

        input(
            "\nPress Enter to exit..."
        )

        return

    if not slides:

        print()
        print(
            "ERROR: No poem slides found."
        )

        input(
            "\nPress Enter to exit..."
        )

        return

    theme = choose_theme()

    print()
    print(
        f"Selected theme: "
        f"{theme['name']}"
    )

    print()
    print(
        "Creating carousel..."
    )

    generate_carousel(
        title,
        slides,
        theme
    )

    generate_reel(
        title,
        slides,
        theme
    )

    print()
    print("==============================")
    print("          COMPLETE")
    print("==============================")
    print()

    print(
        f"Carousel:"
        f"  output/{theme['name'].lower()}/carousel/"
    )

    print(
        f"Reel:"
        f"      output/{theme['name'].lower()}/reel.mp4"
    )

    print()

    input(
        "Press Enter to exit..."
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
