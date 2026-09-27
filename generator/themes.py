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
