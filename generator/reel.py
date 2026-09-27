from PIL import Image, ImageDraw
import math
import subprocess
import imageio_ffmpeg

from .config import (
    REEL_WIDTH,
    REEL_HEIGHT,
    FPS,
    TITLE_DURATION,
    TITLE_FONT_SIZE,
    BODY_FONT_SIZE,
    OUTPUT_FOLDER,
    MAX_TEXT_DRIFT,
)

from .text_renderer import (
    load_font,
    hex_to_rgb,
    create_background,
    draw_poem_text,
)

from .timing import calculate_slide_duration
from .atmosphere import Atmosphere


def create_reel_title_frame(
    title,
    theme,
    progress=0.0,
    animated=False
):
    image = create_background(
        REEL_WIDTH,
        REEL_HEIGHT,
        theme,
        progress,
        movement=animated
    )

    draw = ImageDraw.Draw(image)
    font = load_font(TITLE_FONT_SIZE)

    bbox = draw.textbbox(
        (0, 0),
        title,
        font=font
    )

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (REEL_WIDTH - text_width) / 2
    y = (REEL_HEIGHT - text_height) / 2

    draw.text(
        (x, y),
        title,
        font=font,
        fill=hex_to_rgb(theme["text"])
    )

    return image


def create_reel_frame(
    slide_lines,
    theme,
    progress,
    atmosphere,
    animated_background
):
    # The base background remains visually stable.
    # Motion is supplied by the atmosphere layer.
    image = create_background(
        REEL_WIDTH,
        REEL_HEIGHT,
        theme,
        progress,
        movement=animated_background
    )

    image = atmosphere.apply(
        image,
        progress
    )

    text_drift = (
        MAX_TEXT_DRIFT *
        (
            0.5 -
            0.5 *
            math.cos(
                progress * math.pi * 2
            )
        )
    )

    draw = ImageDraw.Draw(image)

    draw_poem_text(
        draw,
        slide_lines,
        REEL_WIDTH,
        REEL_HEIGHT,
        BODY_FONT_SIZE,
        hex_to_rgb(theme["text"]),
        text_drift=text_drift
    )

    return image


def write_frame(process, image):
    image = image.convert("RGB")
    process.stdin.write(image.tobytes())


def generate_reel(
    title,
    mood,
    mode,
    slides,
    theme
):
    output_folder = (
        OUTPUT_FOLDER /
        theme["name"].lower()
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = output_folder / "reel.mp4"

    if output_file.exists():
        output_file.unlink()

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

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
        str(output_file),
    ]

    print()
    print("Generating Reel...")
    print()

    atmosphere = Atmosphere(
        mood=mood,
        mode=mode,
        seed=42
    )

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE
    )

    # Keep the base gradient essentially stable.
    # Cinematic mode gets only the tiny existing gradient motion.
    animated_background = mode == "cinematic"

    try:
        if title:
            print(
                f"Title: {TITLE_DURATION:.2f} seconds"
            )

            title_frames = int(
                TITLE_DURATION * FPS
            )

            for frame in range(title_frames):
                progress = (
                    frame /
                    max(1, title_frames - 1)
                )

                # Atmospheric animation begins with the poem,
                # not the title. Cinematic may animate the base
                # background very subtly.
                title_animation = (
                    mode == "cinematic"
                )

                image = create_reel_title_frame(
                    title,
                    theme,
                    progress,
                    animated=title_animation
                )

                write_frame(
                    process,
                    image
                )

        # Show fuller chunks on screen: combine adjacent poem slides in pairs.
        # The carousel remains unchanged; this only affects Reel pacing/layout.
        reel_slides = []
        for start in range(0, len(slides), 2):
            chunk = slides[start:start + 2]
            combined = []
            for part_index, part in enumerate(chunk):
                if part_index:
                    combined.append("")
                combined.extend(part)
            reel_slides.append(combined)

        total_slides = len(reel_slides)

        for index, slide in enumerate(reel_slides):
            duration = calculate_slide_duration(
                slide,
                index,
                total_slides
            )

            frame_count = int(
                duration * FPS
            )

            print(
                f"Slide {index + 1}: "
                f"{duration:.1f} seconds"
            )

            for frame in range(frame_count):
                local_progress = (
                    frame /
                    max(1, frame_count - 1)
                )

                if total_slides <= 1:
                    global_progress = 1.0
                else:
                    global_progress = (
                        index +
                        local_progress
                    ) / total_slides

                image = create_reel_frame(
                    slide,
                    theme,
                    global_progress,
                    atmosphere,
                    animated_background
                )

                write_frame(
                    process,
                    image
                )

    except BrokenPipeError:
        print("FFmpeg stopped unexpectedly.")

    finally:
        if process.stdin:
            process.stdin.close()

        process.wait()

    if process.returncode != 0:
        raise RuntimeError(
            "FFmpeg failed to create the Reel."
        )

    print()
    print(f"Created Reel: {output_file}")
