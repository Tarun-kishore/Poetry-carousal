import math

from PIL import Image, ImageDraw, ImageFont
from .config import FONT_PATH


def load_font(size):
    if not FONT_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {FONT_PATH}.\n"
            f"Put your .ttf font beside main.py "
            f"and rename it to font.ttf."
        )

    return ImageFont.truetype(str(FONT_PATH), size)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i + 2], 16)
        for i in (0, 2, 4)
    )


def interpolate_color(start, end, amount):
    amount = max(0, min(1, amount))

    return tuple(
        int(start[i] + (end[i] - start[i]) * amount)
        for i in range(3)
    )


def create_background(
    width,
    height,
    theme,
    progress=0.0,
    movement=True
):
    if theme["type"] == "solid":
        return Image.new(
            "RGB",
            (width, height),
            hex_to_rgb(theme["background"])
        )

    # The base gradient is deliberately subtle and stable.
    # Animated objects are handled by Atmosphere.
    small_width = max(1, width // 4)
    small_height = max(1, height // 4)

    start = hex_to_rgb(theme["gradient_start"])
    end = hex_to_rgb(theme["gradient_end"])

    image = Image.new(
        "RGB",
        (small_width, small_height)
    )

    draw = ImageDraw.Draw(image)
    max_distance = max(
        1,
        small_width + small_height - 2
    )

    if movement:
        # Tiny non-wrapping oscillation. This is intentionally
        # much weaker than the actual atmospheric animation.
        movement_amount = (
            0.035 *
            (
                0.5 -
                0.5 *
                math.cos(
                    progress * math.pi * 2
                )
            )
        )
    else:
        movement_amount = 0.0

    for y in range(small_height):
        for x in range(small_width):
            ratio = (x + y) / max_distance

            ratio = max(
                0.0,
                min(
                    1.0,
                    ratio + movement_amount
                )
            )

            color = interpolate_color(
                start,
                end,
                ratio
            )

            draw.point(
                (x, y),
                fill=color
            )

    return image.resize(
        (width, height),
        Image.Resampling.BILINEAR
    )


def get_line_height(draw, font):
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
    fill,
    x_offset=0
):
    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = bbox[2] - bbox[0]

    x = (width - text_width) / 2
    x += x_offset

    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill
    )


def draw_poem_text(
    draw,
    lines,
    width,
    height,
    font_size,
    text_color,
    text_drift=0
):
    font = load_font(font_size)

    line_height = get_line_height(
        draw,
        font
    )

    line_spacing = 20
    stanza_spacing = 45
    total_height = 0

    for line in lines:
        if line == "":
            total_height += stanza_spacing
        else:
            total_height += (
                line_height +
                line_spacing
            )

    total_height -= line_spacing

    y = (height - total_height) / 2

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
            text_color,
            x_offset=text_drift
        )

        y += line_height + line_spacing
