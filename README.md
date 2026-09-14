
# Poetry Carousel

A small Python tool that turns poems into Instagram-ready carousel slides and vertical Reels.

The program reads a poem from `poem.txt`, generates clean visual slides using Pillow, and creates a vertical MP4 Reel using FFmpeg.

## Features

* Generate Instagram carousel slides
* Generate vertical 1080×1920 Reels
* Automatic Reel timing based on word count and punctuation
* 3-second title screen
* Four visual themes:

  * Midnight
  * Paper
  * Dusk
  * Ember
* Custom `.ttf` font support
* Minimal monochrome/gradient aesthetic
* Simple text-based poem format

## Requirements

* Python 3.10+
* Pillow
* imageio-ffmpeg

Install the dependencies with:

```bash
pip install pillow imageio-ffmpeg
```

## Project Structure

```text
Poetry-carousal/
│
├── main.py
├── poem.txt
├── font.ttf
├── .gitignore
└── README.md
```

The `output/` directory is generated automatically and is not tracked by Git.

## Writing a Poem

Create a file called `poem.txt`.

Use `TITLE:` for the title and `---` to separate slides.

Example:

```text
TITLE: The Swordsman

There once was a swordsman
Who was called the greatest

---

Won every match
No one even came close

---

He had a scar
Along his left eye

---

"What's that scar?"
"It's from a sword."

---

"Who could've been
skilled enough to hurt you?"

---

"Me."
```

Blank lines are preserved as stanza breaks.

## Running the Program

Run:

```bash
python main.py
```

The program will ask you to choose a theme:

```text
1. Midnight
2. Paper
3. Dusk
4. Ember
```

After generation, the files will be placed inside:

```text
output/
```

For example:

```text
output/
└── midnight/
    ├── carousel/
    │   ├── 01.png
    │   ├── 02.png
    │   └── ...
    │
    └── reel.mp4
```

## Custom Font

Place your `.ttf` font in the project directory and name it:

```text
font.ttf
```

If you use a different filename, update `FONT_PATH` in `main.py`.

Make sure you have permission to redistribute the font if you commit it to the repository.

## Themes

### Midnight

Dark, minimal, and monochrome.

### Paper

Warm off-white background with dark text.

### Dusk

Dark blue-to-purple gradient.

### Ember

Black-to-deep-red gradient.

## Reel Timing

The title remains on screen for exactly 3 seconds.

Poem slides are automatically timed according to their word count and punctuation, with minimum and maximum limits to keep the Reel readable.

## Output

The generated carousel uses a 1080×1350 format.

The generated Reel uses a 1080×1920 vertical format suitable for Instagram Reels.

## License

This project is provided as-is for personal and creative use.

If you redistribute or modify the project, make sure any fonts or other third-party assets you include have licenses that permit redistribution.
