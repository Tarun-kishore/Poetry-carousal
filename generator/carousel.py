from PIL import ImageDraw

from .config import (
    WIDTH,
    HEIGHT,
    TITLE_FONT_SIZE,
    BODY_FONT_SIZE,
    PAGE_FONT_SIZE,
    OUTPUT_FOLDER,
)

from .text_renderer import (
    load_font,
    hex_to_rgb,
    create_background,
    draw_poem_text,
)


def create_carousel_title(title, theme):

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


def create_carousel_frame(
    lines,
    theme,
    page_number=None
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

    if page_number is not None:

        page_font = load_font(
            PAGE_FONT_SIZE
        )

        page_text = str(
            page_number
        )

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
            WIDTH -
            text_width -
            margin_right
        )

        y = (
            HEIGHT -
            PAGE_FONT_SIZE -
            margin_bottom
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


def generate_carousel(
    title,
    slides,
    theme
):

    output_folder = (
        OUTPUT_FOLDER /
        theme["name"].lower() /
        "carousel"
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # ------------------------------
    # TITLE
    # ------------------------------

    if title:

        title_image = (
            create_carousel_title(
                title,
                theme
            )
        )

        title_image.save(
            output_folder / "01.png"
        )

        start_number = 2

    else:

        start_number = 1

    # ------------------------------
    # POEM SLIDES
    # ------------------------------

    for index, slide in enumerate(
        slides,
        start=start_number
    ):

        image = create_carousel_frame(
            slide,
            theme,
            index - 1
        )

        image.save(
            output_folder /
            f"{index:02d}.png"
        )

    print(
        f"Created Carousel: {output_folder}"
    )
