from generator.poem_parser import load_poem
from generator.themes import choose_theme
from generator.carousel import generate_carousel
from generator.reel import generate_reel
from generator.analysis import analyze_poem
from generator.modes import choose_reel_mode


def main():
    print()
    print("==============================")
    print("       POETRY GENERATOR")
    print("==============================")

    try:
        title, slides = load_poem()
    except Exception as error:
        print()
        print(f"ERROR: {error}")
        input("\nPress Enter to exit...")
        return

    if not slides:
        print()
        print("ERROR: No poem slides found.")
        input("\nPress Enter to exit...")
        return

    print()
    print(f"Title: {title or '(untitled)'}")
    print()

    analyze_poem(title, slides)

    theme = choose_theme()
    mode, mood = choose_reel_mode()

    print()
    print(f"Selected theme: {theme['name']}")
    print(f"Reel mode:      {mode}")
    print(f"Reel mood:      {mood}")
    print()

    print("Creating carousel...")
    generate_carousel(title, slides, theme)

    generate_reel(
        title,
        mood,
        mode,
        slides,
        theme
    )

    print()
    print("==============================")
    print("          COMPLETE")
    print("==============================")
    print()

    print(
        f"Carousel: "
        f"output/{theme['name'].lower()}/carousel/"
    )
    print(
        f"Reel: "
        f"output/{theme['name'].lower()}/reel.mp4"
    )
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
