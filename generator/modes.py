def choose_reel_mode():
    print()
    print("==============================")
    print("       CHOOSE REEL MODE")
    print("==============================")
    print()
    print("1. Auto")
    print("2. Minimal")
    print("3. Cinematic")
    print("4. Atmospheric")
    print()

    while True:
        choice = input("Enter 1-4: ").strip()

        if choice in {"1", "2", "3", "4"}:
            break

        print("Please enter 1, 2, 3, or 4.")

    modes = {
        "1": "auto",
        "2": "minimal",
        "3": "cinematic",
        "4": "atmospheric",
    }

    mode = modes[choice]

    if mode == "auto":
        print()
        print("Auto mode uses the mood you choose below.")

    print()
    print("==============================")
    print("       CHOOSE REEL MOOD")
    print("==============================")
    print()
    print("1. Storm")
    print("2. Horror")
    print("3. Melancholy")
    print("4. Ocean")
    print("5. Dream")
    print("6. Dark")
    print("7. Calm")
    print("8. Mystery")
    print()

    moods = {
        "1": "storm",
        "2": "horror",
        "3": "melancholy",
        "4": "ocean",
        "5": "dream",
        "6": "dark",
        "7": "calm",
        "8": "mystery",
    }

    while True:
        choice = input("Enter 1-8: ").strip()

        if choice in moods:
            return mode, moods[choice]

        print("Please enter a number from 1 to 8.")
